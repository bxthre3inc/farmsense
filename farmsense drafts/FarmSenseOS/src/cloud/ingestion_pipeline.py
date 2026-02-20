"""
FarmSense OS v1.0 - Data Ingestion Pipeline

Receives data from:
- Enterprise: Jetson Nano cloud mirrors (via secure API)
- Cloud tiers: Direct sensor connections (LoRa gateways)

All data archived immediately upon receipt.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import json

from archive_engine import ArchiveEngine, ArchiveEntry
from tenant_manager import TenantManager


@dataclass
class IngestionBatch:
    """Batch of sensor data for ingestion."""
    tenant_id: str
    field_id: str
    source_type: str  # 'jetson_mirror', 'cloud_gateway', 'direct_sensor'
    measurements: List[Dict]
    received_at: str
    jetson_id: Optional[str] = None  # For enterprise tier


class IngestionPipeline:
    """
    Central ingestion pipeline for all FarmSense data.
    Handles both enterprise (Jetson) and cloud (direct) data sources.
    """
    
    def __init__(
        self,
        archive_engine: ArchiveEngine,
        tenant_manager: TenantManager
    ):
        self.archive = archive_engine
        self.tenants = tenant_manager
        self.batch_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.processing_task = asyncio.create_task(self._process_loop())
        
        # Metrics
        self.metrics = {
            'total_batches_received': 0,
            'total_measurements_archived': 0,
            'enterprise_batches': 0,
            'cloud_batches': 0
        }
    
    async def ingest_from_jetson(
        self,
        jetson_id: str,
        tenant_id: str,
        payload: Dict
    ) -> Dict:
        """
        Ingest data from enterprise Jetson Nano cloud mirror.
        
        Payload format from Jetson:
        {
            'batch_id': 'uuid',
            'jetson_id': 'jetson_001',
            'field_id': 'field_001',
            'measurements': [...],
            'signatures': {...},
            'previous_hash': 'sha256:...'
        }
        """
        # Verify tenant exists and is enterprise tier
        tenant = await self.tenants.get_tenant(tenant_id)
        if tenant['tier'] != 'enterprise':
            return {'error': 'Jetson ingestion only for enterprise tier'}
        
        # Verify Jetson ownership
        if tenant.get('hardware', {}).get('jetson_id') != jetson_id:
            return {'error': 'Jetson not registered to tenant'}
        
        batch = IngestionBatch(
            tenant_id=tenant_id,
            field_id=payload['field_id'],
            source_type='jetson_mirror',
            measurements=payload['measurements'],
            received_at=datetime.utcnow().isoformat(),
            jetson_id=jetson_id
        )
        
        await self.batch_queue.put(batch)
        self.metrics['enterprise_batches'] += 1
        
        return {
            'status': 'queued',
            'batch_id': payload.get('batch_id'),
            'queue_position': self.batch_queue.qsize()
        }
    
    async def ingest_from_cloud_gateway(
        self,
        gateway_id: str,
        tenant_id: str,
        measurements: List[Dict]
    ) -> Dict:
        """
        Ingest data from cloud tier LoRa gateway.
        Used for free and paid tiers (direct sensor connections).
        """
        tenant = await self.tenants.get_tenant(tenant_id)
        
        # Determine field from first measurement
        field_id = measurements[0].get('field_id', 'default')
        
        batch = IngestionBatch(
            tenant_id=tenant_id,
            field_id=field_id,
            source_type='cloud_gateway',
            measurements=measurements,
            received_at=datetime.utcnow().isoformat()
        )
        
        await self.batch_queue.put(batch)
        self.metrics['cloud_batches'] += 1
        
        return {
            'status': 'queued',
            'measurements_received': len(measurements),
            'queue_position': self.batch_queue.qsize()
        }
    
    async def _process_loop(self):
        """Background processing loop."""
        while True:
            try:
                batch = await self.batch_queue.get()
                await self._process_batch(batch)
                self.batch_queue.task_done()
            except Exception as e:
                # Log error, continue processing
                print(f"Ingestion error: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch: IngestionBatch):
        """Process a single ingestion batch."""
        tenant = await self.tenants.get_tenant(batch.tenant_id)
        
        for measurement in batch.measurements:
            # Create archive entry
            entry = ArchiveEntry(
                timestamp=measurement['timestamp'],
                tenant_id=batch.tenant_id,
                field_id=batch.field_id,
                sensor_id=measurement['sensor_id'],
                measurement_type=measurement['type'],
                value=measurement['value'],
                unit=measurement.get('unit', 'vwc_percent'),
                depth_inches=measurement.get('depth_inches'),
                latitude=measurement.get('latitude', 0.0),
                longitude=measurement.get('longitude', 0.0),
                data_hash=measurement.get('data_hash', ''),
                signature=measurement.get('signature', ''),
                tier=tenant['tier']
            )
            
            # Archive immediately (forensic requirement)
            await self.archive.archive_measurement(entry)
            self.metrics['total_measurements_archived'] += 1
        
        self.metrics['total_batches_received'] += 1
    
    async def get_metrics(self) -> Dict:
        """Get ingestion pipeline metrics."""
        return {
            **self.metrics,
            'queue_depth': self.batch_queue.qsize(),
            'timestamp': datetime.utcnow().isoformat()
        }


class JetsonMirrorProtocol:
    """
    Protocol for enterprise Jetson Nano to cloud mirror synchronization.
    
    Each enterprise Jetson maintains a live mirror on the cloud server.
    On Jetson failure, cloud mirror can immediately take over.
    """
    
    def __init__(self, ingestion_pipeline: IngestionPipeline):
        self.ingestion = ingestion_pipeline
        self.active_mirrors: Dict[str, Dict] = {}  # jetson_id -> mirror info
    
    async def register_mirror(
        self,
        jetson_id: str,
        tenant_id: str,
        field_ids: List[str]
    ) -> Dict:
        """Register a new Jetson cloud mirror."""
        self.active_mirrors[jetson_id] = {
            'tenant_id': tenant_id,
            'field_ids': field_ids,
            'registered_at': datetime.utcnow().isoformat(),
            'last_heartbeat': datetime.utcnow().isoformat(),
            'status': 'active',
            'takeover_ready': True
        }
        
        return {
            'mirror_id': f"mirror_{jetson_id}",
            'endpoint': f"wss://api.farmsense.zo.computer/mirror/{jetson_id}",
            'status': 'registered'
        }
    
    async def heartbeat(
        self,
        jetson_id: str,
        status: Dict
    ) -> Dict:
        """Receive heartbeat from Jetson."""
        if jetson_id not in self.active_mirrors:
            return {'error': 'Mirror not registered'}
        
        mirror = self.active_mirrors[jetson_id]
        mirror['last_heartbeat'] = datetime.utcnow().isoformat()
        mirror['status'] = 'active'
        
        # Check for failover conditions
        if status.get('failover_initiated'):
            mirror['status'] = 'jetson_failing_over'
            return {'action': 'prepare_takeover'}
        
        return {'action': 'continue'}
    
    async def initiate_failover(self, jetson_id: str) -> Dict:
        """
        Initiate cloud takeover from failed Jetson.
        Called when heartbeat timeout detected.
        """
        if jetson_id not in self.active_mirrors:
            return {'error': 'Mirror not found'}
        
        mirror = self.active_mirrors[jetson_id]
        mirror['status'] = 'cloud_primary'
        
        # Notify tenant of failover
        return {
            'status': 'failover_complete',
            'mirror_id': f"mirror_{jetson_id}",
            'previous_jetson': jetson_id,
            'current_primary': 'cloud',
            'cold_spare_action': 'contact_farmer_for_swap'
        }
    
    async def restore_jetson(
        self,
        jetson_id: str,
        new_jetson_id: Optional[str] = None
    ) -> Dict:
        """
        Restore primary Jetson after repair/swap.
        Cloud mirror syncs state back to new Jetson.
        """
        mirror = self.active_mirrors.get(jetson_id)
        if not mirror:
            return {'error': 'No mirror found'}
        
        # Get archived data since failure
        # (In production, query archive engine)
        
        return {
            'status': 'jetson_restored',
            'sync_required': True,
            'data_to_sync': 'since_failover_timestamp'
        }


# FastAPI endpoints for cloud server
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="FarmSense Cloud API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Global instances (in production, use dependency injection)
ingestion_pipeline: Optional[IngestionPipeline] = None
mirror_protocol: Optional[JetsonMirrorProtocol] = None


@app.post("/ingest/jetson/{jetson_id}")
async def ingest_jetson_data(
    jetson_id: str,
    payload: Dict,
    token: str = Depends(oauth2_scheme)
):
    """Endpoint for Jetson Nano cloud mirror to push data."""
    # Validate token, extract tenant_id
    tenant_id = "extracted_from_token"  # Simplified
    
    result = await ingestion_pipeline.ingest_from_jetson(
        jetson_id, tenant_id, payload
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@app.post("/ingest/gateway/{gateway_id}")
async def ingest_gateway_data(
    gateway_id: str,
    measurements: List[Dict],
    token: str = Depends(oauth2_scheme)
):
    """Endpoint for LoRa gateways to push sensor data."""
    tenant_id = "extracted_from_token"
    
    result = await ingestion_pipeline.ingest_from_cloud_gateway(
        gateway_id, tenant_id, measurements
    )
    
    return result


@app.websocket("/mirror/{jetson_id}")
async def mirror_websocket(websocket: WebSocket, jetson_id: str):
    """WebSocket for real-time Jetson-to-cloud sync."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'heartbeat':
                response = await mirror_protocol.heartbeat(jetson_id, data)
                await websocket.send_json(response)
                
            elif data.get('type') == 'measurements':
                # Process measurement batch
                pass
                
    except Exception as e:
        await websocket.close()


@app.post("/mirror/{jetson_id}/failover")
async def trigger_failover(jetson_id: str):
    """Admin endpoint to trigger failover manually."""
    result = await mirror_protocol.initiate_failover(jetson_id)
    return result
