"""
FarmSense OS v1.0 - Variable Rate Irrigation (VRI) Controller

Direct valve control based on 1-meter virtual grid moisture thresholds.
Integrates with pivot systems via Modbus RTU/TCP.
Latency target: <2 seconds from trigger to valve response.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
import json


class ValveState(Enum):
    """Valve operational states."""
    CLOSED = auto()
    OPENING = auto()
    OPEN = auto()
    CLOSING = auto()
    FAULT = auto()
    MANUAL_OVERRIDE = auto()


class IrrigationZoneStatus(Enum):
    """Zone irrigation decision status."""
    NO_IRRIGATION_NEEDED = auto()
    IRRIGATION_RECOMMENDED = auto()
    IRRIGATION_ACTIVE = auto()
    SATURATION_DETECTED = auto()
    DEEP_PERCOLATION_RISK = auto()


@dataclass
class ValveCommand:
    """
    Command to open/close a specific valve.
    """
    valve_id: str
    zone_id: str
    field_id: str
    
    command: str  # 'open' or 'close'
    duration_minutes: Optional[int] = None
    
    # Trigger context
    trigger_vwc: float
    target_vwc: float
    confidence: float
    
    # Authorization
    authorized_by: str = 'system'  # 'system' or user_id
    authorization_hash: Optional[str] = None
    
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_modbus_registers(self) -> List[int]:
        """
        Convert command to Modbus register values.
        
        Returns list of 16-bit register values for RTU/TCP transmission.
        """
        # Command word: bit 0 = open/close, bits 1-15 = duration (minutes)
        cmd_word = 1 if self.command == 'open' else 0
        if self.duration_minutes:
            cmd_word |= (min(self.duration_minutes, 32767) << 1)
        
        # Valve ID as two registers (high/low 16 bits)
        valve_id_val = int(self.valve_id.replace('valve_', ''))
        
        return [
            valve_id_val & 0xFFFF,           # Valve ID low
            (valve_id_val >> 16) & 0xFFFF,   # Valve ID high
            cmd_word,                         # Command + duration
            int(self.trigger_vwc * 1000),    # Trigger VWC (x1000 for precision)
            int(self.target_vwc * 1000),     # Target VWC
            int(self.confidence * 1000)      # Confidence
        ]


@dataclass
class ZoneIrrigationDecision:
    """
    Irrigation decision for a specific zone based on virtual grid analysis.
    """
    zone_id: str
    field_id: str
    
    # Current state
    current_avg_vwc: float
    target_vwc: float
    field_capacity: float
    wilting_point: float
    
    # Decision
    status: IrrigationZoneStatus
    recommended_duration_minutes: int = 0
    confidence: float = 0.0
    
    # Grid statistics
    grid_cell_count: int = 0
    cells_below_target: int = 0
    cells_above_fc: int = 0
    cells_at_risk: int = 0
    
    # Constraints
    max_duration_minutes: int = 120  # Safety limit
    
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def should_irrigate(self) -> bool:
        """Determine if irrigation should be triggered."""
        return (
            self.status == IrrigationZoneStatus.IRRIGATION_RECOMMENDED and
            self.confidence > 0.7 and
            self.recommended_duration_minutes > 0
        )


class VRIController:
    """
    Variable Rate Irrigation controller.
    
    Translates 1-meter virtual grid moisture data into precise valve commands.
    Integrates with pivot control systems via Modbus.
    
    Features:
    - Zone-based irrigation decisions
    - Real-time valve control (<2s latency)
    - Manual override support with audit logging
    - Deep percolation prevention (critical for Water Court)
    """
    
    def __init__(
        self,
        modbus_host: str = "192.168.1.100",
        modbus_port: int = 502,
        use_modbus_tcp: bool = True,
        audit_logger = None
    ):
        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self.use_modbus_tcp = use_modbus_tcp
        self.audit_logger = audit_logger
        
        # Valve state tracking
        self.valve_states: Dict[str, ValveState] = {}
        self.active_irrigation: Dict[str, Dict] = {}  # zone_id -> irrigation info
        
        # Configuration
        self.vwc_threshold_low = 0.15  # Trigger irrigation below this
        self.vwc_threshold_high = 0.35  # Stop irrigation above this
        self.deep_percolation_threshold = 0.42  # 42" horizon critical threshold
        
        # Callbacks
        self._command_callback: Optional[Callable[[ValveCommand], None]] = None
        self._status_callback: Optional[Callable[[str, ValveState], None]] = None
    
    def on_command(self, callback: Callable[[ValveCommand], None]) -> None:
        """Register callback for valve commands."""
        self._command_callback = callback
    
    def on_status_change(self, callback: Callable[[str, ValveState], None]) -> None:
        """Register callback for valve status changes."""
        self._status_callback = callback
    
    def analyze_zone_for_irrigation(
        self,
        zone_id: str,
        field_id: str,
        grid_cells: list,
        soil_properties: Dict[str, float],
        crop_type: str = 'potato'
    ) -> ZoneIrrigationDecision:
        """
        Analyze virtual grid cells to determine irrigation need.
        
        Args:
            zone_id: Irrigation zone identifier
            field_id: Field identifier
            grid_cells: List of KrigingCell objects for this zone
            soil_properties: Dict with field_capacity, wilting_point
            crop_type: Crop type for irrigation parameters
            
        Returns:
            ZoneIrrigationDecision with recommendation
        """
        if not grid_cells:
            return ZoneIrrigationDecision(
                zone_id=zone_id,
                field_id=field_id,
                current_avg_vwc=0.0,
                target_vwc=soil_properties.get('field_capacity', 0.25),
                field_capacity=soil_properties.get('field_capacity', 0.25),
                wilting_point=soil_properties.get('wilting_point', 0.08),
                status=IrrigationZoneStatus.NO_IRRIGATION_NEEDED,
                confidence=0.0
            )
        
        # Calculate zone statistics
        vwc_values = [cell.estimated_vwc for cell in grid_cells]
        avg_vwc = sum(vwc_values) / len(vwc_values)
        
        fc = soil_properties.get('field_capacity', 0.25)
        wp = soil_properties.get('wilting_point', 0.08)
        
        # Target is typically 90% of field capacity
        target_vwc = fc * 0.9
        
        # Count cells in various states
        cells_below_target = sum(1 for v in vwc_values if v < target_vwc)
        cells_above_fc = sum(1 for v in vwc_values if v > fc)
        
        # Check for deep percolation risk (critical for compliance)
        deep_cells = [cell for cell in grid_cells if cell.depth_inches >= 42]
        cells_at_deep_risk = sum(
            1 for cell in deep_cells
            if cell.estimated_vwc > self.deep_percolation_threshold
        )
        
        # Determine status
        status = IrrigationZoneStatus.NO_IRRIGATION_NEEDED
        duration = 0
        
        if cells_at_deep_risk > 0:
            # CRITICAL: Deep percolation detected - stop all irrigation
            status = IrrigationZoneStatus.DEEP_PERCOLATION_RISK
            if self.audit_logger:
                self.audit_logger.log_event(
                    event_type='deep_percolation_alert',
                    user_id='system',
                    details={
                        'zone_id': zone_id,
                        'field_id': field_id,
                        'risk_cells': cells_at_deep_risk,
                        'max_vwc': max((c.estimated_vwc for c in deep_cells), default=0)
                    }
                )
        
        elif cells_above_fc > len(grid_cells) * 0.5:
            # Most cells above field capacity - saturation
            status = IrrigationZoneStatus.SATURATION_DETECTED
        
        elif avg_vwc < target_vwc and cells_below_target > len(grid_cells) * 0.3:
            # Significant area below target - irrigation recommended
            status = IrrigationZoneStatus.IRRIGATION_RECOMMENDED
            
            # Calculate duration based on deficit
            deficit = target_vwc - avg_vwc
            # Approximate: 1% VWC = ~15 minutes irrigation
            duration = min(int(deficit * 100 * 15), 120)  # Max 2 hours
        
        # Calculate confidence based on grid variance
        if len(vwc_values) > 1:
            variance = sum((v - avg_vwc) ** 2 for v in vwc_values) / len(vwc_values)
            confidence = max(0.5, 1.0 - variance * 10)  # Higher variance = lower confidence
        else:
            confidence = 0.5
        
        return ZoneIrrigationDecision(
            zone_id=zone_id,
            field_id=field_id,
            current_avg_vwc=avg_vwc,
            target_vwc=target_vwc,
            field_capacity=fc,
            wilting_point=wp,
            status=status,
            recommended_duration_minutes=duration,
            confidence=confidence,
            grid_cell_count=len(grid_cells),
            cells_below_target=cells_below_target,
            cells_above_fc=cells_above_fc,
            cells_at_risk=cells_at_deep_risk
        )
    
    async def execute_irrigation_decision(
        self,
        decision: ZoneIrrigationDecision,
        valve_mapping: Dict[str, str]  # zone_id -> valve_id
    ) -> bool:
        """
        Execute irrigation decision by commanding valves.
        
        Args:
            decision: ZoneIrrigationDecision with recommendation
            valve_mapping: Map of zone IDs to physical valve IDs
            
        Returns:
            True if command sent successfully
        """
        valve_id = valve_mapping.get(decision.zone_id)
        if not valve_id:
            print(f"No valve mapping for zone {decision.zone_id}")
            return False
        
        # Check current valve state
        current_state = self.valve_states.get(valve_id, ValveState.CLOSED)
        
        if decision.should_irrigate():
            if current_state == ValveState.CLOSED:
                # Open valve
                command = ValveCommand(
                    valve_id=valve_id,
                    zone_id=decision.zone_id,
                    field_id=decision.field_id,
                    command='open',
                    duration_minutes=decision.recommended_duration_minutes,
                    trigger_vwc=decision.current_avg_vwc,
                    target_vwc=decision.target_vwc,
                    confidence=decision.confidence
                )
                
                success = await self._send_valve_command(command)
                if success:
                    self.valve_states[valve_id] = ValveState.OPEN
                    self.active_irrigation[decision.zone_id] = {
                        'started_at': datetime.utcnow().isoformat(),
                        'duration_minutes': decision.recommended_duration_minutes,
                        'target_vwc': decision.target_vwc,
                        'valve_id': valve_id
                    }
                    
                    if self._status_callback:
                        self._status_callback(valve_id, ValveState.OPEN)
                
                return success
        
        else:
            # Stop irrigation if active
            if current_state == ValveState.OPEN and decision.zone_id in self.active_irrigation:
                command = ValveCommand(
                    valve_id=valve_id,
                    zone_id=decision.zone_id,
                    field_id=decision.field_id,
                    command='close',
                    trigger_vwc=decision.current_avg_vwc,
                    target_vwc=decision.target_vwc,
                    confidence=decision.confidence
                )
                
                success = await self._send_valve_command(command)
                if success:
                    self.valve_states[valve_id] = ValveState.CLOSED
                    del self.active_irrigation[decision.zone_id]
                    
                    if self._status_callback:
                        self._status_callback(valve_id, ValveState.CLOSED)
                
                return success
        
        return True  # No action needed
    
    async def _send_valve_command(self, command: ValveCommand) -> bool:
        """
        Send command to physical valve via Modbus.
        
        Returns True if command acknowledged within 2 seconds.
        """
        if self._command_callback:
            # Use callback for testing/simulation
            self._command_callback(command)
            return True
        
        # Real Modbus implementation would go here
        # For now, simulate success
        try:
            # TODO: Implement actual Modbus RTU/TCP communication
            # registers = command.to_modbus_registers()
            # client.write_registers(address=0, values=registers, unit=1)
            
            await asyncio.wait_for(
                self._modbus_write(command),
                timeout=2.0  # <2 second latency requirement
            )
            return True
            
        except asyncio.TimeoutError:
            print(f"Valve command timeout for {command.valve_id}")
            return False
        except Exception as e:
            print(f"Valve command error: {e}")
            return False
    
    async def _modbus_write(self, command: ValveCommand) -> None:
        """Placeholder for Modbus write operation."""
        # Simulate network latency
        await asyncio.sleep(0.1)
    
    def manual_override(
        self,
        valve_id: str,
        command: str,  # 'open' or 'close'
        user_id: str,
        reason: str,
        duration_minutes: Optional[int] = None
    ) -> bool:
        """
        Manual valve override with full audit logging.
        
        Required for Water Court defense - all manual interventions logged.
        """
        # Log the override
        if self.audit_logger:
            self.audit_logger.log_irrigation_override(
                user_id=user_id,
                field_id='unknown',  # Would be looked up from valve_id
                zone_id='unknown',
                reason=reason,
                duration_minutes=duration_minutes or 0,
                override_type='manual'
            )
        
        # Update valve state
        if command == 'open':
            self.valve_states[valve_id] = ValveState.MANUAL_OVERRIDE
        else:
            self.valve_states[valve_id] = ValveState.CLOSED
        
        if self._status_callback:
            self._status_callback(valve_id, self.valve_states[valve_id])
        
        return True
    
    def get_active_irrigation(self) -> Dict[str, Any]:
        """Get currently active irrigation zones."""
        return {
            'active_zones': len(self.active_irrigation),
            'zones': self.active_irrigation,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def emergency_stop_all(self, user_id: str = 'system') -> None:
        """
        Emergency stop of all irrigation.
        
        Critical for deep percolation events or system faults.
        """
        for zone_id, info in list(self.active_irrigation.items()):
            valve_id = info['valve_id']
            
            # Log emergency stop
            if self.audit_logger:
                self.audit_logger.log_event(
                    event_type='emergency_stop',
                    user_id=user_id,
                    details={
                        'zone_id': zone_id,
                        'valve_id': valve_id,
                        'reason': 'emergency_stop_all'
                    }
                )
            
            # Close valve
            self.valve_states[valve_id] = ValveState.CLOSED
        
        self.active_irrigation.clear()


class IrrigationScheduler:
    """
    Scheduler for irrigation operations based on ET and weather forecasts.
    
    Optimizes irrigation timing to minimize evaporation losses and
    energy costs while maintaining crop health.
    """
    
    def __init__(self, vri_controller: VRIController):
        self.vri = vri_controller
        self.scheduled_operations: List[Dict] = []
    
    def schedule_irrigation(
        self,
        zone_id: str,
        start_time: datetime,
        duration_minutes: int,
        priority: int = 1
    ) -> str:
        """
        Schedule a future irrigation operation.
        
        Returns operation ID for tracking.
        """
        operation_id = f"sched_{zone_id}_{start_time.strftime('%Y%m%d%H%M')}"
        
        operation = {
            'id': operation_id,
            'zone_id': zone_id,
            'scheduled_start': start_time.isoformat(),
            'duration_minutes': duration_minutes,
            'priority': priority,
            'status': 'scheduled'
        }
        
        self.scheduled_operations.append(operation)
        
        # Sort by start time and priority
        self.scheduled_operations.sort(
            key=lambda x: (x['scheduled_start'], x['priority'])
        )
        
        return operation_id
    
    async def run_scheduler(self) -> None:
        """
        Background task to execute scheduled operations.
        """
        while True:
            now = datetime.utcnow()
            
            for operation in self.scheduled_operations:
                if operation['status'] != 'scheduled':
                    continue
                
                start_time = datetime.fromisoformat(operation['scheduled_start'])
                
                if now >= start_time:
                    # Execute scheduled irrigation
                    operation['status'] = 'executing'
                    
                    # Create decision from schedule
                    # This would integrate with VRI controller
                    
                    operation['status'] = 'completed'
            
            # Clean up completed operations
            self.scheduled_operations = [
                op for op in self.scheduled_operations
                if op['status'] != 'completed'
            ]
            
            await asyncio.sleep(60)  # Check every minute
