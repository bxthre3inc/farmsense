from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.api.main import get_db
from app.models.devices import HardwareDevice as Device, DeviceType

router = APIRouter(prefix="/api/v1/integration", tags=["Vendor Integration"])

# --- Schemas ---
class TelemetryPayload(BaseModel):
    external_id: str
    timestamp: datetime
    data: Dict[str, Any]
    battery_level: Optional[float] = None

class MissionUpdate(BaseModel):
    external_id: str
    status: str
    path_data: Optional[List[Dict[str, float]]] = None
    coverage_area_m2: Optional[float] = None
    report: Optional[Dict[str, Any]] = None

# --- Endpoints ---

@router.post("/telemetry")
async def ingest_vendor_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    """Standardized endpoint for third-party sensors and machinery to push data"""
    device = db.query(Device).filter(Device.serial_number == payload.external_id).first()
    if not device:
        # Auto-registration for known vendors (simplified)
        raise HTTPException(status_code=404, detail="Device not registered. Please register device via portal first.")
    
    device.last_communication = payload.timestamp
    if payload.battery_level is not None:
        device.battery_voltage = payload.battery_level
        
    db.commit()
    return {"status": "success", "received_at": datetime.utcnow()}

@router.post("/robotics/mission")
async def update_robotics_mission(payload: MissionUpdate, db: Session = Depends(get_db)):
    """Endpoint for autonomous robots to report mission progress/completion"""
    device = db.query(Device).filter(Device.serial_number == payload.external_id).first()
    if not device:
        raise HTTPException(status_code=400, detail="Invalid robotics device ID")
    
    return {"status": "mission_updated"}

@router.get("/devices", response_model=List[dict])
async def list_registered_devices(field_id: str, db: Session = Depends(get_db)):
    """Headless access to list all integrated hardware on a field"""
    devices = db.query(Device).filter(Device.field_id == field_id).all()
    return [{"id": str(d.id), "serial_number": d.serial_number, "type": d.device_type.value, "status": d.status.value} for d in devices]
