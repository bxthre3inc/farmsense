# farmsenseOS - Precision Agriculture Platform

**Full-stack precision agriculture application with virtual sensor networks, adaptive recalculation, and regulatory compliance.**

---

## 🌾 Overview

farmsenseOS is a nationally-scalable precision agriculture platform that:

- **Ingests multi-source data**: Soil sensors (2-depth + vertical profiling), pump telemetry, weather stations, Sentinel-1/2 imagery, Landsat historical data
- **Computes virtual sensor grids**:
  - **Edge (20m resolution)**: Real-time field-level processing on Raspberry Pi/Jetson
  - **Cloud (1m resolution)**: High-resolution interpolation with satellite integration
- **Adaptive recalculation logic**: 1min → 12hr windows based on field trends and events
- **Compliance reporting**: SLV 2026 regulatory alignment with audit trails
- **Multi-stakeholder dashboards**: Farmers, regulators, consultants

---

## 📁 Repository Structure

```
farmsense-code/
├── backend/                    # FastAPI backend services
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   │   └── main.py        # Main API application
│   │   ├── models/            # SQLAlchemy data models
│   │   │   └── sensor_data.py # Sensor & grid models
│   │   ├── services/          # Business logic
│   │   │   └── adaptive_recalc_engine.py  # Recalculation engine
│   │   └── core/              # Config, database, auth
│   ├── Dockerfile
│   └── requirements.txt
│
├── edge-compute/              # Edge processing (20m grid)
│   ├── src/
│   │   └── edge_processor.go  # Go-based edge compute
│   └── config/                # Edge device configurations
│
├── cloud-processing/          # Cloud analytics (1m grid)
│   ├── pipelines/
│   │   └── kriging_1m.py      # Regression Kriging interpolation
│   └── ml/                    # ML models
│
├── frontend/                  # Web applications
│   ├── farmer-dashboard/      # Farmer interface (React + Mapbox)
│   └── regulatory-portal/     # Compliance dashboard
│
├── database/                  # Database schemas
│   ├── migrations/            # Alembic migrations
│   └── seeds/                 # Sample data
│
└── deployment/                # Infrastructure
    ├── docker/
    │   └── docker-compose.yml # Local dev environment
    └── kubernetes/            # Production K8s manifests
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (20.10+)
- **Python** 3.11+ (for local development)
- **Go** 1.21+ (for edge module)
- **Node.js** 18+ (for frontend)

### 1. Clone Repository

```bash
# Repository would be cloned here
cd farmsense-code
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required environment variables:**

```env
# Database
DB_PASSWORD=your_secure_password
TIMESCALE_PASSWORD=your_timescale_password

# Message Queue
RABBITMQ_PASSWORD=your_rabbitmq_password

# API Keys
SENTINEL_API_KEY=your_copernicus_key
LANDSAT_API_KEY=your_usgs_key
MAPBOX_TOKEN=your_mapbox_token

# Security
SECRET_KEY=your_jwt_secret_key

# Environment
ENVIRONMENT=development
```

### 3. Start Services

```bash
cd deployment/docker
docker-compose up -d
```

**Services will be available at:**

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Farmer Dashboard**: http://localhost:3000
- **Regulatory Portal**: http://localhost:3001
- **Grafana Monitoring**: http://localhost:3002
- **RabbitMQ Management**: http://localhost:15672

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed sample data (optional)
docker-compose exec backend python scripts/seed_data.py
```

### 5. Test API

```bash
# Health check
curl http://localhost:8000/health

# Ingest sensor reading
curl -X POST http://localhost:8000/api/v1/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "s001",
    "field_id": "field_001",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "moisture_surface": 0.25,
    "moisture_root": 0.30,
    "temp_surface": 22.5
  }'
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    FARMSENSE PLATFORM                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐    │
│  │   Sensors  │  │   Pumps    │  │   Weather     │    │
│  │  (IoT)     │  │ (Telemetry)│  │  (Stations)   │    │
│  └──────┬─────┘  └──────┬─────┘  └───────┬───────┘    │
│         │                │                 │             │
│         └────────────────┴─────────────────┘             │
│                          │                               │
│                    ┌─────▼──────┐                       │
│                    │   EDGE     │  (Raspberry Pi)       │
│                    │  20m Grid  │  IDW Interpolation    │
│                    └─────┬──────┘                       │
│                          │                               │
│         ┌────────────────┴────────────────┐             │
│         │                                  │             │
│    ┌────▼─────┐                   ┌───────▼────────┐   │
│    │  Cloud   │ ◄─Sentinel/Landsat│   Satellite    │   │
│    │  1m Grid │                    │   Processing   │   │
│    │ (Kriging)│                    │                │   │
│    └────┬─────┘                    └────────────────┘   │
│         │                                                │
│    ┌────▼──────────────┐                                │
│    │  Adaptive Recalc  │ (1min - 12hr windows)         │
│    │     Engine        │ Event-driven triggers          │
│    └────┬──────────────┘                                │
│         │                                                │
│    ┌────▼──────────────────────────────┐                │
│    │        Analytics & ML              │                │
│    │  • Irrigation scheduling           │                │
│    │  • Crop stress detection           │                │
│    │  • Yield forecasting               │                │
│    └────┬──────────────────────────────┘                │
│         │                                                │
│    ┌────▼────────────────────────────────────┐          │
│    │           Dashboards                    │          │
│    │  • Farmer (Field view + alerts)        │          │
│    │  • Regulatory (Compliance reports)     │          │
│    │  • Consultant (Multi-field analysis)   │          │
│    └─────────────────────────────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion**: Sensors → REST API → TimescaleDB
2. **Edge Processing**: Local compute → 20m grid → PostgreSQL/PostGIS
3. **Cloud Processing**: Satellite integration → Regression Kriging → 1m grid
4. **Adaptive Logic**: Trend analysis → Mode selection (1min/15min/12hr)
5. **Analytics**: ML models → Irrigation recommendations → Compliance reports
6. **Delivery**: WebSocket updates → Real-time dashboards

---

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.api.main:app --reload --port 8000
```

### Edge Module Development

```bash
cd edge-compute/src

# Build
go build -o edge_processor edge_processor.go

# Run with config
./edge_processor --config ../config/field_001.json
```

### Frontend Development

```bash
cd frontend/farmer-dashboard

# Install dependencies
npm install

# Run dev server
npm start
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📊 API Documentation

### Key Endpoints

#### Sensor Data Ingestion

```http
POST /api/v1/sensors/readings
Content-Type: application/json

{
  "sensor_id": "s001",
  "field_id": "field_001",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "moisture_surface": 0.25,
  "moisture_root": 0.30,
  "temp_surface": 22.5
}
```

#### Get Virtual Grid (20m)

```http
GET /api/v1/fields/{field_id}/grid/20m?limit=1000
```

#### Field Analytics

```http
GET /api/v1/fields/{field_id}/analytics
```

**Response:**

```json
{
  "field_id": "field_001",
  "avg_moisture": 0.27,
  "stress_area_pct": 15.3,
  "irrigation_zones": [
    {"need": "none", "count": 45},
    {"need": "low", "count": 30},
    {"need": "medium", "count": 20},
    {"need": "high", "count": 5}
  ],
  "current_mode": "active",
  "next_recalc": "2026-02-12T15:30:00Z"
}
```

#### Compliance Reports

```http
POST /api/v1/compliance/reports/generate
{
  "field_id": "field_001",
  "period_start": "2026-01-01T00:00:00Z",
  "period_end": "2026-01-31T23:59:59Z",
  "report_type": "monthly"
}
```

**Full API documentation**: http://localhost:8000/docs

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Edge Module Tests

```bash
cd edge-compute
go test ./src/... -v
```

### Integration Tests

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/ -v
```

---

## 📈 Monitoring

### Metrics Collection

- **Prometheus**: Collects metrics from all services
- **Grafana**: Visualizes system performance

**Key Dashboards:**

1. **System Health**: API latency, throughput, error rates
2. **Data Pipeline**: Ingestion rates, processing times
3. **Field Monitoring**: Grid computation times, recalculation frequency
4. **Resource Usage**: CPU, memory, disk I/O

### Logging

```bash
# View backend logs
docker-compose logs -f backend

# View edge processor logs
docker-compose logs -f cloud-processor

# View all logs
docker-compose logs -f
```

---

## 🚢 Production Deployment

### Kubernetes Deployment

```bash
cd deployment/kubernetes

# Create namespace
kubectl create namespace farmsense

# Deploy PostgreSQL
kubectl apply -f database/

# Deploy backend services
kubectl apply -f backend/

# Deploy frontend
kubectl apply -f frontend/

# Check status
kubectl get pods -n farmsense
```

### Scaling

```bash
# Scale backend
kubectl scale deployment farmsense-backend --replicas=5 -n farmsense

# Scale cloud processors
kubectl scale deployment cloud-processor --replicas=10 -n farmsense
```

### Edge Device Deployment

```bash
# Package edge binary
cd edge-compute
GOOS=linux GOARCH=arm64 go build -o edge_processor_arm64 src/edge_processor.go

# Deploy to Raspberry Pi
scp edge_processor_arm64 pi@field-device:/opt/farmsense/
scp config/field_config.json pi@field-device:/opt/farmsense/
ssh pi@field-device "sudo systemctl restart farmsense-edge"
```

---

## 🔐 Security

### Authentication

- **JWT tokens** for API authentication
- **OAuth2** for third-party integrations
- **Role-based access control** (RBAC)

### Data Protection

- **TLS 1.3** for all communications
- **AES-256 encryption** for data at rest
- **Field-level encryption** for sensitive data
- **Regular security audits** and penetration testing

### Compliance

- **SLV 2026** regulatory alignment
- **Immutable audit logs** with blockchain-style hashing
- **GDPR compliance** for user data
- **ISO 27001** certification roadmap

---

## 📚 Additional Resources

### Documentation

- [System Architecture](https://www.genspark.ai/doc_agent?id=b0db7361-09c7-4f59-8007-0b644ec4310d) - Complete technical specs
- [API Reference](http://localhost:8000/docs) - Interactive API docs
- [Database Schema](./docs/database_schema.md) - Data model documentation
- [Deployment Guide](./docs/deployment.md) - Production deployment

### Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@farmsense.io

### Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📄 License

Copyright © 2026 Project FarmSense. All rights reserved.

---

## 🙏 Acknowledgments

- **Sentinel Hub** - Satellite imagery
- **USGS** - Landsat data
- **Copernicus** - Earth observation data
- **Open-source community** - Foundational tools and libraries

---

**Built with ❤️ for sustainable agriculture** 🌾
