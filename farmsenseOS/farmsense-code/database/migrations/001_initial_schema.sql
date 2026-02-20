-- FarmSense Database Initialization
-- Creates PostGIS extensions and TimescaleDB hypertables

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertables for time-series data
SELECT create_hypertable('soil_sensor_readings', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

SELECT create_hypertable('pump_telemetry', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

SELECT create_hypertable('weather_data', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

SELECT create_hypertable('virtual_sensor_grid_20m', 'timestamp',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

SELECT create_hypertable('virtual_sensor_grid_1m', 'timestamp',
    if_not_exists => TRUE
);

SELECT create_hypertable('virtual_sensor_grid_50m', 'timestamp',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);



-- Create spatial indices
CREATE INDEX IF NOT EXISTS idx_soil_sensors_location 
    ON soil_sensor_readings USING GIST (location);

CREATE INDEX IF NOT EXISTS idx_grid_20m_location 
    ON virtual_sensor_grid_20m USING GIST (location);

    ON virtual_sensor_grid_1m USING GIST (location);

CREATE INDEX IF NOT EXISTS idx_grid_50m_location 
    ON virtual_sensor_grid_50m USING GIST (location);



-- Create composite indices for common queries
CREATE INDEX IF NOT EXISTS idx_soil_field_time_quality 
    ON soil_sensor_readings (field_id, timestamp DESC, quality_flag);

CREATE INDEX IF NOT EXISTS idx_pump_field_status_time 
    ON pump_telemetry (field_id, status, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_weather_field_type_time 
    ON weather_data (field_id, data_type, timestamp DESC);

-- Retention policies (optional - keep last 2 years of raw data)
SELECT add_retention_policy('soil_sensor_readings', INTERVAL '2 years', if_not_exists => TRUE);
SELECT add_retention_policy('pump_telemetry', INTERVAL '2 years', if_not_exists => TRUE);
SELECT add_retention_policy('weather_data', INTERVAL '2 years', if_not_exists => TRUE);

-- Keep virtual grids for 1 year
SELECT add_retention_policy('virtual_sensor_grid_20m', INTERVAL '1 year', if_not_exists => TRUE);
SELECT add_retention_policy('virtual_sensor_grid_1m', INTERVAL '1 year', if_not_exists => TRUE);

-- Continuous aggregates for efficient analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_field_stats
WITH (timescaledb.continuous) AS
SELECT 
    field_id,
    time_bucket('1 hour', timestamp) AS bucket,
    AVG(moisture_surface) AS avg_moisture_surface,
    AVG(moisture_root) AS avg_moisture_root,
    AVG(temp_surface) AS avg_temp_surface,
    STDDEV(moisture_surface) AS stddev_moisture,
    COUNT(*) AS reading_count
FROM soil_sensor_readings
WHERE quality_flag = 'valid'
GROUP BY field_id, bucket;

-- Refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('hourly_field_stats',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Sample fields table (master data)
CREATE TABLE IF NOT EXISTS fields (
    field_id VARCHAR(50) PRIMARY KEY,
    farm_id VARCHAR(50) NOT NULL,
    field_name VARCHAR(200) NOT NULL,
    boundary GEOMETRY(POLYGON, 4326) NOT NULL,
    area_hectares FLOAT,
    crop_type VARCHAR(100),
    planting_date DATE,
    harvest_date DATE,
    soil_type VARCHAR(100),
    irrigation_system VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fields_boundary ON fields USING GIST (boundary);
CREATE INDEX idx_fields_farm ON fields (farm_id);

-- Sample data insertion (for testing)
INSERT INTO fields (field_id, farm_id, field_name, boundary, area_hectares, crop_type, soil_type)
VALUES 
    ('field_001', 'farm_001', 'North Field', 
     ST_GeomFromText('POLYGON((-122.42 37.77, -122.41 37.77, -122.41 37.78, -122.42 37.78, -122.42 37.77))', 4326),
     10.5, 'Wheat', 'Loam'),
    ('field_002', 'farm_001', 'South Field',
     ST_GeomFromText('POLYGON((-122.42 37.76, -122.41 37.76, -122.41 37.77, -122.42 37.77, -122.42 37.76))', 4326),
     8.3, 'Corn', 'Clay Loam')
ON CONFLICT (field_id) DO NOTHING;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO farmsense_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO farmsense_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'FarmSense database initialized successfully!';
END $$;
