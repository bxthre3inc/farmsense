# FarmSense Tier Structure - Final Specification

## Tier Overview

| Tier | Price | Grid Resolution | Key Differentiator |
|------|-------|-----------------|-------------------|
| **Free** | $0 | 50m | Read-only monitoring |
| **Basic** | $49/mo | 20m | Irrigation recommendations |
| **Pro** | $199/mo | 10m | Full automation (actuation) |
| **Enterprise** | Custom | 1m | Compliance guarantee |

## Website Links

- **Marketing Home**: `/`
- **Investor Portal**: `/investor` (not #investor)
- **Farmer Dashboard**: `/farmers`
- **Documentation**: `/docs`
- **Command Center**: Hidden from navigation, accessible via direct URL only

## Detailed Feature Matrix

### Free Tier
**Grid Access:**
- ✅ 50m resolution data only

**Actuation:**
- ❌ No pump/valve control
- ❌ No VRI control

**Recommendations:**
- ❌ No irrigation recommendations
- ✅ Manual decision making from 50m data

**Compliance:**
- ❌ No compliance guarantee
- ✅ Manual paper compliance reports
- ❌ No in-app reporting

**Hardware:**
- ❌ No sensor/hardware connectivity

**Reporting:**
- ✅ Monthly reports
- ❌ Weekly reports
- ❌ Daily reports

---

### Basic Tier
**Grid Access:**
- ✅ 50m resolution
- ✅ 20m resolution

**Actuation:**
- ❌ No pump/valve control
- ❌ No VRI control

**Recommendations:**
- ✅ Irrigation recommendations included
- ✅ Data-driven decisions

**Compliance:**
- ❌ No compliance guarantee
- ✅ In-app compliance reports
- ❌ Manual paper reports (not needed)

**Hardware:**
- ❌ No sensor/hardware connectivity

**Reporting:**
- ✅ Monthly reports
- ❌ Weekly reports
- ❌ Daily reports

---

### Pro Tier
**Grid Access:**
- ✅ 50m resolution
- ✅ 20m resolution
- ✅ 10m resolution

**Actuation:**
- ✅ Pump/valve control
- ✅ VRI (Variable Rate Irrigation) control

**Recommendations:**
- ✅ Irrigation recommendations

**Compliance:**
- ❌ No compliance guarantee
- ✅ In-app compliance reports

**Hardware:**
- ✅ Connect any sensors/hardware

**Reporting:**
- ❌ Monthly reports
- ✅ Weekly reports
- ❌ Daily reports

---

### Enterprise Tier
**Grid Access:**
- ✅ 50m resolution
- ✅ 20m resolution
- ✅ 10m resolution
- ✅ 1m research-grade grid

**Actuation:**
- ✅ Pump/valve control with compliance guarantee
- ✅ VRI control with compliance guarantee

**Recommendations:**
- ✅ Irrigation recommendations

**Compliance:**
- ✅ SLV 2026 compliance guarantee
- ✅ In-app compliance reports
- ❌ Manual paper reports (not needed)

**Hardware:**
- ✅ Connect any sensors/hardware

**Reporting:**
- ❌ Monthly reports
- ❌ Weekly reports
- ✅ Daily reports

---

## API Endpoint Access

| Endpoint | Tier Required |
|----------|---------------|
| `GET /grid/50m` | Free+ |
| `GET /grid/20m` | Basic+ |
| `GET /grid/10m` | Pro+ |
| `GET /grid/1m` | Enterprise |
| `GET /irrigation-recommendation` | Basic+ |
| `POST /actuation/pumps/{id}/start` | Pro+ |
| `POST /actuation/pumps/{id}/stop` | Pro+ |
| `POST /actuation/vri/{id}/set-zones` | Pro+ |
| `POST /compliance/reports/generate` | Basic+ |

## Key Terms

- **Actuation**: Remote control of pumps, valves, and irrigation systems
- **VRI**: Variable Rate Irrigation - zone-based water application
- **SLV 2026**: San Luis Valley 2026 water regulations
- **Compliance Guarantee**: Enterprise tier includes legally defensible data and audit trail for water court proceedings
- **1m Grid**: Research-grade 1-meter resolution soil moisture mapping (19M+ data points per subdistrict)

## Use Case Recommendations

**Free**: Individual farmers exploring precision ag, small operations (< 100 acres)

**Basic**: Growing farms with irrigation planning needs, medium operations (100-500 acres)

**Pro**: Large-scale precision agriculture operations, VRI-enabled pivots, automated irrigation (500-2000 acres)

**Enterprise**: Water court proceedings, research institutions, regulatory compliance requirements, largest operations (2000+ acres)
