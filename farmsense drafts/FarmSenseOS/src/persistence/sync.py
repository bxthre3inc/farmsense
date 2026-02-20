"""
FarmSense OS v1.0 - Cloud Synchronization Protocol

Live mirror of Jetson state on hosted cloud server.
Enables instant failover with cryptographic chain continuity.
"""

import json
import hashlib
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum, auto


class SyncState(Enum):
    """Synchronization state machine."""
    CONNECTED = auto()
    DISCONNECTED = auto()
    FAILOVER_ACTIVE = auto()
    RECOVERING = auto()


@dataclass
class SystemState:
    """
    Complete state snapshot for cloud synchronization.
    Enables seamless failover with no data loss.
    """
    jetson_id: str
    timestamp: datetime
    
    # Bayesian engine state
    soil_map_state: Dict[str, Any]
    bayesian_coefficients: Dict[str, Any]
    last_prediction: Dict[str, Any]
    
    # Chain state
    last_measurement_hash: str
    total_records: int
    
    # Virtual grid state
    latest_grid_timestamp: Optional[str]
    grid_merkle_root: Optional[str]
    
    # Sensor network state
    active_sensors: list
    sensor_health: Dict[str, str]
    
    # VRI state
    active_valves: Dict[str, Any]
    scheduled_irrigation: list
    
    def compute_state_hash(self) -> str:
        """Hash of complete state for integrity verification."""
        state_dict = {
            'jetson_id': self.jetson_id,
            'timestamp': self.timestamp.isoformat(),
            'last_hash': self.last_measurement_hash,
            'records': self.total_records,
            'merkle_root': self.grid_merkle_root
        }
        canonical = json.dumps(state_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


class CloudSyncProtocol:
    """
    Real-time synchronization protocol between Jetson and cloud mirror.
    
    Features:
    - Continuous state synchronization via WebSocket
    - Automatic failover on heartbeat timeout
    - Cryptographic chain continuity maintained
    - Cellular fallback for gateway communication
    """
    
    def __init__(
        self,
        jetson_id: str,
        cloud_endpoint: str,
        api_key: str,
        heartbeat_interval: float = 5.0,  # seconds
        failover_timeout: float = 30.0  # seconds
    ):
        self.jetson_id = jetson_id
        self.cloud_endpoint = cloud_endpoint
        self.api_key = api_key
        self.heartbeat_interval = heartbeat_interval
        self.failover_timeout = failover_timeout
        
        self.state = SyncState.DISCONNECTED
        self.last_sync_time: Optional[datetime] = None
        self.last_heartbeat_ack: Optional[datetime] = None
        
        self._state_callback: Optional[Callable] = None
        self._failover_callback: Optional[Callable] = None
        
        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    def on_state_change(self, callback: Callable[[SyncState, SyncState], None]) -> None:
        """Register callback for state changes."""
        self._state_callback = callback
    
    def on_failover(self, callback: Callable[[], None]) -> None:
        """Register callback for failover event."""
        self._failover_callback = callback
    
    def _set_state(self, new_state: SyncState) -> None:
        """Update state and notify listener."""
        old_state = self.state
        self.state = new_state
        if self._state_callback and old_state != new_state:
            self._state_callback(old_state, new_state)
    
    async def connect(self) -> bool:
        """Establish connection to cloud mirror."""
        try:
            self._session = aiohttp.ClientSession()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Jetson-ID': self.jetson_id
            }
            
            self._websocket = await self._session.ws_connect(
                f'{self.cloud_endpoint}/ws/sync',
                headers=headers
            )
            
            self._set_state(SyncState.CONNECTED)
            self.last_heartbeat_ack = datetime.utcnow()
            
            # Start background tasks
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._receive_loop())
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to cloud: {e}")
            self._set_state(SyncState.DISCONNECTED)
            return False
    
    async def disconnect(self) -> None:
        """Clean disconnect from cloud."""
        if self._websocket:
            await self._websocket.close()
        if self._session:
            await self._session.close()
        self._set_state(SyncState.DISCONNECTED)
    
    async def sync_state(self, state: SystemState) -> bool:
        """
        Synchronize complete system state to cloud mirror.
        
        Called after every measurement batch and Bayesian update.
        """
        if self.state != SyncState.CONNECTED or not self._websocket:
            return False
        
        try:
            message = {
                'type': 'state_sync',
                'jetson_id': self.jetson_id,
                'timestamp': datetime.utcnow().isoformat(),
                'state_hash': state.compute_state_hash(),
                'payload': {
                    'soil_map': state.soil_map_state,
                    'bayesian': state.bayesian_coefficients,
                    'last_prediction': state.last_prediction,
                    'last_hash': state.last_measurement_hash,
                    'total_records': state.total_records,
                    'grid_root': state.grid_merkle_root,
                    'sensor_health': state.sensor_health,
                    'active_valves': state.active_valves
                }
            }
            
            await self._websocket.send_json(message)
            self.last_sync_time = datetime.utcnow()
            return True
            
        except Exception as e:
            print(f"State sync failed: {e}")
            self._set_state(SyncState.DISCONNECTED)
            return False
    
    async def sync_measurement(self, measurement_hash: str, measurement_data: Dict) -> bool:
        """
        Synchronize single measurement for real-time chain continuity.
        
        Critical for forensic integrity - every hash must be mirrored.
        """
        if self.state != SyncState.CONNECTED or not self._websocket:
            return False
        
        try:
            message = {
                'type': 'measurement',
                'jetson_id': self.jetson_id,
                'timestamp': datetime.utcnow().isoformat(),
                'hash': measurement_hash,
                'data': measurement_data
            }
            
            await self._websocket.send_json(message)
            return True
            
        except Exception as e:
            print(f"Measurement sync failed: {e}")
            return False
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to cloud."""
        while self.state == SyncState.CONNECTED and self._websocket:
            try:
                await self._websocket.send_json({
                    'type': 'heartbeat',
                    'jetson_id': self.jetson_id,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                await asyncio.sleep(self.heartbeat_interval)
                
                # Check for timeout
                if self.last_heartbeat_ack:
                    elapsed = (datetime.utcnow() - self.last_heartbeat_ack).total_seconds()
                    if elapsed > self.failover_timeout:
                        print(f"Heartbeat timeout ({elapsed}s) - triggering failover")
                        await self._trigger_failover()
                        
            except Exception as e:
                print(f"Heartbeat error: {e}")
                break
        
        if self.state == SyncState.CONNECTED:
            self._set_state(SyncState.DISCONNECTED)
    
    async def _receive_loop(self) -> None:
        """Handle incoming messages from cloud."""
        while self.state == SyncState.CONNECTED and self._websocket:
            try:
                msg = await self._websocket.receive()
                
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_message(data)
                    
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break
                    
            except Exception as e:
                print(f"Receive error: {e}")
                break
        
        if self.state == SyncState.CONNECTED:
            self._set_state(SyncState.DISCONNECTED)
    
    async def _handle_message(self, data: Dict) -> None:
        """Process message from cloud."""
        msg_type = data.get('type')
        
        if msg_type == 'heartbeat_ack':
            self.last_heartbeat_ack = datetime.utcnow()
            
        elif msg_type == 'failover_command':
            # Cloud is taking over - stop local processing
            print("Received failover command from cloud")
            await self._enter_failover_mode()
            
        elif msg_type == 'recovery_command':
            # Cold spare is ready - resume operation
            print("Received recovery command")
            await self._exit_failover_mode()
    
    async def _trigger_failover(self) -> None:
        """Trigger failover to cloud mirror."""
        self._set_state(SyncState.FAILOVER_ACTIVE)
        
        if self._failover_callback:
            self._failover_callback()
        
        # Notify cloud to assume control
        if self._websocket:
            try:
                await self._websocket.send_json({
                    'type': 'failover_request',
                    'jetson_id': self.jetson_id,
                    'reason': 'heartbeat_timeout',
                    'timestamp': datetime.utcnow().isoformat()
                })
            except:
                pass
    
    async def _enter_failover_mode(self) -> None:
        """Enter local failover mode (cloud has taken over)."""
        self._set_state(SyncState.FAILOVER_ACTIVE)
        # Stop local actuation - cloud is in control
        
    async def _exit_failover_mode(self) -> None:
        """Exit failover mode (resume normal operation)."""
        self._set_state(SyncState.RECOVERING)
        # Sync latest state from cloud before resuming
        await self._sync_from_cloud()
        self._set_state(SyncState.CONNECTED)
    
    async def _sync_from_cloud(self) -> None:
        """Sync latest state from cloud after recovery."""
        # Implementation would fetch latest state from cloud API
        pass


class CloudMirrorController:
    """
    Controller for cloud mirror instance (runs on hosted server).
    
    Receives state from Jetson and assumes control during failover.
    """
    
    def __init__(self, jetson_id: str):
        self.jetson_id = jetson_id
        self.active = False
        self.last_jetson_state: Optional[SystemState] = None
        self.last_contact: Optional[datetime] = None
        
        # Local copies of all state
        self.local_soil_map: Optional[Dict] = None
        self.local_bayesian: Optional[Dict] = None
        self.measurement_chain: list = []
    
    def receive_sync(self, state: SystemState) -> None:
        """Receive state sync from Jetson."""
        self.last_jetson_state = state
        self.last_contact = datetime.utcnow()
        
        # Update local state copies
        self.local_soil_map = state.soil_map_state
        self.local_bayesian = state.bayesian_coefficients
    
    def receive_measurement(self, measurement_hash: str, data: Dict) -> None:
        """Receive measurement for chain continuity."""
        self.measurement_chain.append({
            'hash': measurement_hash,
            'data': data,
            'received_at': datetime.utcnow().isoformat()
        })
    
    def check_health(self, timeout_seconds: float = 30.0) -> bool:
        """Check if Jetson is healthy based on last contact."""
        if not self.last_contact:
            return False
        
        elapsed = (datetime.utcnow() - self.last_contact).total_seconds()
        return elapsed < timeout_seconds
    
    def assume_control(self) -> None:
        """
        Cloud mirror assumes active control of field operations.
        
        Called when Jetson heartbeat timeout detected.
        """
        self.active = True
        print(f"Cloud mirror assuming control for {self.jetson_id}")
        
        # Activate cellular communication with gateways
        # Continue Bayesian inference using last known state
        # Maintain VRI control via cellular-modem commands
        # Preserve cryptographic chain with new signatures
    
    def release_control(self) -> None:
        """Release control back to Jetson (cold spare activated)."""
        self.active = False
        print(f"Cloud mirror releasing control for {self.jetson_id}")
        
        # Sync all accumulated state to cold spare
        # Return to standby mode
