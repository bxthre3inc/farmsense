# FarmSenseOS: Hardware-Software Integration Architecture

## Executive Summary

This document bridges the gap between the hardware BOM specifications and the software stack, detailing how each hardware component communicates with the FarmSenseOS backend, data flows, API endpoints, and integration requirements.

---

## Hardware-Software Interface Matrix

### 1. LRZ (Lateral Root-Zone Scout) - Dumb Node

**Hardware Spec:**
- Nordic nRF52840 (Cortex-M4)
- Capacitive moisture traces (FR4 PCB)
- 19Ah LiSOCl2 D-cell battery (12-year lifespan)
- 900MHz mesh radio

**Software Integration:**
```yaml
Communication_Protocol: "900MHz mesh → DHU"
Data_Format: "Binary protobuf (ultra-low overhead)"
Transmission_Mode: "Burst transmit-only (no handshake)"
API_Endpoint: "POST /api/v1/ingest/lrz-bulk"
Frequency: "Every 15 minutes"
Payload_Size: "~64 bytes per reading"
```

**Backend Requirements:**
- High-throughput ingestion endpoint for 15,600 concurrent devices
- Time-series database (TimescaleDB) for moisture telemetry
- Geospatial indexing for 1-meter grid mapping

**API Contract:**
```json
{
  "device_id": "LRZ-15.6k-UUID",
  "timestamp": "2026-02-16T22:00:00Z",
  "lat": 37.5748,
  "lon": -105.9856,
  "moisture_vwc": 0.32,
  "battery_mv": 3300,
  "sequence_num": 15420
}
```

---

### 2. VFA (Vertical Field Anchor) - Ground Truth

**Hardware Spec:**
- NXP i.MX RT1060 (Cortex-M7, 600MHz)
- TDR Probe Array (Gold-plated, legal-grade)
- BME280 (Atmospheric: temp, humidity, pressure)
- AS7262 (Visible/IR 6-channel spectrometer)
- LTU Lite 5GHz radio
- 40Ah LiFePO4 battery

**Software Integration:**
```yaml
Communication_Protocol: "5GHz Ubiquiti LTU → DHU → RSS"
Data_Format: "JSON + Binary attachments"
Transmission_Mode: "Full-duplex, ACK-required"
API_Endpoints:
  - "POST /api/v1/sensors/vfa/telemetry"
  - "POST /api/v1/sensors/vfa/spectral"
  - "GET /api/v1/sensors/vfa/{id}/calibration"
Frequency: "Every 5 minutes (normal), 1 minute (irrigation active)"
```

**Key Features:**
- **TDR Data Processing**: Raw TDR waveforms require edge-processing to convert to VWC (Volumetric Water Content)
- **Spectral Analysis**: AS7262 data feeds into crop health indices (NDVI proxy)
- **Legal-Grade Timestamping**: Cryptographic signing for Water Court defensibility

**API Contract:**
```json
{
  "device_id": "VFA-1280-UUID",
  "field_id": "field_001",
  "timestamp": "2026-02-16T22:00:00Z",
  "location": {"lat": 37.5748, "lon": -105.9856, "elevation": 2295},
  "tdr": {
    "depth_6in": {"vwc": 0.28, "ec_ms_m": 1.2, "temp_c": 12.5},
    "depth_12in": {"vwc": 0.31, "ec_ms_m": 0.9, "temp_c": 11.2},
    "depth_24in": {"vwc": 0.35, "ec_ms_m": 0.7, "temp_c": 10.8}
  },
  "atmospheric": {
    "temp_c": 18.5,
    "humidity_pct": 42,
    "pressure_hpa": 1013.2,
    "solar_wm2": 0
  },
  "spectral": {
    "410nm": 1250, "435nm": 3400, "460nm": 5600,
    "485nm": 7200, "510nm": 8100, "535nm": 7800
  },
  "battery": {"voltage": 13.2, "current_ma": 450, "soc_pct": 78},
  "signature": "sha256:abcd...1234"
}
```

---

### 3. PFA (Pressure & Flow Anchor) - Well Sentry

**Hardware Spec:**
- NXP i.MX RT (Cortex-M7)
- Dwyer PBLTX Hydrostatic Depth Sounder (300ft vented)
- 400A Split-Core CT Clamps (x3 phases)
- 200 PSI Pressure Transducer (line pressure)
- Omron 30A Industrial Relay (pump control)
- AC Step-down + 40Ah LiFePO4

**Software Integration:**
```yaml
Communication_Protocol: "5GHz mesh → DHU"
Data_Format: "JSON + Binary pump signatures"
Transmission_Mode: "Event-driven + heartbeat"
API_Endpoints:
  - "POST /api/v1/wells/{id}/telemetry"
  - "POST /api/v1/wells/{id}/pump-signature"
  - "POST /api/v1/wells/{id}/emergency-stop"  # Critical!
  - "GET /api/v1/wells/{id}/depth-history"
Frequency:
  normal: "Every 60 seconds"
  pumping: "Every 5 seconds"
  alarm: "Immediate (WebSocket)"
```

**Critical Features:**
- **Autonomous Reflex**: PFA can trigger pump shutdown WITHOUT cloud connectivity
- **Predictive Maintenance**: CT clamp signatures analyzed for cavitation/dry-pump detection
- **Water Court Compliance**: Vented depth sounder provides legally defensible aquifer drawdown data

**API Contract:**
```json
{
  "device_id": "PFA-1280-UUID",
  "well_id": "well_001",
  "timestamp": "2026-02-16T22:00:00Z",
  "depth_sounder": {
    "water_column_ft": 142.5,
    "drawdown_rate_ft_hr": 0.8,
    "recovery_rate_ft_hr": 2.1,
    "static_level_ft": 145.2
  },
  "electrical": {
    "l1_amps": 38.5, "l2_amps": 39.1, "l3_amps": 38.8,
    "voltage": 478,
    "power_kw": 32.1,
    "energy_kwh": 1247.5,
    "pump_signature_match": 0.94,
    "anomaly_detected": false
  },
  "hydraulic": {
    "line_pressure_psi": 42,
    "flow_rate_gpm": 850
  },
  "pump_state": "running",
  "relay_state": "closed",
  "autonomous_triggers": {
    "dry_pump_detected": false,
    "cavitation_detected": false,
    "emergency_stop_active": false
  }
}
```

---

### 4. PMT (Pivot Tracking Module) - Flow Auditor

**Hardware Spec:**
- Cortex-M4 Processing Sled
- u-blox ZED-F9P RTK GNSS (cm-level accuracy)
- Bosch BNO055 9-Axis IMU
- Badger Meter Dynasonics Ultrasonic Transit-Time ($648!)
- 10W Solar + LiFePO4
- BLE Whip antenna

**Software Integration:**
```yaml
Communication_Protocol: "BLE → VFA → DHU"
Data_Format: "JSON + binary GNSS/IMU"
Transmission_Mode: "Continuous streaming during operation"
API_Endpoints:
  - "POST /api/v1/pivots/{id}/kinematics"
  - "POST /api/v1/pivots/{id}/flow-meter"
  - "POST /api/v1/pivots/{id}/health"
  - "GET /api/v1/pivots/{id}/coverage-map"
Frequency:
  gnss_imu: "10Hz (100ms)"
  flow: "1Hz (every second)"
  health: "Every 60 seconds"
```

**Advanced Features:**
- **VRI Integration**: Variable Rate Irrigation control based on soil variability maps
- **Crabbing Detection**: IMU tilt analysis prevents catastrophic pivot collapse
- **Coverage Verification**: RTK GNSS tracks exact water application location

**API Contract:**
```json
{
  "device_id": "PMT-1280-UUID",
  "pivot_id": "pivot_001",
  "timestamp": "2026-02-16T22:00:00Z",
  "kinematics": {
    "position": {"lat": 37.5748, "lon": -105.9856, "accuracy_cm": 2.1},
    "heading_deg": 245.5,
    "speed_m_s": 0.15,
    "span_tilt_deg": 1.2,
    "crabbing_detected": false,
    "tower_status": [
      {"tower": 1, "drive_on": true, "alignment_ok": true},
      {"tower": 2, "drive_on": true, "alignment_ok": true},
      {"tower": 3, "drive_on": true, "alignment_ok": false, "alarm": "minor_misalignment"}
    ]
  },
  "flow": {
    "velocity_m_s": 2.45,
    "flow_rate_gpm": 847.3,
    "total_gallons": 1247500,
    "accumulated_acre_inches": 8.42
  },
  "vri": {
    "zone_valve_states": [0.8, 0.9, 1.0, 0.7, 0.9],
    "prescription_applied": "prescription_2026_02_16",
    "actual_vs_target": 0.97
  },
  "health": {
    "solar_voltage": 14.2,
    "battery_soc": 85,
    "ultrasonic_signal_strength": 92,
    "gnss_sats": 18,
    "rtk_fix": true
  }
}
```

---

### 5. DHU (District Hub) - Regional Aggregator

**Hardware Spec:**
- OnLogic CL210 8-Core ARM SoC
- 128GB pSLC Industrial SSD (extreme write endurance)
- 3x Ubiquiti LTU Sector antennas (360° coverage)
- Telit LTE-M/NB-IoT modem
- 200W Solar + 200Ah heated LiFePO4
- 35ft Class 4 timber pole

**Software Integration:**
```yaml
Role: "Edge Computing + Mesh Coordination + Backhaul"
Local_Services:
  - "MQTT Broker (local mesh)"
  - "TimescaleDB (local cache)"
  - "Kriging Engine (lightweight)"
  - "DHCP + DNS for field devices"
API_Endpoints:
  - "POST /api/v1/dhu/{id}/ingest"  # From field devices
  - "POST /api/v1/dhu/{id}/sync"    # To RSS
  - "GET /api/v1/dhu/{id}/status"
  - "GET /api/v1/dhu/{id}/blackbox"
Connection:
  upstream: "RSS via LTE/Starlink/Fiber"
  downstream: "500+ field devices via 5GHz"
```

**Edge Computing:**
- Local Kriging interpolation (reduced resolution)
- Data decimation (compress before sending to RSS)
- Black box recording (local 30-day buffer)
- Autonomous actuation (pump shutdown if RSS unreachable)

**API Contract:**
```json
{
  "hub_id": "DHU-025-SLV",
  "timestamp": "2026-02-16T22:00:00Z",
  "location": {"lat": 37.5748, "lon": -105.9856},
  "connectivity": {
    "upstream": "lte_primary",
    "signal_dbm": -78,
    "latency_ms": 45
  },
  "devices_connected": 487,
  "ingestion_rate_s": 42.5,
  "local_storage": {
    "used_gb": 89.2,
    "free_gb": 38.8,
    "oldest_record": "2026-01-17T00:00:00Z"
  },
  "kriging_queue": 12,
  "cpu_load": 0.45,
  "memory_used_pct": 62
}
```

---

### 6. RSS (Regional Superstation) - The Cortex

**Hardware Spec:**
- AMD Threadripper PRO 64-core
- 50TB NVMe RAID-10 (WD Gold Enterprise)
- Starlink Business + Fiber ONT
- 1.2kW Solar + 800Ah battery
- 5kW Honda dual-fuel generator

**Software Stack:**
```yaml
Primary_Services:
  - "Zo Kriging Engine (High-Resolution)"
  - "TimescaleDB Cluster (Primary)"
  - "PostGIS (Spatial Analysis)"
  - "RabbitMQ (Event Bus)"
  - "Redis (Cache + Session Store)"
  - "FastAPI Backend"
  - "React Dashboards"
  
Backup_Services:
  - "Cloud Sync to Oracle Shadow"
  - "P2P Mesh Failover to other RSS"
  - "Air-Gap Mode capability"

API_Endpoints: "All primary API endpoints"
```

**High-Performance Computing:**
- 1-meter resolution Kriging for entire subdistrict
- Machine learning model training
- Water court report generation
- Real-time pivot VRI optimization

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW HIERARCHY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LRZ (15,600) ──900MHz──┐                                                   │
│                          │                                                   │
│  VFA (1,280) ───5GHz────┼──→ DHU (25) ──LTE/Starlink──→ RSS (1) ──Cloud    │
│                          │         ↑                         │               │
│  PFA (1,280) ───5GHz────┘    Local Kriging           Zo Engine              │
│                                   +                         +                │
│  PMT (1,280) ──BLE→VFA     Black Box Buffer      High-Res Kriging            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Software Requirements by Hardware Component

| Component | Backend Service | Database | Real-Time | Security |
|-----------|----------------|----------|-----------|----------|
| **LRZ** | High-throughput ingest | TimescaleDB | No | Protobuf + CRC |
| **VFA** | Full-featured API | TimescaleDB + PostGIS | WebSocket | TLS 1.3 + Sig |
| **PFA** | Critical path API | TimescaleDB | WebSocket (alarm) | TLS 1.3 + Auth |
| **PMT** | Streaming API | TimescaleDB | WebSocket | TLS 1.3 |
| **DHU** | Edge services | Local TimescaleDB | MQTT | Internal TLS |
| **RSS** | Full stack | Primary cluster | All protocols | Full PKI |

---

## API Endpoint Summary

### Ingestion Endpoints
- `POST /api/v1/ingest/lrz-bulk` - Bulk LRZ data
- `POST /api/v1/sensors/vfa/telemetry` - VFA telemetry
- `POST /api/v1/wells/{id}/telemetry` - PFA well data
- `POST /api/v1/pivots/{id}/kinematics` - PMT pivot data

### Control Endpoints
- `POST /api/v1/wells/{id}/emergency-stop` - PFA pump shutdown
- `POST /api/v1/pivots/{id}/vri-command` - PMT VRI control
- `POST /api/v1/dhu/{id}/sync` - DHU upstream sync

### Query Endpoints
- `GET /api/v1/fields/{id}/moisture-map` - Kriged moisture
- `GET /api/v1/wells/{id}/depth-history` - Aquifer levels
- `GET /api/v1/pivots/{id}/coverage-map` - Irrigation coverage
- `GET /api/v1/compliance/report` - Water court data

---

## Critical Integration Points

### 1. Autonomous Reflex (PFA)
**Requirement**: PFA must trigger pump shutdown within 2 seconds of fault detection, even without internet connectivity.

**Implementation**:
- Local rule engine on PFA microcontroller
- Hardwired relay control (no software intermediation)
- Fail-safe: relay opens on communication loss

### 2. Legal-Grade Timestamping (VFA)
**Requirement**: Data must be cryptographically signed for Water Court defensibility.

**Implementation**:
- SHA-256 signing at VFA
- Certificate chain verification at RSS
- Immutable ledger storage

### 3. VRI Optimization (PMT)
**Requirement**: Variable Rate Irrigation based on real-time soil variability.

**Implementation**:
- Kriging engine generates prescription maps
- PMT receives zone commands via BLE
- Real-time flow modulation

---

## Deployment Checklist

### Pre-Deployment
- [ ] Configure device provisioning system
- [ ] Generate cryptographic keypairs for all devices
- [ ] Load firmware with unique IDs
- [ ] Test mesh connectivity

### Deployment
- [ ] GPS tag each device location
- [ ] Verify RF handshake with parent hub
- [ ] Calibrate sensors (TDR, ultrasonic, etc.)
- [ ] Document as-installed configuration

### Post-Deployment
- [ ] Verify data flow to RSS
- [ ] Test autonomous reflex (PFA)
- [ ] Validate Kriging interpolation accuracy
- [ ] Train users on dashboards

---

## Total System Scale (Subdistrict 1)

| Metric | Value |
|--------|-------|
| **Total Devices** | 19,466 |
| **Sensor Readings/Day** | ~2.8 million |
| **Data Volume/Day** | ~150 GB |
| **Geographic Coverage** | ~117,000 acres |
| **Hardware Investment** | $5,382,940 |
| **Annual O&M** | ~$450,000 |

---

*This document ensures seamless integration between the hardware procurement and software development teams.*
