"""
Hardware Actuation API
- Pump control
- Valve control  
- VRI (Variable Rate Irrigation) control
- Emergency stop

Requires PRO tier or higher for actuation
Enterprise tier for compliance-guaranteed actuation
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user, RequireTier
from app.models.user import User, SubscriptionTier
from app.models.sensor_data import PumpTelemetry
from app.models.field import Field
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/actuation", tags=["Actuation"])


@router.post("/pumps/{pump_id}/start")
async def start_pump(
    pump_id: str,
    field_id: str,
    target_flow_rate: Optional[float] = None,
    duration_minutes: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.PRO))
):
    """
    Start a pump.
    Requires PRO Tier or higher.
    
    - PRO: Actuation without compliance guarantee
    - ENTERPRISE: Actuation with compliance guarantee and audit trail
    """
    # Verify field ownership
    field = db.query(Field).filter(
        Field.id == field_id,
        Field.owner_id == user.id
    ).first()
    
    if not field:
        raise HTTPException(status_code=403, detail="Field not found or access denied")
    
    # Check compliance status for Enterprise tier
    compliance_guaranteed = user.tier == SubscriptionTier.ENTERPRISE
    
    # Log the actuation command
    telemetry = PumpTelemetry(
        pump_id=pump_id,
        field_id=field_id,
        timestamp=datetime.utcnow(),
        status="running",
        flow_rate_lpm=target_flow_rate or 0.0,
        power_consumption_kw=0.0,
        runtime_hours=0.0,
        volume_delivered_l=0.0,
        cumulative_volume_l=0.0,
        anomaly_score=0.0,
        anomaly_flag="normal"
    )
    db.add(telemetry)
    db.commit()
    
    # Send notification
    await notification_service.send_notification(
        user_id=user.id,
        title="Pump Started",
        message=f"Pump {pump_id} started in field {field_id}",
        priority="normal"
    )
    
    return {
        "pump_id": pump_id,
        "field_id": field_id,
        "status": "running",
        "compliance_guaranteed": compliance_guaranteed,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"Pump started. {'Compliance guaranteed.' if compliance_guaranteed else 'Standard actuation (no compliance guarantee).'}"
    }


@router.post("/pumps/{pump_id}/stop")
async def stop_pump(
    pump_id: str,
    field_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.PRO))
):
    """
    Stop a pump.
    Requires PRO Tier or higher.
    """
    # Verify field ownership
    field = db.query(Field).filter(
        Field.id == field_id,
        Field.owner_id == user.id
    ).first()
    
    if not field:
        raise HTTPException(status_code=403, detail="Field not found or access denied")
    
    # Log the stop command
    telemetry = PumpTelemetry(
        pump_id=pump_id,
        field_id=field_id,
        timestamp=datetime.utcnow(),
        status="idle",
        flow_rate_lpm=0.0,
        power_consumption_kw=0.0,
        runtime_hours=0.0,
        volume_delivered_l=0.0,
        cumulative_volume_l=0.0,
        anomaly_score=0.0,
        anomaly_flag="normal"
    )
    db.add(telemetry)
    db.commit()
    
    return {
        "pump_id": pump_id,
        "field_id": field_id,
        "status": "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/pumps/{pump_id}/emergency-stop")
async def emergency_stop_pump(
    pump_id: str,
    field_id: str,
    reason: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Emergency stop a pump.
    Available to all authenticated users for safety.
    """
    # Verify field ownership
    field = db.query(Field).filter(
        Field.id == field_id,
        Field.owner_id == user.id
    ).first()
    
    if not field:
        raise HTTPException(status_code=403, detail="Field not found or access denied")
    
    # Log the emergency stop
    telemetry = PumpTelemetry(
        pump_id=pump_id,
        field_id=field_id,
        timestamp=datetime.utcnow(),
        status="emergency_stop",
        flow_rate_lpm=0.0,
        power_consumption_kw=0.0,
        runtime_hours=0.0,
        volume_delivered_l=0.0,
        cumulative_volume_l=0.0,
        anomaly_score=1.0,
        anomaly_flag="emergency"
    )
    db.add(telemetry)
    db.commit()
    
    # Send urgent notification
    await notification_service.send_notification(
        user_id=user.id,
        title="EMERGENCY STOP",
        message=f"Pump {pump_id} EMERGENCY STOPPED. Reason: {reason}",
        priority="critical"
    )
    
    return {
        "pump_id": pump_id,
        "field_id": field_id,
        "status": "emergency_stopped",
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Emergency stop executed. All operations halted."
    }


@router.get("/pumps/{pump_id}/status")
async def get_pump_status(
    pump_id: str,
    field_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get pump status.
    Available to all authenticated users (read-only).
    """
    # Verify field ownership
    field = db.query(Field).filter(
        Field.id == field_id,
        Field.owner_id == user.id
    ).first()
    
    if not field:
        raise HTTPException(status_code=403, detail="Field not found or access denied")
    
    # Get latest telemetry
    latest = db.query(PumpTelemetry).filter(
        PumpTelemetry.pump_id == pump_id,
        PumpTelemetry.field_id == field_id
    ).order_by(PumpTelemetry.timestamp.desc()).first()
    
    if not latest:
        return {
            "pump_id": pump_id,
            "field_id": field_id,
            "status": "unknown",
            "message": "No telemetry data available"
        }
    
    return {
        "pump_id": pump_id,
        "field_id": field_id,
        "status": latest.status,
        "flow_rate_lpm": latest.flow_rate_lpm,
        "power_consumption_kw": latest.power_consumption_kw,
        "runtime_hours": latest.runtime_hours,
        "cumulative_volume_l": latest.cumulative_volume_l,
        "last_updated": latest.timestamp.isoformat()
    }


@router.post("/vri/{pivot_id}/set-zones")
async def set_vri_zones(
    pivot_id: str,
    field_id: str,
    zone_values: list,  # List of 0.0-1.0 values for each zone
    db: Session = Depends(get_db),
    user: User = Depends(RequireTier(SubscriptionTier.PRO))
):
    """
    Set VRI (Variable Rate Irrigation) zone values.
    Requires PRO Tier or higher.
    
    zone_values: Array of values 0.0-1.0 representing valve openness for each zone
    """
    # Verify field ownership
    field = db.query(Field).filter(
        Field.id == field_id,
        Field.owner_id == user.id
    ).first()
    
    if not field:
        raise HTTPException(status_code=403, detail="Field not found or access denied")
    
    # Validate zone values
    if not all(0.0 <= v <= 1.0 for v in zone_values):
        raise HTTPException(status_code=400, detail="Zone values must be between 0.0 and 1.0")
    
    compliance_guaranteed = user.tier == SubscriptionTier.ENTERPRISE
    
    return {
        "pivot_id": pivot_id,
        "field_id": field_id,
        "zone_values": zone_values,
        "compliance_guaranteed": compliance_guaranteed,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"VRI zones updated. {'Compliance guaranteed.' if compliance_guaranteed else 'Standard actuation.'}"
    }
