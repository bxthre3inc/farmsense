# Portal Alignment Summary

## Current State

### Investor Portal (`/investor`)
- **Status**: Created ✅
- **Data Issues**: Hardware costs don't match BOM ($9.4M shown vs $5.38M actual)
- **Missing**: Clear "Target" labels on projected stats

### Grant Portal (`/grant`)
- **Status**: Created as API route, needs proper page
- **Purpose**: Grant reviewers see BOMs, specs, timeline, compliance

## Required Changes

### Both Portals Need:

1. **Correct Hardware Data**:
   - Total: $5.38M (BOM cost)
   - LRZ: 15,600 units @ $270 = $4.21M
   - VFA: 1,280 units @ $1,230 = $1.57M  
   - PFA: 1,280 units @ $1,572 = $2.01M
   - PMT: 1,280 units @ $2,578 = $3.30M
   - DHU: 25 units @ $22,677 = $0.57M
   - RSS: 1 unit @ $22,000 = $0.02M

2. **Clear "Target" Labels**:
   - 117,000 acres (Target: Subdistrict 1)
   - 2.4B gallons water saved (Target)
   - 45,000 metric tons CO₂ (Target)
   - 94.2% compliance (Target)

3. **Validation Partner**:
   - CSU San Luis Valley Research Center

### Investor Portal Specific:
- Focus on ROI, market opportunity, competitive advantages
- Show $47B TAM, $4.2B SAM, $420M initial market
- Emphasize revenue potential, retention

### Grant Portal Specific:
- Focus on public benefit, compliance, validation
- Show timeline phases with milestones
- Include downloadable BOMs and specs
- Emphasize SLV 2026 compliance, Water Court defensibility

## Action Items

1. Update `/investor` with correct hardware costs ($5.38M)
2. Create proper `/grant` page (currently API route)
3. Ensure both portals show "Target" labels prominently
4. Add validation partner: CSU SLV RC

## File References
- Shared data: `/home/workspace/farmsenseOS/SHARED_PORTAL_DATA.md`
- Hardware BOMs: `/home/workspace/hardware BOM&specs/`