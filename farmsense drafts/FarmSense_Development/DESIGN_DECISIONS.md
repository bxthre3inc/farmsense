# FARMSENSE DESIGN DECISIONS
## Fresh Build Rationale

### 1. Jetson Nano + Gateway Pairing
**Decision:** Each Jetson Nano is paired with one dedicated gateway hub.

**Rationale:**
- Clear hardware budgeting: Each deployment unit includes both devices
- Simplified troubleshooting: 1:1 relationship between compute and connectivity
- Redundancy isolation: Gateway failure doesn't cascade to multiple Jetsons
- Power budget clarity: Solar/battery sizing per paired unit

**From Project FarmSense v3.9:** Gateway hubs specified as "1-2" for pilot; clarified here as 1:1 pairing with cost implications.

---

### 2. Cloud as Live Mirror (Not Batch Backup)
**Decision:** Cloud instance maintains real-time synchronized state with Jetson.

**Rationale:**
- Instant failover: No data gap during transition
- Seamless handoff: DNS cutover vs. state restoration
- Audit continuity: No missing timestamps in forensic chain
- Parallel operation: Cloud can validate Jetson decisions in real-time

**From Previous Builds:** Earlier designs used batch/cloud-dependent processing; this design makes cloud subordinate to edge.

---

### 3. Cold Spare Physical Replacement
**Decision:** Cold spare is a physical Jetson on-site, not just cloud backup.

**Rationale:**
- Ultimate reliability: Physical hardware replaces failed unit
- No cloud dependency: Works even during extended outages
- 30-minute swap: Acceptable for 15-minute update intervals
- Pre-loaded keys: Maintains cryptographic chain continuity

**From Project FarmSense v3.9:** "Hosted cloud + cold spare on-site" specified; this design defines the activation workflow.

---

### 4. Rust for Systems, Python for ML
**Decision:** Split language approach based on workload characteristics.

**Rationale:**
- Rust: Memory safety, zero-cost abstractions, reliable systems code
- Python: Ecosystem (CuPy, scipy), rapid ML prototyping, GPU acceleration
- Clear boundaries: Data ingestion/failover in Rust; Bayesian/kriging in Python
- Maintainability: Each language where it excels

**Fresh Decision:** Not carried from previous builds; selected for optimal performance.

---

### 5. NATS over MQTT/RabbitMQ
**Decision:** NATS for messaging backbone.

**Rationale:**
- Lightweight: Single binary, minimal resource use
- Jetson-optimized: Designed for edge/IoT workloads
- Built-in resilience: Automatic reconnection, buffering
- Performance: Millions of messages/second capability

**Fresh Decision:** Selected specifically for FarmSense requirements.

---

### 6. TimescaleDB over InfluxDB/Timescale
**Decision:** TimescaleDB (PostgreSQL extension) for time-series.

**Rationale:**
- SQL interface: Familiar querying, complex analytics
- Time-series optimization: Hypertables, continuous aggregation
- Forensic suitability: ACID compliance, audit logging friendly
- Ecosystem: GIS extensions for geospatial queries

**Fresh Decision:** Chosen for forensic integrity requirements.

---

### 7. Ed25519 over RSA/ECDSA
**Decision:** Ed25519 for cryptographic signing.

**Rationale:**
- Compact signatures: 64 bytes vs. 256+ bytes for RSA
- Fast verification: Critical for real-time processing
- Secure: No timing side-channels
- Hardware support: Many MCUs have accelerated implementations

**Fresh Decision:** Selected for sensor-level signing efficiency.

---

### 8. Regression Kriging with Soil Variability
**Decision:** Use soil texture maps as trend variables in kriging.

**Rationale:**
- Physical basis: Soil properties explain moisture distribution
- Bayesian integration: Soil map evolves with observations
- Better than IDW: Accounts for spatial autocorrelation
- GPU parallelizable: Matrix operations on Jetson

**From Project FarmSense v3.9:** "Recursive Bayesian filter learns soil texture"; this implements it in kriging.

---

### 9. 15-Minute Intervals
**Decision:** 15-minute sensor update intervals.

**Rationale:**
- Irrigation timing: Matches typical pivot rotation periods
- Data volume: Manageable for ~270 points × 9 fields
- Power budget: Balances LoRa duty cycle with battery life
- Court admissibility: Sufficient granularity for legal proof

**From Project FarmSense v3.9:** Explicitly specified; maintained.

---

### 10. 1-Meter Grid Resolution
**Decision:** 1-meter virtual sensor grid.

**Rationale:**
- VRI control: Matches precision agriculture standards
- Computational feasible: ~4.7 million cells for 1,170 acres
- Spatial detail: Captures field variability
- Satellite fusion: 1m is appropriate scale for Sentinel integration

**From Project FarmSense v3.9:** Explicitly specified; maintained.

---

## FEATURES EXTRACTED FROM PREVIOUS BUILDS

| Feature | Source | Implementation |
|---------|--------|----------------|
| SHA-256 hashing | Previous builds | Sensor firmware + edge services |
| Cryptographic signing | Previous builds | Ed25519 at sensor level |
| Bayesian soil learning | Previous builds | EKF with texture adaptation |
| Regression kriging | Previous builds | GPU-accelerated CuPy |
| Triple redundancy | Previous builds | Jetson + cloud + cold spare |
| 24-month retention | Previous builds | TimescaleDB local storage |
| VRI integration | Previous builds | Modbus TCP/RTU controller |

## FEATURES DELIBERATELY CHANGED

| Feature | Previous | Current | Rationale |
|---------|----------|---------|-----------|
| Cloud dependency | Primary compute | Backup only | Edge-first autonomy |
| Failover timing | Manual restore | Instant DNS cutover | Hiccup-free operation |
| Gateway ratio | Shared | 1:1 per Jetson | Clear cost accounting |
| Language | Python-heavy | Rust + Python | Systems reliability |
| Database | SQLite/Influx | TimescaleDB | Forensic integrity |

---

*Document Version: 1.0*  
*Date: February 2026*
