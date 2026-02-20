"""
Cloud Processing Pipeline - 1m Virtual Sensor Grid
High-resolution interpolation using Regression Kriging with satellite data integration
"""
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.interpolate import griddata
import logging

logger = logging.getLogger(__name__)


@dataclass
class SensorPoint:
    """Sensor location and readings"""
    sensor_id: str
    x: float  # Longitude
    y: float  # Latitude
    moisture_surface: float
    moisture_root: float
    temperature: float
    elevation: float = 0.0


@dataclass
class SatellitePixel:
    """Satellite-derived covariates"""
    x: float
    y: float
    ndvi: float
    ndwi: float
    lst: float  # Land Surface Temperature
    elevation: float
    slope: float


class RegressionKriging:
    """
    Regression Kriging for 1m resolution interpolation
    Combines trend model (satellite covariates) with residual kriging
    """
    
    def __init__(self, variogram_model: str = 'spherical'):
        self.variogram_model = variogram_model
        self.trend_model = None
        self.scaler = StandardScaler()
        self.variogram_params = None
        
    def fit_trend(
        self, 
        sensor_points: List[SensorPoint],
        satellite_data: List[SatellitePixel]
    ) -> LinearRegression:
        """
        Fit trend model: moisture ~ NDVI + NDWI + LST + elevation + slope
        """
        # Match sensor points to nearest satellite pixels
        X_trend = []
        y_moisture = []
        
        for sensor in sensor_points:
            # Find nearest satellite pixel
            sat_pixel = self._find_nearest_pixel(sensor, satellite_data)
            if sat_pixel:
                features = [
                    sat_pixel.ndvi,
                    sat_pixel.ndwi,
                    sat_pixel.lst,
                    sat_pixel.elevation,
                    sat_pixel.slope
                ]
                X_trend.append(features)
                y_moisture.append(sensor.moisture_surface)
        
        X_trend = np.array(X_trend)
        y_moisture = np.array(y_moisture)
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X_trend)
        
        # Fit linear trend
        self.trend_model = LinearRegression()
        self.trend_model.fit(X_scaled, y_moisture)
        
        logger.info(f"Trend model R²: {self.trend_model.score(X_scaled, y_moisture):.3f}")
        
        return self.trend_model
    
    def fit_variogram(
        self,
        sensor_points: List[SensorPoint],
        residuals: np.ndarray
    ):
        """
        Fit variogram to residuals for kriging
        Uses method of moments with spherical model
        """
        # Calculate pairwise distances
        coords = np.array([[s.x, s.y] for s in sensor_points])
        distances = cdist(coords, coords, metric='euclidean')
        
        # Calculate semivariance
        n = len(residuals)
        gamma = np.zeros_like(distances)
        
        for i in range(n):
            for j in range(i+1, n):
                gamma[i, j] = 0.5 * (residuals[i] - residuals[j])**2
                gamma[j, i] = gamma[i, j]
        
        # Bin distances and calculate average semivariance
        max_dist = np.max(distances) / 2  # Use half max distance for variogram range
        bins = np.linspace(0, max_dist, 15)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        bin_gamma = []
        
        for i in range(len(bins)-1):
            mask = (distances >= bins[i]) & (distances < bins[i+1])
            if np.any(mask):
                bin_gamma.append(np.mean(gamma[mask]))
            else:
                bin_gamma.append(0)
        
        # Fit spherical variogram model: γ(h) = c0 + c * [1.5(h/a) - 0.5(h/a)³]
        # Simplified fitting - use variance of residuals as sill
        sill = np.var(residuals)
        nugget = bin_gamma[0] if len(bin_gamma) > 0 else 0.1 * sill
        range_param = max_dist * 0.5
        
        self.variogram_params = {
            'model': 'spherical',
            'sill': sill,
            'range': range_param,
            'nugget': nugget
        }
        
        logger.info(f"Variogram params: sill={sill:.4f}, range={range_param:.1f}m, nugget={nugget:.4f}")
    
    def predict_1m_grid(
        self,
        sensor_points: List[SensorPoint],
        satellite_data: List[SatellitePixel],
        grid_bounds: Tuple[float, float, float, float],  # (min_x, min_y, max_x, max_y)
        resolution: float = 1.0  # meters
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate 1m resolution predictions across field
        Returns: (x_grid, y_grid, predictions, variances)
        """
        logger.info("Starting 1m grid prediction...")
        
        # 1. Fit trend model
        self.fit_trend(sensor_points, satellite_data)
        
        # 2. Calculate residuals at sensor locations
        residuals = self._calculate_residuals(sensor_points, satellite_data)
        
        # 3. Fit variogram to residuals
        self.fit_variogram(sensor_points, residuals)
        
        # 4. Create 1m grid
        min_x, min_y, max_x, max_y = grid_bounds
        
        # Convert resolution from meters to degrees (approximate)
        res_deg = resolution / 111320.0  # 1 degree ≈ 111.32 km
        
        x_coords = np.arange(min_x, max_x, res_deg)
        y_coords = np.arange(min_y, max_y, res_deg)
        x_grid, y_grid = np.meshgrid(x_coords, y_coords)
        
        grid_shape = x_grid.shape
        n_points = x_grid.size
        
        logger.info(f"Grid shape: {grid_shape}, Total points: {n_points}")
        
        # 5. Predict trend at grid points
        trend_predictions = self._predict_trend_at_grid(
            x_grid.flatten(),
            y_grid.flatten(),
            satellite_data
        )
        
        # 6. Krige residuals at grid points
        residual_predictions, variances = self._krige_residuals(
            x_grid.flatten(),
            y_grid.flatten(),
            sensor_points,
            residuals
        )
        
        # 7. Combine trend + residuals
        final_predictions = trend_predictions + residual_predictions
        
        # Reshape to grid
        predictions_grid = final_predictions.reshape(grid_shape)
        variances_grid = variances.reshape(grid_shape)
        
        logger.info("1m grid prediction complete")
        
        return x_grid, y_grid, predictions_grid, variances_grid
    
    def _find_nearest_pixel(
        self, 
        sensor: SensorPoint, 
        satellite_data: List[SatellitePixel]
    ) -> Optional[SatellitePixel]:
        """Find nearest satellite pixel to sensor location"""
        if not satellite_data:
            return None
        
        min_dist = float('inf')
        nearest = None
        
        for pixel in satellite_data:
            dist = np.sqrt((sensor.x - pixel.x)**2 + (sensor.y - pixel.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = pixel
        
        return nearest
    
    def _calculate_residuals(
        self,
        sensor_points: List[SensorPoint],
        satellite_data: List[SatellitePixel]
    ) -> np.ndarray:
        """Calculate residuals: observed - trend"""
        observed = []
        predicted = []
        
        for sensor in sensor_points:
            sat_pixel = self._find_nearest_pixel(sensor, satellite_data)
            if sat_pixel:
                features = np.array([[
                    sat_pixel.ndvi,
                    sat_pixel.ndwi,
                    sat_pixel.lst,
                    sat_pixel.elevation,
                    sat_pixel.slope
                ]])
                features_scaled = self.scaler.transform(features)
                pred = self.trend_model.predict(features_scaled)[0]
                
                observed.append(sensor.moisture_surface)
                predicted.append(pred)
        
        residuals = np.array(observed) - np.array(predicted)
        return residuals
    
    def _predict_trend_at_grid(
        self,
        x_points: np.ndarray,
        y_points: np.ndarray,
        satellite_data: List[SatellitePixel]
    ) -> np.ndarray:
        """Predict trend component at grid points using satellite data"""
        predictions = []
        
        # For each grid point, interpolate satellite covariates
        sat_coords = np.array([[p.x, p.y] for p in satellite_data])
        sat_ndvi = np.array([p.ndvi for p in satellite_data])
        sat_ndwi = np.array([p.ndwi for p in satellite_data])
        sat_lst = np.array([p.lst for p in satellite_data])
        sat_elev = np.array([p.elevation for p in satellite_data])
        sat_slope = np.array([p.slope for p in satellite_data])
        
        grid_coords = np.column_stack([x_points, y_points])
        
        # Interpolate each covariate to grid points
        ndvi_interp = griddata(sat_coords, sat_ndvi, grid_coords, method='linear')
        ndwi_interp = griddata(sat_coords, sat_ndwi, grid_coords, method='linear')
        lst_interp = griddata(sat_coords, sat_lst, grid_coords, method='linear')
        elev_interp = griddata(sat_coords, sat_elev, grid_coords, method='linear')
        slope_interp = griddata(sat_coords, sat_slope, grid_coords, method='linear')
        
        # Stack features
        X_grid = np.column_stack([ndvi_interp, ndwi_interp, lst_interp, elev_interp, slope_interp])
        
        # Handle NaN values (outside convex hull)
        nan_mask = np.isnan(X_grid).any(axis=1)
        X_grid[nan_mask] = 0  # Placeholder, will have high variance
        
        # Predict using trend model
        X_grid_scaled = self.scaler.transform(X_grid)
        predictions = self.trend_model.predict(X_grid_scaled)
        
        return predictions
    
    def _krige_residuals(
        self,
        x_points: np.ndarray,
        y_points: np.ndarray,
        sensor_points: List[SensorPoint],
        residuals: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ordinary kriging of residuals
        Returns: (predictions, variances)
        """
        sensor_coords = np.array([[s.x, s.y] for s in sensor_points])
        grid_coords = np.column_stack([x_points, y_points])
        
        n_sensors = len(sensor_points)
        n_grid = len(x_points)
        
        predictions = np.zeros(n_grid)
        variances = np.zeros(n_grid)
        
        # Kriging parameters
        sill = self.variogram_params['sill']
        range_param = self.variogram_params['range']
        nugget = self.variogram_params['nugget']
        
        # For efficiency, process in batches
        batch_size = 1000
        
        for batch_start in range(0, n_grid, batch_size):
            batch_end = min(batch_start + batch_size, n_grid)
            batch_coords = grid_coords[batch_start:batch_end]
            
            # Calculate distances from batch points to all sensors
            distances = cdist(batch_coords, sensor_coords, metric='euclidean')
            
            # Calculate kriging weights using variogram
            for i, dist_vector in enumerate(distances):
                # Spherical variogram
                gamma = np.zeros(n_sensors)
                for j, h in enumerate(dist_vector):
                    if h == 0:
                        gamma[j] = 0
                    elif h <= range_param:
                        gamma[j] = nugget + (sill - nugget) * (1.5 * h / range_param - 0.5 * (h / range_param)**3)
                    else:
                        gamma[j] = sill
                
                # Solve kriging system (simplified - no Lagrange multiplier)
                # weights = gamma^(-1) * residuals
                weights = np.exp(-dist_vector / range_param)  # Simplified weighting
                weights /= weights.sum()
                
                # Prediction
                predictions[batch_start + i] = np.dot(weights, residuals)
                
                # Variance (kriging variance)
                variances[batch_start + i] = sill - np.dot(weights, gamma)
        
        return predictions, variances


class SatelliteProcessor:
    """Process Sentinel-2 and Landsat imagery for covariates"""
    
    @staticmethod
    def calculate_ndvi(nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Vegetation Index"""
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir_band - red_band) / (nir_band + red_band)
            ndvi[np.isnan(ndvi)] = 0
        return ndvi
    
    @staticmethod
    def calculate_ndwi(green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Water Index"""
        with np.errstate(divide='ignore', invalid='ignore'):
            ndwi = (green_band - nir_band) / (green_band + nir_band)
            ndwi[np.isnan(ndwi)] = 0
        return ndwi
    
    @staticmethod
    def process_sentinel2(
        image_path: str,
        field_bounds: Tuple[float, float, float, float]
    ) -> Dict[str, np.ndarray]:
        """
        Process Sentinel-2 image to extract indices
        Returns dict with 'ndvi', 'ndwi', 'coords'
        """
        with rasterio.open(image_path) as src:
            # Read bands (Sentinel-2 L2A)
            # Band 3 = Green (560nm)
            # Band 4 = Red (665nm)
            # Band 8 = NIR (842nm)
            
            green = src.read(3).astype(float)
            red = src.read(4).astype(float)
            nir = src.read(8).astype(float)
            
            # Calculate indices
            ndvi = SatelliteProcessor.calculate_ndvi(nir, red)
            ndwi = SatelliteProcessor.calculate_ndwi(green, nir)
            
            # Get coordinates for each pixel
            height, width = ndvi.shape
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            xs, ys = rasterio.transform.xy(src.transform, rows, cols)
            
            return {
                'ndvi': ndvi,
                'ndwi': ndwi,
                'x_coords': np.array(xs),
                'y_coords': np.array(ys),
                'transform': src.transform,
                'crs': src.crs
            }
    
    @staticmethod
    def extract_pixels_for_field(
        satellite_data: Dict[str, np.ndarray],
        field_bounds: Tuple[float, float, float, float]
    ) -> List[SatellitePixel]:
        """Extract satellite pixels within field bounds"""
        min_x, min_y, max_x, max_y = field_bounds
        
        ndvi = satellite_data['ndvi']
        ndwi = satellite_data['ndwi']
        xs = satellite_data['x_coords']
        ys = satellite_data['y_coords']
        
        pixels = []
        for i in range(ndvi.shape[0]):
            for j in range(ndvi.shape[1]):
                x, y = xs[i][j], ys[i][j]
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    pixels.append(SatellitePixel(
                        x=x, y=y,
                        ndvi=ndvi[i, j],
                        ndwi=ndwi[i, j],
                        lst=0.0,  # TODO: from thermal band
                        elevation=0.0,  # TODO: from DEM
                        slope=0.0
                    ))
        
        return pixels


# Example usage
if __name__ == "__main__":
    # Mock data for demonstration
    sensors = [
        SensorPoint("s1", -122.4194, 37.7749, 0.25, 0.30, 22.5),
        SensorPoint("s2", -122.4180, 37.7760, 0.28, 0.32, 23.0),
        SensorPoint("s3", -122.4170, 37.7755, 0.22, 0.27, 22.0),
    ]
    
    satellite_pixels = [
        SatellitePixel(-122.4194, 37.7749, 0.65, 0.25, 25.0, 100.0, 2.0),
        SatellitePixel(-122.4180, 37.7760, 0.70, 0.20, 24.0, 105.0, 1.5),
        SatellitePixel(-122.4170, 37.7755, 0.60, 0.30, 26.0, 95.0, 2.5),
    ]
    
    # Initialize kriging
    rk = RegressionKriging()
    
    # Generate 1m grid
    bounds = (-122.4200, 37.7740, -122.4160, 37.7770)
    x_grid, y_grid, predictions, variances = rk.predict_1m_grid(
        sensors, satellite_pixels, bounds, resolution=1.0
    )
    
    print(f"Generated grid: {predictions.shape}")
    print(f"Mean prediction: {np.mean(predictions):.3f}")
    print(f"Mean variance: {np.mean(variances):.4f}")
