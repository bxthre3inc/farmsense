# FarmSense Component Libraries

Two distinct component libraries based on ACTUAL design patterns from the FarmSense marketing page.

## FarmSense UI

**Purpose:** Marketing pages, investor portal, grant portal, admin dashboards
**Design:** Clean, solid colors, minimal borders, no glassmorphism

### Components:
- **Hero** - Main landing section with stats
- **Section** - Content wrapper with title/subtitle
- **Card** - Basic card with title/subtitle/content
- **MetricCard** - Stat display with TARGET support
- **PricingTier** - Subscription tier display
- **HardwareCard** - Hardware spec card
- **Button** - Primary/secondary/ghost buttons
- **Badge** - Status badges
- **Header** - Navigation header
- **Footer** - Site footer

### Design System:
- Backgrounds: `bg-white`, `bg-slate-50`
- Borders: `border-slate-200`
- Text: `text-slate-900`, `text-slate-600`
- Accent: `emerald-600`
- No backdrop-blur, no semi-transparent backgrounds

## SilasUI

**Purpose:** Farmer field dashboard
**Design:** Minimal, decision-focused, single-action interface

### Components:
- **WaterDecision** - Main decision card showing WATER/WAIT/OFF

### Design System:
- Large, clear action display
- Essential metrics only (moisture, temp, battery, signal)
- Single-button actions
- Clean white background with colored decision box

## Usage Example:

```tsx
// Marketing page
import { Hero, Section, Card, PricingTier } from './farmsense-ui';

<Hero
  badge={{ icon: Shield, text: "SLV 2026 Compliant" }}
  title="Precision Agriculture"
  highlight="at Every Scale"
  subtitle="From 50m to 1m resolution"
  stats={[
    { value: "19,466", label: "Devices" },
    { value: "2.8M", label: "Daily Readings" }
  ]}
/>

// Farmer dashboard
import { WaterDecision } from './silas-ui';

<WaterDecision
  fieldId="field_01"
  moisture={0.32}
  temperature={24.5}
  battery={85}
  signal={92}
  decision="WATER"
  reason="Moisture below threshold"
  lastUpdate="2 min ago"
/>
```

## All stats should show "(TARGET)" for pilot deployment:
```tsx
<MetricCard value="19,466" label="Devices" isTarget />
```
