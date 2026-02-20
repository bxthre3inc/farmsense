# SilasUI Component Architecture

## Component Hierarchy

```
components/
├── primitives/          # Atomic building blocks (no dependencies)
│   ├── Box.tsx         # Layout container
│   ├── Text.tsx        # Typography
│   ├── Stack.tsx       # Flex layout
│   ├── Label.tsx       # Form label
│   ├── Input.tsx       # Form input
│   ├── Button.tsx      # Action button
│   ├── Spinner.tsx     # Loading indicator
│   ├── IconWrapper.tsx # Icon container
│   └── Divider.tsx     # Separator
│
├── composites/          # Composed from primitives
│   ├── FormField.tsx   # Label + Input + Error
│   ├── FormError.tsx   # Error message
│   ├── CardHeader.tsx  # Card title section
│   ├── CardBody.tsx    # Card content wrapper
│   ├── MetricValue.tsx # Big number display
│   ├── MetricTrend.tsx # Trend indicator
│   ├── Badge.tsx       # Status badge
│   ├── Alert.tsx       # Alert message
│   ├── EmptyState.tsx  # Empty state view
│   └── LoadingOverlay.tsx # Loading state
│
└── [Legacy Components]  # Composed from both
    ├── Card.tsx
    ├── Login.tsx
    └── MetricCard.tsx
```

## Usage Examples

### Using Primitives Directly

```tsx
import { Box, Stack, Text, Button, Input } from './primitives';

<Box border padding="md">
  <Stack gap="md">
    <Text as="h2" size="lg" weight="semibold">
      Title
    </Text>
    <Input
      value={value}
      onChange={setValue}
      placeholder="Enter text"
    />
    <Button variant="primary">Submit</Button>
  </Stack>
</Box>
```

### Using Composites

```tsx
import { FormField, Alert, Badge } from './composites';

<FormField
  id="email"
  label="Email"
  type="email"
  value={email}
  onChange={setEmail}
  error="Invalid email"
/>

<Alert variant="success" title="Success">
  Your changes have been saved.
</Alert>

<Badge variant="success">Active</Badge>
```

### Using Legacy Components (Full Pages)

```tsx
import { Login, Card, MetricCard } from './components';

<Login
  onLogin={handleLogin}
  variant="farmer"
  demoCredentials={[...]}
/>

<Card title="Section" subtitle="Description">
  Content here
</Card>

<MetricCard
  title="Moisture"
  value={32}
  unit="%"
  change={5}
  trend="up"
  icon={<Droplets />}
/>
```

## Component Principles

1. **Primitives are atomic** - No internal dependencies
2. **Composites compose primitives** - No direct styling
3. **Legacy components are deprecated** - Will be refactored to use primitives
4. **All props are explicit** - No magic values
5. **Minimal styling** - Only essential visual hierarchy
