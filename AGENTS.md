# FarmSense Project Memory

## CRITICAL INSTRUCTIONS FOR AI ASSISTANT

### Before Creating ANYTHING:
1. **CHECK EXISTING ROUTES FIRST**: Use `list_space_routes` to see all current pages and APIs
2. **CHECK EXISTING FILES**: Use `grep_search` or `list_files` before creating new files
3. **CHECK AGENTS.MD**: Read this file at the start of every conversation for context
4. **ASSUME NOTHING EXISTS**: Always verify before assuming something needs to be created

## Architecture Principle: Anti-AI / Deterministic
FarmSense uses **deterministic, judgment-based algorithms** - NOT ML/AI black boxes.
- Water courts don't accept AI decisions
- All logic must be explainable and auditable
- See `file 'farmsenseOS/GENUINELY_NOVEL_IP.md'` for defensible moats

**Future AI**: Post-beta, sandboxed Digital Twin simulations only.
- See `file 'farmsenseOS/AI_INTEGRATION_ROADMAP.md'`
- **DO NOT ACT** until user says "begin to integrate AI per our previous discussions"

## Dependency Reduction
See `file 'farmsenseOS/DEPENDENCY_REDUCTION.md'` for full plan.
- Phase 1 ✅: Removed numpy, pandas, scipy, scikit-learn, redis, celery, requests
- Next: Phase 3 (clsx/tailwind-merge replacement)

## Component Libraries

### FarmSense UI (Clean Design)
**Location:** `file 'farmsenseOS/farmsense-code/frontend/shared/components/farmsense-ui/'`
**Purpose:** Marketing pages, investor portal, grant portal, admin dashboards
**Design:** Solid colors, minimal borders, NO glassmorphism
- Backgrounds: `bg-white`, `bg-slate-50`
- Borders: `border-slate-200`
- Accent: `emerald-600`

### SilasUI (Field Interface)
**Location:** `file 'farmsenseOS/farmsense-code/frontend/shared/components/silas-ui/'`
**Purpose:** Farmer field dashboard
**Design:** Minimal, decision-focused, single-action (WATER/WAIT/OFF)

**READ:** `file 'farmsenseOS/farmsense-code/frontend/shared/components/README.md'`

### Stats Convention
All projected stats MUST show "PILOT TARGET" badge using `isTarget: true` prop.

### Current zo.space Routes (as of last update):
- `/` - Main marketing page (public)
- `/auth` - Unified login/signup (public)
- `/farmers` - Farmer login (private)
- `/farmers/dashboard` - Farmer dashboard (private)
- `/investor` - Investor portal (public)
- `/grant` - Grant reviewer portal (public)
- `/docs` - Documentation (public)
- `/command` - Command Center (API serves HTML)
- `/oversight` - Oversight portal (API serves HTML)

### Key User Types & Their Portals:
| User Type | Portal Path | Description |
|-----------|-------------|-------------|
| Farmer | `/farmers/dashboard` | Field management, irrigation |
| Investor | `/investor` | Investment info, targets |
| Grant Reviewer | `/grant` | Grant applications, BOMs |
| Admin | `/command` | System management |
| Regulator | `/oversight` | Compliance monitoring |
| Partner | `/partner` | Partner dashboard |
| Researcher | `/grant` | Research data (shared with grant) |

### Shared Data Across Portals:
All portals use the SAME source data with different messaging:
- **Hardware BOMs**: See `file 'hardware BOM&specs/'` folder
- **Stats**: Always mark as "TARGET" (not live data)
- **Team Members**: Use `file 'farmsenseOS/farmsense-code/backend/app/models/operations.py'`
- **Pilot Stats**: 19,466 devices, $5.38M hardware investment

### Tier Structure (CANONICAL):
| Tier | Price | Grid | Features |
|------|-------|------|----------|
| Free | $0 | 50m | Read only, no actuation |
| Basic | $49/mo | 20m | Irrigation recommendations |
| Pro | $199/mo | 10m | Actuation, daily reports |
| Enterprise | Custom | 1m | Compliance guarantee, connect any hardware |

### File Locations:
- **Backend**: `/home/workspace/farmsenseOS/farmsense-code/backend/`
- **Frontend**: `/home/workspace/farmsenseOS/farmsense-code/frontend/`
- **Shared Components**: `/home/workspace/farmsenseOS/farmsense-code/frontend/shared/components/`
- **Hardware BOMs**: `/home/workspace/hardware BOM&specs/`
- **Key Docs**: `file 'farmsenseOS/CANONICAL_BOM.md'`, `file 'farmsenseOS/TIER_STRUCTURE_FINAL.md'`

### Current Pilot Status:
- **Phase**: Pre-deployment (targets, not live data)
- **Location**: San Luis Valley, Colorado
- **Subdistrict 1**: 117,000 acres, 19,466 devices
- **Hardware Investment**: $5,382,940

### Action Items:
1. ✅ DONE
2. ✅ DONE
3. ✅ DONE
4. ✅ DONE

### Recently Completed (2026-02-20):
- Created `/invest` page with three investment options
- Added advanced navigation with User Types and Use Cases dropdowns
- Updated home page with urgent CSU SLVRC pilot funding message
- Added "Zero Hardware Costs" messaging for farmers
- Updated Pre-Valuation Equity to 0.01% guarantee (36 months)
- Dependency reduction Phases 1-2 complete (paused)
- AI integration strategy documented (not implementing yet)

---
*Last updated: 2026-02-20*
*Read this file at the START of every conversation*
