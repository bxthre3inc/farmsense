# FarmSense Dependency Reduction Plan

## Objective
Remove unnecessary dependencies, preferring custom code and logic for maximum flexibility and minimal external risk.

---

## Current Status: **PAUSED** (2026-02-19)

Phases 3-4 on hold pending user direction.

---

## Phase 1: Dead Code Removal ✅ COMPLETE

**Date:** 2026-02-19

### Removed from `backend/requirements.txt`:
| Dependency | Reason |
|------------|--------|
| `redis` | Not used anywhere |
| `celery` | Not used anywhere |
| `numpy` | Imported but never called |
| `pandas` | Not used anywhere |
| `scipy` | Not used anywhere |
| `scikit-learn` | Not used anywhere (anti-AI architecture) |
| `requests` | Consolidated to aiohttp (async-first) |

### Removed from `cloud-processing/ml/requirements.txt`:
| Dependency | Reason |
|------------|--------|
| `numpy` | Not used (was just imported) |
| `scikit-learn` | Not used |
| `pandas` | Not used |

### Code Changes:
- Removed `import numpy as np` from `adaptive_recalc_engine.py`
- Removed `import numpy as np` from `model_stubs.py`

### Impact:
- **Zero functional changes** - all removed deps were unused
- **Reduced attack surface** - fewer packages to audit
- **Smaller deployment** - fewer packages to install
- **Cleaner architecture** - aligns with deterministic, anti-AI approach

---

## Phase 2: Unused Import Cleanup ✅ COMPLETE

**Date:** 2026-02-19

Done as part of Phase 1.

---

## Phase 3: Utility Replacement 🔜 NEXT

**Dependencies:** `clsx` + `tailwind-merge`

**Files Affected:**
- `marketing-site/src/App.tsx`

**Replacement:**
```typescript
// Custom cn() utility (~8 lines)
function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}
```

**Risk:** Low - single file, simple utility

---

## Phase 4: Animation Replacement 🔜 PENDING

**Dependencies:** `framer-motion`

**Files Affected:**
- `marketing-site/src/App.tsx`

**Replacement:** CSS transitions + custom hooks

**Risk:** Low - marketing site only, not core functionality

---

## Phase 5: HTTP Client Consolidation 🔜 PENDING

**Dependencies:** Convert `requests` → `aiohttp` everywhere

**Files Affected:**
- `external_data_service.py` - weather/soil API calls
- `satellite_service.py` - STAC API calls

**Replacement:** Async aiohttp with proper session management

**Risk:** Medium - requires async refactoring, but straightforward

---

## Phase 6: Chart Replacement 🔜 PENDING

**Dependencies:** `recharts`

**Files Affected:**
- `research-portal/src/App.tsx`
- `investor-dashboard/src/App.tsx`
- `grant-portal/src/App.tsx`

**Replacement:** Custom SVG charts (~200 LOC per chart type)

**Risk:** Medium-High - significant UI work, but maintains control

---

## Phase 7: ML Module Removal 🔜 PENDING

**Entire module:** `cloud-processing/ml/`

**Rationale:**
- Contains mock/stub prediction code
- Contradicts deterministic, anti-AI architecture
- Only 90 LOC of mock code
- No real functionality

**Risk:** Low - not integrated with core system

---

## Current Dependency Count

| Category | Before | After Phase 1 | Target |
|----------|--------|---------------|--------|
| Backend Python | 16 | 9 | 7 |
| Frontend (per project) | 4-6 | 4-6 | 2-3 |
| Total npm packages | ~40 | ~40 | ~15 |

---

## Principles

1. **Custom over convenience** - Build it ourselves when practical
2. **Async-first** - Prefer async patterns for scalability
3. **Deterministic** - No ML/AI black boxes (anti-AI architecture)
4. **Minimal attack surface** - Fewer deps = fewer vulnerabilities
5. **Easy pivots** - Modular code allows quick changes

---

*Last updated: 2026-02-19*
