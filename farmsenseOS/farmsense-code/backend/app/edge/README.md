# FarmSense Edge Optimization Modules

Software-only optimizations for the FarmSense network that work within existing hardware constraints.

## Modules

### 1. `delta_encoder.py` - Delta Compression
Compresses sensor readings by encoding changes rather than absolute values.

**Key Features:**
- Reduces LRZ transmission from ~200 bytes JSON to ~8 bytes binary
- Adaptive compression levels based on network conditions
- Batch encoding for VFA→DHU transmission

**Usage:**
```python
from app.edge.delta_encoder import DeltaEncoder, CompressionLevel

encoder = DeltaEncoder()

# Encode a reading
encoded = encoder.encode('LRZ-12345', reading, CompressionLevel.LIGHT)
# Returns ~8 bytes vs 200 bytes JSON

# Decode at DHU/RSS
decoded = encoder.decode('LRZ-12345', encoded)
```

**Expected Impact:** 94% reduction in airtime for LRZ→VFA

---

### 2. `adaptive_sampler.py` - Dynamic Sampling
Adjusts sampling rates based on field conditions to extend battery life.

**Key Features:**
- 1-minute sampling during irrigation
- 6-hour sampling during winter dormancy
- Battery-aware emergency mode
- Tracks 12-year battery target

**Usage:**
```python
from app.edge.adaptive_sampler import AdaptiveSampler, FieldConditions

sampler = AdaptiveSampler()

# Update field conditions
sampler.update_field_conditions('field_001', FieldConditions(
    irrigation_active=True,
    is_dormant_season=False
))

# Get optimal interval
decision = sampler.get_next_sample_interval('LRZ-12345', 'field_001')
# Returns interval in seconds based on conditions
```

**Expected Impact:** 200-300% battery life extension during dormant periods

---

### 3. `timeseries_compression.py` - Database Optimization
TimescaleDB compression and rollup strategies.

**Key Features:**
- Native TimescaleDB compression (10:1 ratio)
- Continuous aggregates for fast queries
- Precision reduction for historical data

**Usage:**
```python
from app.edge.timeseries_compression import TimeseriesCompressor

compressor = TimeseriesCompressor(db_connection)

# Enable compression
compressor.setup_compression_policy('sensor_readings')

# Create hourly rollups
compressor.create_rollups('sensor_readings', '1 hour')

# Compress old data
stats = compressor.compress_old_data('sensor_readings', older_than_days=7)
print(f"Compression ratio: {stats.compression_ratio:.1f}:1")
```

**Expected Impact:** 70% storage reduction, 10x faster analytics queries

---

### 4. `network_optimizer.py` - Network Resilience
QUIC, FEC, and mesh optimizations for unreliable agricultural networks.

**Key Features:**
- 0-RTT connection resumption (survives Starlink handoffs)
- Forward Error Correction for lossy 900MHz mesh
- Priority queuing (emergency stops get through first)
- Connection pooling for DHU→RSS

**Usage:**
```python
from app.edge.network_optimizer import ResilientConnection, ConnectionPool

# Single resilient connection
conn = ResilientConnection('https://rss.farmsense.io', 
                           fec_enabled=True, quic_enabled=True)

# Queue critical message
msg_id = conn.enqueue(emergency_payload, priority=0)  # 0=emergency

# Or use connection pool
pool = ConnectionPool(['rss1.farmsense.io', 'rss2.farmsense.io'])
await pool.initialize()
msg_id = await pool.send_with_failover(payload, priority=1)
```

**Expected Impact:** Survives 10% packet loss without retransmission

---

## Integration Guide

### Step 1: Enable at VFA (Edge Gateway)

Modify `vfa_firmware.py`:
```python
from edge.delta_encoder import DeltaEncoder
from edge.adaptive_sampler import AdaptiveSampler

class VFAGateway:
    def __init__(self):
        self.encoder = DeltaEncoder()
        self.sampler = AdaptiveSampler()
    
    def process_lrz_batch(self, readings):
        # Apply delta encoding
        encoded = []
        for r in readings:
            encoded.append(self.encoder.encode(r['device_id'], r))
        
        # Apply batch compression
        return self.encoder.encode_batch(device_id, encoded)
```

### Step 2: Configure DHU (District Hub)

Modify `dhu_processor.py`:
```python
from edge.network_optimizer import ConnectionPool
from edge.timeseries_compression import TimeseriesCompressor

class DHUProcessor:
    def __init__(self):
        self.rss_pool = ConnectionPool(rss_endpoints)
        self.compressor = TimeseriesCompressor(db)
    
    async def sync_to_rss(self, batch):
        # High-compression for backhaul
        compressed = self.compressor.compress_batch(batch)
        await self.rss_pool.send_with_failover(compressed)
```

### Step 3: Configure RSS (Regional Superstation)

Enable TimescaleDB compression:
```sql
-- Run once on database setup
SELECT create_hypertable('sensor_readings', 'time', chunk_time_interval => INTERVAL '1 day');

ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('sensor_readings', INTERVAL '7 days');
```

---

## Expected System-Wide Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LRZ→VFA Airtime | 200 bytes × 15,600 devices | 8 bytes × 15,600 devices | 96% reduction |
| Daily Data Volume | 150 GB | 45 GB | 70% reduction |
| LRZ Battery Life | 8 years | 12+ years | 50% extension |
| DHU→RSS Bandwidth | 100% utilization | 15% utilization | 85% reduction |
| Query Latency | 200ms | 50ms | 75% faster |
| Storage (90-day) | 13.5 TB | 4 TB | 70% reduction |

---

## Testing

Run unit tests:
```bash
cd /home/workspace/farmsenseOS/farmsense-code/backend
python -m pytest tests/edge/test_delta_encoder.py -v
python -m pytest tests/edge/test_adaptive_sampler.py -v
```

Load test simulation:
```python
from edge.benchmark import run_simulation

# Simulate 15,600 LRZ devices for 1 hour
results = run_simulation(
    num_devices=15600,
    duration_hours=1,
    compression=True,
    adaptive_sampling=True
)

print(f"Total bytes transmitted: {results.total_bytes}")
print(f"Battery consumption: {results.battery_drain_mv}mV")
```

---

## Hardware Compatibility

All optimizations are **software-only** and work with existing hardware:

- **LRZ**: Uses existing 128-bit AES, no changes needed
- **VFA**: Uses existing AES-256 hardware, no changes needed  
- **PFA**: No changes (emergency reflex unchanged)
- **PMT**: No changes (BLE stack unchanged)
- **DHU**: Software optimization of existing 8-core ARM
- **RSS**: TimescaleDB configuration changes only

No BOM changes required. No firmware reflashing needed for field devices.
