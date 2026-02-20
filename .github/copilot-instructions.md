# FarmSense Copilot Instructions

## Project Overview
FarmSense is a comprehensive agricultural operating system with **11 domain-specific intelligence engines** (Planning, Field Prep, Planting, Irrigation, Nutrient, Pest & Weed, Harvest, Processing, Packaging, Warehousing, Logistics), **multi-vendor equipment control** (Lindsay, Valley, Reinke, Netafim, Jain + generic protocols), and a deterministic decision framework. The architecture combines a React frontend, Node.js/tRPC backend, PostgreSQL database, and Python subprocess engines.

## Architecture Foundation

### Core Tech Stack
- **Frontend**: React 19 + TypeScript + Tailwind CSS 4 + Vite
- **Backend**: Node.js + Express + tRPC 11 + PostgreSQL + Drizzle ORM
- **Decision Engine**: Python 3.8+ deterministic logic (Zero-Hour Engine with 18 IP claims)
- **IPC**: Node subprocess ↔ Python via JSON over stdin/stdout

**Recent Major Features** (January 2026):
- **Spatial Grid Analytics**: 10m × 10m grid with real-time metrics, virtual sensors via IDW interpolation
- **Multi-Vendor Equipment Control**: Lindsay, Valley, Reinke, Netafim, Jain adapters with unified API
- **Zero-Hour Engine**: Deterministic spatiotemporal arbitrage optimization with full audit trail

### Critical Architectural Patterns

#### 1. **Unified Recommendation Model** (Non-Negotiable)
All 11 domain engines use a single enum for base recommendations:
```
NOW → SOON → LATER → WAIT → MONITOR
```
Recommendation Timeframes:
- **NOW** - Take action in 0-2 hours
- **SOON** - Take action in 3-6 hours
- **LATER** - Take action in 7-12 hours
- **WAIT** - Take action in 13-48 hours
- **MONITOR** - Take action in 49+ hours

Every recommendation includes:
- **Context Flags** (WEATHER_DELAY, LABOR_CONSTRAINT, EQUIPMENT_CONSTRAINT, CAPACITY_CONSTRAINT, MATERIALS_CONSTRAINT)
- **Severity Overlays** (EMERGENCY = requires human confirmation)
- **Full Explainability** (inputs_used, thresholds_crossed, thresholds_approaching, trends_considered, crop_stage)
- **KPIs** (domain-specific performance metrics)
- **Audit Trail** (audit_log_id for complete reconstruction)

**Key File**: [shared/types.ts](file:///workspaces/farmsense/shared/types.ts) — defines BaseRecommendation, ContextFlag, SeverityOverlay, DomainType enums.

#### 2. **Domain Engine Registry Pattern**
Each domain inherits from [BaseEngine](file:///workspaces/farmsense/server/domains/BaseEngine.ts) (abstract class with shared hardening/trending logic). The registry ([server/domains/index.ts](file:///workspaces/farmsense/server/domains/index.ts)) instantiates all 11 engines and provides lookup via `domainRegistry.getEngine(domainType)`.

**Example Implementation** ([server/domains/IrrigationEngine.ts](file:///workspaces/farmsense/server/domains/IrrigationEngine.ts)):
```typescript
export class IrrigationEngine extends BaseEngine {
  constructor() {
    super(DomainType.IRRIGATION);
  }

  async generateRecommendation(input: DomainEngineInput): Promise<Recommendation> {
    const hardenedMetrics = this.hardenInputs(input);
    
    // Zero-Hour Engine integration
    const zeroHourInput: ZeroHourEngineInput = {
      fieldId: input.fieldId,
      bioticValue: this.estimateBioticValue(hardenedMetrics, input),
      cwsi: this.calculateCWSI(hardenedMetrics),
      // ... other inputs
    };
    
    const { decision: zeroHourDecision, auditRecord } = 
      await this.zeroHourOrchestrator.executeWithAudit(zeroHourInput);
    
    // Convert to unified recommendation format
    let base: BaseRecommendation = BaseRecommendation.MONITOR;
    switch (zeroHourDecision.decision) {
      case ZeroHourDecision.START_AT_TIME:
        base = BaseRecommendation.NOW;
        break;
      case ZeroHourDecision.DEFER:
        base = BaseRecommendation.LATER;
        break;
      // ... other cases
    }
    
    return this.createRecommendation(input.fieldId, {
      base,
      contextFlags: [],
      severityOverlays: [],
      explainability: {
        inputsUsed: Object.keys(hardenedMetrics),
        thresholdsCrossed: [`Arbitrage ratio: ${zeroHourDecision.arbitrage_ratio}`],
        // ... other fields
      },
      kpis: {
        arbitrage_ratio: zeroHourDecision.arbitrage_ratio,
        water_efficiency: zeroHourDecision.delivery_efficiency * 100
      }
    });
  }
}
```

**When adding features**: Follow the same structure—extend BaseEngine, implement `generateRecommendation()`, register in domainRegistry.

#### 3. **Python-TypeScript Bridge (Zero-Hour Pattern)**
The [ZeroHourOrchestrator](file:///workspaces/farmsense/server/ZeroHourOrchestrator.ts) spawns Python subprocesses for deterministic compute:
- TypeScript sends JSON via stdin
- Python writes JSON to stdout
- Errors are logged immutably to `zero_hour_decisions` table
- Full reconstruction possible (re-run with same inputs, same outputs)

**For Python logic changes**: Edit [python-engine/zero_hour_engine.py](file:///workspaces/farmsense/python-engine/zero_hour_engine.py) or domain-specific engines like [potato_logic.py](file:///workspaces/farmsense/python-engine/potato_logic.py). Test with [test_zero_hour_engine.py](file:///workspaces/farmsense/python-engine/test_zero_hour_engine.py).

#### 4. **Supporting Services Architecture**
Beyond domain engines, critical services handle cross-cutting concerns:
- **HardeningService** ([server/services/HardeningService.ts](file:///workspaces/farmsense/server/services/HardeningService.ts)): Validates + weights metrics by confidence/resolution (spatial & temporal). Used by all engines via `this.hardenInputs(input)` in BaseEngine.
- **PredictiveService** ([server/services/PredictiveService.ts](file:///workspaces/farmsense/server/services/PredictiveService.ts)): Generates probabilistic scenarios (e.g., "rain in 3 hours" → reduced irrigation need). Outputs confidence-scored outcomes.
- **SafetyService** ([server/services/SafetyService.ts](file:///workspaces/farmsense/server/services/SafetyService.ts)): Interlocks (e.g., prevent irrigation if frost predicted), resolution metadata tracking.
- **SpatialGridService** ([server/services/SpatialGridService.ts](file:///workspaces/farmsense/server/services/SpatialGridService.ts)): Geospatial grid aggregation for multi-field operations & MapView queries.
- **SensorNetworkService** ([server/services/SensorNetworkService.ts](file:///workspaces/farmsense/server/services/SensorNetworkService.ts)): Manages real IoT sensors (24+ per field) and virtual sensors (1,200+ interpolated points via inverse distance weighting).
- **EquipmentHealthService** ([server/services/EquipmentHealthService.ts](file:///workspaces/farmsense/server/services/EquipmentHealthService.ts)): Monitors equipment health metrics (vibration, temperature, power consumption).
- **AnalyticsService** ([server/services/AnalyticsService.ts](file:///workspaces/farmsense/server/services/AnalyticsService.ts)): Calculates field analytics, ROI breakdowns, and benchmark comparisons.
- **MobileFieldOptimizationService** ([server/services/MobileFieldOptimizationService.ts](file:///workspaces/farmsense/server/services/MobileFieldOptimizationService.ts)): Optimizes field operations for mobile interfaces.

**When to use**: Always call `hardenInputs()` first in `generateRecommendation()`, then feed hardened metrics to domain-specific logic. Use SensorNetworkService for field sensor initialization and virtual sensor interpolation.

#### 5. **Dual-Layer Sensor Network Architecture**
FarmSense implements a comprehensive sensor network for spatial data collection:

**Real Sensor Layer (24+ per field):**
- Physical IoT devices distributed across field (e.g., Decagon GS3, Sentek sensors)
- Measure soil moisture, temperature, nitrogen at grid points
- Store calibration coefficients for unit conversion
- Track status, signal strength, battery level
- Located in [realSensors table](file:///workspaces/farmsense/server/db/schema.ts)

**Virtual Sensor Layer (1,200+ per field for 400m × 300m at 10m resolution):**
- Computed values at every 10m × 10m grid point via **Inverse Distance Weighting (IDW)**
- Formula: V(x,y) = Σ(w_i × v_i) / Σ(w_i), where w_i = 1 / d_i²
- Uses K=3 nearest real sensors (configurable via `interpolationRadius`)
- Confidence score reflects distance to nearest sensors
- Interpolated flag and data_source='interpolated' in spatialGridMetrics

**Integration Flow:**
1. Real sensor reading recorded → `sensorNetworkService.recordSensorReading()`
2. Grid config updated with sensor positions
3. Virtual sensors auto-populate via `spatialGridService.populateVirtualSensorValues()`
4. MapView queries both real and virtual for complete coverage
5. Confidence metadata guides decision engines on data quality

**Usage in Code:**
```typescript
// Initialize field with 24 real sensors + 1,200 virtual grid points
await spatialGridService.initializeGridConfig(fieldId, 400, 300, 10, 24);

// Record real sensor data
await sensorNetworkService.recordSensorReading({
  sensorId: 'FIELD-abc-SENSOR-01',
  metricType: 'soil_moisture',
  value: 22.5,
  confidence: 0.95
});

// Get interpolated values at any grid point
const interpolated = await sensorNetworkService.getInterpolatedMetrics(
  fieldId, gridX, gridY, ['soil_moisture', 'soil_temperature']
);
```

See [SENSOR_NETWORK_ARCHITECTURE.md](file:///workspaces/farmsense/SENSOR_NETWORK_ARCHITECTURE.md) for detailed spatial math and configuration.

#### 6. **Multi-Vendor Equipment Control Architecture**
FarmSense provides vendor-neutral control over irrigation equipment via adapter pattern:

**Supported Vendors:**
- **Center Pivot/Linear**: Lindsay Zimmatic (FieldNET), Valley Connect, Reinke RemoteCommand
- **Drip/Micro**: Netafim AgSmart, Jain MyWeather
- **Generic**: HTTP/REST, Modbus TCP, MQTT

**Key Components:**
- **EquipmentControlService** ([server/equipment/EquipmentControlService.ts](file:///workspaces/farmsense/server/equipment/EquipmentControlService.ts)): Unified command execution across vendors
- **BaseEquipmentAdapter** ([server/equipment/adapters/BaseEquipmentAdapter.ts](file:///workspaces/farmsense/server/equipment/adapters/BaseEquipmentAdapter.ts)): Abstract adapter interface
- **Vendor Adapters**: Protocol-specific implementations (e.g., [LindsayZimmaticAdapter.ts](file:///workspaces/farmsense/server/equipment/adapters/LindsayZimmaticAdapter.ts))
- **Equipment Registry** ([server/equipment/EquipmentRegistry.ts](file:///workspaces/farmsense/server/equipment/EquipmentRegistry.ts)): Runtime equipment discovery and management

**Command Interface:**
```typescript
enum ControlCommand {
  START, STOP, ADJUST_SPEED, ADJUST_SECTOR, SET_DURATION
}
```

**Usage Pattern:**
```typescript
// Register equipment
await equipmentControlService.registerEquipment({
  id: 'pivot-1',
  vendor: EquipmentVendor.LINDSAY_ZIMMATIC,
  controlProtocol: 'HTTP',
  networkConfig: { hostname: 'api.fieldnet.com' }
}, { apiKey: process.env.FIELDNET_API_KEY });

// Execute command
const response = await equipmentControlService.executeCommand(
  'pivot-1', ControlCommand.START, undefined, 120
);
```

**Example Adapter Implementation** ([server/equipment/adapters/LindsayZimmaticAdapter.ts](file:///workspaces/farmsense/server/equipment/adapters/LindsayZimmaticAdapter.ts)):
```typescript
export class LindsayZimmaticAdapter extends BaseEquipmentAdapter {
  async executeCommand(context: CommandContext): Promise<ControlResponse> {
    if (!this.isAuthenticated) {
      await this.authenticate();
    }

    if (context.executionMode.isDryRun) {
      return this.formatResponse(true, `[DRY RUN] ${context.command}`, {
        dryRun: true,
        command: context.command,
        targetValue: context.targetValue
      });
    }

    try {
      const deviceId = this.deviceId || this.equipment.id;

      switch (context.command) {
        case ControlCommand.START:
          return await this.startPivot(deviceId);
        case ControlCommand.STOP:
          return await this.stopPivot(deviceId);
        case ControlCommand.ADJUST_SPEED:
          return await this.adjustSpeed(deviceId, context.targetValue as number);
        // ... other commands
        default:
          throw new Error(`Unsupported command: ${context.command}`);
      }
    } catch (error) {
      const message = (error as Error).message;
      this.updateStatusError(message);
      return this.formatResponse(false, message);
    }
  }

  private async startPivot(deviceId: string): Promise<ControlResponse> {
    const response = await this.apiClient!.post<FieldNETResponse<{ jobId: string }>>(
      `/devices/${deviceId}/commands/start`,
      {}
    );

    if (response.data.success) {
      this.updateStatusOnline();
      return this.formatResponse(true, 'Pivot started successfully', {
        jobId: response.data.data?.jobId
      });
    }
    // ... error handling
  }
}
```

**Safety Features:**
- Global emergency stop across all vendors
- Connection validation before critical operations
- Audit logging of all commands
- Equipment health monitoring via EquipmentHealthService

**Key File**: [server/equipment/index.ts](file:///workspaces/farmsense/server/equipment/index.ts) — exports unified equipment control interface.

#### 7. **Database Schema Approach**
- **Raw data**: `raw_metrics` (unprocessed sensor/satellite/other input, full lineage)
- **Processed**: `normalized_metrics` (standardized, confidence-scored, resolution-tracked, virtual sensors)
- **Decisions**: Domain-specific logs (irrigation_recommendations, zero_hour_decisions, etc.)
- **Audit**: `audit_logs` (immutable, reconstruction-enabled via audit_log_id)
- **Sensors**: `real_sensors` (physical IoT devices), `spatial_grid_metrics` (grid point values including virtual sensors)

Use [Drizzle ORM](file:///workspaces/farmsense/server/db/schema.ts) with migrations: `npm run db:generate` after schema edits, then `npm run db:push`.

## Development Workflow

### Environment Requirements
- **Node.js**: >=20.0.0 (check with `node --version`)
- **Python**: 3.8+ (for Zero-Hour Engine subprocess execution)
- **PostgreSQL**: Running and accessible (configure via `.env` DATABASE_URL)

### Quick Start
```bash
npm install                           # Install dependencies
npm run dev                           # Runs server + client concurrently
npm run dev:server                    # Node.js hot-reload with tsx watch
npm run dev:client                    # Vite dev server on port 5173
npm run db:push                       # Apply pending migrations
npm run test                          # Vitest (unit tests)
npm run build                         # TypeScript + Vite
```

**Development Environment**: This workspace runs in a dev container with Ubuntu 24.04.3 LTS, including Node.js, Python, PostgreSQL, and all required tools. Use `"$BROWSER" <url>` to open web pages in the host browser.

### Testing Patterns
- **Domain logic**: Use [decisionEngine.test.ts](file:///workspaces/farmsense/server/decisionEngine.test.ts) as template (mock fields, crops, metrics)
- **Python engines**: Run `python python-engine/test_zero_hour_engine.py` — validates all 18 IP claims + determinism
- **E2E**: Use tRPC client in frontend tests via `useQuery(trpc.domains.getRecommendation)`
- **Equipment adapters**: Mock API responses, test dry-run mode, validate error handling

**Example Test Pattern** ([server/decisionEngine.test.ts](file:///workspaces/farmsense/server/decisionEngine.test.ts)):
```typescript
describe('IrrigationEngine', () => {
  it('should generate NOW recommendation when soil moisture below threshold', async () => {
    const input: DomainEngineInput = {
      fieldId: 'test-field',
      currentMetrics: {
        soil_moisture: { value: 15, unit: '%', timestamp: new Date(), confidenceScore: 0.9, metricType: 'soil_moisture' },
        // ... other metrics
      },
      soilData: { fieldCapacityPercent: 30, wiltingPointPercent: 12 }
    };

    const engine = new IrrigationEngine();
    const recommendation = await engine.generateRecommendation(input);

    expect(recommendation.base).toBe(BaseRecommendation.NOW);
    expect(recommendation.explainability.thresholdsCrossed).toContain('SM < 15%');
  });
});
```

### Code Changes: Expected Patterns

#### Adding a Domain Engine Feature
1. Extend [BaseEngine](file:///workspaces/farmsense/server/domains/BaseEngine.ts) — reuse `hardenInputs()`, `calculateTrend()`, `createRecommendation()`
2. Implement `generateRecommendation(input: DomainEngineInput)` — must return Promise<Recommendation>
3. Register in [domainRegistry](file:///workspaces/farmsense/server/domains/index.ts)
4. Add tRPC procedure in [api/router.ts](file:///workspaces/farmsense/server/api/router.ts) if new endpoint needed
5. Test with mock metrics from decisionEngine.test.ts pattern

#### Modifying Decision Logic
- **Threshold-based**: Edit domain engine (IrrigationEngine.ts, NutrientEngine.ts, etc.) — no external dependencies
- **Python deterministic compute**: Edit python-engine files (zero_hour_engine.py, potato_logic.py)
  - Subprocess spawned in [ZeroHourOrchestrator](file:///workspaces/farmsense/server/ZeroHourOrchestrator.ts) or [pythonEngineWrapper.ts](file:///workspaces/farmsense/server/pythonEngineWrapper.ts)
  - JSON serialization handles type conversion—validate with test suite

#### Database Changes
1. Edit [server/db/schema.ts](file:///workspaces/farmsense/server/db/schema.ts) (use Drizzle `pgTable()`)
2. Run `npm run db:generate` (creates migration in drizzle/migrations/)
3. Review migration file, then `npm run db:push` to apply
4. Query with Drizzle ORM in service/API layer: `db.select().from(tableName).where(eq(field, value))`

**Example Schema Addition** ([server/db/schema.ts](file:///workspaces/farmsense/server/db/schema.ts)):
```typescript
// Spatial Grid Metrics (10m x 10m grid for field-level analytics)
export const spatialGridMetrics = pgTable('spatial_grid_metrics', {
  id: uuid('id').primaryKey().defaultRandom(),
  fieldId: uuid('field_id').references(() => fields.id).notNull(),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  
  // Grid coordinates (10m x 10m resolution)
  gridX: integer('grid_x').notNull(),
  gridY: integer('grid_y').notNull(),
  
  // Soil metrics
  soilMoisture: decimal('soil_moisture', { precision: 5, scale: 2 }), // %
  soilTemperature: decimal('soil_temperature', { precision: 5, scale: 2 }), // °C
  // ... other metrics
  
  // Status classification
  moistureStatus: varchar('moisture_status', { length: 20 }), // 'optimal', 'dry', 'wet'
  healthStatus: varchar('health_status', { length: 20 }), // 'healthy', 'stressed', 'critical'
  
  // Recommendations (generated from metrics)
  recommendation: varchar('recommendation', { length: 50 }), // NOW, SOON, LATER, WAIT, MONITOR
  actionNeeded: text('action_needed'), // Description of recommended action
  
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow()
});
```

## Critical Conventions

### Environment Variables & Security
- **Never hardcode credentials**: All API keys, database URLs, and secrets must use `process.env.*`
- **.env file**: Protected via `.gitignore`, never committed
- **Centralized config**: Use [server/config/environment.ts](file:///workspaces/farmsense/server/config/environment.ts) for all environment variables
- **Production validation**: App fails fast if required credentials missing
- **Audit logging**: All equipment commands and decisions logged immutably

### Recommendation Generation
Every domain engine must include:
```typescript
// In generateRecommendation():
const recommendation = {
  domain: this.domain,
  base: BaseRecommendation.NOW,  // Always use enum
  contextFlags: [ContextFlag.WEATHER_DELAY],
  severityOverlays: [],  // Only EMERGENCY if human confirmation needed
  explainability: {
    inputsUsed: ["soil_moisture", "evapotranspiration"],
    thresholds_crossed: ["SM < 15%"],
    trends_considered: ["trending up"],
    crop_stage: "V6"
  },
  kpis: { water_efficiency: 0.92, stress_avoidance: 0.88 },
  audit_log_id: uuidv4()  // Immutable tracking
};
```

### Emergency Overrides
If `EMERGENCY` severity → `requires_human_confirmation = true`. Frontend must surface for user sign-off before actuation.

### Resolution Metadata
All metrics tracked with:
- Source confidence (0.0–1.0)
- Temporal resolution (raw vs. hourly aggregation)
- Spatial resolution (point sensor vs. spatial interpolation)
- Data quality flags (missing, outlier, interpolated)

Used by HardeningService to weight inputs in decision logic.

## File Organization Primer

| Path | Purpose |
|------|---------|
| `client/src/pages/` | Dashboard, MapView, Robotics, Settings (main UI) |
| `client/src/components/` | Reusable (IdleModeOverlay, RecommendationCard) |
| `server/domains/` | 11 domain engines + BaseEngine abstract class |
| `server/api/` | tRPC router + procedures |
| `server/services/` | HardeningService (data validation), PredictiveService, SafetyService, SpatialGridService, EquipmentHealthService |
| `server/equipment/` | EquipmentControlService, adapters for Lindsay/Valley/Reinke/Netafim/Jain, EquipmentRegistry |
| `python-engine/` | Deterministic compute (engine.py, zero_hour_engine.py, potato_logic.py) |
| `shared/types.ts` | Single source of truth for recommendation enums |

## When Adding Features: Questions to Answer

1. **Is this a new domain?** → Create new file in `server/domains/`, extend BaseEngine, register.
2. **Is this domain-specific?** → Add logic to existing domain engine file.
3. **Does this need Python compute?** → Add to python-engine/, spawn in orchestrator, log audit trail.
4. **Does this require new metrics?** → Add to schema.ts, generate migration, wire into data ingestion.
5. **Does this require human sign-off?** → Use `EMERGENCY` severity overlay + `requires_human_confirmation = true`.
6. **Does this involve equipment control?** → Extend BaseEquipmentAdapter, implement in `server/equipment/adapters/`, register in EquipmentRegistry.
7. **Does this need new tRPC procedures?** → Add to `server/api/router.ts`, follow existing patterns.

## Debugging Tips

- **Determinism check**: Re-run same input → expect identical JSON output (audit trail stored in DB)
- **Python errors**: Check stderr from subprocess in `ZeroHourOrchestrator` error handler
- **Type safety**: `shared/types.ts` is enforced across all layers—mismatches surface at compile time
- **Audit trail**: Query `zero_hour_decisions` table with `audit_log_id` to trace any decision
