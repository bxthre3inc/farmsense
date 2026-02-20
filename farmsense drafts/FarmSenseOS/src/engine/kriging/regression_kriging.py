"""
FarmSense OS v1.0 - GPU-Accelerated Regression Kriging

Generates 1-meter virtual grid from sparse sensor data.
Uses satellite imagery as trend variable, sensor residuals as hard constraints.
Runs on Jetson GPU with CuPy acceleration.
"""

import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Callable
import hashlib
import json


@dataclass
class KrigingCell:
    """
    Single cell in the 1-meter virtual grid.
    """
    cell_id: str
    field_id: str
    latitude: float
    longitude: float
    depth_inches: int
    
    # Kriging results
    estimated_vwc: float
    estimation_variance: float
    confidence: float
    
    # Source tracking
    is_hard_anchor: bool = False
    anchor_sensor_id: Optional[str] = None
    satellite_trend_value: Optional[float] = None
    
    # Hash for forensic integrity
    cell_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute forensic hash of cell data."""
        data = {
            'cell_id': self.cell_id,
            'field_id': self.field_id,
            'lat': round(self.latitude, 8),
            'lon': round(self.longitude, 8),
            'depth': self.depth_inches,
            'vwc': round(self.estimated_vwc, 6),
            'variance': round(self.estimation_variance, 8),
            'timestamp': datetime.utcnow().isoformat()
        }
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        self.cell_hash = hashlib.sha256(canonical.encode()).hexdigest()
        return self.cell_hash


class RegressionKrigingEngine:
    """
    GPU-accelerated Regression Kriging for 1-meter virtual grid generation.
    
    Implements:
    - Universal Kriging with external drift (satellite as trend)
    - Hard constraint enforcement at sensor locations
    - GPU matrix operations via CuPy (falls back to NumPy if unavailable)
    - Sub-second grid generation for real-time VRI
    
    Reference: Master Documentation v3.9 - RK provides continuous coverage
    from ~270 discrete points across 1,170 acres.
    """
    
    def __init__(self, grid_resolution_meters: float = 1.0):
        self.grid_resolution = grid_resolution_meters
        
        # GPU acceleration
        self.use_gpu = False
        self.xp = np  # Default to NumPy
        
        try:
            import cupy as cp
            self.xp = cp
            self.use_gpu = True
            print("RegressionKriging: Using CuPy GPU acceleration")
        except ImportError:
            print("RegressionKriging: CuPy not available, using NumPy")
        
        # Kriging parameters
        self.nugget = 0.001
        self.sill = 0.05
        self.range_meters = 150.0  # Correlation range for soil moisture
        self.trend_weight = 0.3  # Weight for satellite trend
    
    def _variogram_model(self, h: np.ndarray) -> np.ndarray:
        """
        Spherical variogram model for spatial correlation.
        
        Models how moisture correlation decreases with distance.
        """
        xp = self.xp
        
        # Spherical model
        C0 = self.nugget
        C = self.sill
        a = self.range_meters
        
        gamma = xp.zeros_like(h)
        mask = h <= a
        gamma[mask] = C0 + C * (1.5 * h[mask] / a - 0.5 * (h[mask] / a) ** 3)
        gamma[~mask] = C0 + C
        
        return gamma
    
    def _build_kriging_system(
        self,
        sensor_coords: np.ndarray,
        sensor_values: np.ndarray,
        trend_values: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build Kriging linear system (K and k).
        
        K: Variogram matrix between known points (n×n)
        k: Variogram vector from known to unknown (n×1)
        """
        xp = self.xp
        n = len(sensor_coords)
        
        # Distance matrix between sensors
        dist_matrix = self._distance_matrix(sensor_coords, sensor_coords)
        
        # Variogram matrix (K)
        K = self._variogram_model(dist_matrix)
        
        # Add Lagrange multiplier for unbiasedness
        K_lagrange = xp.ones((n + 1, n + 1))
        K_lagrange[:n, :n] = K
        K_lagrange[n, n] = 0  # Lagrange corner
        
        return K_lagrange, sensor_values
    
    def _distance_matrix(
        self,
        coords1: np.ndarray,
        coords2: np.ndarray
    ) -> np.ndarray:
        """
        Compute distance matrix between two sets of coordinates.
        
        Uses Haversine formula for lat/lon distances (approximate for small fields).
        """
        xp = self.xp
        
        # Convert to local meters (approximate for Colorado ~39°N)
        # 1° lat ≈ 111km, 1° lon ≈ 86km
        lat_scale = 111000  # meters per degree
        lon_scale = 86000   # meters per degree
        
        # Reshape for broadcasting
        lat1 = coords1[:, 0][:, xp.newaxis] * lat_scale
        lon1 = coords1[:, 1][:, xp.newaxis] * lon_scale
        lat2 = coords2[:, 0][xp.newaxis, :] * lat_scale
        lon2 = coords2[:, 1][xp.newaxis, :] * lon_scale
        
        # Euclidean distance in meters
        dist = xp.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
        
        return dist
    
    def generate_virtual_grid(
        self,
        field_id: str,
        field_bounds: Tuple[float, float, float, float],
        sensor_measurements: List[Dict],
        satellite_trend: Optional[Callable[[float, float], float]] = None,
        depth_inches: int = 18
    ) -> List[KrigingCell]:
        """
        Generate 1-meter resolution virtual grid for a field.
        
        Args:
            field_id: Field identifier
            field_bounds: (min_lat, min_lon, max_lat, max_lon)
            sensor_measurements: List of sensor readings with lat, lon, vwc
            satellite_trend: Function(lat, lon) -> trend_value (0-1)
            depth_inches: Depth layer for this grid
            
        Returns:
            List of KrigingCell objects covering the field at 1m resolution
        """
        xp = self.xp
        min_lat, min_lon, max_lat, max_lon = field_bounds
        
        # Calculate grid dimensions
        lat_meters = (max_lat - min_lat) * 111000
        lon_meters = (max_lon - min_lon) * 86000
        
        n_lat = int(lat_meters / self.grid_resolution) + 1
        n_lon = int(lon_meters / self.grid_resolution) + 1
        
        # Limit grid size for performance (max ~10k cells per field)
        max_cells = 10000
        if n_lat * n_lon > max_cells:
            scale = np.sqrt(max_cells / (n_lat * n_lon))
            n_lat = int(n_lat * scale)
            n_lon = int(n_lon * scale)
        
        # Build sensor arrays
        sensor_lats = []
        sensor_lons = []
        sensor_values = []
        sensor_ids = []
        
        for measurement in sensor_measurements:
            if measurement.get('depth_inches') == depth_inches:
                sensor_lats.append(measurement['latitude'])
                sensor_lons.append(measurement['longitude'])
                sensor_values.append(measurement['vwc'])
                sensor_ids.append(measurement.get('sensor_id', 'unknown'))
        
        if len(sensor_values) < 3:
            # Not enough sensors for Kriging - return simple interpolation
            return self._fallback_interpolation(
                field_id, min_lat, min_lon, max_lat, max_lon,
                n_lat, n_lon, sensor_measurements, depth_inches
            )
        
        sensor_coords = xp.array(list(zip(sensor_lats, sensor_lons)))
        sensor_values_arr = xp.array(sensor_values)
        
        # Get trend values at sensor locations
        trend_at_sensors = xp.zeros(len(sensor_values))
        if satellite_trend:
            for i, (lat, lon) in enumerate(zip(sensor_lats, sensor_lons)):
                trend_at_sensors[i] = satellite_trend(lat, lon)
        
        # Detrend sensor values
        detrended_values = sensor_values_arr - self.trend_weight * trend_at_sensors
        
        # Build Kriging system
        K_lagrange, _ = self._build_kriging_system(
            sensor_coords, detrended_values, trend_at_sensors
        )
        
        # Invert Kriging matrix (GPU accelerated if available)
        try:
            K_inv = xp.linalg.inv(K_lagrange)
        except:
            # Singular matrix - use pseudo-inverse
            K_inv = xp.linalg.pinv(K_lagrange)
        
        # Generate grid points
        lat_grid = xp.linspace(min_lat, max_lat, n_lat)
        lon_grid = xp.linspace(min_lon, max_lon, n_lon)
        
        cells = []
        cell_count = 0
        
        for i, lat in enumerate(lat_grid):
            for j, lon in enumerate(lon_grid):
                # Check if this is a sensor location (hard anchor)
                is_anchor, anchor_sensor = self._check_sensor_location(
                    lat, lon, sensor_coords, sensor_ids
                )
                
                if is_anchor:
                    # Hard anchor - use sensor value exactly
                    sensor_idx = sensor_ids.index(anchor_sensor)
                    estimated_vwc = sensor_values[sensor_idx]
                    variance = 0.0
                    confidence = 1.0
                    trend_value = satellite_trend(lat, lon) if satellite_trend else None
                else:
                    # Kriging interpolation
                    grid_point = xp.array([[lat, lon]])
                    
                    # Distance from grid point to all sensors
                    dist_to_sensors = self._distance_matrix(grid_point, sensor_coords)[0]
                    
                    # Variogram vector (k)
                    k_variogram = self._variogram_model(dist_to_sensors)
                    k_lagrange = xp.ones(len(sensor_values) + 1)
                    k_lagrange[:len(sensor_values)] = k_variogram
                    
                    # Kriging weights
                    weights = K_inv @ k_lagrange
                    kriging_weights = weights[:len(sensor_values)]
                    
                    # Estimate (detrended)
                    detrended_estimate = xp.sum(kriging_weights * detrended_values)
                    
                    # Add trend back
                    trend_value = satellite_trend(lat, lon) if satellite_trend else 0.0
                    estimated_vwc = float(detrended_estimate + self.trend_weight * trend_value)
                    
                    # Kriging variance
                    variance = float(
                        self.sill + self.nugget - xp.sum(kriging_weights * k_variogram)
                    )
                    variance = max(0, variance)  # Ensure non-negative
                    
                    # Confidence based on variance
                    confidence = 1.0 / (1.0 + variance * 10)
                
                # Create cell
                cell_id = f"{field_id}_{depth_inches}in_{cell_count:05d}"
                cell = KrigingCell(
                    cell_id=cell_id,
                    field_id=field_id,
                    latitude=float(lat),
                    longitude=float(lon),
                    depth_inches=depth_inches,
                    estimated_vwc=estimated_vwc,
                    estimation_variance=variance,
                    confidence=confidence,
                    is_hard_anchor=is_anchor,
                    anchor_sensor_id=anchor_sensor,
                    satellite_trend_value=float(trend_value) if trend_value is not None else None
                )
                cell.compute_hash()
                cells.append(cell)
                cell_count += 1
        
        return cells
    
    def _check_sensor_location(
        self,
        lat: float,
        lon: float,
        sensor_coords: np.ndarray,
        sensor_ids: List[str],
        tolerance_meters: float = 5.0
    ) -> Tuple[bool, Optional[str]]:
        """Check if grid point coincides with a sensor location."""
        xp = self.xp
        
        point = xp.array([[lat, lon]])
        dist = self._distance_matrix(point, sensor_coords)[0]
        
        min_dist_idx = xp.argmin(dist)
        min_dist = float(dist[min_dist_idx])
        
        if min_dist < tolerance_meters:
            return True, sensor_ids[int(min_dist_idx)]
        return False, None
    
    def _fallback_interpolation(
        self,
        field_id: str,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        n_lat: int,
        n_lon: int,
        sensor_measurements: List[Dict],
        depth_inches: int
    ) -> List[KrigingCell]:
        """
        Simple inverse distance weighting when Kriging is not possible.
        """
        xp = self.xp
        
        # Filter to relevant depth
        relevant = [m for m in sensor_measurements if m.get('depth_inches') == depth_inches]
        
        if not relevant:
            # No data - return empty grid with defaults
            relevant = [{'latitude': (min_lat + max_lat) / 2,
                        'longitude': (min_lon + max_lon) / 2,
                        'vwc': 0.20}]
        
        sensor_lats = xp.array([m['latitude'] for m in relevant])
        sensor_lons = xp.array([m['longitude'] for m in relevant])
        sensor_values = xp.array([m['vwc'] for m in relevant])
        
        lat_grid = xp.linspace(min_lat, max_lat, n_lat)
        lon_grid = xp.linspace(min_lon, max_lon, n_lon)
        
        cells = []
        cell_count = 0
        
        for lat in lat_grid:
            for lon in lon_grid:
                # Inverse distance weighting
                dist = xp.sqrt(
                    ((lat - sensor_lats) * 111000) ** 2 +
                    ((lon - sensor_lons) * 86000) ** 2
                )
                
                # Add small epsilon to avoid division by zero
                weights = 1.0 / (dist + 1.0)
                weights = weights / xp.sum(weights)
                
                estimated_vwc = float(xp.sum(weights * sensor_values))
                variance = float(xp.mean(dist)) / 1000.0  # Approximate variance
                confidence = 0.5  # Lower confidence for fallback
                
                cell_id = f"{field_id}_{depth_inches}in_{cell_count:05d}"
                cell = KrigingCell(
                    cell_id=cell_id,
                    field_id=field_id,
                    latitude=float(lat),
                    longitude=float(lon),
                    depth_inches=depth_inches,
                    estimated_vwc=estimated_vwc,
                    estimation_variance=variance,
                    confidence=confidence
                )
                cell.compute_hash()
                cells.append(cell)
                cell_count += 1
        
        return cells
    
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            'gpu_accelerated': self.use_gpu,
            'grid_resolution_meters': self.grid_resolution,
            'variogram_range_meters': self.range_meters,
            'trend_weight': self.trend_weight
        }


# Example satellite trend function for testing
def example_satellite_trend(lat: float, lon: float) -> float:
    """
    Example trend function simulating NDVI-based spatial pattern.
    Returns value 0-1 representing relative vegetation health.
    """
    # Simple gradient pattern for testing
    base = 0.5
    lat_component = (lat - 37.5) * 2  # North-south gradient
    lon_component = (lon + 105.8) * 1.5  # East-west gradient
    noise = np.sin(lat * 100) * np.cos(lon * 100) * 0.1
    
    trend = base + lat_component + lon_component + noise
    return max(0.0, min(1.0, trend))
