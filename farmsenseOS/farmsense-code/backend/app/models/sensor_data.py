"""
Data models for sensor telemetry and virtual grid outputs
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
import uuid
from datetime import datetime

Base = declarative_base()


class SoilSensorReading(Base):
    """Raw soil sensor readings - 2-depth + vertical profiling"""
    __tablename__ = 'soil_sensor_readings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(String(50), nullable=False, index=True)
    field_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Geospatial
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Dual-depth readings
    moisture_surface = Column(Float)  # 0-30cm
    moisture_root = Column(Float)     # 30-60cm
    temp_surface = Column(Float)
    temp_root = Column(Float)
    
    # Vertical profiling (JSON array for flexibility)
    vertical_profile = Column(JSON)  # [{depth_cm: 10, moisture: 0.25, temp: 18.5}, ...]
    
    # Salinity and nutrients
    ec_surface = Column(Float)  # Electrical conductivity
    ec_root = Column(Float)
    ph = Column(Float)
    
    # Quality flags
    quality_flag = Column(String(20), default='valid')  # valid, suspect, invalid
    battery_voltage = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sensor_field_time', 'sensor_id', 'field_id', 'timestamp'),
        Index('idx_field_time', 'field_id', 'timestamp'),
        Index('idx_spatial', 'location', postgresql_using='gist'),
    )


class PumpTelemetry(Base):
    """Pump operational data"""
    __tablename__ = 'pump_telemetry'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pump_id = Column(String(50), nullable=False, index=True)
    field_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Operational metrics
    status = Column(String(20))  # running, idle, maintenance, error
    flow_rate_lpm = Column(Float)  # Liters per minute
    pressure_bar = Column(Float)
    power_consumption_kw = Column(Float)
    runtime_hours = Column(Float)
    
    # Volume tracking
    volume_delivered_l = Column(Float)
    cumulative_volume_l = Column(Float)
    
    # Anomaly detection
    anomaly_score = Column(Float)
    anomaly_flag = Column(String(20), default='normal')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_pump_field_time', 'pump_id', 'field_id', 'timestamp'),
    )


class WeatherData(Base):
    """Weather station and forecast data"""
    __tablename__ = 'weather_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(String(50), index=True)
    field_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    data_type = Column(String(20))  # observed, forecast
    
    # Atmospheric
    temperature_c = Column(Float)
    humidity_pct = Column(Float)
    pressure_hpa = Column(Float)
    wind_speed_ms = Column(Float)
    wind_direction_deg = Column(Float)
    
    # Precipitation
    rainfall_mm = Column(Float)
    rainfall_intensity = Column(String(20))  # light, moderate, heavy, extreme
    
    # Solar & ET
    solar_radiation_wm2 = Column(Float)
    et0_mm = Column(Float)  # Reference evapotranspiration
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_field_time_type', 'field_id', 'timestamp', 'data_type'),
    )


class VirtualSensorGrid20m(Base):
    """Edge-computed 20m virtual sensor grid"""
    __tablename__ = 'virtual_sensor_grid_20m'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    grid_id = Column(String(50), nullable=False, index=True)  # e.g., "field123_x10_y05"
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Geospatial
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    grid_cell = Column(Geometry('POLYGON', srid=4326))
    
    # Interpolated values
    moisture_surface = Column(Float)
    moisture_root = Column(Float)
    temperature = Column(Float)
    
    # Derived metrics
    water_deficit_mm = Column(Float)
    stress_index = Column(Float)  # 0-1 scale
    irrigation_need = Column(String(20))  # none, low, medium, high, critical
    
    # Computation metadata
    computation_mode = Column(String(20))  # stable, active, critical, out_of_turn
    source_sensors = Column(JSON)  # List of contributing sensor IDs
    confidence = Column(Float)  # 0-1 interpolation confidence
    
    created_at = Column(DateTime, default=datetime.utcnow)
    physical_probe_value = Column(Float) # Ground truth for cross-validation
    edge_device_id = Column(String(50))
    
    __table_args__ = (
        Index('idx_field_grid_time', 'field_id', 'grid_id', 'timestamp'),
        Index('idx_spatial_20m', 'location', postgresql_using='gist'),
    )


class VirtualSensorGrid50m(Base):
    """Edge-computed 50m virtual sensor grid"""
    __tablename__ = 'virtual_sensor_grid_50m'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    grid_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Geospatial
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    grid_cell = Column(Geometry('POLYGON', srid=4326))
    
    # Interpolated values
    moisture_surface = Column(Float)
    moisture_root = Column(Float)
    temperature = Column(Float)
    
    # Derived metrics
    water_deficit_mm = Column(Float)
    stress_index = Column(Float)
    irrigation_need = Column(String(20))
    
    # Computation metadata
    computation_mode = Column(String(20))
    source_sensors = Column(JSON)
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    physical_probe_value = Column(Float) # Ground truth for cross-validation
    edge_device_id = Column(String(50))
    
    __table_args__ = (
        Index('idx_field_grid_time_50m', 'field_id', 'grid_id', 'timestamp'),
        Index('idx_spatial_50m', 'location', postgresql_using='gist'),
    )


class VirtualSensorGrid10m(Base):
    """Edge-computed 10m virtual sensor grid - high-res for VRI zones"""
    __tablename__ = 'virtual_sensor_grid_10m'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    grid_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Geospatial
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    grid_cell = Column(Geometry('POLYGON', srid=4326))
    
    # Interpolated values
    moisture_surface = Column(Float)
    moisture_root = Column(Float)
    temperature = Column(Float)
    
    # Derived metrics
    water_deficit_mm = Column(Float)
    stress_index = Column(Float)
    irrigation_need = Column(String(20))
    
    # VRI-specific fields
    vri_zone_id = Column(String(20))  # Zone assignment for variable rate irrigation
    prescription_rate = Column(Float)  # Target irrigation rate for this zone
    
    # Computation metadata
    computation_mode = Column(String(20))
    source_sensors = Column(JSON)
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    physical_probe_value = Column(Float)
    edge_device_id = Column(String(50))
    
    __table_args__ = (
        Index('idx_field_grid_time_10m', 'field_id', 'grid_id', 'timestamp'),
        Index('idx_spatial_10m', 'location', postgresql_using='gist'),
    )




class VirtualSensorGrid1m(Base):
    """Cloud-computed 1m high-resolution virtual sensor grid"""
    __tablename__ = 'virtual_sensor_grid_1m'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    grid_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Geospatial
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Multi-source fusion
    moisture_surface = Column(Float)
    moisture_root = Column(Float)
    temperature = Column(Float)
    ndvi = Column(Float)  # From Sentinel-2
    ndwi = Column(Float)  # Normalized Difference Water Index
    
    confidence_score = Column(Float, default=1.0) # 0.0 to 1.0 based on data source quality
    physical_probe_value = Column(Float) # Ground truth for cross-validation
    edge_device_id = Column(String(50))
    
    # Advanced analytics
    crop_stress_probability = Column(Float)  # ML model output
    yield_forecast_kgha = Column(Float)
    irrigation_priority = Column(Integer)  # 1-5 scale
    
    # Uncertainty quantification
    kriging_variance = Column(Float)
    prediction_std = Column(Float)
    
    # Satellite data integration
    sentinel_cloud_pct = Column(Float)
    landsat_qa = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_field_time_1m', 'field_id', 'timestamp'),
        Index('idx_spatial_1m', 'location', postgresql_using='gist'),
        # Partitioning by field_id and month for scalability
    )


class RecalculationLog(Base):
    """Audit log for adaptive recalculation engine"""
    __tablename__ = 'recalculation_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Recalculation trigger
    trigger_type = Column(String(50))  # scheduled, sensor_anomaly, weather_event, manual
    trigger_details = Column(JSON)
    
    # Mode determination
    previous_mode = Column(String(20))
    new_mode = Column(String(20))
    mode_reason = Column(String(200))
    
    # Trend analysis
    moisture_trend = Column(String(20))  # stable, increasing, decreasing, volatile
    trend_rate = Column(Float)  # Change per hour
    
    # Next recalculation
    next_scheduled = Column(DateTime)
    
    # Performance
    computation_duration_ms = Column(Integer)
    grid_cells_updated = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_field_timestamp', 'field_id', 'timestamp'),
    )


class ComplianceReport(Base):
    """SLV 2026 compliance reporting"""
    __tablename__ = 'compliance_reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(String(50), nullable=False, index=True)
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    report_type = Column(String(50))  # monthly, seasonal, annual, audit
    
    # Water usage
    total_irrigation_m3 = Column(Float)
    water_use_efficiency = Column(Float)
    allocation_compliance_pct = Column(Float)
    validation_score = Column(Float) # Cross-validation score vs. physical probes
    
    # Environmental metrics
    avg_soil_health_index = Column(Float)
    nutrient_runoff_risk = Column(String(20))
    biodiversity_score = Column(Float)
    
    # Audit trail
    data_completeness_pct = Column(Float)
    sensor_uptime_pct = Column(Float)
    validation_status = Column(String(20))  # draft, submitted, approved
    
    # Regulatory
    slv_2026_compliant = Column(String(10))  # yes, no, pending
    violations = Column(JSON)  # List of any compliance issues
    corrective_actions = Column(JSON)
    
    # Digital signature
    report_hash = Column(String(64))  # SHA-256 of report data
    signed_by = Column(String(100))
    signature = Column(String(512))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_field_period', 'field_id', 'report_period_start', 'report_period_end'),
    )

class AnonymizedResearchArchive(Base):
    """
    Centralized collection for FarmSense platform.
    Stripped of PII and linked only by salted-hash field/user IDs.
    """
    __tablename__ = 'research_archive'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Salted hash of field_id to allow temporal tracking without identity
    anon_field_hash = Column(String(64), index=True) 
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Aggregated metrics (Raw telemetry but no link to user)
    avg_moisture = Column(Float)
    avg_temperature = Column(Float)
    total_water_m3 = Column(Float)
    
    # Context (Non-PII)
    soil_type = Column(String(50))
    region_code = Column(String(20)) # e.g. 'SLV-01'
    
    created_at = Column(DateTime, default=datetime.utcnow)
