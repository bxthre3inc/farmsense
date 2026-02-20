# Top 10 Enterprise Improvements Needed

## 1. Add API Rate Limiting (CRITICAL)
**Why:** Prevent DDoS, protect resources, ensure fair usage
**Implementation:**
```python
# pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/sensors/readings")
@limiter.limit("100/minute")
async def ingest_sensor_reading(...):
```

## 2. Replace API Keys with JWT + OAuth2 (CRITICAL)
**Why:** API keys don't expire, can't be revoked easily, no refresh mechanism
**Implementation:**
```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

## 3. Write Test Suite (CRITICAL)
**Why:** 0% coverage is unacceptable for enterprise
**Start with:**
```python
# tests/test_api.py
async def test_ingest_sensor_reading(client, db):
    response = await client.post("/api/v1/sensors/readings", json={...})
    assert response.status_code == 201
    assert response.json()["quality_flag"] == "valid"
```

## 4. Add Structured Logging (HIGH)
**Why:** Current logs are plaintext; need JSON for parsing
**Implementation:**
```python
import structlog

logger = structlog.get_logger()
logger.info("sensor_reading_ingested", 
            sensor_id="S-123", 
            field_id="F-456",
            request_id="req-789")
```

## 5. Implement Health Check Endpoints (HIGH)
**Why:** Kubernetes needs these for orchestration
**Implementation:**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/health/deep")
async def deep_health_check(db: Session = Depends(get_db)):
    # Check DB connectivity
    # Check external APIs
    # Check disk space
```

## 6. Add Request ID Middleware (HIGH)
**Why:** Trace requests across services
**Implementation:**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

## 7. Setup Database Migrations with Alembic (HIGH)
**Why:** Track schema changes, enable rollbacks
**Commands:**
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## 8. Add Input Validation Layer (HIGH)
**Why:** Pydantic handles basics but business rules need validation
**Implementation:**
```python
from pydantic import validator

class SensorReadingCreate(BaseModel):
    @validator('moisture_surface')
    def validate_moisture(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Moisture must be between 0 and 1')
        return v
```

## 9. Implement Circuit Breaker Pattern (MEDIUM)
**Why:** Prevent cascade failures when external APIs fail
**Implementation:**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def fetch_satellite_data(lat, lon):
    # Call to external satellite API
```

## 10. Add Application Metrics (MEDIUM)
**Why:** Need visibility into performance
**Implementation:**
```python
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    api_requests.labels(endpoint=request.url.path).inc()
    request_duration.observe(duration)
    return response
```

---

## Quick Wins (Can do today)

1. **Add security headers to main.py:**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["farmsense.io", "*.farmsense.io", "*.zocomputer.io"]
)
```

2. **Add CORS properly:**
```python
# Replace wildcard with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://farmsense.io", "https://*.zocomputer.io"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

3. **Add request validation:**
```python
# Add to all endpoints
async def endpoint(data: SensorReadingCreate):
    if data.moisture_surface < 0:
        raise HTTPException(400, "Invalid moisture value")
```

4. **Add simple health check:**
```python
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

---

## Priority Order

**Week 1:** 1, 2, 4 (Security + Observability)
**Week 2:** 3, 5, 6 (Testing + Reliability)
**Week 3:** 7, 8, 9 (Data Integrity + Resilience)
**Week 4:** 10 + UI improvements (Metrics + Polish)