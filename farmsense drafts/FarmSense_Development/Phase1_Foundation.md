# FARMSENSE DEVELOPMENT PLAN - PHASE 1
## Foundation Architecture (Weeks 1-3)

### 1.1 Core Architecture Overview

**Hub-and-Spoke Topology:**
- 1 Jetson Nano serves 9 fields (~1,170 acres total)
- Each Jetson paired with dedicated gateway hub (1:1)
- Cloud instance is live mirror, not batch backup
- Cold spare on-site, pre-configured, ready for activation

**Failover Hierarchy:**
1. Primary: Jetson Nano (real-time processing)
2. Secondary: Hosted cloud (instant takeover on failure)
3. Tertiary: Cold spare (manual swap <30 min)

### 1.2 Technology Stack (Fresh Selection)

**Edge Compute:**
- OS: Ubuntu 22.04 LTS (ARM64)
- Systems: Rust
- ML/Computation: Python + CuPy
- GPU: CUDA 11.8
- Database: TimescaleDB
- Messaging: NATS

**Gateway:**
- LoRa: RFM95W 915MHz (15-mile range)
- Mesh: 5GHz WiFi
- Cellular: LTE failover
- Power: Solar + LiFePO4 battery

**Cloud:**
- Self-hosted infrastructure
- Real-time replication from Jetson
- Automatic DNS cutover <30 seconds

### 1.3 Sensor Network

**Horizontal Blanket Sensors:**
- ~99 total (11 per field average)
- 18" length, 2-depth (12", 18")
- TDR measurement, ±2% VWC accuracy
- 3/16" 316 stainless steel shell
- Drive-tip deployment

**Master Vertical Nails:**
- 9 total (1 per field)
- Medium: 42" depth, 5 measurement points
- Large: 60" depth, 7 measurement points
- Crop-dependent selection
- Compliance gate at 42"/60"

**Pilot Totals:**
- ~108 sensors
- ~270 measurement points
- 15-minute update intervals
