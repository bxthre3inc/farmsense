"""
Adaptive Sampling Engine
Dynamically adjusts sensor sampling rates based on field conditions,
battery state, and data utility. Extends battery life without hardware changes.
"""
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import statistics


class SamplingMode(Enum):
    """Sampling modes based on field activity"""
    IRRIGATION_ACTIVE = 60        # 1 minute - high activity
    POST_IRRIGATION = 300         # 5 minutes - settling period
    WEATHER_EVENT = 180           # 3 minutes - rain/wind
    NORMAL_ACTIVE = 900           # 15 minutes - default
    STABLE_CONDITIONS = 3600      # 1 hour - minimal change
    WINTER_DORMANT = 21600        # 6 hours - deep sleep
    EMERGENCY_LOW_BATTERY = 86400 # 24 hours - survival mode


@dataclass
class FieldConditions:
    """Current field state for sampling decisions"""
    irrigation_active: bool = False
    rainfall_rate_mm_hr: float = 0.0
    wind_speed_ms: float = 0.0
    soil_temp_c: float = 10.0
    air_temp_c: float = 20.0
    moisture_trend_1h: float = 0.0
    moisture_trend_24h: float = 0.0
    is_dormant_season: bool = False
    growth_stage: str = "unknown"  # germination, vegetative, reproductive, dormant
    recent_pump_events: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'irrigation_active': self.irrigation_active,
            'rainfall_rate_mm_hr': self.rainfall_rate_mm_hr,
            'wind_speed_ms': self.wind_speed_ms,
            'soil_temp_c': self.soil_temp_c,
            'air_temp_c': self.air_temp_c,
            'moisture_trend_1h': self.moisture_trend_1h,
            'moisture_trend_24h': self.moisture_trend_24h,
            'is_dormant_season': self.is_dormant_season,
            'growth_stage': self.growth_stage,
            'recent_pump_events': self.recent_pump_events
        }


@dataclass
class DeviceState:
    """Device-specific state for sampling optimization"""
    battery_mv: int = 3300
    battery_trend: float = 0.0  # mV per day
    temperature_c: float = 20.0
    last_sample_time: float = field(default_factory=time.time)
    sample_count: int = 0
    history: deque = field(default_factory=lambda: deque(maxlen=24))
    
    def battery_percentage(self) -> float:
        """Convert mV to approximate percentage (LiFePO4 chemistry)"""
        # LiFePO4: 3200mV = 20%, 3300mV = 50%, 3400mV = 90%
        if self.battery_mv >= 3400:
            return 90 + (self.battery_mv - 3400) / 20
        elif self.battery_mv >= 3300:
            return 50 + (self.battery_mv - 3300) / 10
        elif self.battery_mv >= 3200:
            return 20 + (self.battery_mv - 3200) / 5
        else:
            return max(0, (self.battery_mv - 3000) / 10)


@dataclass
class SamplingDecision:
    """Output of sampling decision"""
    interval_seconds: int
    mode: SamplingMode
    reason: str
    next_sample_time: float
    quality_score: float  # 0-1, estimated data utility


class AdaptiveSampler:
    """
    Adaptive sampling engine for FarmSense devices.
    
    Optimizes for:
    1. Battery life (critical for 12-year LRZ target)
    2. Data utility (sample more when things are changing)
    3. Event capture (ensure irrigation events are well-sampled)
    """
    
    # Thresholds for decision making
    MOISTURE_CHANGE_THRESHOLD = 0.02  # 2% VWC change is significant
    TEMP_CHANGE_THRESHOLD = 2.0       # 2°C change is significant
    RAIN_THRESHOLD = 0.5              # 0.5 mm/hr is measurable
    WIND_THRESHOLD = 10.0             # 10 m/s is significant
    BATTERY_CRITICAL = 3100           # mV - emergency mode
    BATTERY_LOW = 3200                # mV - conservative mode
    
    def __init__(self):
        self._device_states: Dict[str, DeviceState] = {}
        self._field_conditions: Dict[str, FieldConditions] = {}
        self._decision_history: Dict[str, List[SamplingDecision]] = {}
        self._callbacks: List[Callable] = []
    
    def register_device(self, device_id: str, 
                        initial_battery: int = 3300) -> None:
        """Initialize tracking for a new device"""
        self._device_states[device_id] = DeviceState(
            battery_mv=initial_battery,
            last_sample_time=time.time()
        )
        self._decision_history[device_id] = []
    
    def update_field_conditions(self, field_id: str, 
                                conditions: FieldConditions) -> None:
        """Update field conditions for all devices in field"""
        self._field_conditions[field_id] = conditions
    
    def update_device_reading(self, device_id: str, 
                              reading: Dict) -> None:
        """Update device state with new reading"""
        if device_id not in self._device_states:
            self.register_device(device_id)
        
        state = self._device_states[device_id]
        
        # Update state
        state.battery_mv = reading.get('battery_mv', state.battery_mv)
        state.temperature_c = reading.get('temperature_c', state.temperature_c)
        state.sample_count += 1
        state.history.append({
            'timestamp': reading.get('timestamp', time.time()),
            'moisture': reading.get('moisture_vwc', 0),
            'battery': state.battery_mv
        })
        state.last_sample_time = reading.get('timestamp', time.time())
    
    def get_next_sample_interval(self, device_id: str, 
                                 field_id: str) -> SamplingDecision:
        """
        Calculate optimal sampling interval for a device.
        
        This is the core algorithm - makes intelligent tradeoffs
        between battery life and data quality.
        """
        device = self._device_states.get(device_id, DeviceState())
        field = self._field_conditions.get(field_id, FieldConditions())
        
        # Priority 1: Battery conservation
        if device.battery_mv < self.BATTERY_CRITICAL:
            return SamplingDecision(
                interval_seconds=SamplingMode.EMERGENCY_LOW_BATTERY.value,
                mode=SamplingMode.EMERGENCY_LOW_BATTERY,
                reason="Critical battery level - survival mode",
                next_sample_time=time.time() + SamplingMode.EMERGENCY_LOW_BATTERY.value,
                quality_score=0.3
            )
        
        # Priority 2: Dormant season deep sleep
        if field.is_dormant_season:
            # Even in dormant season, check battery occasionally
            if device.battery_mv < self.BATTERY_LOW:
                return SamplingDecision(
                    interval_seconds=SamplingMode.WINTER_DORMANT.value,
                    mode=SamplingMode.WINTER_DORMANT,
                    reason="Winter dormancy + low battery",
                    next_sample_time=time.time() + SamplingMode.WINTER_DORMANT.value,
                    quality_score=0.5
                )
            else:
                return SamplingDecision(
                    interval_seconds=SamplingMode.WINTER_DORMANT.value,
                    mode=SamplingMode.WINTER_DORMANT,
                    reason="Winter dormancy - minimal change expected",
                    next_sample_time=time.time() + SamplingMode.WINTER_DORMANT.value,
                    quality_score=0.6
                )
        
        # Priority 3: Active irrigation (highest frequency)
        if field.irrigation_active:
            # Sample more frequently during irrigation
            # but also check if we've been irrigating a long time
            if field.recent_pump_events > 5:
                # After 5 pump cycles, soil is saturated
                return SamplingDecision(
                    interval_seconds=SamplingMode.POST_IRRIGATION.value,
                    mode=SamplingMode.POST_IRRIGATION,
                    reason="Irrigation active - soil saturating",
                    next_sample_time=time.time() + SamplingMode.POST_IRRIGATION.value,
                    quality_score=0.95
                )
            else:
                return SamplingDecision(
                    interval_seconds=SamplingMode.IRRIGATION_ACTIVE.value,
                    mode=SamplingMode.IRRIGATION_ACTIVE,
                    reason="Irrigation just started - capture wetting front",
                    next_sample_time=time.time() + SamplingMode.IRRIGATION_ACTIVE.value,
                    quality_score=1.0
                )
        
        # Priority 4: Weather events
        if field.rainfall_rate_mm_hr > self.RAIN_THRESHOLD:
            return SamplingDecision(
                interval_seconds=SamplingMode.WEATHER_EVENT.value,
                mode=SamplingMode.WEATHER_EVENT,
                reason=f"Rainfall detected ({field.rainfall_rate_mm_hr:.1f} mm/hr)",
                next_sample_time=time.time() + SamplingMode.WEATHER_EVENT.value,
                quality_score=0.9
            )
        
        if field.wind_speed_ms > self.WIND_THRESHOLD:
            return SamplingDecision(
                interval_seconds=SamplingMode.WEATHER_EVENT.value,
                mode=SamplingMode.WEATHER_EVENT,
                reason=f"High winds ({field.wind_speed_ms:.1f} m/s) - ET changes",
                next_sample_time=time.time() + SamplingMode.WEATHER_EVENT.value,
                quality_score=0.85
            )
        
        # Priority 5: Rapid soil changes (post-irrigation, etc.)
        if abs(field.moisture_trend_1h) > self.MOISTURE_CHANGE_THRESHOLD:
            return SamplingDecision(
                interval_seconds=SamplingMode.POST_IRRIGATION.value,
                mode=SamplingMode.POST_IRRIGATION,
                reason=f"Rapid moisture change ({field.moisture_trend_1h:+.3f} VWC/hr)",
                next_sample_time=time.time() + SamplingMode.POST_IRRIGATION.value,
                quality_score=0.9
            )
        
        # Priority 6: Growth stage considerations
        if field.growth_stage == "germination":
            # Critical period - need good data
            if device.battery_percentage() > 50:
                return SamplingDecision(
                    interval_seconds=SamplingMode.NORMAL_ACTIVE.value,
                    mode=SamplingMode.NORMAL_ACTIVE,
                    reason="Germination stage - monitoring seedbed",
                    next_sample_time=time.time() + SamplingMode.NORMAL_ACTIVE.value,
                    quality_score=0.85
                )
        
        # Priority 7: Stable conditions - conserve battery
        if abs(field.moisture_trend_24h) < 0.01:
            # Very stable soil conditions
            if device.battery_percentage() < 30:
                return SamplingDecision(
                    interval_seconds=SamplingMode.STABLE_CONDITIONS.value,
                    mode=SamplingMode.STABLE_CONDITIONS,
                    reason="Stable conditions + low battery",
                    next_sample_time=time.time() + SamplingMode.STABLE_CONDITIONS.value,
                    quality_score=0.7
                )
        
        # Default: Normal operation
        return SamplingDecision(
            interval_seconds=SamplingMode.NORMAL_ACTIVE.value,
            mode=SamplingMode.NORMAL_ACTIVE,
            reason="Normal operation - default interval",
            next_sample_time=time.time() + SamplingMode.NORMAL_ACTIVE.value,
            quality_score=0.8
        )
    
    def should_sample_now(self, device_id: str, field_id: str) -> bool:
        """
        Check if device should sample based on scheduled interval.
        Call this on device wake to decide whether to transmit.
        """
        device = self._device_states.get(device_id)
        if not device:
            return True  # No history, sample to establish baseline
        
        decision = self.get_next_sample_interval(device_id, field_id)
        
        # Store decision for analytics
        if device_id not in self._decision_history:
            self._decision_history[device_id] = []
        self._decision_history[device_id].append(decision)
        
        # Keep only last 100 decisions
        if len(self._decision_history[device_id]) > 100:
            self._decision_history[device_id] = self._decision_history[device_id][-100:]
        
        return time.time() >= decision.next_sample_time
    
    def get_battery_projection(self, device_id: str, 
                               days_ahead: int = 365) -> Dict:
        """
        Project battery life based on current sampling rate and trends.
        
        Returns:
            Dict with estimated life remaining and recommendations
        """
        device = self._device_states.get(device_id)
        if not device or len(device.history) < 2:
            return {'error': 'Insufficient data for projection'}
        
        # Calculate battery drain trend
        readings = list(device.history)
        if len(readings) >= 2:
            first = readings[0]
            last = readings[-1]
            time_span_days = (last['timestamp'] - first['timestamp']) / 86400
            
            if time_span_days > 0:
                drain_per_day = (first['battery'] - last['battery']) / time_span_days
                
                # Project remaining life
                remaining_mv = device.battery_mv - 3100  # Critical threshold
                if drain_per_day > 0:
                    remaining_days = remaining_mv / drain_per_day
                    
                    return {
                        'current_voltage_mv': device.battery_mv,
                        'drain_rate_mv_per_day': round(drain_per_day, 2),
                        'estimated_remaining_days': int(remaining_days),
                        'estimated_remaining_years': round(remaining_days / 365, 1),
                        'target_lifespan_years': 12,
                        'on_track': remaining_days >= (12 * 365),
                        'recommendation': self._get_battery_recommendation(
                            remaining_days, drain_per_day
                        )
                    }
        
        return {'error': 'Could not calculate trend'}
    
    def _get_battery_recommendation(self, remaining_days: float, 
                                   drain_rate: float) -> str:
        """Generate human-readable battery recommendation"""
        target_days = 12 * 365  # 12 years
        
        if remaining_days >= target_days:
            return "Battery life on track for 12-year target"
        elif remaining_days >= target_days * 0.8:
            return "Consider enabling aggressive compression to extend life"
        elif remaining_days >= target_days * 0.6:
            return "Enable dormant season deep sleep; monitor closely"
        else:
            return "CRITICAL: Reduce sampling frequency immediately"
    
    def get_field_sampling_stats(self, field_id: str) -> Dict:
        """Get aggregate sampling statistics for a field"""
        # Find all devices in this field
        # (In production, would query device registry)
        
        stats = {
            'field_id': field_id,
            'device_count': 0,
            'avg_sampling_interval': 0,
            'battery_status': {'healthy': 0, 'low': 0, 'critical': 0},
            'mode_distribution': {m.name: 0 for m in SamplingMode}
        }
        
        # Calculate stats from decision history
        for device_id, decisions in self._decision_history.items():
            if not decisions:
                continue
            
            stats['device_count'] += 1
            latest = decisions[-1]
            stats['avg_sampling_interval'] += latest.interval_seconds
            stats['mode_distribution'][latest.mode.name] += 1
        
        if stats['device_count'] > 0:
            stats['avg_sampling_interval'] /= stats['device_count']
            stats['avg_sampling_interval'] = int(stats['avg_sampling_interval'])
        
        return stats


# Singleton instance for application-wide use
_default_sampler = None

def get_sampler() -> AdaptiveSampler:
    """Get or create the default sampler instance"""
    global _default_sampler
    if _default_sampler is None:
        _default_sampler = AdaptiveSampler()
    return _default_sampler


# Convenience functions
def calculate_next_interval(device_id: str, field_id: str,
                            reading: Dict, conditions: Dict) -> int:
    """
    One-shot function to calculate next sampling interval.
    
    Args:
        device_id: Device unique identifier
        field_id: Field identifier
        reading: Current sensor reading
        conditions: Current field conditions dict
        
    Returns:
        Optimal interval in seconds
    """
    sampler = get_sampler()
    sampler.update_device_reading(device_id, reading)
    sampler.update_field_conditions(field_id, FieldConditions(**conditions))
    
    decision = sampler.get_next_sample_interval(device_id, field_id)
    return decision.interval_seconds
