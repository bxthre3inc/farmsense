# FarmSense AI Integration Roadmap

## Status: FROZEN

**DO NOT PROCEED** until explicit user authorization.

## Trigger Phrase

The following phrase (or derivative) must be spoken by the user before any AI integration work begins:

> "begin to integrate AI per our previous discussions"

## Post-Beta AI Strategy

### Purpose
AI will be used **only** for Digital Twin simulations to optimize soil variability maps.

### Scope
- **Sandboxed environment** - completely isolated from production systems
- **Simulation-only** - no direct control or actuation
- **Optimization research** - improve Kriging interpolation parameters
- **What-if scenarios** - test irrigation strategies before deployment

### Why Post-Beta?
1. **Water Court Requirements**: Current architecture is deterministic and legally defensible
2. **Pilot Validation**: Need real-world data before simulation accuracy can be trusted
3. **Simplification First**: Remove complexity, prove deterministic system works, then add optional AI layer
4. **Customer Trust**: Farmers need to trust the deterministic system before AI augmentation

### Architecture Principle
```
Production System (Deterministic) ← Water Court Defensible
         ↑
         │ (simulation results only, never direct control)
         │
Sandboxed AI Digital Twin ← Research/Optimization Layer
```

### Implementation Notes (Future)
- AI module will be a separate microservice
- No API keys in production code
- Results flow one direction: AI → Simulation → Human Review → Optional Manual Integration
- All AI-generated recommendations require human approval

### Dependencies (Future, Not Now)
- `numpy` (for numerical computation in sandbox)
- `scipy` (for interpolation algorithms in sandbox)
- `torch` or `jax` (for neural network simulations in sandbox)

**These should NOT be added to main requirements.txt** - they will live in a separate `ai-sandbox/` module.

---

## Current Status: NOT STARTED

This document is for future planning only.

*Created: 2026-02-19*
*Last updated: 2026-02-19*
