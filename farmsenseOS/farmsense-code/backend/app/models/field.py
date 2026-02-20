"""
Field Model - Store actual field metadata including coordinates
"""
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
import uuid
from datetime import datetime

Base = declarative_base()


class Field(Base):
    """Farm field metadata with real coordinates"""
    __tablename__ = 'fields'
    
    id = Column(String(50), primary_key=True)  # e.g., "field_001"
    name = Column(String(100), nullable=False)
    organization = Column(String(100))
    
    # Geographic boundaries (actual field polygon)
    boundary = Column(Geometry('POLYGON', srid=4326))
    center_point = Column(Geometry('POINT', srid=4326))
    
    # Coordinates for external API calls
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    
    # Area
    area_hectares = Column(Float)
    area_acres = Column(Float)
    
    # Soil properties (from SoilGrids or manual input)
    soil_type = Column(String(50))
    soil_ph = Column(Float)
    soil_soc = Column(Float)  # Soil Organic Carbon
    soil_texture = Column(String(20))  # clay, sandy, loam, etc.
    
    # Water rights and compliance
    water_allocation_m3 = Column(Float)
    water_district_id = Column(String(50))
    
    # Device associations
    sensor_ids = Column(JSON)  # List of sensor IDs
    pump_ids = Column(JSON)  # List of pump IDs
    pivot_ids = Column(JSON)  # List of pivot IDs
    
    # Contact for alerts
    alert_email = Column(String(100))
    alert_phone = Column(String(20))
    
    # Settings
    moisture_threshold_critical = Column(Float, default=0.10)
    moisture_threshold_warning = Column(Float, default=0.18)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeviceMapping(Base):
    """Maps hardware devices to fields and their types"""
    __tablename__ = 'device_mappings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String(50), nullable=False, index=True)  # e.g., "LRZ-001"
    device_type = Column(String(20), nullable=False)  # LRZ, VFA, PFA, PMT, DHU
    field_id = Column(String(50), nullable=False, index=True)
    
    # Location within field
    location = Column(Geometry('POINT', srid=4326))
    lat = Column(Float)
    lon = Column(Float)
    
    # Hardware metadata
    hardware_version = Column(String(20))
    firmware_version = Column(String(20))
    
    # Network
    parent_hub_id = Column(String(50))  # Parent DHU for mesh devices
    communication_protocol = Column(String(20))  # 900MHz, 5GHz, BLE, LTE
    
    # Status
    is_active = Column(String(10), default='true')
    last_seen = Column(DateTime)
    battery_level = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
