"""
FarmSense OS v1.0 - Sensor Entity Models

Physical sensor definitions for the Nail architecture.
All sensors are permanent fixtures with 20+ year operational life.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional
from datetime import datetime
import hashlib
import json


class SensorType(Enum):
    """Nail architecture sensor types."""
    HORIZONTAL_BLANKET = auto()
    MASTER_VERTICAL_MEDIUM = auto()  # 42", 5-depth
    MASTER_VERTICAL_LARGE = auto()   # 60", 7-depth


class DepthConfiguration(Enum):
    """Depth measurement configurations."""
    BLANKET_2DEPTH = [12, 18]  # inches
    MASTER_MEDIUM_5DEPTH = [18, 24, 30, 36, 42]
    MASTER_LARGE_7DEPTH = [18, 24, 30, 36, 42, 52, 60]


@dataclass(frozen=True)
class SensorLocation:
    """GPS coordinates with field reference."""
    field_id: str
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            'field_id': self.field_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elevation_m': self.elevation_m
        }


@dataclass
class Sensor:
    """
    Permanent sensor fixture (Nail architecture).
    
    Horizontal blankets: 18" length, 2-depth (12", 18")
    Master vertical nails: 42" or 60" active depth, 5 or 7 measurement points
    """
    sensor_id: str
    sensor_type: SensorType
    location: SensorLocation
    depths_inches: List[int] = field(default_factory=list)
    installation_date: datetime = field(default_factory=datetime.utcnow)
    hardware_version: str = "v1.0"
    
    # Cryptographic identity
    public_key_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.depths_inches:
            self.depths_inches = self._default_depths()
    
    def _default_depths(self) -> List[int]:
        """Return default depths based on sensor type."""
        if self.sensor_type == SensorType.HORIZONTAL_BLANKET:
            return DepthConfiguration.BLANKET_2DEPTH.value
        elif self.sensor_type == SensorType.MASTER_VERTICAL_MEDIUM:
            return DepthConfiguration.MASTER_MEDIUM_5DEPTH.value
        elif self.sensor_type == SensorType.MASTER_VERTICAL_LARGE:
            return DepthConfiguration.MASTER_LARGE_7DEPTH.value
        return []
    
    @property
    def measurement_point_count(self) -> int:
        """Total measurement points this sensor generates."""
        return len(self.depths_inches)
    
    @property
    def is_master_nail(self) -> bool:
        """True if this is a vertical master nail."""
        return self.sensor_type in (
            SensorType.MASTER_VERTICAL_MEDIUM,
            SensorType.MASTER_VERTICAL_LARGE
        )
    
    def compute_identity_hash(self) -> str:
        """Compute SHA-256 hash of sensor identity for forensic chain."""
        identity_data = {
            'sensor_id': self.sensor_id,
            'type': self.sensor_type.name,
            'location': self.location.to_dict(),
            'depths': self.depths_inches,
            'installed': self.installation_date.isoformat(),
            'hardware': self.hardware_version
        }
        canonical = json.dumps(identity_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.name,
            'location': self.location.to_dict(),
            'depths_inches': self.depths_inches,
            'installation_date': self.installation_date.isoformat(),
            'hardware_version': self.hardware_version,
            'public_key_hash': self.public_key_hash,
            'identity_hash': self.compute_identity_hash()
        }


@dataclass
class SensorNetwork:
    """
    Complete sensor network for a deployment.
    
    Pilot: 9 fields, ~108 sensors (~99 blankets + 9 masters)
    Full: 520,000 acres, ~48,000 sensors
    """
    network_id: str
    sensors: List[Sensor] = field(default_factory=list)
    deployment_phase: str = "pilot"  # pilot, expansion, full
    
    def add_sensor(self, sensor: Sensor) -> None:
        """Add sensor to network."""
        self.sensors.append(sensor)
    
    @property
    def total_sensors(self) -> int:
        return len(self.sensors)
    
    @property
    def total_measurement_points(self) -> int:
        return sum(s.measurement_point_count for s in self.sensors)
    
    @property
    def blanket_count(self) -> int:
        return sum(1 for s in self.sensors 
                   if s.sensor_type == SensorType.HORIZONTAL_BLANKET)
    
    @property
    def master_nail_count(self) -> int:
        return sum(1 for s in self.sensors if s.is_master_nail)
    
    def sensors_by_field(self, field_id: str) -> List[Sensor]:
        """Get all sensors for a specific field."""
        return [s for s in self.sensors if s.location.field_id == field_id]
    
    def compute_network_hash(self) -> str:
        """Compute aggregate hash of entire network for audit."""
        sensor_hashes = sorted([s.compute_identity_hash() for s in self.sensors])
        canonical = json.dumps(sensor_hashes, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


# Factory functions for creating standard sensor deployments

def create_horizontal_blanket(
    sensor_id: str,
    field_id: str,
    latitude: float,
    longitude: float
) -> Sensor:
    """Create a standard 18" horizontal blanket sensor."""
    return Sensor(
        sensor_id=sensor_id,
        sensor_type=SensorType.HORIZONTAL_BLANKET,
        location=SensorLocation(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude
        )
    )


def create_master_nail_medium(
    sensor_id: str,
    field_id: str,
    latitude: float,
    longitude: float
) -> Sensor:
    """Create a 42" (5-depth) master vertical nail."""
    return Sensor(
        sensor_id=sensor_id,
        sensor_type=SensorType.MASTER_VERTICAL_MEDIUM,
        location=SensorLocation(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude
        )
    )


def create_master_nail_large(
    sensor_id: str,
    field_id: str,
    latitude: float,
    longitude: float
) -> Sensor:
    """Create a 60" (7-depth) master vertical nail."""
    return Sensor(
        sensor_id=sensor_id,
        sensor_type=SensorType.MASTER_VERTICAL_LARGE,
        location=SensorLocation(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude
        )
    )


def create_pilot_network(network_id: str = "pilot_2026") -> SensorNetwork:
    """
    Create the 9-field pilot sensor network.
    ~99 horizontal blankets + 9 master nails = ~108 sensors
    ~270 measurement points
    """
    network = SensorNetwork(network_id=network_id, deployment_phase="pilot")
    
    # Field 1 (Hub) - mixed crops
    network.add_sensor(create_master_nail_medium("M001", "F001", 37.5000, -105.8000))
    for i in range(11):
        network.add_sensor(create_horizontal_blanket(
            f"B001_{i:02d}", "F001", 37.5000 + i*0.001, -105.8000
        ))
    
    # Fields 2-9 (Spokes)
    for field_num in range(2, 10):
        field_id = f"F{field_num:03d}"
        lat_base = 37.5000 + (field_num - 1) * 0.01
        
        # One master nail per field
        if field_num <= 5:  # Potatoes/barley
            network.add_sensor(create_master_nail_medium(
                f"M{field_num:03d}", field_id, lat_base, -105.8000
            ))
        else:  # Alfalfa
            network.add_sensor(create_master_nail_large(
                f"M{field_num:03d}", field_id, lat_base, -105.8000
            ))
        
        # ~11 horizontal blankets per field
        for i in range(11):
            network.add_sensor(create_horizontal_blanket(
                f"B{field_num:03d}_{i:02d}", field_id, 
                lat_base + i*0.001, -105.8000
            ))
    
    return network
