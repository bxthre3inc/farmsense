"""
FarmSense OS v1.0 - Recursive Bayesian Filter

Core inference engine running on Jetson GPU.
Continuous validation loop evolving the field's digital twin.
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json


@dataclass
class MoistureState:
    """
    Predicted moisture state at a location.
    """
    latitude: float
    longitude: float
    depth_inches: int
    predicted_vwc: float
    prediction_variance: float
    confidence: float
    timestamp: datetime
    
    def to_array(self) -> np.ndarray:
        return np.array([self.predicted_vwc, self.prediction_variance])


@dataclass
class SoilCoefficients:
    """
    Learned soil hydraulic coefficients for a zone.
    """
    zone_id: str
    
    # Hydraulic properties
    ksat: float = 10.0  # cm/hr, saturated hydraulic conductivity
    field_capacity: float = 0.25  # v/v
    wilting_point: float = 0.08  # v/v
    
    # Texture estimate
    sand_ratio: float = 0.33
    silt_ratio: float = 0.33
    clay_ratio: float = 0.34
    
    # Uncertainty
    coefficient_variance: float = 0.1
    update_count: int = 0
    
    def to_array(self) -> np.ndarray:
        return np.array([
            self.ksat, self.field_capacity, self.wilting_point,
            self.sand_ratio, self.silt_ratio, self.clay_ratio
        ])
    
    def update_from_residual(self, residual: float, learning_rate: float = 0.05) -> None:
        """
        Bayesian update of coefficients based on prediction residual.
        
        Args:
            residual: observed - predicted (positive = wetter than expected)
            learning_rate: adaptation speed (0.0-1.0)
        """
        # Wetter than expected = slower drainage = more clay, less sand
        if abs(residual) < 0.02:  # Within 2% VWC - no update needed
            return
        
        if residual > 0:
            # Retaining more water - increase clay, decrease sand
            self.clay_ratio = min(0.6, self.clay_ratio + learning_rate * 0.05)
            self.sand_ratio = max(0.1, self.sand_ratio - learning_rate * 0.05)
        else:
            # Draining faster - increase sand, decrease clay
            self.sand_ratio = min(0.8, self.sand_ratio + learning_rate * 0.05)
            self.clay_ratio = max(0.1, self.clay_ratio - learning_rate * 0.05)
        
        # Re-normalize
        total = self.sand_ratio + self.silt_ratio + self.clay_ratio
        self.sand_ratio /= total
        self.silt_ratio /= total
        self.clay_ratio /= total
        
        # Update derived properties
        self._recalculate_hydraulics()
        
        self.update_count += 1
        self.coefficient_variance *= 0.95  # Confidence increases with updates
    
    def _recalculate_hydraulics(self) -> None:
        """Recalculate Ksat, FC, PWP from updated texture."""
        # Kozeny-Carman for Ksat
        self.ksat = 10 ** (-0.6 + 1.3 * self.sand_ratio - 0.6 * self.clay_ratio) * 100
        
        # Field capacity estimate
        self.field_capacity = 0.2576 - 0.002 * self.sand_ratio + 0.0036 * self.clay_ratio
        
        # Wilting point
        self.wilting_point = 0.026 + 0.005 * self.clay_ratio


class RecursiveBayesianFilter:
    """
    Core Bayesian inference engine for FarmSense OS.
    
    Implements continuous prediction-observation-update loop:
    1. Predict moisture state from soil map + ET data
    2. Observe sensor residuals and satellite data
    3. Update soil coefficients if error exceeds threshold
    
    Runs on Jetson GPU with CuPy acceleration.
    """
    
    def __init__(
        self,
        update_threshold: float = 0.03,  # 3% VWC error triggers update
        learning_rate: float = 0.05
    ):
        self.update_threshold = update_threshold
        self.learning_rate = learning_rate
        
        # Zone-specific learned coefficients
        self.coefficients: Dict[str, SoilCoefficients] = {}
        
        # Last prediction cache
        self.last_predictions: Dict[str, MoistureState] = {}
        
        # Statistics
        self.total_predictions = 0
        self.total_updates = 0
    
    def get_or_create_coefficients(self, zone_id: str) -> SoilCoefficients:
        """Get existing coefficients or create new ones for a zone."""
        if zone_id not in self.coefficients:
            self.coefficients[zone_id] = SoilCoefficients(zone_id=zone_id)
        return self.coefficients[zone_id]
    
    def predict(
        self,
        zone_id: str,
        latitude: float,
        longitude: float,
        depth_inches: int,
        et_rate_mm_day: float,
        hours_since_last: float,
        soil_texture: Optional[Dict] = None
    ) -> MoistureState:
        """
        Predict moisture state based on current conditions.
        
        Uses simple water balance:
        - Start from last observed/predicted VWC
        - Subtract ET losses
        - Add any irrigation (if scheduled)
        - Account for drainage based on Ksat
        """
        coeffs = self.get_or_create_coefficients(zone_id)
        
        # Get baseline VWC
        key = f"{zone_id}_{depth_inches}"
        if key in self.last_predictions:
            baseline_vwc = self.last_predictions[key].predicted_vwc
        else:
            baseline_vwc = coeffs.field_capacity
        
        # ET loss (simplified - assume 60% of ET from top 18")
        et_fraction = 0.6 if depth_inches <= 18 else 0.3 if depth_inches <= 36 else 0.1
        et_loss = (et_rate_mm_day / 24 * hours_since_last) / 1000 * et_fraction  # Convert to m/m
        
        # Drainage (if above field capacity)
        drainage = 0.0
        if baseline_vwc > coeffs.field_capacity:
            excess = baseline_vwc - coeffs.field_capacity
            # Simple drainage model: Ksat * time * gradient
            drainage = min(excess, coeffs.ksat / 100 * (hours_since_last / 24) * 0.1)
        
        # Predicted VWC
        predicted_vwc = baseline_vwc - et_loss - drainage
        predicted_vwc = max(coeffs.wilting_point, min(0.5, predicted_vwc))
        
        # Prediction uncertainty grows with time
        variance = coeffs.coefficient_variance * (1 + hours_since_last / 24)
        confidence = 1.0 / (1.0 + variance)
        
        state = MoistureState(
            latitude=latitude,
            longitude=longitude,
            depth_inches=depth_inches,
            predicted_vwc=predicted_vwc,
            prediction_variance=variance,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
        
        self.last_predictions[key] = state
        self.total_predictions += 1
        
        return state
    
    def update(
        self,
        zone_id: str,
        sensor_id: str,
        depth_inches: int,
        observed_vwc: float,
        predicted_vwc: float
    ) -> Dict:
        """
        Bayesian update based on observed vs predicted residual.
        
        Returns dict with update information.
        """
        residual = observed_vwc - predicted_vwc
        abs_error = abs(residual)
        
        update_info = {
            'zone_id': zone_id,
            'sensor_id': sensor_id,
            'depth': depth_inches,
            'observed': observed_vwc,
            'predicted': predicted_vwc,
            'residual': residual,
            'updated': False
        }
        
        # Only update if error exceeds threshold
        if abs_error > self.update_threshold:
            coeffs = self.get_or_create_coefficients(zone_id)
            coeffs.update_from_residual(residual, self.learning_rate)
            
            update_info['updated'] = True
            update_info['new_ksat'] = coeffs.ksat
            update_info['new_field_capacity'] = coeffs.field_capacity
            update_info['texture'] = {
                'sand': coeffs.sand_ratio,
                'silt': coeffs.silt_ratio,
                'clay': coeffs.clay_ratio
            }
            
            self.total_updates += 1
        
        # Update prediction cache with observed value
        key = f"{zone_id}_{depth_inches}"
        if key in self.last_predictions:
            self.last_predictions[key].predicted_vwc = observed_vwc
            self.last_predictions[key].prediction_variance *= 0.5  # Observation reduces uncertainty
        
        return update_info
    
    def process_batch(
        self,
        measurements: List[Dict],
        et_rate_mm_day: float,
        hours_since_last: float
    ) -> Dict:
        """
        Process a batch of measurements through predict-observe-update cycle.
        
        Args:
            measurements: List of measurement dicts with sensor_id, lat, lon, depth, vwc
            et_rate_mm_day: Current evapotranspiration rate
            hours_since_last: Hours since last update cycle
            
        Returns:
            Processing results with predictions, updates, and statistics
        """
        results = {
            'predictions': [],
            'updates': [],
            'stats': {
                'total_processed': 0,
                'updates_triggered': 0,
                'average_residual': 0.0
            }
        }
        
        total_residual = 0.0
        
        for measurement in measurements:
            zone_id = measurement.get('field_id', 'unknown')
            
            # Prediction phase
            prediction = self.predict(
                zone_id=zone_id,
                latitude=measurement['latitude'],
                longitude=measurement['longitude'],
                depth_inches=measurement['depth_inches'],
                et_rate_mm_day=et_rate_mm_day,
                hours_since_last=hours_since_last
            )
            
            results['predictions'].append({
                'sensor_id': measurement['sensor_id'],
                'predicted_vwc': prediction.predicted_vwc,
                'confidence': prediction.confidence
            })
            
            # Update phase
            update_result = self.update(
                zone_id=zone_id,
                sensor_id=measurement['sensor_id'],
                depth_inches=measurement['depth_inches'],
                observed_vwc=measurement['vwc'],
                predicted_vwc=prediction.predicted_vwc
            )
            
            results['updates'].append(update_result)
            
            if update_result['updated']:
                results['stats']['updates_triggered'] += 1
            
            total_residual += abs(update_result['residual'])
            results['stats']['total_processed'] += 1
        
        if results['stats']['total_processed'] > 0:
            results['stats']['average_residual'] = total_residual / results['stats']['total_processed']
        
        return results
    
    def get_state_dict(self) -> Dict:
        """Serialize current state for cloud synchronization."""
        return {
            'coefficients': {
                zone_id: {
                    'ksat': coeffs.ksat,
                    'field_capacity': coeffs.field_capacity,
                    'wilting_point': coeffs.wilting_point,
                    'sand': coeffs.sand_ratio,
                    'silt': coeffs.silt_ratio,
                    'clay': coeffs.clay_ratio,
                    'variance': coeffs.coefficient_variance,
                    'updates': coeffs.update_count
                }
                for zone_id, coeffs in self.coefficients.items()
            },
            'stats': {
                'total_predictions': self.total_predictions,
                'total_updates': self.total_updates,
                'update_rate': self.total_updates / max(1, self.total_predictions)
            }
        }
    
    def restore_state(self, state_dict: Dict) -> None:
        """Restore state from cloud synchronization."""
        for zone_id, coeffs_data in state_dict.get('coefficients', {}).items():
            coeffs = SoilCoefficients(zone_id=zone_id)
            coeffs.ksat = coeffs_data.get('ksat', coeffs.ksat)
            coeffs.field_capacity = coeffs_data.get('field_capacity', coeffs.field_capacity)
            coeffs.wilting_point = coeffs_data.get('wilting_point', coeffs.wilting_point)
            coeffs.sand_ratio = coeffs_data.get('sand', coeffs.sand_ratio)
            coeffs.silt_ratio = coeffs_data.get('silt', coeffs.silt_ratio)
            coeffs.clay_ratio = coeffs_data.get('clay', coeffs.clay_ratio)
            coeffs.coefficient_variance = coeffs_data.get('variance', coeffs.coefficient_variance)
            coeffs.update_count = coeffs_data.get('updates', 0)
            self.coefficients[zone_id] = coeffs
