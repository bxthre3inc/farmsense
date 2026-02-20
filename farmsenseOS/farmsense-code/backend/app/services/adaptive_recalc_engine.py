"""
Adaptive Recalculation Engine - Judgment-based timing logic
Determines when to recompute virtual sensor grids based on field conditions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session


class RecalcMode(Enum):
    """Operational modes for recalculation frequency"""
    STABLE = "stable"          # 12 hour intervals
    ACTIVE = "active"          # 15 minute intervals
    CRITICAL = "critical"      # 1 minute intervals
    OUT_OF_TURN = "out_of_turn"  # Immediate, event-driven


@dataclass
class FieldCondition:
    """Current field state for decision making"""
    field_id: str
    current_mode: RecalcMode
    last_recalc: datetime
    
    # Moisture metrics
    avg_moisture_surface: float
    avg_moisture_root: float
    moisture_std_dev: float
    moisture_trend_1h: float  # % change per hour
    moisture_trend_6h: float
    
    # Environmental
    current_temp: float
    et0_rate: float  # mm/day
    rainfall_last_1h: float
    rainfall_forecast_6h: float
    wind_speed: float
    
    # Operational
    pumps_running: int
    irrigation_active: bool
    sensor_coverage_pct: float
    
    # Events
    sensor_anomalies: List[Dict]
    extreme_weather_alerts: List[Dict]


@dataclass
class RecalcDecision:
    """Output of decision engine"""
    should_recalculate: bool
    new_mode: RecalcMode
    reason: str
    next_scheduled: datetime
    priority: int  # 1-5, higher = more urgent
    trigger_type: str


class AdaptiveRecalculationEngine:
    """
    Judgment-based recalculation engine using trend analysis
    and configurable thresholds
    """
    
    # Configurable thresholds (per crop type, can be overridden)
    DEFAULT_THRESHOLDS = {
        'moisture_stable_band': 0.05,      # ±5% is stable
        'moisture_active_threshold': 0.15,  # >15% = active
        'moisture_critical_threshold': 0.30, # >30% = critical
        'trend_volatile_threshold': 2.0,    # >2%/hr = volatile
        'temp_stress_threshold': 35.0,      # >35°C = heat stress
        'rainfall_event_threshold': 10.0,   # >10mm = significant
        'wind_stress_threshold': 8.0,       # >8 m/s = high wind
        'et0_high_threshold': 8.0,          # >8mm/day = high ET
    }
    
    def __init__(self, db_session: Session, config: Optional[Dict] = None):
        self.db = db_session
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(config or {})}
    
    def evaluate_field(self, condition: FieldCondition) -> RecalcDecision:
        """
        Main decision logic: determine if and when to recalculate
        
        Decision tree:
        1. Check for critical events (immediate recalc)
        2. Check for out-of-turn triggers (sensor/weather events)
        3. Analyze trends to determine mode
        4. Check if scheduled recalc is due
        """
        
        # 1. Critical event check - highest priority
        critical_check = self._check_critical_events(condition)
        if critical_check:
            return critical_check
        
        # 2. Out-of-turn event check
        oot_check = self._check_out_of_turn_triggers(condition)
        if oot_check:
            return oot_check
        
        # 3. Determine appropriate mode based on trends
        new_mode = self._determine_mode(condition)
        
        # 4. Check if recalculation is due based on current mode
        time_since_last = datetime.utcnow() - condition.last_recalc
        is_due, next_scheduled = self._is_recalc_due(
            condition.current_mode, 
            new_mode, 
            time_since_last
        )
        
        if is_due:
            reason = self._generate_reason(condition, new_mode)
            return RecalcDecision(
                should_recalculate=True,
                new_mode=new_mode,
                reason=reason,
                next_scheduled=next_scheduled,
                priority=self._calculate_priority(new_mode, condition),
                trigger_type='scheduled'
            )
        
        # Not due yet
        return RecalcDecision(
            should_recalculate=False,
            new_mode=condition.current_mode,
            reason="Next scheduled recalculation not due",
            next_scheduled=next_scheduled,
            priority=1,
            trigger_type='none'
        )
    
    def _check_critical_events(self, condition: FieldCondition) -> Optional[RecalcDecision]:
        """
        Critical events requiring immediate 1-minute recalculation
        - Extreme moisture drops (>30% in 6h)
        - Heat stress + low moisture
        - Pump failures during active irrigation
        """
        reasons = []
        
        # Rapid moisture depletion
        if condition.moisture_trend_6h < -self.thresholds['moisture_critical_threshold']:
            reasons.append(f"Critical moisture drop: {condition.moisture_trend_6h:.1f}% in 6h")
        
        # Heat stress with inadequate moisture
        if (condition.current_temp > self.thresholds['temp_stress_threshold'] and 
            condition.avg_moisture_surface < 0.20):
            reasons.append(f"Heat stress event: {condition.current_temp}°C with low moisture")
        
        # Irrigation system failure
        if condition.irrigation_active and condition.pumps_running == 0:
            reasons.append("Pump failure during active irrigation")
        
        # Multiple sensor failures
        if condition.sensor_coverage_pct < 50.0:
            reasons.append(f"Low sensor coverage: {condition.sensor_coverage_pct:.1f}%")
        
        if reasons:
            return RecalcDecision(
                should_recalculate=True,
                new_mode=RecalcMode.CRITICAL,
                reason=" | ".join(reasons),
                next_scheduled=datetime.utcnow() + timedelta(minutes=1),
                priority=5,
                trigger_type='critical_event'
            )
        
        return None
    
    def _check_out_of_turn_triggers(self, condition: FieldCondition) -> Optional[RecalcDecision]:
        """
        Out-of-turn recalculation for unexpected events
        - Sensor anomalies
        - Sudden weather changes
        - Pump state changes
        """
        reasons = []
        
        # Sensor anomaly detection
        if condition.sensor_anomalies:
            anomaly_count = len(condition.sensor_anomalies)
            reasons.append(f"{anomaly_count} sensor anomalies detected")
        
        # Significant rainfall event
        if condition.rainfall_last_1h > self.thresholds['rainfall_event_threshold']:
            reasons.append(f"Rainfall event: {condition.rainfall_last_1h:.1f}mm in 1h")
        
        # Extreme weather alert
        if condition.extreme_weather_alerts:
            alert_types = [a['type'] for a in condition.extreme_weather_alerts]
            reasons.append(f"Weather alerts: {', '.join(alert_types)}")
        
        # High ET rate with active irrigation
        if (condition.et0_rate > self.thresholds['et0_high_threshold'] and 
            condition.irrigation_active):
            reasons.append(f"High ET rate: {condition.et0_rate:.1f}mm/day during irrigation")
        
        if reasons:
            return RecalcDecision(
                should_recalculate=True,
                new_mode=RecalcMode.OUT_OF_TURN,
                reason=" | ".join(reasons),
                next_scheduled=datetime.utcnow() + timedelta(minutes=5),  # Resume normal after event
                priority=4,
                trigger_type='out_of_turn_event'
            )
        
        return None
    
    def _determine_mode(self, condition: FieldCondition) -> RecalcMode:
        """
        Determine appropriate recalculation mode based on field trends
        
        STABLE (12h): Moisture stable, no irrigation, normal conditions
        ACTIVE (15min): Irrigation active OR moisture trending OR moderate weather
        CRITICAL (1min): Rapid changes OR stress conditions OR high volatility
        """
        
        # Calculate volatility score (0-1)
        volatility_factors = []
        
        # Moisture volatility
        if abs(condition.moisture_trend_1h) > self.thresholds['trend_volatile_threshold']:
            volatility_factors.append(0.4)
        elif abs(condition.moisture_trend_1h) > self.thresholds['moisture_active_threshold']:
            volatility_factors.append(0.2)
        
        # High spatial variability
        if condition.moisture_std_dev > 0.15:
            volatility_factors.append(0.3)
        
        # Active irrigation
        if condition.irrigation_active:
            volatility_factors.append(0.3)
        
        # High ET conditions
        if condition.et0_rate > self.thresholds['et0_high_threshold']:
            volatility_factors.append(0.2)
        
        # Wind stress
        if condition.wind_speed > self.thresholds['wind_stress_threshold']:
            volatility_factors.append(0.2)
        
        # Forecast significant rainfall
        if condition.rainfall_forecast_6h > self.thresholds['rainfall_event_threshold']:
            volatility_factors.append(0.3)
        
        volatility_score = min(sum(volatility_factors), 1.0)
        
        # Mode determination thresholds
        if volatility_score > 0.7:
            return RecalcMode.CRITICAL
        elif volatility_score > 0.3:
            return RecalcMode.ACTIVE
        else:
            return RecalcMode.STABLE
    
    def _is_recalc_due(
        self, 
        current_mode: RecalcMode, 
        new_mode: RecalcMode,
        time_since_last: timedelta
    ) -> Tuple[bool, datetime]:
        """
        Check if recalculation is due based on mode intervals
        Returns (is_due, next_scheduled_time)
        """
        
        mode_intervals = {
            RecalcMode.STABLE: timedelta(hours=12),
            RecalcMode.ACTIVE: timedelta(minutes=15),
            RecalcMode.CRITICAL: timedelta(minutes=1),
            RecalcMode.OUT_OF_TURN: timedelta(minutes=1),  # Immediate
        }
        
        # Use the shorter interval if mode is changing
        interval = min(
            mode_intervals.get(current_mode, timedelta(hours=12)),
            mode_intervals.get(new_mode, timedelta(hours=12))
        )
        
        is_due = time_since_last >= interval
        next_scheduled = datetime.utcnow() + interval
        
        return is_due, next_scheduled
    
    def _calculate_priority(self, mode: RecalcMode, condition: FieldCondition) -> int:
        """Calculate urgency priority 1-5"""
        priority_map = {
            RecalcMode.STABLE: 1,
            RecalcMode.ACTIVE: 3,
            RecalcMode.CRITICAL: 5,
            RecalcMode.OUT_OF_TURN: 4,
        }
        
        base_priority = priority_map[mode]
        
        # Boost priority if moisture is critically low
        if condition.avg_moisture_surface < 0.15:
            base_priority = min(base_priority + 1, 5)
        
        return base_priority
    
    def _generate_reason(self, condition: FieldCondition, new_mode: RecalcMode) -> str:
        """Generate human-readable reason for recalculation"""
        
        reasons = [f"Mode: {new_mode.value}"]
        
        if new_mode == RecalcMode.CRITICAL:
            reasons.append(f"High volatility detected")
            if condition.irrigation_active:
                reasons.append("Active irrigation")
        elif new_mode == RecalcMode.ACTIVE:
            if condition.irrigation_active:
                reasons.append("Irrigation in progress")
            reasons.append(f"Moisture trend: {condition.moisture_trend_1h:+.1f}%/h")
        else:
            reasons.append("Stable conditions")
        
        if condition.et0_rate > 6.0:
            reasons.append(f"ET0: {condition.et0_rate:.1f}mm/day")
        
        return " | ".join(reasons)


class RecalculationScheduler:
    """
    Orchestrates recalculation across multiple fields
    Manages priority queue and resource allocation
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.engine = AdaptiveRecalculationEngine(db_session)
    
    def schedule_batch(self, field_conditions: List[FieldCondition]) -> List[RecalcDecision]:
        """
        Evaluate multiple fields and return prioritized recalculation queue
        """
        decisions = []
        
        for condition in field_conditions:
            decision = self.engine.evaluate_field(condition)
            if decision.should_recalculate:
                decisions.append((condition.field_id, decision))
        
        # Sort by priority (descending) and scheduled time
        decisions.sort(key=lambda x: (-x[1].priority, x[1].next_scheduled))
        
        return decisions
    
    def get_next_due_fields(self, limit: int = 100) -> List[str]:
        """
        Query database for fields whose recalculation is overdue
        Returns list of field_ids to process
        """
        # Query logic to find fields based on their last recalc time and mode
        # Implementation depends on database structure
        pass
