# 🌾 FarmSense Precision Agriculture Platform

## 📦 Split Deployment Guide

This project is configured for a **Hybrid Cloud Deployment**:

- **Core Platform (Zo.computer)**: Hosts the API, processing, and frontend applications.
- **Map Stack (Oracle Cloud)**: Hosts the geospatial database and map tile services.

### 1. Oracle Cloud (Map Stack) Setup

Deploy this FIRST to ensure the database is available for the core platform.

```bash
# On your Oracle Instance
cd deployment/docker
docker-compose -f docker-compose.oracle.yml up -d
```

**Services Started:**

- `postgis-map`: Review `docker-compose.oracle.yml` for credentials (Default: `map_user`/`changeme`).
- `map-service`: Tile serving endpoint (Port 8001).

**Network Config:**

- Ensure Port `5432` is accessible from your Zo.computer IP (configure Oracle Security List / VCN).

### 2. Zo.computer (Core Platform) Setup

```bash
# On your Zo Instance
cd deployment/docker

# Set the connection string to your Oracle instance
export MAP_DATABASE_URL="postgresql://map_user:changeme@<ORACLE_IP>:5432/farmsense_map"

docker-compose -f docker-compose.zo.yml up -d
```

**Services Started:**

- `backend-api`: Main API (Port 8000).
- `frontend-dashboard`: Farmer Dashboard (Port 3000).
- Core DBs: Postgres, Timescale, Redis.

### 3. Verification

1. Access the Dashboard at `http://<ZO_IP>:3000`.
2. The map tiles will be served from `http://<ZO_IP>:8000/api/v1/tiles/...` which internally queries the Oracle DB.

---

## 🏗️ Development Setup

For local development (single machine), use the standard compose file:

```bash
docker-compose up -d
```
