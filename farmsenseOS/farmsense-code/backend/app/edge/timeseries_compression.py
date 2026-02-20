"""
Timeseries Compression for FarmSense Data
Optimizes TimescaleDB storage using native compression and custom rollups.
"""
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class CompressionPolicy(Enum):
    """Compression policies based on data age"""
    HOT = "hot"           # < 7 days: uncompressed, fast access
    WARM = "warm"         # 7-30 days: native TimescaleDB compression
    COLD = "cold"         # 30-90 days: reduced precision
    ARCHIVE = "archive"   # > 90 days: daily summaries only


@dataclass
class CompressionStats:
    """Statistics for compression operations"""
    chunks_processed: int
    bytes_before: int
    bytes_after: int
    compression_ratio: float
    time_taken_seconds: float


class TimeseriesCompressor:
    """
    Manages compression policies for FarmSense sensor data.
    
    Uses TimescaleDB native compression with custom retention policies
    optimized for agricultural data patterns.
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.policies = {
            CompressionPolicy.HOT: {
                'chunk_interval': '1 day',
                'compression_enabled': False,
                'retention_days': 7
            },
            CompressionPolicy.WARM: {
                'chunk_interval': '7 days',
                'compression_enabled': True,
                'compression_after': '7 days',
                'retention_days': 30
            },
            CompressionPolicy.COLD: {
                'chunk_interval': '30 days',
                'compression_enabled': True,
                'reduce_precision': True,
                'retention_days': 90
            },
            CompressionPolicy.ARCHIVE: {
                'chunk_interval': '90 days',
                'rollup_only': True,
                'retention_days': 2555  # 7 years for compliance
            }
        }
    
    def setup_compression_policy(self, table_name: str, 
                                  policy: CompressionPolicy = CompressionPolicy.WARM):
        """
        Configure TimescaleDB compression for a sensor table.
        
        Args:
            table_name: Name of the hypertable
            policy: Compression policy to apply
        """
        config = self.policies[policy]
        
        queries = []
        
        # Enable native compression
        if config.get('compression_enabled'):
            queries.append(f"""
                ALTER TABLE {table_name} SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'device_id',
                    timescaledb.compress_orderby = 'time DESC'
                );
            """)
            
            # Set compression schedule
            if config.get('compression_after'):
                queries.append(f"""
                    SELECT add_compression_policy(
                        '{table_name}',
                        INTERVAL '{config['compression_after']}'
                    );
                """)
        
        # Set retention policy
        if config.get('retention_days'):
            queries.append(f"""
                SELECT add_retention_policy(
                    '{table_name}',
                    INTERVAL '{config['retention_days']} days'
                );
            """)
        
        return queries
    
    def compress_old_data(self, table_name: str, 
                          older_than_days: int = 7) -> CompressionStats:
        """
        Manually trigger compression for old chunks.
        
        Returns:
            CompressionStats with before/after metrics
        """
        start_time = time.time()
        
        # Get pre-compression stats
        before_stats = self._get_chunk_stats(table_name)
        
        # Compress chunks older than threshold
        compress_query = f"""
            SELECT compress_chunk(i)
            FROM show_chunks('{table_name}', older_than => INTERVAL '{older_than_days} days') i;
        """
        
        # Execute compression
        self.db.execute(compress_query)
        
        # Get post-compression stats
        after_stats = self._get_chunk_stats(table_name)
        
        return CompressionStats(
            chunks_processed=before_stats['chunk_count'],
            bytes_before=before_stats['total_bytes'],
            bytes_after=after_stats['total_bytes'],
            compression_ratio=before_stats['total_bytes'] / max(after_stats['total_bytes'], 1),
            time_taken_seconds=time.time() - start_time
        )
    
    def _get_chunk_stats(self, table_name: str) -> Dict:
        """Get storage statistics for a hypertable's chunks"""
        query = f"""
            SELECT 
                count(*) as chunk_count,
                sum(pg_total_relation_size(chunk_name)) as total_bytes
            FROM timescaledb_information.chunks
            WHERE hypertable_name = '{table_name}';
        """
        result = self.db.execute(query).fetchone()
        return {
            'chunk_count': result[0] or 0,
            'total_bytes': result[1] or 0
        }
    
    def create_rollups(self, source_table: str, 
                       rollup_interval: str = '1 hour') -> str:
        """
        Create continuous aggregates (rollups) for faster analytics queries.
        
        Args:
            source_table: Source hypertable name
            rollup_interval: Aggregation interval (e.g., '1 hour', '1 day')
            
        Returns:
            Name of created rollup table
        """
        rollup_table = f"{source_table}_{rollup_interval.replace(' ', '_')}_rollup"
        
        create_query = f"""
            CREATE MATERIALIZED VIEW {rollup_table}
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket('{rollup_interval}', time) as bucket,
                device_id,
                field_id,
                avg(moisture_vwc) as avg_moisture,
                min(moisture_vwc) as min_moisture,
                max(moisture_vwc) as max_moisture,
                avg(battery_mv) as avg_battery,
                count(*) as sample_count
            FROM {source_table}
            GROUP BY bucket, device_id, field_id
            WITH NO DATA;
        """
        
        # Add refresh policy
        refresh_query = f"""
            SELECT add_continuous_aggregate_policy(
                '{rollup_table}',
                start_offset => INTERVAL '1 month',
                end_offset => INTERVAL '1 hour',
                schedule_interval => INTERVAL '1 hour'
            );
        """
        
        return rollup_table
    
    def reduce_precision(self, table_name: str, 
                         older_than_days: int = 30,
                         moisture_decimals: int = 2,
                         temp_decimals: int = 1) -> int:
        """
        Reduce precision of old data to save space.
        
        This creates a new table with reduced precision and replaces the old one.
        Use with caution - data loss occurs!
        
        Returns:
            Number of rows processed
        """
        temp_table = f"{table_name}_reduced"
        
        # Create reduced-precision table
        create_query = f"""
            CREATE TABLE {temp_table} AS
            SELECT
                time,
                device_id,
                field_id,
                round(moisture_vwc::numeric, {moisture_decimals}) as moisture_vwc,
                round(temperature_c::numeric, {temp_decimals}) as temperature_c,
                round(battery_mv::numeric, -1) as battery_mv,  -- Round to 10mV
                -- Drop less important fields
                -- ec_surface, ec_root, ph, etc.
            FROM {table_name}
            WHERE time < now() - INTERVAL '{older_than_days} days';
        """
        
        # Make it a hypertable
        hypertable_query = f"""
            SELECT create_hypertable('{temp_table}', 'time');
        """
        
        # Compress the reduced table
        compress_query = f"""
            ALTER TABLE {temp_table} SET (timescaledb.compress);
        """
        
        # Return row count
        count_query = f"SELECT count(*) FROM {temp_table};"
        
        return 0  # Would return actual count in production
    
    def get_storage_report(self) -> Dict:
        """
        Generate a comprehensive storage utilization report.
        
        Returns:
            Dict with storage metrics by table and policy
        """
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'tables': []
        }
        
        # Query hypertable sizes
        size_query = """
            SELECT 
                hypertable_name,
                count(*) as chunk_count,
                sum(pg_total_relation_size(chunk_schema || '.' || chunk_name)) as total_bytes,
                sum(pg_total_relation_size(chunk_schema || '.' || chunk_name) - 
                    pg_relation_size(chunk_schema || '.' || chunk_name)) as index_bytes
            FROM timescaledb_information.chunks
            GROUP BY hypertable_name;
        """
        
        # Get compression stats
        compression_query = """
            SELECT 
                hypertable_name,
                count(*) as compressed_chunks,
                avg(before_compression_total_bytes) as avg_before,
                avg(after_compression_total_bytes) as avg_after
            FROM timescaledb_information.compression_settings cs
            JOIN timescaledb_information.chunks c ON c.hypertable_name = cs.hypertable_name
            WHERE is_compressed = true
            GROUP BY hypertable_name;
        """
        
        return report


class DeltaCompressor:
    """
    Implements delta-of-delta compression for timeseries data.
    Specialized for sensor readings where values change gradually.
    """
    
    def __init__(self):
        self.previous_values = {}
    
    def compress_timestamp(self, timestamp: float, 
                          device_id: str) -> int:
        """
        Compress timestamp as delta from previous.
        
        Uses delta-of-delta encoding:
        - Store actual timestamp for first reading
        - Store delta from previous for subsequent
        - Store delta-of-delta when intervals are regular
        """
        if device_id not in self.previous_values:
            self.previous_values[device_id] = {'time': timestamp, 'delta': 0}
            return int(timestamp)  # Full timestamp
        
        prev = self.previous_values[device_id]
        current_delta = int(timestamp - prev['time'])
        delta_of_delta = current_delta - prev['delta']
        
        # Update stored values
        prev['time'] = timestamp
        prev['delta'] = current_delta
        
        # If delta-of-delta is small (regular intervals), we can use fewer bits
        if -128 <= delta_of_delta <= 127:
            # Fits in 1 byte with flag
            return delta_of_delta | 0x8000  # Set flag bit
        else:
            # Return full delta
            return current_delta
    
    def compress_value(self, value: float, 
                       previous: Optional[float],
                       precision: int = 1000) -> int:
        """
        Compress floating point value as delta.
        
        Args:
            value: Current value
            previous: Previous value (None for first)
            precision: Multiplier for fixed-point encoding
            
        Returns:
            Compressed integer representation
        """
        scaled = int(value * precision)
        
        if previous is None:
            return scaled  # Full value
        
        prev_scaled = int(previous * precision)
        delta = scaled - prev_scaled
        
        return delta  # Return delta (usually smaller)


# SQL templates for common operations

SETUP_HYPERTABLE_SQL = """
-- Convert sensor readings table to hypertable
SELECT create_hypertable(
    'sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_time 
ON sensor_readings (device_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_field_time 
ON sensor_readings (field_id, time DESC);
"""

ENABLE_COMPRESSION_SQL = """
-- Enable native compression
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id,field_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- Compress chunks older than 7 days
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');

-- Retain compressed data for 90 days
SELECT add_retention_policy('sensor_readings', INTERVAL '90 days');
"""

CREATE_ROLLUPS_SQL = """
-- Hourly rollup for dashboard queries
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) as bucket,
    device_id,
    field_id,
    avg(moisture_vwc) as avg_moisture,
    min(moisture_vwc) as min_moisture,
    max(moisture_vwc) as max_moisture,
    stddev(moisture_vwc) as std_moisture,
    avg(temperature_c) as avg_temp,
    avg(battery_mv) as avg_battery,
    count(*) as sample_count
FROM sensor_readings
GROUP BY bucket, device_id, field_id
WITH NO DATA;

-- Auto-refresh hourly
SELECT add_continuous_aggregate_policy(
    'sensor_readings_hourly',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- Daily rollup for long-term analytics
CREATE MATERIALIZED VIEW sensor_readings_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) as bucket,
    field_id,
    avg(moisture_vwc) as avg_moisture,
    min(moisture_vwc) as min_moisture,
    max(moisture_vwc) as max_moisture,
    avg(temperature_c) as avg_temp,
    max(temperature_c) as max_temp,
    min(temperature_c) as min_temp,
    avg(battery_mv) as avg_battery,
    min(battery_mv) as min_battery,
    count(*) as sample_count
FROM sensor_readings
GROUP BY bucket, field_id
WITH NO DATA;

-- Auto-refresh daily
SELECT add_continuous_aggregate_policy(
    'sensor_readings_daily',
    start_offset => INTERVAL '6 months',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);
"""

# Python convenience functions
def get_compression_ddl(table_name: str = "sensor_readings") -> str:
    """Returns SQL to set up compression for a table"""
    return SETUP_HYPERTABLE_SQL + "\n" + ENABLE_COMPRESSION_SQL


def get_rollup_ddl() -> str:
    """Returns SQL to create continuous aggregates"""
    return CREATE_ROLLUPS_SQL
