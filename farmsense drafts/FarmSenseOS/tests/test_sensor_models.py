"""
FarmSense OS v1.0 - Unit Tests

Tests for core data models and functionality.
"""

import pytest
import asyncio
from datetime import datetime

import sys
sys.path.insert(0, '/home/workspace/FarmSenseOS/src')

from models.sensor import Sensor, SensorType, SensorNetwork
from models.measurement import Measurement, MeasurementBatch
from models.soil_map import SoilMap, SoilCell, SoilTexture


class TestSensorModels:
    """Test sensor entity models."""
    
    def test_blanket_sensor_creation(self):
        """Test horizontal blanket sensor creation."""
        sensor = Sensor.create_blanket(
            sensor_id="blanket_001",
            field_id="field_001",
            latitude=37.1234,
            longitude=-105.5678
        )
        
        assert sensor.sensor_id == "blanket_001"
        assert sensor.sensor_type == SensorType.HORIZONTAL_BLANKET
        assert sensor.depths_inches == [12, 18]
        assert sensor.active == True
    
    def test_master_nail_creation(self):
        """Test master vertical nail creation."""
        sensor = Sensor.create_master_nail(
            sensor_id="nail_001",
            field_id="field_001",
            latitude=37.1234,
            longitude=-105.5678,
            active_depth=42
        )
        
        assert sensor.sensor_type == SensorType.MASTER_VERTICAL_NAIL
        assert len(sensor.depths_inches) == 5  # 42" nail has 5 depths
        assert 42 in sensor.depths_inches
    
    def test_deep_nail_creation(self):
        """Test 60" deep nail for alfalfa."""
        sensor = Sensor.create_master_nail(
            sensor_id="nail_002",
            field_id="field_002",
            latitude=37.1234,
            longitude=-105.5678,
            active_depth=60
        )
        
        assert len(sensor.depths_inches) == 7  # 60" nail has 7 depths
        assert 60 in sensor.depths_inches


class TestMeasurementModels:
    """Test measurement and batch models."""
    
    def test_measurement_creation(self):
        """Test measurement with forensic hashing."""
        measurement = Measurement(
            timestamp="2026-02-10T05:30:00Z",
            sensor_id="blanket_001",
            field_id="field_001",
            tenant_id="tenant_001",
            measurement_type="vwc",
            value=23.5,
            unit="percent",
            depth_inches=12,
            latitude=37.1234,
            longitude=-105.5678
        )
        
        # Verify forensic hashing
        assert measurement.data_hash is not None
        assert len(measurement.data_hash) == 16
        assert measurement.signature is not None
    
    def test_measurement_validation(self):
        """Test measurement data validation."""
        measurement = Measurement(
            timestamp="2026-02-10T05:30:00Z",
            sensor_id="blanket_001",
            field_id="field_001",
            tenant_id="tenant_001",
            measurement_type="vwc",
            value=150.0,  # Invalid: > 100%
            unit="percent",
            depth_inches=12,
            latitude=37.1234,
            longitude=-105.5678
        )
        
        errors = measurement.validate()
        assert len(errors) > 0
        assert any("value" in str(e).lower() for e in errors)
    
    def test_batch_hash(self):
        """Test batch integrity hashing."""
        measurements = [
            Measurement(
                timestamp="2026-02-10T05:30:00Z",
                sensor_id="blanket_001",
                field_id="field_001",
                tenant_id="tenant_001",
                measurement_type="vwc",
                value=23.5,
                unit="percent",
                depth_inches=12,
                latitude=37.1234,
                longitude=-105.5678
            ),
            Measurement(
                timestamp="2026-02-10T05:30:00Z",
                sensor_id="blanket_002",
                field_id="field_001",
                tenant_id="tenant_001",
                measurement_type="vwc",
                value=21.2,
                unit="percent",
                depth_inches=12,
                latitude=37.1244,
                longitude=-105.5688
            )
        ]
        
        batch = MeasurementBatch(
            batch_id="batch_001",
            timestamp="2026-02-10T05:30:00Z",
            measurements=measurements,
            tenant_id="tenant_001",
            field_id="field_001",
            previous_hash="sha256:abc123"
        )
        
        assert batch.batch_hash is not None
        assert len(batch.measurements) == 2


class TestSoilMapModels:
    """Test soil variability models."""
    
    def test_soil_cell_creation(self):
        """Test soil cell with learned texture."""
        cell = SoilCell(
            cell_id="cell_001",
            latitude=37.1234,
            longitude=-105.5678,
            size_meters=1.0,
            initial_texture=SoilTexture.LOAM
        )
        
        assert cell.initial_texture == SoilTexture.LOAM
        assert cell.learned_texture is None  # Not yet learned
        assert cell.confidence == 1.0  # Initial confidence
    
    def test_bayesian_texture_update(self):
        """Test soil texture learning via Bayesian update."""
        cell = SoilCell(
            cell_id="cell_001",
            latitude=37.1234,
            longitude=-105.5678,
            size_meters=1.0,
            initial_texture=SoilTexture.LOAM
        )
        
        # Simulate observation suggesting sandy loam
        cell.update_from_observation(
            observed_drainage_rate=0.25,  # Faster than loam
            predicted_drainage_rate=0.15,
            confidence=0.8
        )
        
        assert cell.learned_texture == SoilTexture.SANDY_LOAM
        assert cell.confidence < 1.0  # Confidence adjusted
        assert cell.update_count == 1


class TestSensorNetwork:
    """Test sensor network topology."""
    
    def test_pilot_network_creation(self):
        """Test 9-field hub-and-spoke pilot network."""
        network = SensorNetwork.create_pilot_network()
        
        assert network.network_id == "pilot_9_field"
        assert len(network.fields) == 9
        assert len(network.sensors) == 108  # 99 blankets + 9 nails
        
        # Count by type
        blankets = [s for s in network.sensors.values() 
                   if s.sensor_type == SensorType.HORIZONTAL_BLANKET]
        nails = [s for s in network.sensors.values() 
                if s.sensor_type == SensorType.MASTER_VERTICAL_NAIL]
        
        assert len(blankets) == 99
        assert len(nails) == 9
    
    def test_measurement_point_count(self):
        """Verify ~270 measurement points for pilot."""
        network = SensorNetwork.create_pilot_network()
        
        total_points = sum(
            len(sensor.depths_inches) 
            for sensor in network.sensors.values()
        )
        
        # 99 blankets × 2 depths + 9 nails × 5-7 depths ≈ 243-261
        assert 240 <= total_points <= 270


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
