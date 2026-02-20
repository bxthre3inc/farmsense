"""
Real WebSocket Manager for Live Data Streaming
Handles actual sensor data ingestion and broadcasting
"""
from typing import Dict, List, Set, Optional
from datetime import datetime
import json
import asyncio
import logging
from sqlalchemy.orm import Session

from app.models.sensor_data import SoilSensorReading
from app.models.field import DeviceMapping
from app.services.notification_service import notification_service
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections by field and user"""
    
    def __init__(self):
        # Field_id -> Set of WebSocket connections
        self.field_connections: Dict[str, Set] = {}
        # Connection -> User metadata
        self.connection_metadata: Dict = {}
        # Device_id -> Last reading timestamp (for dedup)
        self.device_last_seen: Dict[str, datetime] = {}
    
    async def connect(self, websocket, field_id: str, user_id: str = None):
        """Register new WebSocket connection"""
        await websocket.accept()
        
        if field_id not in self.field_connections:
            self.field_connections[field_id] = set()
        
        self.field_connections[field_id].add(websocket)
        self.connection_metadata[websocket] = {
            "field_id": field_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow()
        }
        
        logger.info(f"WebSocket connected: field={field_id}, user={user_id}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "field_id": field_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket):
        """Remove WebSocket connection"""
        metadata = self.connection_metadata.get(websocket)
        if metadata:
            field_id = metadata["field_id"]
            if field_id in self.field_connections:
                self.field_connections[field_id].discard(websocket)
                
                # Clean up empty field entries
                if not self.field_connections[field_id]:
                    del self.field_connections[field_id]
            
            del self.connection_metadata[websocket]
            logger.info(f"WebSocket disconnected: field={field_id}")
    
    async def broadcast_to_field(self, field_id: str, message: dict):
        """Broadcast message to all connections for a field"""
        if field_id not in self.field_connections:
            return
        
        disconnected = set()
        
        for connection in self.field_connections[field_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket: {e}")
                disconnected.add(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast to all connected clients"""
        for field_id in list(self.field_connections.keys()):
            await self.broadcast_to_field(field_id, message)
    
    def get_connection_stats(self) -> dict:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.connection_metadata),
            "fields_monitored": len(self.field_connections),
            "connections_by_field": {
                field_id: len(conns) 
                for field_id, conns in self.field_connections.items()
            }
        }


class DataIngestionService:
    """Handles incoming sensor data ingestion"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.batch_queue = []
        self.batch_size = 100
        self.batch_interval_seconds = 5
        self._batch_task = None
    
    async def start_batch_processor(self):
        """Start background batch processing"""
        self._batch_task = asyncio.create_task(self._batch_processor_loop())
    
    async def _batch_processor_loop(self):
        """Process batched writes to database"""
        while True:
            await asyncio.sleep(self.batch_interval_seconds)
            
            if self.batch_queue:
                await self._flush_batch()
    
    async def _flush_batch(self):
        """Write queued data to database"""
        if not self.batch_queue:
            return
        
        batch = self.batch_queue[:self.batch_size]
        self.batch_queue = self.batch_queue[self.batch_size:]
        
        db = SessionLocal()
        try:
            for reading_data in batch:
                reading = SoilSensorReading(**reading_data)
                db.add(reading)
                
                # Check for alerts
                notification_service.evaluate_reading(reading, db)
            
            db.commit()
            logger.info(f"Flushed {len(batch)} readings to database")
        except Exception as e:
            db.rollback()
            logger.error(f"Batch write failed: {e}")
        finally:
            db.close()
    
    async def ingest_sensor_reading(self, data: dict) -> dict:
        """
        Ingest a single sensor reading
        
        Args:
            data: Sensor reading with device_id, field_id, readings, etc.
        
        Returns:
            Processing result with status
        """
        device_id = data.get("device_id")
        field_id = data.get("field_id")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())
        
        # Deduplication check
        if device_id in self.manager.device_last_seen:
            last_seen = self.manager.device_last_seen[device_id]
            current = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if (current - last_seen).total_seconds() < 60:  # 1 minute dedup
                return {"status": "duplicate", "device_id": device_id}
        
        self.manager.device_last_seen[device_id] = datetime.fromisoformat(
            timestamp.replace('Z', '+00:00')
        )
        
        # Prepare reading data
        reading_data = {
            "sensor_id": device_id,
            "field_id": field_id,
            "timestamp": timestamp,
            "location": f"POINT({data.get('lon', 0)} {data.get('lat', 0)})",
            "moisture_surface": data.get("moisture_surface"),
            "moisture_root": data.get("moisture_root"),
            "temp_surface": data.get("temp_surface"),
            "temp_root": data.get("temp_root"),
            "battery_voltage": data.get("battery_voltage"),
            "quality_flag": "valid"
        }
        
        # Add to batch queue
        self.batch_queue.append(reading_data)
        
        # Broadcast to connected clients
        await self.manager.broadcast_to_field(field_id, {
            "type": "SENSOR_READING",
            "timestamp": timestamp,
            "data": {
                "sensor_id": device_id,
                "moisture_surface": reading_data["moisture_surface"],
                "moisture_root": reading_data["moisture_root"],
                "temp_surface": reading_data["temp_surface"],
                "battery_voltage": reading_data["battery_voltage"]
            }
        })
        
        # Flush if batch is full
        if len(self.batch_queue) >= self.batch_size:
            await self._flush_batch()
        
        return {
            "status": "accepted",
            "device_id": device_id,
            "queued_position": len(self.batch_queue)
        }
    
    async def ingest_bulk_readings(self, readings: List[dict]) -> dict:
        """
        Ingest multiple sensor readings (for LRZ batch uploads)
        """
        results = []
        for reading in readings:
            result = await self.ingest_sensor_reading(reading)
            results.append(result)
        
        accepted = sum(1 for r in results if r["status"] == "accepted")
        duplicates = sum(1 for r in results if r["status"] == "duplicate")
        
        return {
            "status": "complete",
            "total": len(readings),
            "accepted": accepted,
            "duplicates": duplicates
        }
    
    async def handle_device_status(self, device_id: str, status: dict):
        """Handle device status/heartbeat messages"""
        field_id = status.get("field_id")
        
        # Update device last seen
        self.manager.device_last_seen[device_id] = datetime.utcnow()
        
        # Broadcast status to field
        await self.manager.broadcast_to_field(field_id, {
            "type": "DEVICE_STATUS",
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": {
                "battery_level": status.get("battery_level"),
                "signal_strength": status.get("signal_strength"),
                "firmware_version": status.get("firmware_version"),
                "uptime_seconds": status.get("uptime_seconds")
            }
        })
    
    async def handle_alert(self, device_id: str, alert: dict):
        """Handle device-generated alerts (PFA emergency stops, etc.)"""
        field_id = alert.get("field_id")
        
        # Broadcast alert immediately
        await self.manager.broadcast_to_field(field_id, {
            "type": "DEVICE_ALERT",
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": alert.get("severity", "warning"),
            "message": alert.get("message"),
            "action_required": alert.get("action_required", False)
        })
        
        # Also send to admin connections
        await self.manager.broadcast_to_all({
            "type": "ADMIN_ALERT",
            "source_field": field_id,
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": alert.get("severity"),
            "message": alert.get("message")
        })


# Global instances
manager = ConnectionManager()
ingestion_service = DataIngestionService(manager)
