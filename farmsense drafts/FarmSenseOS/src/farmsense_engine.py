"""
FarmSense OS v1.0 - Main Engine

Central orchestration layer coordinating:
- Sensor data ingestion
- Bayesian inference
- Regression Kriging interpolation
- Cloud synchronization
- VRI valve control
- Forensic integrity
- API serving

Hub-and-spoke topology: 1 Jetson Nano serves 9 fields.
Each Jetson has dedicated gateway hub.
Cloud mirror provides instant failover.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import signal
import sys

# Import our modules
from models.sensor import SensorNetwork, SensorType, Sensor
from models.measurement import Measurement, BatchMeasurement
from models.soil_map import SoilVariabilityMap, SoilTexture
from persistence.timeseries import TimeSeriesStore, VirtualGridStore
from persistence.sync import CloudSyncProtocol, SystemState
from engine.bayesian.filter import RecursiveBayesianFilter
from engine.kriging.regression_kriging import RegressionKrigingEngine, KrigingCell
from forensic.integrity import ForensicHasher, AuditLogger, create_measurement_with_integrity
from vri.controller import VRIController, ZoneIrrigationDecision, IrrigationZoneStatus
from api.research_api import ResearchAPI


@dataclass
class EngineConfig:
    """Configuration for FarmSense Engine instance."""
    # Identity
    jetson_id: str
    hub_field_id: str
    spoke_field_ids: List[str]
    
    # Hardware
    gateway_hub_id: str
    has_cold_spare: bool = True
    
    # Cloud
    cloud_endpoint: str = "https://cloud.farmsense.io"
    api_key: str = ""
    
    # Timing
    measurement_interval_minutes: int = 15
    kriging_interval_minutes: int = 15
    
    # Storage
    data_dir: str = "/var/farmsense/data"
    retention_months: int = 24
    
    # VRI
    modbus_host: str = "192.168.1.100"
    enable_valve_control: bool = True


class FarmSenseEngine:
    """
    Main orchestration engine for FarmSense OS.
    
    Coordinates the complete data flow:
    1. Sensor ingestion (every 15 minutes)
    2. Bayesian prediction/update
    3. Kriging interpolation (1-meter grid)
    4. VRI valve control
    5. Cloud synchronization
    6. Forensic integrity maintenance
    
    Handles failover to cloud mirror when primary fails,
    and cold spare activation for extended outages.
    """
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self.running = False
        self.start_time: Optional[datetime] = None
        
        # Component instances
        self.sensor_network: Optional[SensorNetwork] = None
        self.timeseries_store: Optional[TimeSeriesStore] = None
        self.grid_store: Optional[VirtualGridStore] = None
        self.bayesian_filter: Optional[RecursiveBayesianFilter] = None
        self.kriging_engine: Optional[RegressionKrigingEngine] = None
        self.vri_controller: Optional[VRIController] = None
        self.cloud_sync: Optional[CloudSyncProtocol] = None
        self.hasher: Optional[ForensicHasher] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.research_api: Optional[ResearchAPI] = None
        
        # State tracking
        self.last_measurement_time: Optional[datetime] = None
        self.last_kriging_time: Optional[datetime] = None
        self.total_measurements_processed = 0
        self.total_grids_generated = 0
        
        # Failover state
        self.is_cloud_controlled = False
        self.failover_start_time: Optional[datetime] = None
        
        # Statistics
        self.statistics = {
            'measurements_processed': 0,
            'bayesian_updates': 0,
            'grids_generated': 0,
            'irrigation_decisions': 0,
            'deep_percolation_alerts': 0,
            'uptime_hours': 0.0
        }
    
    async def initialize(self) -> bool:
        """
        Initialize all engine components.
        
        Returns True if all components initialized successfully.
        """
        print(f"FarmSense Engine v1.0 initializing on Jetson {self.config.jetson_id}...")
        
        try:
            # 1. Initialize forensic layer first (critical for integrity)
            print("  Initializing forensic integrity layer...")
            self.hasher = ForensicHasher(signing_key=self.config.api_key[:32])
            self.audit_logger = AuditLogger(log_dir=f"{self.config.data_dir}/audit")
            
            # 2. Initialize persistence
            print("  Initializing persistence layer...")
            self.timeseries_store = TimeSeriesStore(
                db_path=f"{self.config.data_dir}/measurements.db"
            )
            self.grid_store = VirtualGridStore(
                db_path=f"{self.config.data_dir}/virtual_grid.db"
            )
            
            # 3. Initialize sensor network
            print("  Initializing sensor network...")
            self.sensor_network = SensorNetwork(network_id=self.config.jetson_id)
            self._configure_pilot_sensors()
            
            # 4. Initialize inference engines
            print("  Initializing Bayesian filter...")
            self.bayesian_filter = RecursiveBayesianFilter(
                update_threshold=0.03,
                learning_rate=0.05
            )
            
            print("  Initializing Kriging engine...")
            self.kriging_engine = RegressionKrigingEngine(grid_resolution_meters=1.0)
            
            # 5. Initialize VRI controller
            print("  Initializing VRI controller...")
            self.vri_controller = VRIController(
                modbus_host=self.config.modbus_host,
                audit_logger=self.audit_logger
            )
            
            # 6. Initialize cloud synchronization
            print("  Initializing cloud sync...")
            self.cloud_sync = CloudSyncProtocol(
                jetson_id=self.config.jetson_id,
                cloud_endpoint=self.config.cloud_endpoint,
                api_key=self.config.api_key,
                heartbeat_interval=5.0,
                failover_timeout=30.0
            )
            self.cloud_sync.on_failover(self._handle_cloud_failover)
            
            # 7. Initialize research API
            print("  Initializing research API...")
            self.research_api = ResearchAPI(
                timeseries_store=self.timeseries_store,
                grid_store=self.grid_store,
                audit_logger=self.audit_logger
            )
            
            # Log initialization
            self.audit_logger.log_event(
                event_type='engine_initialized',
                user_id='system',
                details={
                    'jetson_id': self.config.jetson_id,
                    'fields': [self.config.hub_field_id] + self.config.spoke_field_ids,
                    'sensor_count': len(self.sensor_network.sensors)
                }
            )
            
            print(f"  Initialization complete. Managing {len(self.sensor_network.sensors)} sensors across {1 + len(self.config.spoke_field_ids)} fields.")
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def _configure_pilot_sensors(self) -> None:
        """Configure sensors for 9-field pilot deployment."""
        all_fields = [self.config.hub_field_id] + self.config.spoke_field_ids
        
        for i, field_id in enumerate(all_fields):
            # Add horizontal blankets (~11 per field)
            for j in range(11):
                sensor_id = f"{field_id}_hb_{j:02d}"
                lat = 37.5 + i * 0.01 + j * 0.0005
                lon = -105.8 + j * 0.001
                
                sensor = Sensor(
                    sensor_id=sensor_id,
                    sensor_type=SensorType.HORIZONTAL_BLANKET_MEDIUM,
                    field_id=field_id,
                    latitude=lat,
                    longitude=lon,
                    installed_depths_inches=[12, 18]
                )
                self.sensor_network.add_sensor(sensor)
            
            # Add master nail (1 per field)
            master_id = f"{field_id}_master"
            master_lat = 37.5 + i * 0.01 + 0.005
            master_lon = -105.8 + 0.005
            
            # Alternate between 42" and 60" based on crop
            is_deep_crop = i % 3 == 0  # Every 3rd field has alfalfa
            sensor_type = (
                SensorType.MASTER_VERTICAL_60IN if is_deep_crop
                else SensorType.MASTER_VERTICAL_42IN
            )
            depths = [18, 24, 30, 36, 42, 52, 60] if is_deep_crop else [18, 24, 30, 36, 42]
            
            master = Sensor(
                sensor_id=master_id,
                sensor_type=sensor_type,
                field_id=field_id,
                latitude=master_lat,
                longitude=master_lon,
                installed_depths_inches=depths
            )
            self.sensor_network.add_sensor(master)
    
    async def run(self) -> None:
        """Main engine run loop."""
        if not await self.initialize():
            print("Engine failed to initialize. Exiting.")
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        print(f"\nFarmSense Engine started at {self.start_time.isoformat()}")
        print(f"Monitoring {len(self.sensor_network.sensors)} sensors every {self.config.measurement_interval_minutes} minutes.")
        
        # Connect to cloud
        cloud_connected = await self.cloud_sync.connect()
        print(f"Cloud sync: {'Connected' if cloud_connected else 'Offline mode'}")
        
        # Schedule tasks
        measurement_task = asyncio.create_task(self._measurement_loop())
        kriging_task = asyncio.create_task(self._kriging_loop())
        cloud_sync_task = asyncio.create_task(self._cloud_sync_loop())
        
        # Wait for shutdown signal
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            # Cancel tasks
            measurement_task.cancel()
            kriging_task.cancel()
            cloud_sync_task.cancel()
            
            await self.shutdown()
    
    async def _measurement_loop(self) -> None:
        """Background task: collect sensor measurements."""
        while self.running:
            try:
                await self._collect_and_process_measurements()
                self.last_measurement_time = datetime.utcnow()
                
                # Wait for next interval
                await asyncio.sleep(self.config.measurement_interval_minutes * 60)
                
            except Exception as e:
                print(f"Measurement loop error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    async def _collect_and_process_measurements(self) -> None:
        """Collect measurements from all sensors and process."""
        print(f"\n[{datetime.utcnow().isoformat()}] Collecting measurements...")
        
        measurements = []
        previous_hash = self.timeseries_store.get_last_hash()
        
        # Simulate sensor readings (in production, read from LoRa gateway)
        for sensor in self.sensor_network.sensors:
            for depth in sensor.installed_depths_inches:
                # Simulate VWC reading (would come from actual sensor)
                vwc = self._simulate_sensor_reading(sensor, depth)
                
                measurement = create_measurement_with_integrity(
                    sensor_id=sensor.sensor_id,
                    depth_inches=depth,
                    vwc=vwc,
                    previous_hash=previous_hash,
                    soil_temp_c=15.0 + (20 - depth) * 0.2,  # Simulated
                    signer_key=self.config.api_key[:32]
                )
                
                measurements.append(measurement)
                previous_hash = measurement['measurement_hash']
        
        # Store in time-series database
        stored_count = self.timeseries_store.store_batch({
            'measurements': measurements,
            'batch_hash': '',  # Computed by store
            'timestamp': datetime.utcnow().isoformat()
        })
        
        print(f"  Stored {stored_count} measurements.")
        self.total_measurements_processed += stored_count
        self.statistics['measurements_processed'] += stored_count
        
        # Run Bayesian update
        await self._run_bayesian_update(measurements)
        
        # Sync to cloud
        for measurement in measurements:
            await self.cloud_sync.sync_measurement(
                measurement['measurement_hash'],
                measurement
            )
    
    def _simulate_sensor_reading(self, sensor: Sensor, depth: int) -> float:
        """Simulate a sensor reading for testing."""
        import random
        
        # Base VWC varies by depth
        if depth <= 18:
            base = 0.22  # Surface tends to be drier
        elif depth <= 42:
            base = 0.25  # Root zone
        else:
            base = 0.28  # Deep layer
        
        # Add some realistic variation
        variation = random.gauss(0, 0.03)
        
        # Master nails read slightly different
        if sensor.sensor_type in [SensorType.MASTER_VERTICAL_42IN, SensorType.MASTER_VERTICAL_60IN]:
            base += 0.01
        
        return max(0.05, min(0.45, base + variation))
    
    async def _run_bayesian_update(self, measurements: List[Dict]) -> None:
        """Run Bayesian filter update on new measurements."""
        # Group by field
        by_field: Dict[str, List[Dict]] = {}
        for m in measurements:
            sensor = self.sensor_network.get_sensor(m['sensor_id'])
            if sensor:
                if sensor.field_id not in by_field:
                    by_field[sensor.field_id] = []
                by_field[sensor.field_id].append({
                    'sensor_id': m['sensor_id'],
                    'field_id': sensor.field_id,
                    'depth_inches': m['depth_inches'],
                    'latitude': sensor.latitude,
                    'longitude': sensor.longitude,
                    'vwc': m['volumetric_water_content']
                })
        
        # Process each field
        for field_id, field_measurements in by_field.items():
            results = self.bayesian_filter.process_batch(
                measurements=field_measurements,
                et_rate_mm_day=5.0,  # Would come from weather service
                hours_since_last=0.25  # 15 minutes
            )
            
            self.statistics['bayesian_updates'] += results['stats']['updates_triggered']
    
    async def _kriging_loop(self) -> None:
        """Background task: generate virtual grids."""
        while self.running:
            try:
                await self._generate_all_grids()
                self.last_kriging_time = datetime.utcnow()
                
                # Wait for next interval
                await asyncio.sleep(self.config.kriging_interval_minutes * 60)
                
            except Exception as e:
                print(f"Kriging loop error: {e}")
                await asyncio.sleep(60)
    
    async def _generate_all_grids(self) -> None:
        """Generate 1-meter virtual grids for all fields."""
        print(f"\n[{datetime.utcnow().isoformat()}] Generating virtual grids...")
        
        all_fields = [self.config.hub_field_id] + self.config.spoke_field_ids
        
        for field_id in all_fields:
            # Get recent measurements for this field
            recent_measurements = list(self.timeseries_store.get_measurements(
                start_time=datetime.utcnow() - timedelta(hours=1),
                limit=1000
            ))
            
            # Filter to this field
            field_sensors = [s.sensor_id for s in self.sensor_network.sensors if s.field_id == field_id]
            field_measurements = [m for m in recent_measurements if m.get('sensor_id') in field_sensors]
            
            if not field_measurements:
                continue
            
            # Generate grid for 18" depth (primary irrigation depth)
            grid_cells = self.kriging_engine.generate_virtual_grid(
                field_id=field_id,
                field_bounds=(37.5, -105.8, 37.6, -105.7),  # Would be actual field bounds
                sensor_measurements=field_measurements,
                satellite_trend=None,  # Would be actual satellite trend function
                depth_inches=18
            )
            
            # Store grid
            self.grid_store.store_grid({
                'field_id': field_id,
                'timestamp': datetime.utcnow().isoformat(),
                'cells': [{
                    'cell_id': c.cell_id,
                    'field_id': c.field_id,
                    'latitude': c.latitude,
                    'longitude': c.longitude,
                    'depth_inches': c.depth_inches,
                    'estimated_vwc': c.estimated_vwc,
                    'estimation_variance': c.estimation_variance,
                    'confidence': c.confidence,
                    'is_hard_anchor': c.is_hard_anchor,
                    'cell_hash': c.cell_hash
                } for c in grid_cells]
            })
            
            # Make VRI decision
            await self._make_vri_decision(field_id, grid_cells)
            
            self.total_grids_generated += 1
            self.statistics['grids_generated'] += 1
        
        print(f"  Generated grids for {len(all_fields)} fields.")
    
    async def _make_vri_decision(self, field_id: str, grid_cells: List[KrigingCell]) -> None:
        """Make irrigation decision based on virtual grid."""
        # Simple single-zone per field for now
        decision = self.vri_controller.analyze_zone_for_irrigation(
            zone_id=f"{field_id}_zone1",
            field_id=field_id,
            grid_cells=grid_cells,
            soil_properties={'field_capacity': 0.25, 'wilting_point': 0.08},
            crop_type='potato'
        )
        
        # Check for deep percolation risk
        if decision.status == IrrigationZoneStatus.DEEP_PERCOLATION_RISK:
            print(f"  ALERT: Deep percolation risk in {field_id}!")
            self.statistics['deep_percolation_alerts'] += 1
            
            # Emergency stop
            self.vri_controller.emergency_stop_all(user_id='system')
        
        self.statistics['irrigation_decisions'] += 1
    
    async def _cloud_sync_loop(self) -> None:
        """Background task: synchronize state to cloud."""
        while self.running:
            try:
                # Build system state
                state = SystemState(
                    jetson_id=self.config.jetson_id,
                    timestamp=datetime.utcnow(),
                    soil_map_state={},
                    bayesian_coefficients=self.bayesian_filter.get_state_dict() if self.bayesian_filter else {},
                    last_prediction={},
                    last_measurement_hash=self.timeseries_store.get_last_hash() if self.timeseries_store else "0" * 64,
                    total_records=self.total_measurements_processed,
                    latest_grid_timestamp=self.last_kriging_time.isoformat() if self.last_kriging_time else None,
                    grid_merkle_root=None,
                    active_sensors=[s.sensor_id for s in self.sensor_network.sensors] if self.sensor_network else [],
                    sensor_health={},
                    active_valves=self.vri_controller.get_active_irrigation() if self.vri_controller else {},
                    scheduled_irrigation=[]
                )
                
                # Sync to cloud
                await self.cloud_sync.sync_state(state)
                
                # Wait before next sync
                await asyncio.sleep(30)  # Sync every 30 seconds
                
            except Exception as e:
                print(f"Cloud sync error: {e}")
                await asyncio.sleep(60)
    
    def _handle_cloud_failover(self) -> None:
        """Handle failover to cloud mirror."""
        print("\n*** FAILOVER TO CLOUD MIRROR ***")
        self.is_cloud_controlled = True
        self.failover_start_time = datetime.utcnow()
        
        # Log the event
        self.audit_logger.log_event(
            event_type='failover_to_cloud',
            user_id='system',
            details={
                'jetson_id': self.config.jetson_id,
                'reason': 'heartbeat_timeout',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Stop local actuation (cloud takes over)
        # VRI control transitions to cloud via cellular modem
    
    async def shutdown(self) -> None:
        """Graceful shutdown."""
        print("\nShutting down FarmSense Engine...")
        
        # Log shutdown
        if self.audit_logger:
            uptime = (datetime.utcnow() - self.start_time).total_seconds() / 3600 if self.start_time else 0
            self.audit_logger.log_event(
                event_type='engine_shutdown',
                user_id='system',
                details={
                    'uptime_hours': uptime,
                    'measurements_processed': self.total_measurements_processed,
                    'grids_generated': self.total_grids_generated
                }
            )
        
        # Disconnect from cloud
        if self.cloud_sync:
            await self.cloud_sync.disconnect()
        
        # Close stores
        # (SQLite connections close automatically)
        
        print("Shutdown complete.")
    
    def get_status(self) -> Dict:
        """Get current engine status."""
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds() / 3600
        
        return {
            'jetson_id': self.config.jetson_id,
            'status': 'running' if self.running else 'stopped',
            'uptime_hours': uptime,
            'cloud_sync_state': self.cloud_sync.state.name if self.cloud_sync else 'unknown',
            'is_cloud_controlled': self.is_cloud_controlled,
            'statistics': self.statistics,
            'last_measurement': self.last_measurement_time.isoformat() if self.last_measurement_time else None,
            'last_kriging': self.last_kriging_time.isoformat() if self.last_kriging_time else None
        }


# === Entry Point ===

def main():
    """Main entry point for FarmSense Engine."""
    
    # Create configuration for 9-field pilot
    config = EngineConfig(
        jetson_id="jetson_hub_001",
        hub_field_id="field_01",
        spoke_field_ids=[f"field_{i:02d}" for i in range(2, 10)],
        gateway_hub_id="gateway_001",
        cloud_endpoint="https://cloud.farmsense.io",
        api_key="dev_key_placeholder",
        measurement_interval_minutes=15,
        kriging_interval_minutes=15
    )
    
    # Create and run engine
    engine = FarmSenseEngine(config)
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal.")
        engine.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    asyncio.run(engine.run())


if __name__ == "__main__":
    main()
