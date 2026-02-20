# FarmSense OS v1.0

## Deterministic Farming Operating System

**Ground-up rebuild** | **CLI-first, headless architecture** | **Zo Cloud Native**

FarmSense OS is a deterministic farming operating system designed to eliminate irrigation guesswork through forensic-grade data integrity. Built entirely from scratch with a CLI-first, headless architecture.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FARMSENSE ECOSYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ZO CLOUD (farmsense.zo.computer)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │   │
│  │  │ FREE TIER    │  │ PAID TIER    │  │ ENTERPRISE TIER          │  │   │
│  │  │ 1 field      │  │ 3+ fields    │  │ 9+ fields (Jetson Nano)  │  │   │
│  │  │ Hourly       │  │ 15-min       │  │ 15-min local + cloud     │  │   │
│  │  │ 30m grid     │  │ 1m grid      │  │ 1m grid                  │  │   │
│  │  │ Suggestions  │  │ Full features│  │ VRI control              │  │   │
│  │  │ No compliance│  │ No compliance│  │ COMPLIANCE PROMISE       │  │   │
│  │  └──────────────┘  └──────────────┘  │ Cold spare + failover    │  │   │
│  │                                       └──────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    MAIN SERVER (Zo)                            │  │   │
│  │  │  • Multi-tenant tenant management                               │  │   │
│  │  │  • Long-term archive (10+ years from deployment)               │  │   │
│  │  │  • Compliance reporting for all tiers                          │  │   │
│  │  │  • Cloud mirror for enterprise failover                        │  │   │
│  │  │  • API for CSU research partnership                            │  │   │
│  │  └─────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FIELD DEPLOYMENT (Enterprise)                   │   │
│  │                                                                     │   │
│  │  ┌──────────────┐      ┌─────────────────────────────────────────┐ │   │
│  │  │ JETSON NANO  │◄────►│  9 Fields (Hub-and-Spoke)               │ │   │
│  │  │ + Gateway    │      │  • ~99 horizontal blanket sensors       │ │   │
│  │  │              │      │  • 9 master vertical nails (5/7-depth)  │ │   │
│  │  │ Primary      │      │  • ~270 measurement points              │ │   │
│  │  │ Compute      │      │  • 1-meter virtual grid (Kriging)       │ │   │
│  │  └──────────────┘      │  • 15-minute update intervals           │ │   │
│  │         │              └─────────────────────────────────────────┘ │   │
│  │         │ Failover sync                                          │   │
│  │         ▼                                                          │   │
│  │  ┌──────────────┐      ┌─────────────────────────────────────────┐ │   │
│  │  │ CLOUD MIRROR │      │  Cold Spare Jetson (on-site)            │ │   │
│  │  │ (Zo)         │◄────►│  • Pre-configured, powered off          │ │   │
│  │  │              │      │  • <30 min swap time                    │ │   │
│  │  │ Takes over   │      │  • Auto-sync from cloud mirror          │ │   │
│  │  │ on failure   │      └─────────────────────────────────────────┘ │   │
│  │  └──────────────┘                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Three-Tier Subscription Model

### Free Cloud Tier
- **Fields**: 1 maximum
- **Update interval**: Hourly
- **Virtual grid**: 30-meter resolution
- **Features**: Basic suggestions, limited analytics
- **Compliance**: Auditable by State Engineer, but **no compliance promise to farmer**
- **Contract**: None (free)

### Paid Cloud Tier
- **Fields**: Unlimited (3+ year contract)
- **Update interval**: 15 minutes
- **Virtual grid**: 1-meter resolution
- **Features**: Full analytics, API access, advanced forecasting
- **Compliance**: Auditable, but **no compliance promise** (cloud-only)
- **Contract**: 3 years

### Enterprise Tier
- **Fields**: 9+ (hub-and-spoke), scalable
- **Update interval**: 15 minutes (local edge compute)
- **Virtual grid**: 1-meter resolution
- **Features**: All paid features + VRI control, forensic audit, local compute
- **Compliance**: **Full compliance promise** with local Jetson deployment
- **Hardware**: Jetson Nano + dedicated gateway per field group
- **Failover**: Cloud mirror takeover + cold spare swap
- **Contract**: 5 years (justifies sensor infrastructure investment)

---

## Core Components (Ground-Up Build)

### 1. CLI Interface (`src/cli/`)
Headless command-line interface for all operations:

```bash
# Initialize system
farmsense init --tier enterprise --fields field_001,field_002

# Start daemon (headless)
farmsense daemon start --jetson-id jetson_001

# Sensor operations
farmsense sensor list --field field_001
farmsense sensor read --id blanket_001

# Virtual grid
farmsense grid generate --field field_001 --resolution 1m

# Compliance (all tiers auditable)
farmsense compliance report --period daily
farmsense compliance export --start-date 2026-06-01 --end-date 2026-06-29 --signed

# VRI control (enterprise only)
farmsense vri trigger --zone zone_001 --duration-min 30

# Cloud operations
farmsense cloud sync
farmsense cloud status
```

### 2. Data Models (`src/models/`)
- **Sensor**: Horizontal blankets, master vertical nails
- **Measurement**: Time-series with forensic hashing
- **Soil Map**: Dynamic variability with recursive Bayesian learning
- **Virtual Grid**: 1-meter or 30-meter resolution (tier-dependent)

### 3. Persistence Layer (`src/persistence/`)
- **TimeSeriesDB**: SQLite-backed local storage
- **Sync Protocol**: Live cloud mirror with immediate failover
- **24-month local retention** + **10+ year cloud archive**

### 4. Computational Engine (`src/engine/`)
- **Bayesian Filter**: Recursive moisture state prediction
- **Regression Kriging**: GPU-accelerated spatial interpolation
- **Soil Learning**: Automatic texture coefficient adjustment

### 5. Forensic Security (`src/forensic/`)
- **SHA-256 hashing** at every measurement point
- **Cryptographic signing** at sensor/well-head
- **Immutable audit trail** for Water Court
- **Chain of custody** verification

### 6. Cloud Infrastructure (`src/cloud/`)
- **Tenant Manager**: Multi-tier subscription handling
- **Archive Engine**: Long-term immutable storage
- **Ingestion Pipeline**: Receives from Jetson mirrors and cloud gateways
- **Compliance Exporter**: State Engineer and Water Court reports

### 7. VRI Integration (`src/vri/`)
- Modbus RTU/TCP valve control
- Zone-based irrigation triggers
- <2 second latency from grid update to valve response

---

## Sensor Architecture

### Horizontal Blanket Sensors (Ground Truth)
- **Length**: 18"
- **Depths**: 12" and 18" (2-depth captures 94% of variability)
- **Coverage**: 1 per 10-14 acres
- **Material**: 3/16" 316 stainless steel
- **Lifespan**: 20+ years

### Master Vertical Nails (Compliance Gate)
**Medium (42" active, 5 depths)**: 18", 24", 30", 36", 42"
- Target: Potatoes, barley, shallow-medium root crops

**Large (60" active, 7 depths)**: 18", 24", 30", 36", 42", 52", 60"
- Target: Alfalfa, deep-rooted forage
- Deep percolation detected at 42"/60" horizons

---

## Failover Architecture (Enterprise)

```
Jetson Nano (Primary)
    │ 15-min processing
    │ Live sync
    ▼
Cloud Mirror (Zo) ←── Immediate takeover on failure
    │
    │ Farmer notification
    ▼
Cold Spare Jetson (on-site, powered off)
    │ Manual swap (<30 min)
    ▼
Sync from cloud → Full restoration
```

**Key Points**:
- Cloud mirror maintains **live state** of all Jetson instances
- **Immediate failover** when Jetson heartbeat timeout detected
- **Zero data loss**: All measurements archived to cloud before acknowledgment
- Cold spare activation documented for compliance

---

## Deployment on Zo

### Main Server (Multi-tenant)
```yaml
# deploy/cloud/zo_deployment.yaml
- 3 replicas for high availability
- PostgreSQL for tenant data
- Redis for caching
- Persistent volumes for 10+ year archive
- Load balancer with SSL termination
```

### Enterprise Jetson Setup
```bash
# On Jetson Nano
pip install -r requirements-jetson.txt
farmsense init --tier enterprise --config /opt/farmsense/
farmsense daemon start --jetson-id jetson_hub_001

# Automatic cloud mirror registration
# Live sync begins immediately
```

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Core data models (sensor, measurement, soil map)
- [x] Persistence layer (SQLite + sync)
- [x] CLI interface (headless)
- [ ] Unit tests for all models

### Phase 2: Engine (Weeks 3-4)
- [x] Bayesian filter implementation
- [x] Regression kriging (CPU fallback, GPU optimized)
- [ ] Sensor data ingestion (LoRa protocol)
- [ ] Virtual grid generation

### Phase 3: Security (Week 5)
- [x] SHA-256 hashing framework
- [x] Cryptographic signing
- [x] Audit trail generation
- [ ] Compliance report exporters

### Phase 4: Cloud (Weeks 6-7)
- [x] Multi-tenant architecture
- [x] Archive engine
- [x] Ingestion pipeline
- [ ] Zo deployment automation

### Phase 5: Integration (Weeks 8-9)
- [ ] VRI controller (Modbus)
- [ ] LoRa gateway interface
- [ ] Satellite data ingestion (STAC)
- [ ] API for CSU research

### Phase 6: Pilot Deployment (Weeks 10-12)
- [ ] 9-field hardware installation
- [ ] System calibration
- [ ] CSU validation
- [ ] **June 29: Water Court Trial**

---

## File Structure

```
FarmSenseOS/
├── src/
│   ├── cli/
│   │   └── main.py                 # Headless CLI interface
│   ├── models/
│   │   ├── sensor.py               # Sensor entity models
│   │   ├── measurement.py          # Time-series data
│   │   └── soil_map.py             # Dynamic soil variability
│   ├── persistence/
│   │   ├── timeseries.py           # Local SQLite storage
│   │   └── sync.py                 # Cloud sync protocol
│   ├── engine/
│   │   ├── bayesian/
│   │   │   └── filter.py           # Recursive Bayesian filter
│   │   └── kriging/
│   │       └── regression_kriging.py  # GPU Kriging
│   ├── forensic/
│   │   └── integrity.py            # SHA-256 + signing
│   ├── cloud/
│   │   ├── tenant_manager.py       # Multi-tier subscriptions
│   │   ├── archive_engine.py       # Long-term storage
│   │   └── ingestion_pipeline.py   # Data reception
│   ├── vri/
│   │   └── controller.py           # Valve control
│   └── farmsense_engine.py         # Main orchestration
├── config/
│   └── pilot_config.yaml           # 9-field pilot configuration
├── deploy/
│   └── cloud/
│       └── zo_deployment.yaml      # Zo Kubernetes manifests
├── tests/                          # Test suite
├── docs/                           # Documentation
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Key Principles

1. **Ground-Up Build**: Everything fresh, no legacy code
2. **CLI-First**: Headless operation, frontends as consumers
3. **Feature Inspiration Only**: Prior concepts inform design, not implementation
4. **Security by Design**: Forensic integrity from first line of code
5. **Cloud-Native on Zo**: Main server and mirrors deployed to Zo infrastructure
6. **Tiered Access**: Free/Paid/Enterprise with clear capability boundaries
7. **Compliance Clarity**: Only Enterprise with local Jetson gets compliance promise

---

## Contact

**Lead Architect**: Jeremy Beebe  
**Organization**: Bxthre3 Inc.  
**Email**: getfarmsense@gmail.com  
**Phone**: 7198508651

---

*Document Version: 1.0*  
*Date: February 2026*  
*Status: Development In Progress*
