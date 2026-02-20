# Required Updates for All Portals

## 1. Marketing Page (`/`) - HIGH PRIORITY

### Stats Section (Line ~170-190)
Add "PILOT TARGET" labels to stats:
- 19,466 Devices → Add "PILOT TARGET" below
- 2.8M Daily Readings → Add "PILOT TARGET" below
- 4 Grid Resolutions → No label needed (this is a feature count)
- <2s Emergency Response → Add "PILOT TARGET" below

### Add Banner Above Stats
```tsx
<div className="inline-flex items-center gap-2 bg-amber-50 text-amber-700 px-4 py-2 rounded-full text-sm font-semibold mb-6">
  <Target className="w-4 h-4" />
  Pilot Deployment Targets - Subdistrict 1, San Luis Valley
</div>
```

## 2. Investor Portal (`/investor`) - GOOD
- Already has disclaimer banner ✓
- Forward-looking statement present ✓

## 3. Grant Portal (`/grant`) - NEEDS REVIEW
- Ensure it has target labels on all projections
- Add disclaimer about pre-deployment status

## 4. Docs Page (`/docs`) - GOOD
- Has correct tier structure ✓
- Shows all 4 grid resolutions ✓

## 5. Footer Links
Update all portal footers to link to `/investor` (not `#investor`)

---

## How to Update zo.space Pages

Since zo.space pages are not workspace files, use:
```
get_space_route(path) → Get current code
Edit the code manually with TARGET labels
update_space_route(path, code=updated_code) → Deploy
```

## Current Routes Summary

| Path | Type | Status |
|------|------|--------|
| `/` | Page | Needs TARGET labels |
| `/auth` | Page | Check if correct |
| `/farmers` | Page | Private - Farmer login |
| `/farmers/dashboard` | Page | Private - Dashboard |
| `/investor` | Page | Good - Has disclaimer |
| `/grant` | Page | Check content |
| `/docs` | Page | Good - Correct tiers |
| `/command` | API | Admin Command Center |
| `/oversight` | API | Oversight portal |
