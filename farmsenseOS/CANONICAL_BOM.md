# FarmSense BOM Summary (Canonical)

## Source Files
- `hardware BOM&specs/LRZ Unit Procurement & Sub-BOM.pdf`
- `hardware BOM&specs/VFA Unit Procurement & Sub-BOM.pdf`
- `hardware BOM&specs/PFA Unit Procurement & Sub-BOM.pdf`
- `hardware BOM&specs/PMT Unit Procurement & Sub-BOM.pdf`
- `hardware BOM&specs/DHU Unit Procurement & Sub-BOM.pdf`
- `hardware BOM&specs/RSS Unit Procurement & Sub-BOM.pdf`

## Hardware Investment Summary

| Device | Quantity | Unit Cost | Hardware Subtotal | Total Project Cost |
|--------|----------|-----------|-------------------|-------------------|
| **LRZ** (Lateral Root-Zone Scout) | 15,600 | $85.00 | $1,326,000 | $1,540,500 |
| **VFA** (Vertical Field Anchor) | 1,280 | $455.00 | $582,400 | $672,000 |
| **PFA** (Pressure & Flow Anchor) | 1,280 | $750.00 | $960,000 | $1,248,000 |
| **PMT** (Pivot Tracking Module) | 1,280 | $1,100.00 | $1,408,000 | $1,565,440 |
| **DHU** (District Hub) | 25 | $4,565.00 | $114,125 | $145,000 |
| **RSS** (Regional Superstation) | 1 | — | — | $212,000 |
| **TOTAL** | **19,466** | — | **$4,390,525** | **$5,382,940** |

## Device Roles

- **LRZ**: High-density soil moisture scouts (transmit-only, 12-year battery)
- **VFA**: Ground truth nodes with TDR probes (legal-grade moisture data)
- **PFA**: Well/pump sentries with autonomous shutdown capability
- **PMT**: Pivot tracking with ultrasonic flow auditing
- **DHU**: Regional aggregators with edge computing
- **RSS**: Regional cortex for high-res Kriging

## Key Technical Details

- **LRZ**: Nordic nRF52840, capacitive traces, Viton seals, -40°F rated
- **VFA**: NXP i.MX RT1060, TDR probes (ENIG-finish), legal-grade for Water Court
- **PFA**: Dwyer PBLTX depth sounder (300ft vented), 400A CT clamps, autonomous reflex
- **PMT**: u-blox ZED-F9P RTK GNSS, Badger Meter ultrasonic ($648/unit!)
- **DHU**: OnLogic CL210, 128GB pSLC SSD, 7-day autonomy, lightning arrestors
- **RSS**: AMD Threadripper PRO 64-core, 50TB NVMe RAID-10, Starlink + Fiber

## Coverage

- **Total Devices**: 19,466
- **Coverage**: 117,000 acres (Subdistrict 1 pilot)
- **Daily Readings**: ~2.8 million sensor readings
- **Daily Data**: ~150 GB

---
*This file is auto-generated from the canonical BOM PDFs. Do not edit manually.*