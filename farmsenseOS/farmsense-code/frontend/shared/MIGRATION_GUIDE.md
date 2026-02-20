# FarmSense Shared Component Migration Guide

## Overview

This guide explains how to migrate existing dashboards to use the new shared component library with consistent styling, animations, and optimization features.

---

## Quick Start

### 1. Update Imports

Replace old imports with shared components:

```typescript
// BEFORE (old approach)
import Login from './components/Login';

// AFTER (shared components)
import { 
  Login, 
  Card, 
  Button, 
  MetricCard,
  NetworkStatus,
  CompressionStats,
  useAuth 
} from '../../shared/components';
```

### 2. Update Login Component

```typescript
// BEFORE
<Login onLogin={handleLogin} />

// AFTER
<Login 
  onLogin={(key) => login(key, 'farmer')}
  variant="farmer"  // or 'admin', 'investor', 'regulatory', 'grant', 'research'
  demoCredentials={[
    { label: 'Demo Farmer', key: 'demo-farmer-key' },
  ]}
/>
```

### 3. Update Card Usage

```typescript
// BEFORE
<div className="bg-white p-6 rounded-xl shadow">
  <h2>Title</h2>
  <p>Content</p>
</div>

// AFTER
<Card 
  title="Title" 
  icon={<Icon className="w-5 h-5 text-emerald-400" />}
  glass  // Use glassmorphism style
  glow   // Add glow effect
>
  <p>Content</p>
</Card>
```

### 4. Add Optimization Dashboard

Include the new network and compression status panels:

```typescript
import { NetworkStatus, CompressionStats } from '../../shared/components';

// In your dashboard layout:
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <CompressionStats
    originalBytes={150000000}
    compressedBytes={35714285}
    ratio={4.2}
    deviceCount={15600}
    batteryExtension={250}
  />
  <NetworkStatus />
  <Card title="System Health" glass>
    {/* Your content */}
  </Card>
</div>
```

---

## Dashboard-Specific Configurations

### Admin Dashboard

```typescript
<Login
  variant="admin"
  demoCredentials={[
    { label: 'Admin', key: 'demo-admin-key' },
  ]}
/>
```

### Investor Dashboard

```typescript
<Login
  variant="investor"
  demoCredentials={[
    { label: 'Investor', key: 'demo-investor-key' },
  ]}
/>
```

### Regulatory Dashboard

```typescript
<Login
  variant="regulatory"
  demoCredentials={[
    { label: 'Auditor', key: 'demo-auditor-key' },
  ]}
/>
```

### Grant Portal

```typescript
<Login
  variant="grant"
  demoCredentials={[
    { label: 'Reviewer', key: 'demo-reviewer-key' },
  ]}
/>
```

### Research Portal

```typescript
<Login
  variant="research"
  demoCredentials={[
    { label: 'Researcher', key: 'demo-research-key' },
  ]}
/>
```

---

## Component Reference

### Layout Components

| Component | Props | Description |
|-----------|-------|-------------|
| `Card` | `title`, `icon`, `glass`, `glow`, `loading`, `actions` | Glassmorphism card container |
| `Button` | `variant`, `size`, `loading`, `icon`, `glass` | Styled button with variants |
| `Input` | `label`, `error`, `icon`, `glass` | Form input with validation |
| `Badge` | `variant`, `pulse` | Status badges |

### Data Display Components

| Component | Props | Description |
|-----------|-------|-------------|
| `MetricCard` | `title`, `value`, `unit`, `change`, `icon`, `trend` | KPI metric display |
| `TelemetryCard` | `data`, `showDeviceId` | Sensor reading display |
| `DataTable` | `columns`, `data`, `sortable`, `pagination` | Sortable table |
| `ChartContainer` | `title`, `children` | Chart wrapper |

### Status Components

| Component | Props | Description |
|-----------|-------|-------------|
| `StatusIndicator` | `status`, `label`, `pulse`, `size` | Online/offline indicator |
| `NetworkStatus` | `refreshInterval`, `showDetails` | Network optimization stats |
| `CompressionStats` | `originalBytes`, `compressedBytes`, `ratio` | Compression metrics |
| `Alert` | `variant`, `title`, `dismissible` | Alert notifications |
| `Loading` | `message`, `size`, `fullScreen` | Loading spinner |

### Navigation Components

| Component | Props | Description |
|-----------|-------|-------------|
| `Navigation` | `items`, `activeItem` | Top navigation bar |
| `Sidebar` | `items`, `collapsed` | Sidebar navigation |

### Hooks

| Hook | Returns | Description |
|------|---------|-------------|
| `useAuth` | `{ isAuthenticated, login, logout, apiKey }` | Authentication state |
| `useTelemetry` | `{ data, isLoading, error, refresh }` | Sensor data fetching |
| `useNetworkStatus` | `{ stats, quality, isLoading }` | Network optimization metrics |

---

## Styling Guidelines

### Color Palette

```css
/* Primary Colors */
--primary: #10b981;        /* Emerald 500 */
--primary-glow: rgba(16, 185, 129, 0.4);

/* Background */
--bg-dark: #0b1120;        /* Slate 900 */
--bg-darker: #070b14;      /* Slate 950 */

/* Surface */
--surface-glass: rgba(255, 255, 255, 0.05);
--surface-glass-border: rgba(255, 255, 255, 0.1);

/* Text */
--text-primary: #f8fafc;   /* Slate 50 */
--text-secondary: #94a3b8; /* Slate 400 */
```

### Typography

- **Headings**: Outfit font (600, 800 weights)
- **Body**: Inter font (400, 500, 600, 700 weights)
- **Monospace**: For device IDs and hashes

### Animations

```typescript
// Float animation
<div className="animate-float">

// Pulse glow
<div className="glow-active">

// Loading spinner
<div className="animate-spin">
```

---

## File Structure

```
frontend/
├── shared/
│   ├── components/
│   │   ├── index.ts          # Export all components
│   │   ├── types.ts          # TypeScript types
│   │   ├── Login.tsx         # Unified login
│   │   ├── Card.tsx          # Glassmorphism card
│   │   ├── Button.tsx        # Button variants
│   │   ├── MetricCard.tsx    # KPI display
│   │   ├── TelemetryCard.tsx # Sensor data
│   │   ├── NetworkStatus.tsx # Network stats
│   │   ├── CompressionStats.tsx # Compression metrics
│   │   ├── StatusIndicator.tsx # Status dot
│   │   ├── Badge.tsx         # Status badge
│   │   ├── Input.tsx         # Form input
│   │   ├── Alert.tsx         # Alert notification
│   │   ├── Loading.tsx       # Loading spinner
│   │   ├── EmptyState.tsx    # Empty state
│   │   └── hooks/
│   │       ├── useAuth.ts
│   │       ├── useTelemetry.ts
│   │       └── useNetworkStatus.ts
│   ├── design-system.css     # Global styles
│   └── MIGRATION_GUIDE.md    # This file
│
├── farmer-dashboard/
│   └── src/
│       └── App.tsx           # Migrated example
├── admin-dashboard/
├── investor-dashboard/
├── regulatory-portal/
├── grant-portal/
└── research-portal/
```

---

## Migration Checklist

### Per Dashboard

- [ ] Update `App.tsx` to use shared `Login` component
- [ ] Replace all card containers with shared `Card`
- [ ] Replace buttons with shared `Button`
- [ ] Add `NetworkStatus` panel
- [ ] Add `CompressionStats` panel
- [ ] Replace metric displays with `MetricCard`
- [ ] Add `StatusIndicator` for device status
- [ ] Update navigation to use shared `Navigation`
- [ ] Replace loading states with shared `Loading`
- [ ] Add `EmptyState` for empty data views
- [ ] Test all interactions
- [ ] Verify responsive design

---

## Common Issues

### Import Path Issues

If you get import errors, check the relative path:

```typescript
// From farmer-dashboard/src/App.tsx
import { Login } from '../../shared/components';

// From admin-dashboard/src/App.tsx  
import { Login } from '../../shared/components';
```

### TypeScript Types

Import types when needed:

```typescript
import type { TelemetryData, NetworkStats } from '../../shared/components/types';
```

### Tailwind Classes Not Working

Ensure your `tailwind.config.js` includes the shared components:

```javascript
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    '../shared/components/**/*.{js,ts,jsx,tsx}', // Add this
  ],
}
```

---

## Benefits of Migration

1. **Consistent UX**: All dashboards look and feel the same
2. **Less Code**: Remove duplicate Login components (6 → 1)
3. **Optimization Visibility**: Network and compression stats visible everywhere
4. **Maintainability**: Changes in one place apply everywhere
5. **Performance**: Shared hooks reduce API calls

---

## Next Steps

1. Migrate `admin-dashboard` using this guide
2. Migrate `investor-dashboard`
3. Migrate `regulatory-portal`
4. Migrate `grant-portal`
5. Migrate `research-portal`
6. Archive old duplicate Login components

---

## Support

For questions or issues with migration, refer to:
- `farmer-dashboard/src/App.tsx` - Working example
- `shared/components/README.md` - Component documentation
- `shared/components/types.ts` - Type definitions
