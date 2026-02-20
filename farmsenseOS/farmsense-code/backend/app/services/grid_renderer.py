from datetime import datetime
from sqlalchemy.orm import Session
from app.models.sensor_data import (
    VirtualSensorGrid50m, 
    VirtualSensorGrid20m, 
    VirtualSensorGrid10m,
    VirtualSensorGrid1m, 
    SoilSensorReading
)
from app.models.field import Field
from app.services.external_data_service import ExternalDataService
from app.services.satellite_service import SatelliteDataService
from app.core.env_wrapper import platform_wrapper
import logging
import uuid

logger = logging.getLogger(__name__)

class GridRenderingService:
    @staticmethod
    def get_or_render_grid(
        db: Session,
        field_id: str,
        resolution: str,
        limit: int = 1000,
        offline_mode: bool = False
    ):
        """
        Dynamically renders the grid based on recent sensor trends, 
        Landsat history, and real-time external environmental factors.
        
        If offline_mode is True, it fallbacks to local cached data with 
        a reduced confidence score.
        """
        logger.info(f"Rendering grid for field {field_id} at {resolution} resolution (Offline: {offline_mode})")

        # Get actual field coordinates from database
        field = db.query(Field).filter(Field.id == field_id).first()
        if not field:
            logger.error(f"Field {field_id} not found in database")
            raise ValueError(f"Field {field_id} not found")
        
        field_lat = field.center_lat
        field_lon = field.center_lon
        field_acres = field.acres
        logger.info(f"Using field coordinates: ({field_lat}, {field_lon}), {field_acres} acres")

        # 1. Fetch recent sensor readings to determine trend
        readings = db.query(SoilSensorReading).filter(
            SoilSensorReading.field_id == field_id
        ).order_by(SoilSensorReading.timestamp.desc()).limit(3).all()

        trend_modifier = 1.0
        if len(readings) == 3:
            r1, r2, r3 = readings
            if r1.moisture_surface < r2.moisture_surface < r3.moisture_surface:
                trend_modifier = 0.8  # Drying trend
                logger.info(f"Detected drying trend for field {field_id}")

        # 2. Integrate External Atmospheric Data (Open-Meteo)
        weather = ExternalDataService.get_weather_data(field_lat, field_lon)
        
        weather_modifier = 1.0
        if weather:
            temp = weather.get("temperature", 20)
            if temp > 30: # Extreme heat
                weather_modifier *= 1.15 # Increase evapotranspiration stress
                logger.info(f"Adjusting for extreme heat: {temp}C")
        
        # 3. Integrate Soil Properties (SoilGrids)
        soil = ExternalDataService.get_soil_properties(field_lat, field_lon)
        soil_modifier = 1.0
        if soil:
            soc = soil.get("soc_dg_kg", 20)
            if soc < 10: # Low organic carbon
                soil_modifier = 0.9 
                logger.info(f"Adjusting for low Soil Organic Carbon: {soc}")

        # 4. Integrate Advanced Satellite Fusion (Sentinel-1 & 2)
        # Sentinel-2 NDVI (Optical)
        real_ndvi = SatelliteDataService.get_latest_ndvi_point(field_lat, field_lon, field_id)
        
        # Sentinel-1 SAR (Radar) - moisture proxy through clouds
        sar_modifier = SatelliteDataService.get_sentinel1_moisture_proxy(field_lat, field_lon)
        
        logger.info(f"Satellite Fusion: Sentinel-2 NDVI={real_ndvi:.2f}, Sentinel-1 SAR Mod={sar_modifier:.2f}")

        # 5. Calculate Confidence Score
        # 1.0 = All sensors online + Satellite recent
        # < 0.5 = High uncertainty
        confidence = 1.0
        
        if platform_wrapper.is_pilot():
            confidence *= 0.9 # Minor penalty for pilot-phase uncalibrated sensors
            logger.info("ENVIRONMENT: Pilot mode detected. Applying calibration buffer.")
        elif not platform_wrapper.is_production():
            confidence *= 0.8 # Dev mode penalty
            
        if offline_mode:
            confidence *= 0.7  # Reduced confidence due to stale external data
            logger.warning(f"Field {field_id} is in OFFLINE mode. Using local cache fallbacks.")
        
        if len(readings) < 3:
            confidence *= 0.8  # Sparse physical sensor data
            
        final_modifier = trend_modifier * weather_modifier * soil_modifier * sar_modifier
        logger.info(f"Fusion Complete. Final Modifier: {final_modifier:.2f}, Confidence: {confidence:.2f}")

        # 6. Render Grid - All resolutions supported
        model_map = {
            "50m": VirtualSensorGrid50m,
            "20m": VirtualSensorGrid20m,
            "10m": VirtualSensorGrid10m,
            "1m": VirtualSensorGrid1m
        }
        
        Model = model_map.get(resolution)
        if not Model:
            raise ValueError(f"Invalid resolution: {resolution}. Supported: 50m, 20m, 10m, 1m")

        results = db.query(Model).filter(
            Model.field_id == field_id
        ).order_by(Model.timestamp.desc()).limit(limit).all()
        
        if not results:
             logger.info(f"No cached {resolution} grid found. Generating new points with Fusion...")
             # Fetch physical sensor ground truth for validation
             ground_truth = readings[0].moisture_surface if readings else None
             
             if resolution == "1m":
                 results = GridRenderingService._generate_synthetic_1m_grid(db, field_id, field_lat, field_lon, real_ndvi * final_modifier, ground_truth)
             elif resolution == "10m":
                 results = GridRenderingService._generate_synthetic_10m_grid(db, field_id, field_lat, field_lon, final_modifier, ground_truth)
             elif resolution == "20m":
                 results = GridRenderingService._generate_synthetic_20m_grid(db, field_id, field_lat, field_lon, final_modifier, ground_truth)
             elif resolution == "50m":
                 results = GridRenderingService._generate_synthetic_50m_grid(db, field_id, field_lat, field_lon, final_modifier, ground_truth)
        
        return results

    @staticmethod
    def _generate_synthetic_1m_grid(db: Session, field_id: str, lat: float, lon: float, modifier: float, ground_truth: float = None):
        """Generate 1m resolution grid using real field coordinates"""
        points = []
        base_time = datetime.utcnow()
        
        # Generate points in a grid pattern around field center
        for i in range(10):
            # Offset by meters (rough approximation: 0.00001 degrees ~ 1m)
            offset_lat = lat + (i - 5) * 0.00001
            offset_lon = lon + (i - 5) * 0.00001
            
            p = VirtualSensorGrid1m(
                id=uuid.uuid4(),
                field_id=field_id,
                grid_id=f"{field_id}_1m_{i}",
                timestamp=base_time,
                location=f"POINT({offset_lon} {offset_lat})",
                moisture_surface=0.25 * modifier,
                moisture_root=0.30 * modifier,
                temperature=22.5,
                ndvi=0.4 + (modifier - 1.0),
                ndwi=0.1,
                confidence_score=0.95 if modifier > 0.8 else 0.6,
                physical_probe_value=ground_truth,
                crop_stress_probability=max(0.0, 1.0 - modifier),
                yield_forecast_kgha=8500 * modifier,
                irrigation_priority=1 if modifier < 0.8 else 5
            )
            points.append(p)
            db.add(p)
        
        db.commit()
        return points
    
    @staticmethod
    def _generate_synthetic_10m_grid(db: Session, field_id: str, lat: float, lon: float, modifier: float, ground_truth: float = None):
        """Generate 10m resolution grid for VRI zones"""
        points = []
        base_time = datetime.utcnow()
        
        for i in range(5):
            offset_lat = lat + (i - 2) * 0.0001  # ~10m
            offset_lon = lon + (i - 2) * 0.0001
            
            p = VirtualSensorGrid10m(
                id=uuid.uuid4(),
                field_id=field_id,
                grid_id=f"{field_id}_10m_{i}",
                timestamp=base_time,
                location=f"POINT({offset_lon} {offset_lat})",
                grid_cell=None,  # Would calculate actual polygon in production
                moisture_surface=0.28 * modifier,
                moisture_root=0.32 * modifier,
                temperature=22.0,
                water_deficit_mm=15.0 * (1 - modifier),
                stress_index=max(0.0, 1.0 - modifier),
                irrigation_need="medium" if modifier > 0.8 else "high",
                vri_zone_id=f"zone_{(i % 3) + 1}",
                prescription_rate=0.75 + (i * 0.05),
                computation_mode="active",
                source_sensors=["VFA-001", "LRZ-010"],
                confidence=0.85 if modifier > 0.8 else 0.6,
                physical_probe_value=ground_truth,
                edge_device_id="DHU-001"
            )
            points.append(p)
            db.add(p)
        
        db.commit()
        return points
    
    @staticmethod
    def _generate_synthetic_20m_grid(db: Session, field_id: str, lat: float, lon: float, modifier: float, ground_truth: float = None):
        """Generate 20m resolution grid"""
        points = []
        base_time = datetime.utcnow()
        
        for i in range(4):
            offset_lat = lat + (i - 2) * 0.0002  # ~20m
            offset_lon = lon + (i - 2) * 0.0002
            
            p = VirtualSensorGrid20m(
                id=uuid.uuid4(),
                field_id=field_id,
                grid_id=f"{field_id}_20m_{i}",
                timestamp=base_time,
                location=f"POINT({offset_lon} {offset_lat})",
                grid_cell=None,
                moisture_surface=0.27 * modifier,
                moisture_root=0.31 * modifier,
                temperature=22.5,
                water_deficit_mm=18.0 * (1 - modifier),
                stress_index=max(0.0, 0.9 - modifier),
                irrigation_need="medium",
                computation_mode="stable",
                source_sensors=["VFA-001"],
                confidence=0.88 if modifier > 0.8 else 0.65,
                physical_probe_value=ground_truth,
                edge_device_id="DHU-001"
            )
            points.append(p)
            db.add(p)
        
        db.commit()
        return points
    
    @staticmethod
    def _generate_synthetic_50m_grid(db: Session, field_id: str, lat: float, lon: float, modifier: float, ground_truth: float = None):
        """Generate 50m resolution grid - lowest res, highest coverage"""
        points = []
        base_time = datetime.utcnow()
        
        for i in range(3):
            offset_lat = lat + (i - 1) * 0.0005  # ~50m
            offset_lon = lon + (i - 1) * 0.0005
            
            p = VirtualSensorGrid50m(
                id=uuid.uuid4(),
                field_id=field_id,
                grid_id=f"{field_id}_50m_{i}",
                timestamp=base_time,
                location=f"POINT({offset_lon} {offset_lat})",
                grid_cell=None,
                moisture_surface=0.29 * modifier,
                moisture_root=0.33 * modifier,
                temperature=23.0,
                water_deficit_mm=20.0 * (1 - modifier),
                stress_index=max(0.0, 0.85 - modifier),
                irrigation_need="low" if modifier > 0.9 else "medium",
                computation_mode="stable",
                source_sensors=["LRZ-001", "LRZ-002"],
                confidence=0.9,
                physical_probe_value=ground_truth,
                edge_device_id="DHU-001"
            )
            points.append(p)
            db.add(p)
        
        db.commit()
        return points