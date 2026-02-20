"""
FarmSense Hardware Device Models
Specifically designed for Subdistrict 1 hardware BOM:
- LRZ: 15,600 Long-Range Zigbee nodes (dumb mesh)
- VFA: 1,280 Vertical Field Anchors (legal-grade ground truth)
- PFA: 1,280 Pump/Flow Anchors (autonomous reflex)
- PMT: 1,280 Pivot Monitoring Towers (VRI control)
- DHU: 25 District Hub Units (edge compute)
- RSS: 1 Regional Superstation (cloud cortex)
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Index, ForeignKey, Enum as sqlalchemy_enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from .sensor_data import Base

class DeviceType(str, enum.Enum):
    """FarmSense hardware device types per BOM specifications"""
    LRZ = "lrz"  # Long-Range Zigbee (dumb mesh node)
    VFA = "vfa"  # Vertical Field Anchor (ground truth)
    PFA = "pfa"  # Pump/Flow Anchor (autonomous reflex)
    PMT = "pmt"  # Pivot Monitoring Tower (VRI)
    DHU = "dhu"  # District Hub Unit (edge compute)
    RSS = "rss"  # Regional Superstation (cloud cortex)

class DeviceStatus(str, enum.Enum):
    """Device operational statuses"""
    ACTIVE = "active"
    DORMANT = "dormant"  # Winter hibernation
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"

class HardwareDevice(Base):
    """
    Base hardware device model for FarmSense Subdistrict 1 deployment.
    Supports 19,466 devices across 6 hardware types.
    """
    __tablename__ = 'hardware_devices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Hardware identification
    device_type = Column(sqlalchemy_enum(DeviceType), nullable=False, index=True)
    serial_number = Column(String(100), unique=True, index=True)
    hardware_rev = Column(String(20), default="1.0")
    firmware_version = Column(String(20))
    
    # Network topology
    dhu_id = Column(String(50), index=True)  # Parent District Hub
    rss_id = Column(String(50), index=True)  # Parent Regional Superstation
    mesh_address = Column(String(20))  # 900MHz mesh address (LRZ)
    
    # Location (for field mapping)
    field_id = Column(String(50), nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation_m = Column(Float)
    
    # Power management
    battery_voltage = Column(Float)  # LiSOCl2 or LiFePO4
    battery_percent = Column(Float)
    solar_input_w = Column(Float)  # For solar-equipped units
    last_power_reading = Column(DateTime)
    
    # Communication
    last_communication = Column(DateTime)
    rssi_dbm = Column(Float)  # Signal strength
    snr_db = Column(Float)  # Signal-to-noise ratio
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    
    # Status
    status = Column(sqlalchemy_enum(DeviceStatus), default=DeviceStatus.ACTIVE)
    error_code = Column(String(50))  # Last error
    error_count = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSON)  # Device-specific configuration
    calibration_data = Column(JSON)  # Sensor calibration
    
    # Security
    certificate_thumbprint = Column(String(64))  # SHA-256 of device cert
    last_security_check = Column(DateTime)
    
    # Timestamps
    deployed_at = Column(DateTime)
    last_maintenance = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        Index('idx_device_type_field', 'device_type', 'field_id'),
        Index('idx_device_dhu', 'dhu_id', 'device_type'),
        Index('idx_device_status', 'status', 'last_communication'),
    )

class LRZTelemetry(Base):
    """
    Long-Range Zigbee telemetry data.
    15,600 dumb nodes transmitting every 15 minutes.
    Handles burst ingestion of ~17,000 requests/minute.
    """
    __tablename__ = 'lrz_telemetry'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('hardware_devices.id'), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Sensor readings (TDR probe)
    moisture_vwc = Column(Float)  # Volumetric water content
    temperature_c = Column(Float)  # Soil temperature
    ec_ds_m = Column(Float)  # Electrical conductivity
    
    # Device health
    battery_v = Column(Float)
    rssi_dbm = Column(Float)
    
    # Data integrity
    sequence_number = Column(Integer)  # For detecting missed packets
    is_decimated = Column(Boolean, default=False)  # DHU compressed this?
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_lrz_time', 'device_id', 'timestamp'),
    )
