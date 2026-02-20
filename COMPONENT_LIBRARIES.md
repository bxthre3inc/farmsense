# FarmSense Component Libraries Summary

## Two Separate Design Systems

### FarmSense UI (Glassmorphism)
- **Purpose:** Marketing, investor portal, grant portal, admin dashboards
- **Style:** Backdrop blur, semi-transparent, rich visual hierarchy
- **Components:** Hero, Section, Card, Button, Badge, MetricCard, PricingTier, FeatureList, StatGrid, CTA, Header, Footer
- **Location:** `/frontend/shared/components/farmsense-ui/`

### SilasUI (Minimalist Field Mode)
- **Purpose:** Field-mode farmer dashboard - simple water decisions
- **Style:** Clean, large text, single-button actions, outdoor-visible
- **Components:** WaterDecision, SimpleMetric, StatusBadge, FieldMode
- **Location:** `/frontend/shared/components/silas-ui/`

## Key Principle
**SilasUI is ONLY for SilasUI mode** - the simple "water or not water" field interface.
**Everything else uses FarmSense UI** - marketing, portals, dashboards.

## Stats Convention
All projected stats must show "PILOT TARGET" badge using `isTarget: true` prop.

## Next Steps
1. Refactor marketing page to use FarmSense UI components
2. Create SilasUI mode in farmer dashboard
3. Update all portals to use FarmSense UI
