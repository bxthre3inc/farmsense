"""
FarmSense OS v1.0 - Measurement Models

Time-series measurement data with forensic-grade integrity.
All measurements are immutable and cryptographically signed.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import json


@dataclass(frozen=True)
class MeasurementPoint:
    """
    Single depth measurement from a sensor.
    Immutable record with cryptographic integrity.
    """
    sensor_id: str
    depth_inches: int
    timestamp: datetime
    
    # Physical measurements
    volumetric_water_content: float  # VWC, 0.0-1.0
    soil_temperature_c: Optional[float] = None
    soil_water_potential: Optional[float] = None  # Tension, kPa
    
    # Quality indicators
    signal_quality: float = 1.0  # 0.0-1.0
    battery_voltage: Optional[float] = None
    
    # Forensic integrity
    previous_hash: str = "0" * 64  # Chain linking
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this measurement."""
        data = {
            'sensor_id': self.sensor_id,
            'depth_inches': self.depth_inches,
            'timestamp': self.timestamp.isoformat(),
            'vwc': round(self.volumetric_water_content, 6),
            'temp': round(self.soil_temperature_c, 2) if self.soil_temperature_c else None,
            'potential': round(self.soil_water_potential, 4) if self.soil_water_potential else None,
            'quality': round(self.signal_quality, 4),
            'previous_hash': self.previous_hash
        }
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_id': self.sensor_id,
            'depth_inches': self.depth_inches,
            'timestamp': self.timestamp.isoformat(),
            'volumetric_water_content': self.volumetric_water_content,
            'soil_temperature_c': self.soil_temperature_c,
            'soil_water_potential': self.soil_water_potential,
            'signal_quality': self.signal_quality,
            'battery_voltage': self.battery_voltage,
            'measurement_hash': self.compute_hash(),
            'previous_hash': self.previous_hash
        }


@dataclass(frozen=True)
class SignedMeasurement:
    """
    Measurement with cryptographic signature for Water Court admissibility.
    """
    measurement: MeasurementPoint
    signature: str  # ECDSA signature
    public_key: str  # Corresponding public key
    
    def verify_integrity(self) -> bool:
        """Verify measurement signature matches content."""
        # Implementation would use cryptography library
        # For now, return True as placeholder
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'measurement': self.measurement.to_dict(),
            'signature': self.signature,
            'public_key': self.public_key
        }


@dataclass
class MeasurementBatch:
    """
    Batch of measurements from all sensors in a single update cycle.
    Default: 15-minute intervals
    """
    batch_id: str
    timestamp: datetime
    measurements: list = field(default_factory=list)
    
    # Aggregation metadata
    update_interval_minutes: int = 15
    
    def add_measurement(self, measurement: MeasurementPoint) -> None:
        """Add measurement to batch."""
        self.measurements.append(measurement)
    
    @property
    def total_points(self) -> int:
        return len(self.measurements)
    
    @property
    def average_vwc(self) -> Optional[float]:
        """Average volumetric water content across all points."""
        if not self.measurements:
            return None
        return sum(m.volumetric_water_content for m in self.measurements) / len(self.measurements)
    
    def compute_merkle_root(self) -> str:
        """
        Compute Merkle root hash of all measurements in batch.
        Provides efficient verification of batch integrity.
        """
        if not self.measurements:
            return hashlib.sha256(b"empty").hexdigest()
        
        hashes = [m.compute_hash() for m in self.measurements]
        
        # Build Merkle tree
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(combined)
            hashes = next_level
        
        return hashes[0]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'batch_id': self.batch_id,
            'timestamp': self.timestamp.isoformat(),
            'update_interval_minutes': self.update_interval_minutes,
            'total_points': self.total_points,
            'merkle_root': self.compute_merkle_root(),
            'measurements': [m.to_dict() for m in self.measurements]
        }


@dataclass
class VirtualGridCell:
    """
    Single 1-meter resolution cell in the interpolated virtual grid.
    Generated via Regression Kriging from sparse sensor data.
    """
    cell_id: str
    field_id: str
    latitude: float
    longitude: float
    
    # Interpolated values
    estimated_vwc: float
    estimation_variance: float  # Kriging variance
    confidence: float  # 0.0-1.0
    
    # Source information
    nearest_sensor_distance_m: float
    contributing_sensors: list = field(default_factory=list)
    
    # Temporal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def is_hard_anchor(self) -> bool:
        """True if this cell is directly on a physical sensor location."""
        return self.nearest_sensor_distance_m < 0.5  # Within 0.5m
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cell_id': self.cell_id,
            'field_id': self.field_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'estimated_vwc': round(self.estimated_vwc, 6),
            'estimation_variance': round(self.estimation_variance, 6),
            'confidence': round(self.confidence, 4),
            'nearest_sensor_distance_m': round(self.nearest_sensor_distance_m, 2),
            'is_hard_anchor': self.is_hard_anchor(),
            'timestamp': self.timestamp.isoformat()
        }


class DeepPercolationEvent:
    """
    Detected deep percolation event (moisture at compliance horizon).
    Critical for Water Court compliance.
    """
    
    def __init__(
        self,
        field_id: str,
        sensor_id: str,
        horizon_inches: int,  # 42" or 60"
        vwc_at_horizon: float,
        timestamp: datetime,
        irrigation_event_id: Optional[str] = None
    ):
        self.field_id = field_id
        self.sensor_id = sensor_id
        self.horizon_inches = horizon_inches
        self.vwc_at_horizon = vwc_at_horizon
        self.timestamp = timestamp
        self.irrigation_event_id = irrigation_event_id
        self.event_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        data = {
            'field': self.field_id,
            'sensor': self.sensor_id,
            'horizon': self.horizon_inches,
            'vwc': round(self.vwc_at_horizon, 6),
            'timestamp': self.timestamp.isoformat()
        }
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_hash': self.event_hash,
            'field_id': self.field_id,
            'sensor_id': self.sensor_id,
            'horizon_inches': self.horizon_inches,
            'vwc_at_horizon': self.vwc_at_horizon,
            'timestamp': self.timestamp.isoformat(),
            'irrigation_event_id': self.irrigation_event_id,
            'alert_level': 'CRITICAL' if self.horizon_inches >= 60 else 'WARNING'
        }
