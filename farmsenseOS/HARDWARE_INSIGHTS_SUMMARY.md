# Key Hardware Insights for Software Development

## 1. Total Scale (Subdistrict 1 Pilot)
- **19,466 devices** across 6 hardware types
- **~2.8 million sensor readings per day**
- **~150 GB data volume per day**
- **$5.38 million hardware investment**

## 2. Critical Hardware-Software Interfaces

### Autonomous Reflex (PFA)
- PFA can trigger pump shutdown WITHOUT cloud connectivity
- 2-second response time requirement
- Hardwired relay for fail-safe operation
- **Software must respect and log these autonomous events**

### Legal-Grade Data (VFA + PFA)
- TDR probes provide "Water Court defensible" moisture data
- Vented depth sounder provides legally defensible aquifer data
- Cryptographic signing required at device level
- **Software must maintain immutable audit trail**

### Ultra-Low-Power Mesh (LRZ)
- 15,600 dumb nodes with 12-year battery life
- Transmit-only, no handshakes
- 900MHz long-range coded PHY
- **Software must handle burst ingestion from 15k+ devices**

## 3. Communication Hierarchy
```
LRZ (15,600) ──900MHz──┐
VFA (1,280) ───5GHz────┼──→ DHU (25) ──LTE/Starlink──→ RSS (1) ──Cloud
PFA (1,280) ───5GHz────┘
PMT (1,280) ──BLE→VFA
```

## 4. Edge Computing Requirements
- DHU performs local Kriging and data decimation
- 7-day autonomy (solar + battery)
- Black box recording (30-day local buffer)
- **Software must support edge compute + cloud sync architecture**

## 5. Key API Endpoints Needed

### High-Priority
- `POST /api/v1/ingest/lrz-bulk` (15k devices)
- `POST /api/v1/wells/{id}/emergency-stop` (autonomous reflex)
- `POST /api/v1/sensors/vfa/telemetry` (legal-grade data)

### Analytics
- `GET /api/v1/fields/{id}/moisture-map` (Kriging)
- `GET /api/v1/wells/{id}/depth-history` (Water Court)
- `GET /api/v1/pivots/{id}/coverage-map` (VRI)

## 6. Data Integrity Requirements
- SHA-256 signing at device
- Certificate chain verification
- Zero-loss redundancy (RAID-10)
- Immutable ledger for compliance

## 7. Real-Time Requirements
- PFA alarm: <2 seconds (WebSocket)
- VFA during irrigation: 1-minute intervals
- PMT GNSS/IMU: 10Hz streaming
- LRZ bulk: 15-minute batch

## 8. Notable Hardware Costs
- PMT ultrasonic flow sensor: **$648/unit** (high-precision)
- RSS Threadripper compute: **$22,000** (regional cortex)
- PFA depth sounder: **$185/unit** (legal-grade aquifer monitoring)

## 9. Power Constraints
- LRZ: 19Ah LiSOCl2 (12-year life, no solar)
- VFA: 40Ah LiFePO4 + solar
- PMT: 10W solar + LiFePO4
- DHU: 200W solar + heated battery (7-day autonomy)
- RSS: 1.2kW solar + 800Ah + 5kW generator

## 10. Environmental Challenges
- -40°F operation (Viton seals, heated batteries)
- High-altitude UV (UV-HDPE housing)
- Lightning strikes (GDT arrestors on DHU)
- 120-day winter dormancy (hibernation packs)

---

## Action Items for Software Team

1. **Implement high-throughput ingestion** for 15k LRZ devices
2. **Add cryptographic signing** for legal-grade data
3. **Build autonomous reflex event handling** (PFA emergency stops)
4. **Create Kriging engine** for 1-meter moisture maps
5. **Design air-gapped mode** for RSS (continue during outages)
6. **Implement VRI prescription system** for PMT control
7. **Add predictive maintenance** (CT clamp signature analysis)
8. **Build Water Court reporting** (compliance-grade exports)

---

*These insights bridge hardware procurement and software architecture decisions.*
