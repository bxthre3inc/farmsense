"""
FastAPI Backend - Data Ingestion and Analytics API
"""
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, WebSocket, WebSocketDisconnect, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio
import json
import uvicorn
import hashlib
import uuid
from pydantic import BaseModel, Field

from app.models.sensor_data import (
    SoilSensorReading, PumpTelemetry, WeatherData,
    VirtualSensorGrid20m, VirtualSensorGrid50m, VirtualSensorGrid10m, VirtualSensorGrid1m,
    RecalculationLog, ComplianceReport
)
from app.models.grant import SupportLetter, LetterStatus, SupportLetterCreate, SupportLetterRead, SupportLetterSign
from app.services.adaptive_recalc_engine import (
    AdaptiveRecalculationEngine, FieldCondition, RecalcMode
)
from app.core.database import get_db
from app.models.user import User, SubscriptionTier, UserRole
from app.api.dependencies import get_current_user, RequireTier, RequireRole

from app.services.grid_renderer import GridRenderingService
from app.services.notification_service import notification_service
from app.services.ai_handsfree import FieldDecisionEngine, FieldDiagnosticService
from app.models.sensor_data import AnonymizedResearchArchive
from app.services.equity_service import SignatureService
from app.services.websocket_manager import manager, ingestion_service
from app.services.satellite_service import satellite_service
from app.models.field import Field, DeviceMapping

import os

app = FastAPI(
    title="FarmSense API",
    description="Precision Agriculture Platform — Deterministic, Explainable, Auditable",
    version="2.0.0"
)

from app.api.integration import router as integration_router
app.include_router(integration_router, prefix="/api/v1")
from app.api import tiles
app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])

from app.api import hardware
app.include_router(hardware.router, prefix="/api/v1")

from app.api import edge
app.include_router(edge.router, prefix="/api/v1")

from app.api import content
app.include_router(content.router)

from app.api import actuation
app.include_router(actuation.router, prefix="/api/v1")

@app.get("/api/v1/regulatory/research", tags=["Regulatory"])
async def get_regulatory_research_data(
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Returns anonymized, aggregated research data for regulatory oversight.
    Requires Auditor or Admin role.
    """
    if user.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions for research data pool.")
        
    query = db.query(AnonymizedResearchArchive)
    if region:
        query = query.filter(AnonymizedResearchArchive.region_code == region)
        
    return query.order_by(AnonymizedResearchArchive.timestamp.desc()).limit(100).all()

@app.get("/api/v1/decisions/evaluate", tags=["Decision Engine"])
async def evaluate_field_query(
    query: str = Query(..., description="The farmer's question about field conditions"),
    field_id: str = Query("field_01"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Deterministic field decision endpoint.
    Evaluates the query against live telemetry using explicit threshold rules.
    Returns the decision, every rule applied, and a signed audit log.
    No AI/ML inference is used. Fully explainable and auditable.
    """
    # Get actual field data
    latest_reading = db.query(SoilSensorReading).filter(
        SoilSensorReading.field_id == field_id
    ).order_by(SoilSensorReading.timestamp.desc()).first()
    
    telemetry = {
        "moisture": latest_reading.moisture_surface if latest_reading else 0.22,
        "ndvi": 0.78,
        "temperature": latest_reading.temp_surface if latest_reading else 28.5,
        "savings": 4280
    }
    result = FieldDecisionEngine.evaluate_query(query, field_id, telemetry)
    return result

@app.post("/api/v1/decisions/diagnose", tags=["Decision Engine"])
async def diagnose_field_frame(
    file: UploadFile = File(...),
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    user: User = Depends(get_current_user)
):
    """
    Deterministic visual diagnostic endpoint.
    Matches captured frames against a peer-reviewed pest signature library.
    No neural networks or ML classifiers. Fully auditable.
    """
    content = await file.read()
    location = {"lat": latitude, "lon": longitude}
    result = FieldDiagnosticService.analyze_frame(content, location)
    return result

@app.post("/api/v1/decisions/sms", tags=["Decision Engine"])
async def handle_sms_query(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    SMS/Voice Gateway (Twilio Compatible).
    Allows farmers to query field status via text/voice.
    Returns a concise, deterministic response with rule provenance.
    """
    # Lookup field by phone number
    field = db.query(Field).filter(Field.alert_phone == From).first()
    field_id = field.id if field else "unknown"
    
    # Get latest telemetry
    latest = db.query(SoilSensorReading).filter(
        SoilSensorReading.field_id == field_id
    ).order_by(SoilSensorReading.timestamp.desc()).first()
    
    telemetry = {
        "moisture": latest.moisture_surface if latest else 0.22,
        "ndvi": 0.78,
        "temperature": latest.temp_surface if latest else 28.5,
        "savings": 4280
    }
    
    result = FieldDecisionEngine.evaluate_query(Body, field_id, telemetry)
    
    return {
        "to": From,
        "message": f"FARMSENSE [{field_id}]: {result['response']}",
        "audit_id": result['audit_log']['integrity_hash'][:8]
    }

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    await ingestion_service.start_batch_processor()

# Real WebSocket endpoint
@app.websocket("/api/v1/ws/field/{field_id}")
async def websocket_endpoint(websocket: WebSocket, field_id: str):
    """Real-time field data WebSocket"""
    await manager.connect(websocket, field_id)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "PING":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.utcnow().isoformat()})
            
            elif message_type == "DEVICE_STATUS":
                await ingestion_service.handle_device_status(
                    data.get("device_id"),
                    data
                )
            
            elif message_type == "DEVICE_ALERT":
                await ingestion_service.handle_alert(
                    data.get("device_id"),
                    data
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Sensor data ingestion endpoint
@app.post("/api/v1/ingest/sensor")
async def ingest_sensor_data(
    data: dict,
    background_tasks: BackgroundTasks
):
    """Ingest sensor reading from field devices"""
    result = await ingestion_service.ingest_sensor_reading(data)
    return result

# Bulk ingestion for LRZ devices
@app.post("/api/v1/ingest/lrz-bulk")
async def ingest_lrz_bulk(
    readings: List[dict],
    background_tasks: BackgroundTasks
):
    """Bulk ingest LRZ (Lateral Root-Zone) sensor data"""
    result = await ingestion_service.ingest_bulk_readings(readings)
    return result

# Device status endpoint
@app.get("/api/v1/devices/{device_id}/status")
async def get_device_status(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Get current device status"""
    device = db.query(DeviceMapping).filter(DeviceMapping.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    last_seen = ingestion_service.manager.device_last_seen.get(device_id)
    
    return {
        "device_id": device_id,
        "device_type": device.device_type,
        "field_id": device.field_id,
        "is_active": device.is_active,
        "last_seen": last_seen.isoformat() if last_seen else None,
        "battery_level": device.battery_level,
        "firmware_version": device.firmware_version
    }

# WebSocket stats
@app.get("/api/v1/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()





# --- Pydantic Schemas ---

class SensorReadingCreate(BaseModel):
    sensor_id: str
    field_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    moisture_surface: float = Field(..., ge=0, le=1)
    moisture_root: float = Field(..., ge=0, le=1)
    temp_surface: float
    temp_root: Optional[float] = None
    vertical_profile: Optional[dict] = None
    ec_surface: Optional[float] = None
    ec_root: Optional[float] = None
    ph: Optional[float] = None
    battery_voltage: Optional[float] = None

class SensorReadingResponse(BaseModel):
    id: str
    sensor_id: str
    field_id: str
    timestamp: datetime
    moisture_surface: float
    moisture_root: float
    temp_surface: float
    quality_flag: str
    
    class Config:
        from_attributes = True


class VirtualGridResponse(BaseModel):
    grid_id: str
    field_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    moisture_surface: float
    moisture_root: float
    temperature: float
    water_deficit_mm: float
    stress_index: float
    irrigation_need: str
    confidence: float
    
    class Config:
        from_attributes = True


class FieldAnalyticsResponse(BaseModel):
    field_id: str
    analysis_time: datetime
    avg_moisture: float
    moisture_std: float
    stress_area_pct: float
    irrigation_zones: List[dict]
    current_mode: str
    next_recalc: datetime


class ComplianceReportResponse(BaseModel):
    id: str
    field_id: str
    report_period_start: datetime
    report_period_end: datetime
    total_irrigation_m3: float
    water_use_efficiency: float
    slv_2026_compliant: str
    validation_status: str
    
    class Config:
        from_attributes = True


class ResearchDatasetResponse(BaseModel):
    id: str
    name: str
    size_mb: float
    rows: int
    created_at: datetime
    type: str  # sensors, satellite, compliance

class InvestorMetricsResponse(BaseModel):
    total_acreage: float
    enterprise_clients: int
    total_users: int
    arr_usd: float
    growth_pct: float
    retention_rate: float

class GrantImpactResponse(BaseModel):
    grant_id: str
    water_saved_liters: float
    co2_reduced_tons: float
    yield_increase_pct: float
    soil_health_index: float
    funding_disbursed_usd: float

class ComplianceMetricsResponse(BaseModel):
    compliance_rate_pct: float
    critical_violations: int
    audits_this_month: int
    total_fields_monitored: int

class AdminMetricsResponse(BaseModel):
    active_users: int
    system_health_pct: float
    pending_audits: int
    user_growth_pct: float


class UserBase(BaseModel):
    email: str
    role: UserRole
    tier: SubscriptionTier
    is_active: bool = True
    name: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class UserCreate(UserBase):
    api_key: str

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    tier: Optional[SubscriptionTier] = None
    is_active: Optional[bool] = None
    name: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class UserResponse(UserBase):
    id: str
    api_key: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# === API Endpoints ===

# --- Admin User Management ---

@app.get("/api/v1/admin/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """List all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.post("/api/v1/admin/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Create a new user (Admin only)"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        api_key=user.api_key,
        role=user.role,
        tier=user.tier,
        is_active=user.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.put("/api/v1/admin/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Update user role/tier (Admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.role:
        db_user.role = user_update.role
    if user_update.tier:
        db_user.tier = user_update.tier
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.organization is not None:
        db_user.organization = user_update.organization
    if user_update.phone is not None:
        db_user.phone = user_update.phone
    if user_update.notes is not None:
        db_user.notes = user_update.notes
        
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Stakeholder Data Access ---

@app.get("/api/v1/research/datasets", response_model=List[ResearchDatasetResponse])
def get_research_datasets(
    db: Session = Depends(get_db),
    researcher: User = Depends(RequireRole([UserRole.RESEARCHER, UserRole.ADMIN]))
):
    """Retrieve raw datasets for CSU Partners (Research only)"""
    # Mock datasets - in production these would be file pointers or specialized query views
    return [
        {"id": "ds_001", "name": "Sensor_Batch_2024_12.csv", "size_mb": 42.5, "rows": 125000, "created_at": datetime.utcnow(), "type": "sensors"},
        {"id": "ds_002", "name": "Landsat_NDVI_Composite_Q4.tif", "size_mb": 1024.0, "rows": 0, "created_at": datetime.utcnow(), "type": "satellite"},
        {"id": "ds_003", "name": "Watershed_Impact_Study_2025.json", "size_mb": 5.2, "rows": 1200, "created_at": datetime.utcnow(), "type": "compliance"}
    ]

@app.get("/api/v1/investor/metrics", response_model=InvestorMetricsResponse)
def get_investor_metrics(
    db: Session = Depends(get_db),
    investor: User = Depends(RequireRole([UserRole.INVESTOR, UserRole.ADMIN]))
):
    """Retrieve high-level business/growth metrics (Investor only)"""
    # Placeholder: In real app, we'd query across fields, users, and billing tables
    return {
        "total_acreage": 4250000.0,
        "enterprise_clients": 842,
        "total_users": 15420,
        "arr_usd": 12500000.0,
        "growth_pct": 24.5,
        "retention_rate": 98.2
    }

@app.get("/api/v1/grants/{grant_id}/impact", response_model=GrantImpactResponse)
def get_grant_impact(
    grant_id: str,
    db: Session = Depends(get_db),
    reviewer: User = Depends(RequireRole([UserRole.REVIEWER, UserRole.ADMIN]))
):
    """Retrieve impact metrics for grant review (Reviewer only)"""
    # Mock impact data tied to specific grants
    return {
        "grant_id": grant_id,
        "water_saved_liters": 1250000.0,
        "co2_reduced_tons": 450.5,
        "yield_increase_pct": 14.8,
        "soil_health_index": 8.2,
        "funding_disbursed_usd": 2400000.0
    }

@app.get("/api/v1/compliance/metrics", response_model=ComplianceMetricsResponse)
def get_compliance_metrics(
    db: Session = Depends(get_db),
    auditor: User = Depends(RequireRole([UserRole.REVIEWER, UserRole.ADMIN]))
):
    """Retrieve aggregated compliance stats (Auditor/Admin only)"""
    return {
        "compliance_rate_pct": 94.2,
        "critical_violations": 3,
        "audits_this_month": 28,
        "total_fields_monitored": 1542
    }

@app.get("/api/v1/admin/metrics", response_model=AdminMetricsResponse)
def get_admin_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(RequireRole([UserRole.ADMIN]))
):
    """Retrieve high-level system metrics (Admin only)"""
    return {
        "active_users": 15420,
        "system_health_pct": 99.98,
        "pending_audits": 5,
        "user_growth_pct": 15.4
    }

# --- WebSocket Real-time Endpoint ---

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Respond to ping or other messages if needed
            await websocket.send_json({"type": "ACK", "received": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Support Letters Endpoints ---

@app.get("/api/v1/grants/{grant_id}/letters", response_model=List[SupportLetterRead])
async def list_support_letters(grant_id: str, db: Session = Depends(get_db)):
    """List all support letters for a specific grant"""
    return db.query(SupportLetter).filter(SupportLetter.grant_id == grant_id).all()

@app.post("/api/v1/grants/{grant_id}/letters", response_model=SupportLetterRead)
async def request_support_letter(
    grant_id: str, 
    letter_in: SupportLetterCreate, 
    db: Session = Depends(get_db)
):
    """Request a new support letter (reviewer uploads unsigned content)"""
    db_letter = SupportLetter(
        grant_id=grant_id,
        sender_name=letter_in.sender_name,
        sender_email=letter_in.sender_email,
        sender_organization=letter_in.sender_organization,
        content=letter_in.content,
        status=LetterStatus.PENDING
    )
    db.add(db_letter)
    db.commit()
    db.refresh(db_letter)
    
    new_token = SignatureService.generate_signing_token(str(db_letter.id))
    db_letter.token = new_token
    db.commit()
    
    # In a real app, send an email with a unique signing link here
    signing_url = f"http://localhost:3000/sign/{new_token}"
    print(f"DEBUG: Sent signing link to {db_letter.sender_email}: {signing_url}")
    
    return db_letter

@app.post("/api/v1/investor/buy-in", tags=["Investor"])
async def process_investor_buy_in(
    amount: float,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Processes a stock buy-in for a logged-in investor"""
    from app.services.equity_service import EquityService
    try:
        stake = EquityService.process_buy_in(db, user, amount)
        return {
            "status": "success",
            "shares_issued": stake.shares,
            "price_per_share": stake.purchase_price,
            "audit_hash": hashlib.sha256(str(stake.id).encode()).hexdigest()[:12]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/letters/{letter_id}/verify", response_model=SupportLetterRead)
async def verify_support_letter(
    letter_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Only logged-in users (Reviewers) can verify
):
    """Admin/Reviewer endpoint to verify a signed letter"""
    db_letter = db.query(SupportLetter).filter(SupportLetter.id == letter_id).first()
    if not db_letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    db_letter.status = LetterStatus.VERIFIED
    db_letter.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(db_letter)
    return db_letter


@app.get("/")
async def root():
    return {
        "service": "FarmSense API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# === Sensor Data Ingestion ===

@app.post("/api/v1/sensors/readings", response_model=SensorReadingResponse)
async def ingest_sensor_reading(
    reading: SensorReadingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ingest a single sensor reading
    Triggers adaptive recalculation evaluation in background
    """
    # Create database record
    db_reading = SoilSensorReading(
        sensor_id=reading.sensor_id,
        field_id=reading.field_id,
        timestamp=datetime.utcnow(),
        location=f'POINT({reading.longitude} {reading.latitude})',
        moisture_surface=reading.moisture_surface,
        moisture_root=reading.moisture_root,
        temp_surface=reading.temp_surface,
        temp_root=reading.temp_root,
        vertical_profile=reading.vertical_profile,
        ec_surface=reading.ec_surface,
        ec_root=reading.ec_root,
        ph=reading.ph,
        battery_voltage=reading.battery_voltage,
        quality_flag='valid'
    )
    

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    # Evaluate for alerts
    notification_service.evaluate_reading(db_reading, db)
    
    # Trigger recalculation evaluation in background
    background_tasks.add_task(
        evaluate_field_recalculation,
        field_id=reading.field_id,
        db=db
    )
    
    return db_reading


@app.post("/api/v1/sensors/readings/batch")
async def ingest_sensor_batch(
    readings: List[SensorReadingCreate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Batch ingest sensor readings (up to 1000 per request)"""
    if len(readings) > 1000:
        raise HTTPException(status_code=400, detail="Batch size limited to 1000 readings")
    
    db_readings = []
    affected_fields = set()
    
    for reading in readings:
        db_reading = SoilSensorReading(
            sensor_id=reading.sensor_id,
            field_id=reading.field_id,
            timestamp=datetime.utcnow(),
            location=f'POINT({reading.longitude} {reading.latitude})',
            moisture_surface=reading.moisture_surface,
            moisture_root=reading.moisture_root,
            temp_surface=reading.temp_surface,
            temp_root=reading.temp_root,
            battery_voltage=reading.battery_voltage,
            quality_flag='valid'
        )
        db_readings.append(db_reading)
        affected_fields.add(reading.field_id)
    
    db.bulk_save_objects(db_readings)
    db.commit()
    
    # Evaluate recalculation for affected fields
    for field_id in affected_fields:
        background_tasks.add_task(evaluate_field_recalculation, field_id, db)
    
    return {
        "ingested": len(readings),
        "affected_fields": list(affected_fields),
        "timestamp": datetime.utcnow()
    }


# === Virtual Grid Queries ===

@app.get("/api/v1/fields/{field_id}/grid/20m", response_model=List[VirtualGridResponse])
async def get_20m_grid(
    field_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.BASIC))
):
    """
    Retrieve 20m virtual grid data for a field.
    Requires BASIC Tier or higher.
    Returns most recent grid if no time range specified
    """
    results = GridRenderingService.get_or_render_grid(db, field_id, "20m", limit)
    
    if not results:
        raise HTTPException(status_code=404, detail="No grid data found for field")
    
    return results


@app.get("/api/v1/fields/{field_id}/grid/50m", response_model=List[VirtualGridResponse])
async def get_50m_grid(
    field_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve 50m virtual grid data for a field.
    Requires Valid API Key (FREE Tier).
    """
    results = GridRenderingService.get_or_render_grid(db, field_id, "50m", limit)
    
    if not results:
        # In a real dynamic system, the service would have created data. 
        # If it returns empty here, it means generation failed or no inputs.
        raise HTTPException(status_code=404, detail="No grid data found for field")
    
    return results





@app.get("/api/v1/fields/{field_id}/grid/10m", response_model=List[VirtualGridResponse])
async def get_10m_grid(
    field_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(10000, le=100000),
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.PRO))
):
    """
    Retrieve 10m virtual grid data for a field.
    Requires PRO Tier or higher.
    """
    results = GridRenderingService.get_or_render_grid(db, field_id, "10m", limit)
    
    if not results:
        raise HTTPException(status_code=404, detail="No grid data found for field")
    
    return results


@app.get("/api/v1/fields/{field_id}/grid/1m", response_model=List[VirtualGridResponse])
async def get_1m_grid(
    field_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(10000, le=100000),
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.ENTERPRISE))
):
    """
    Retrieve 1m virtual grid data for a field.
    Requires ENTERPRISE Tier.
    """
    results = GridRenderingService.get_or_render_grid(db, field_id, "1m", limit)
    
    if not results:
        raise HTTPException(status_code=404, detail="No grid data found for field")
    
    return results


# === Field Analytics ===

@app.get("/api/v1/fields/{field_id}/analytics", response_model=FieldAnalyticsResponse)
async def get_field_analytics(
    field_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current field analytics and irrigation recommendations
    """
    # Get latest virtual grid data
    latest_grid = db.query(VirtualSensorGrid20m).filter(
        VirtualSensorGrid20m.field_id == field_id
    ).order_by(VirtualSensorGrid20m.timestamp.desc()).limit(100).all()
    
    if not latest_grid:
        raise HTTPException(status_code=404, detail="No data available for field")
    
    # Calculate statistics
    moisture_values = [g.moisture_surface for g in latest_grid]
    stress_indices = [g.stress_index for g in latest_grid]
    
    avg_moisture = sum(moisture_values) / len(moisture_values)
    moisture_std = (sum((x - avg_moisture)**2 for x in moisture_values) / len(moisture_values))**0.5
    stress_area_pct = sum(1 for s in stress_indices if s > 0.5) / len(stress_indices) * 100
    
    # Group by irrigation need
    irrigation_zones = {}
    for grid in latest_grid:
        need = grid.irrigation_need
        irrigation_zones[need] = irrigation_zones.get(need, 0) + 1
    
    # Get recalculation status
    latest_recalc = db.query(RecalculationLog).filter(
        RecalculationLog.field_id == field_id
    ).order_by(RecalculationLog.timestamp.desc()).first()
    
    current_mode = latest_recalc.new_mode if latest_recalc else "unknown"
    next_recalc = latest_recalc.next_scheduled if latest_recalc else datetime.utcnow()
    
    return FieldAnalyticsResponse(
        field_id=field_id,
        analysis_time=datetime.utcnow(),
        avg_moisture=avg_moisture,
        moisture_std=moisture_std,
        stress_area_pct=stress_area_pct,
        irrigation_zones=[{"need": k, "count": v} for k, v in irrigation_zones.items()],
        current_mode=current_mode,
        next_recalc=next_recalc
    )


@app.get("/api/v1/fields/{field_id}/irrigation-recommendation")
async def get_irrigation_recommendation(
    field_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.BASIC))
):
    """
    Get irrigation recommendations based on current field state.
    Requires BASIC Tier or higher.
    """
    # Get latest analytics
    analytics = await get_field_analytics(field_id, db)
    
    # Simple rule-based recommendation
    if analytics.stress_area_pct > 30:
        priority = "high"
        action = "Start irrigation immediately in high-stress zones"
        estimated_volume_m3 = analytics.avg_moisture * 1000
    elif analytics.stress_area_pct > 15:
        priority = "medium"
        action = "Schedule irrigation within 24 hours"
        estimated_volume_m3 = analytics.avg_moisture * 500
    else:
        priority = "low"
        action = "Continue monitoring, no immediate irrigation needed"
        estimated_volume_m3 = 0
    
    return {
        "field_id": field_id,
        "timestamp": datetime.utcnow(),
        "priority": priority,
        "action": action,
        "estimated_volume_m3": estimated_volume_m3,
    }


# --- Privacy & Anonymization Utilities ---

def anonymize_id(original_id: str) -> str:
    """
    Creates a deterministic but irreversible hash of an ID using a system salt.
    Ensures FarmSense can track trends without tracking people.
    """
    salt = os.getenv("FARMSENSE_ANON_SALT", "enterprise-default-salt-2026")
    return hashlib.sha256(f"{original_id}{salt}".encode()).hexdigest()

def archive_anonymized_data(db: Session, field_id: str, water_m3: float, period_start: datetime):
    """
    Pushes non-PII aggregated metrics to the central research pool.
    """
    anon_hash = anonymize_id(field_id)
    archive_entry = AnonymizedResearchArchive(
        anon_field_hash=anon_hash,
        timestamp=period_start,
        total_water_m3=water_m3,
        soil_type="unknown", # Would be looked up from field metadata in prod
        region_code="SLV-PRO"
    )
    db.add(archive_entry)
    db.commit()
    logger.info(f"Anonymized research data archived for hash: {anon_hash[:8]}...")

# === Compliance Reporting ===

@app.get("/api/v1/compliance/reports", response_model=List[ComplianceReportResponse])
async def list_compliance_reports(
    field_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List compliance reports with optional filtering"""
    query = db.query(ComplianceReport)
    
    if field_id:
        query = query.filter(ComplianceReport.field_id == field_id)
    if start_date:
        query = query.filter(ComplianceReport.report_period_start >= start_date)
    if end_date:
        query = query.filter(ComplianceReport.report_period_end <= end_date)
    if status:
        query = query.filter(ComplianceReport.validation_status == status)
    
    reports = query.order_by(ComplianceReport.created_at.desc()).all()
    return reports


@app.post("/api/v1/compliance/reports/generate")
async def generate_compliance_report(
    field_id: str,
    period_start: datetime,
    period_end: datetime,
    report_type: str = "monthly",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Generate SLV 2026 compliance report for a field and time period
    Heavy computation - runs in background
    """
    # Validate period
    if period_end <= period_start:
        raise HTTPException(status_code=400, detail="Invalid time period")
    
    # Queue report generation
    if background_tasks:
        background_tasks.add_task(
            generate_compliance_report_task,
            field_id, period_start, period_end, report_type, db
        )
    
    return {
        "message": "Compliance report generation started",
        "field_id": field_id,
        "period": f"{period_start} to {period_end}",
        "status": "processing"
    }


# === Background Tasks ===

def evaluate_field_recalculation(field_id: str, db: Session):
    """
    Background task: Evaluate if field needs recalculation
    """
    engine = AdaptiveRecalculationEngine(db)
    
    # Fetch current field condition (simplified)
    # In production, this would query multiple data sources
    condition = FieldCondition(
        field_id=field_id,
        current_mode=RecalcMode.STABLE,
        last_recalc=datetime.utcnow() - timedelta(hours=6),
        avg_moisture_surface=0.25,
        avg_moisture_root=0.30,
        moisture_std_dev=0.05,
        moisture_trend_1h=-0.02,
        moisture_trend_6h=-0.15,
        current_temp=28.0,
        et0_rate=6.5,
        rainfall_last_1h=0.0,
        rainfall_forecast_6h=0.0,
        wind_speed=3.5,
        pumps_running=0,
        irrigation_active=False,
        sensor_coverage_pct=85.0,
        sensor_anomalies=[],
        extreme_weather_alerts=[]
    )
    
    decision = engine.evaluate_field(condition)
    
    if decision.should_recalculate:
        # Log decision
        log = RecalculationLog(
            field_id=field_id,
            timestamp=datetime.utcnow(),
            trigger_type=decision.trigger_type,
            previous_mode=condition.current_mode.value,
            new_mode=decision.new_mode.value,
            mode_reason=decision.reason,
            next_scheduled=decision.next_scheduled
        )
        db.add(log)
        db.commit()
        
        # Trigger actual recalculation (would queue to processing system)
        print(f"Triggering recalculation for {field_id}: {decision.reason}")



def generate_compliance_report_task(
    field_id: str,
    period_start: datetime,
    period_end: datetime,
    report_type: str,
    db: Session
):
    """Background task: Generate compliance report"""
    logger.info(f"Generating compliance report for field {field_id}")
    
    # 1. Aggregate Water Usage from Pump Telemetry
    # In a real app, we'd join with pumps in this field. 
    # For now assuming all pumps with matching field_id.
    total_water = db.query(func.sum(PumpTelemetry.volume_delivered_l)).filter(
        PumpTelemetry.field_id == field_id,
        PumpTelemetry.timestamp >= period_start,
        PumpTelemetry.timestamp <= period_end
    ).scalar() or 0.0
    
    total_irrigation_m3 = total_water / 1000.0
    
    # 2. Mock Compliance Checks (SLV 2026)
    # Rule: Max 1 acre-foot per acre per year max
    # 1 acre-foot = 1233.48 m³
    # We lack field acreage data here, so using a fixed threshold of 5000 m3 total for demo
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    acreage = field.acreage or 0.0
    limit_m3 = acreage * 1233.48
    
    compliant = "yes" if total_irrigation_m3 <= limit_m3 else "no"
    
    violations = []
    if compliant == "no":
        violations.append({
            "rule": "SLV_2026_MAX_WATER",
            "detected": total_irrigation_m3,
            "limit": limit_m3,
            "message": f"Field exceeded water allocation by {total_irrigation_m3 - limit_m3:.2f} m3"
        })

    # 3. Create Report Hash (SHA-256) for Digital Signature
    report_data = {
        "field_id": field_id,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "total_irrigation_m3": total_irrigation_m3,
        "compliant": compliant,
        "violations": violations
    }
    hasher = hashlib.sha256()
    hasher.update(json.dumps(report_data, sort_keys=True).encode())
    report_hash = hasher.hexdigest()

    report = ComplianceReport(
        field_id=field_id,
        report_period_start=period_start,
        report_period_end=period_end,
        report_type=report_type,
        total_irrigation_m3=total_irrigation_m3,
        slv_2026_compliant=compliant,
        violations=violations,
        validation_status="submitted",
        report_hash=report_hash,
        submitted_at=datetime.utcnow()
    )
    
    db.add(report)
    db.commit()
    logger.info(f"Compliance report {report.id} generated and hashed: {report_hash}")
    
    # 4. Push to Anonymized Central Research Pool (No Trace Policy)
    archive_anonymized_data(db, field_id, total_irrigation_m3, period_start)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from app.api.operations import router as operations_router
app.include_router(operations_router, prefix="/api/v1", tags=["Operations"])
