# Grid Resolution Tier Structure Update

## Updated Tier Structure

| Tier | Resolutions | Monthly Price | Use Case |
|------|-------------|---------------|----------|
| **Free** | 50m | $0 | Regional overview, basic field monitoring |
| **Basic** | 50m, 20m | $49 | Field planning, irrigation zone management |
| **Pro** | 50m, 20m, 10m | $199 | Precision agriculture, VRI integration |
| **Enterprise** | 50m, 20m, 10m, **1m** | Custom | Research-grade, water court compliance |

## Changes Made

### 1. Backend API (`backend/app/api/main.py`)
- Updated 1m grid endpoint to require `ENTERPRISE` tier instead of `PRO`
- Updated docstring: "Requires ENTERPRISE Tier."

### 2. User Model (`backend/app/models/user.py`)
- Updated `SubscriptionTier` enum comments:
  - FREE: 50m only
  - BASIC: 50m, 20m
  - PRO: 50m, 20m, 10m
  - ENTERPRISE: 50m, 20m, 10m, 1m

### 3. Marketing Website (`/` route)
- **Pro tier**: Changed from "50m, 20m, 10m, 1m grids" to "50m, 20m, 10m grids"
- **Enterprise tier**: Highlighted 1m as "1m research-grade" in special styling
- **FAQ**: Updated to show 1m as Enterprise-only

### 4. Documentation Website (`/docs` route)
- **Grid descriptions**: Updated all 4 grid tiers with correct access levels
- **1m Grid**: Now labeled as "Enterprise" tier
- **Added**: Tier comparison table showing which resolutions are available at each tier
- Updated Key Features list

## API Endpoints by Tier

| Endpoint | Tier Required | Resolution |
|----------|---------------|------------|
| `GET /api/v1/fields/{id}/grid/50m` | FREE | 50m |
| `GET /api/v1/fields/{id}/grid/20m` | BASIC | 20m |
| `GET /api/v1/fields/{id}/grid/10m` | PRO | 10m |
| `GET /api/v1/fields/{id}/grid/1m` | **ENTERPRISE** | 1m |

## 1m Grid Use Cases (Enterprise Only)

- **Water Court Proceedings**: Legally defensible data at maximum resolution
- **Research Applications**: Scientific studies requiring sub-meter accuracy
- **Academic Partnerships**: University research collaborations
- **Regulatory Compliance**: Detailed reporting for government oversight
- **Insurance Claims**: High-resolution documentation for crop damage claims

## Migration Notes

Any existing Pro tier users with 1m grid access will need to:
1. Upgrade to Enterprise tier to maintain 1m access, OR
2. Use 10m resolution (still available in Pro tier)

The 10m grid provides excellent precision for most agricultural applications at 1/4 the cost of Enterprise.
