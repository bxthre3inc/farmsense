# FarmSense Content Management System

## Overview

A unified content management system for the Command Center that manages all data points used across portals.

## Canonical BOM Data

| Device | Qty | Unit Cost | Hardware Subtotal | Total Project Cost |
|--------|-----|-----------|-------------------|-------------------|
| LRZ (Scout) | 15,600 | $85.00 | $1,326,000 | $1,540,500 |
| VFA (Anchor) | 1,280 | $455.00 | $582,400 | $672,000 |
| PFA (Sentry) | 1,280 | $750.00 | $960,000 | $1,248,000 |
| PMT (Tracker) | 1,280 | $1,100.00 | $1,408,000 | $1,565,440 |
| DHU (Hub) | 25 | $4,565.00 | $114,125 | $145,000 |
| RSS (Superstation) | 1 | — | — | $212,000 |
| **TOTAL** | **19,466** | — | **$4,390,525** | **$5,382,940** |

## Content Types

| Type | Description | Used In |
|------|-------------|---------|
| Team Member | People displayed on portals | All portals |
| Document | Business plans, specs, roadmaps | Grant, Investor |
| BOM Entry | Hardware components and costs | All portals |
| Letter of Support | Partner/government letters | Grant |
| Business Plan Section | Extracted sections for reuse | Investor, Grant |
| Portal Config | Colors, stats, sections per portal | All portals |
| Daily Goal | Team todos and tasks | Command Center |

## API Endpoints

### Team Members
- `GET /api/v1/content/team` - List team members
- `POST /api/v1/content/team` - Create team member
- `PUT /api/v1/content/team/{id}` - Update team member
- `DELETE /api/v1/content/team/{id}` - Delete team member

### Documents
- `GET /api/v1/content/documents` - List documents
- `POST /api/v1/content/documents/upload` - Upload document
- `POST /api/v1/content/documents/{id}/sections` - Create section
- `GET /api/v1/content/sections` - List all sections

### Letters of Support
- `GET /api/v1/content/letters` - List letters
- `POST /api/v1/content/letters` - Create letter

### BOM
- `GET /api/v1/content/bom` - List BOM entries
- `GET /api/v1/content/bom/summary` - Get totals
- `POST /api/v1/content/bom` - Create BOM entry

### Portal Config
- `GET /api/v1/content/portal/{type}` - Get portal config
- `PUT /api/v1/content/portal/{type}` - Update portal config

### Daily Goals
- `GET /api/v1/content/goals` - List goals
- `POST /api/v1/content/goals` - Create goal
- `PUT /api/v1/content/goals/{id}/complete` - Complete goal

### Business Plan
- `GET /api/v1/content/business-plan` - List sections
- `POST /api/v1/content/business-plan` - Create section

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    COMMAND CENTER (/admin)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Team      │  │  Documents  │  │    BOMs     │        │
│  │  Members    │  │   Upload    │  │   Import    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          ▼                                 │
│              ┌─────────────────────┐                       │
│              │  Content Database   │                       │
│              │  (PostgreSQL)       │                       │
│              └──────────┬──────────┘                       │
└─────────────────────────┼──────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Investor│     │  Grant  │     │  Farmer │
    │ Portal  │     │ Portal  │     │ Portal  │
    └─────────┘     └─────────┘     └─────────┘
```

## Files Created

1. **Content Models**: `backend/app/models/content.py`
2. **Content API**: `backend/app/api/content.py`
3. **Canonical BOM**: `farmsenseOS/CANONICAL_BOM.md`

## Next Steps

1. Register content router in main.py
2. Create Command Center UI page at `/admin`
3. Ingest existing documents into the system
4. Import BOM data from canonical files
5. Create portal pages that pull from content system
6. Add document parsing for section extraction
