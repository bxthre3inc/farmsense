"""
FarmSense OS v1.0 - Dynamic Soil Variability Models

Recursive soil mapping that evolves based on observed moisture movement.
Initial static maps (SSURGO) treated as "evolving hypothesis."
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class SoilTexture:
    """
    USDA soil texture classification with hydraulic properties.
    """
    sand_percent: float
    silt_percent: float
    clay_percent: float
    
    # Derived hydraulic properties (learned or from lookup)
    saturated_hydraulic_conductivity: float = 0.0  # cm/hr
    field_capacity: float = 0.0  # v/v
    permanent_wilting_point: float = 0.0  # v/v
    
    def __post_init__(self):
        # Normalize to 100%
        total = self.sand_percent + self.silt_percent + self.clay_percent
        if total > 0:
            self.sand_percent = (self.sand_percent / total) * 100
            self.silt_percent = (self.silt_percent / total) * 100
            self.clay_percent = (self.clay_percent / total) * 100
    
    @property
    def texture_class(self) -> str:
        """USDA texture class based on sand/silt/clay."""
        s, i, c = self.sand_percent, self.silt_percent, self.clay_percent
        
        if c >= 40:
            return 'clay' if s <= 45 else 'sandy_clay'
        elif c >= 35:
            return 'clay_loam' if s <= 20 else 'silty_clay_loam'
        elif c >= 27:
            return 'silty_clay_loam' if i >= 50 else 'clay_loam'
        elif s >= 85:
            return 'sand'
        elif s >= 70:
            return 'loamy_sand'
        elif c >= 20 and s <= 52 and i <= 50:
            return 'loam'
        elif i >= 80 and c < 12:
            return 'silt'
        elif i >= 50:
            return 'silty_loam'
        elif s >= 52:
            return 'sandy_loam'
        else:
            return 'loam'
    
    def estimate_hydraulic_properties(self) -> None:
        """
        Estimate Ksat, FC, PWP from texture using pedotransfer functions.
        This is the initial estimate; system learns actual values over time.
        """
        # Simplified pedotransfer functions
        s, i, c = self.sand_percent / 100, self.silt_percent / 100, self.clay_percent / 100
        
        # Field capacity estimate (volumetric)
        self.field_capacity = 0.2576 - 0.002 * s + 0.0036 * c
        
        # Permanent wilting point
        self.permanent_wilting_point = 0.026 + 0.005 * c
        
        # Saturated hydraulic conductivity (cm/hr) - Kozeny-Carman
        self.saturated_hydraulic_conductivity = 10 ** (
            -0.6 + 1.3 * s - 0.6 * c
        ) * 100  # Convert to cm/hr


@dataclass
class SoilMapCell:
    """
    Single cell in the dynamic soil variability map.
    Resolution: 30m (SSURGO base) with learned refinements.
    """
    cell_id: str
    latitude: float
    longitude: float
    resolution_m: float = 30.0  # SSURGO base resolution
    
    # Base layer (from SSURGO)
    base_texture: Optional[SoilTexture] = None
    base_horizon_depths: Dict[int, SoilTexture] = field(default_factory=dict)
    
    # Learned properties (from observed moisture movement)
    learned_texture: Optional[SoilTexture] = None
    learning_confidence: float = 0.0  # 0.0-1.0
    
    # Hydraulic properties (learned or estimated)
    effective_ksat: float = 0.0  # cm/hr
    effective_fc: float = 0.0
    effective_pwp: float = 0.0
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)
    update_count: int = 0
    
    def get_effective_texture(self) -> Optional[SoilTexture]:
        """Return learned texture if confident, else base texture."""
        if self.learned_texture and self.learning_confidence > 0.7:
            return self.learned_texture
        return self.base_texture
    
    def update_from_observation(
        self,
        predicted_drainage_rate: float,
        observed_drainage_rate: float,
        moisture_residual: float
    ) -> None:
        """
        Bayesian update of soil texture based on observed vs predicted drainage.
        
        If zone drains 20% faster than NRCS map suggests, update to higher sand ratio.
        """
        error = observed_drainage_rate - predicted_drainage_rate
        
        # Only update if significant error
        if abs(error) / (predicted_drainage_rate + 0.001) < 0.1:
            return
        
        # Adjust texture based on error direction
        current = self.get_effective_texture()
        if current is None:
            return
        
        # Faster drainage = more sand, less clay
        if error > 0:  # Draining faster than predicted
            adjustment = min(0.05 * error, 10)  # Max 10% shift
            new_sand = min(current.sand_percent + adjustment, 95)
            new_clay = max(current.clay_percent - adjustment * 0.5, 5)
            new_silt = max(100 - new_sand - new_clay, 0)
        else:  # Draining slower than predicted
            adjustment = min(0.05 * abs(error), 10)
            new_clay = min(current.clay_percent + adjustment, 60)
            new_sand = max(current.sand_percent - adjustment * 0.5, 5)
            new_silt = max(100 - new_sand - new_clay, 0)
        
        self.learned_texture = SoilTexture(new_sand, new_silt, new_clay)
        self.learned_texture.estimate_hydraulic_properties()
        
        # Update confidence
        self.learning_confidence = min(0.95, self.learning_confidence + 0.05)
        self.effective_ksat = self.learned_texture.saturated_hydraulic_conductivity
        self.effective_fc = self.learned_texture.field_capacity
        self.effective_pwp = self.learned_texture.permanent_wilting_point
        
        self.last_updated = datetime.utcnow()
        self.update_count += 1


@dataclass
class DynamicSoilMap:
    """
    Complete dynamic soil variability map for the deployment area.
    
    Initial state: NRCS SSURGO 30m base layer
    Evolution: Recursive updates based on sensor observations
    """
    map_id: str
    cells: Dict[str, SoilMapCell] = field(default_factory=dict)
    
    # Map metadata
    bounds: Tuple[float, float, float, float] = (0, 0, 0, 0)  # min_lat, min_lon, max_lat, max_lon
    base_resolution_m: float = 30.0
    
    # Learning statistics
    total_observations: int = 0
    significant_updates: int = 0
    
    def add_cell(self, cell: SoilMapCell) -> None:
        """Add cell to map."""
        self.cells[cell.cell_id] = cell
    
    def get_cell_at(self, latitude: float, longitude: float) -> Optional[SoilMapCell]:
        """Get soil map cell containing given coordinates."""
        # Simple nearest cell lookup
        min_dist = float('inf')
        nearest = None
        
        for cell in self.cells.values():
            dist = ((cell.latitude - latitude) ** 2 + 
                   (cell.longitude - longitude) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = cell
        
        return nearest
    
    def get_texture_at_depth(
        self, 
        latitude: float, 
        longitude: float, 
        depth_inches: int
    ) -> Optional[SoilTexture]:
        """Get soil texture at specific location and depth."""
        cell = self.get_cell_at(latitude, longitude)
        if cell is None:
            return None
        
        # Return horizon-specific texture if available
        if depth_inches in cell.base_horizon_depths:
            return cell.base_horizon_depths[depth_inches]
        
        return cell.get_effective_texture()
    
    def update_from_batch(
        self,
        sensor_locations: List[Tuple[str, float, float]],
        observed_moisture: Dict[str, float],
        predicted_moisture: Dict[str, float],
        time_delta_hours: float
    ) -> None:
        """
        Update soil map based on batch of sensor observations.
        
        Reverse-engineers local soil texture from moisture movement patterns.
        """
        for sensor_id, lat, lon in sensor_locations:
            if sensor_id not in observed_moisture:
                continue
            
            cell = self.get_cell_at(lat, lon)
            if cell is None:
                continue
            
            observed = observed_moisture[sensor_id]
            predicted = predicted_moisture.get(sensor_id, observed)
            
            # Estimate drainage rates
            observed_rate = abs(observed - predicted) / time_delta_hours
            predicted_rate = 0.1  # Default expected rate (cm/hr proxy)
            
            residual = observed - predicted
            
            cell.update_from_observation(predicted_rate, observed_rate, residual)
            self.total_observations += 1
            
            if cell.update_count > 0:
                self.significant_updates += 1
    
    def get_learning_stats(self) -> Dict:
        """Return statistics on map learning progress."""
        if not self.cells:
            return {}
        
        confident_cells = sum(1 for c in self.cells.values() if c.learning_confidence > 0.7)
        
        return {
            'total_cells': len(self.cells),
            'confident_cells': confident_cells,
            'confidence_rate': confident_cells / len(self.cells),
            'total_observations': self.total_observations,
            'significant_updates': self.significant_updates,
            'average_confidence': sum(c.learning_confidence for c in self.cells.values()) / len(self.cells)
        }


def create_from_ssurgo(
    map_id: str,
    ssurgo_data: List[Dict]
) -> DynamicSoilMap:
    """
    Create dynamic soil map from NRCS SSURGO data.
    
    ssurgo_data: List of dicts with 'mukey', 'lat', 'lon', 'sand', 'silt', 'clay'
    """
    soil_map = DynamicSoilMap(map_id=map_id)
    
    for record in ssurgo_data:
        texture = SoilTexture(
            sand_percent=record.get('sand', 30),
            silt_percent=record.get('silt', 40),
            clay_percent=record.get('clay', 30)
        )
        texture.estimate_hydraulic_properties()
        
        cell = SoilMapCell(
            cell_id=f"cell_{record['mukey']}",
            latitude=record['lat'],
            longitude=record['lon'],
            base_texture=texture,
            effective_ksat=texture.saturated_hydraulic_conductivity,
            effective_fc=texture.field_capacity,
            effective_pwp=texture.permanent_wilting_point
        )
        
        soil_map.add_cell(cell)
    
    return soil_map
