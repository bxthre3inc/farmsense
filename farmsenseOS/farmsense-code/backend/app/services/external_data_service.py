import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ExternalDataService:
    @staticmethod
    def get_weather_data(lat: float, lon: float) -> Optional[Dict]:
        """
        Fetches current weather data from Open-Meteo (Keyless).
        """
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("current_weather")
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None

    @staticmethod
    def get_soil_properties(lat: float, lon: float) -> Optional[Dict]:
        """
        Fetches soil properties from SoilGrids ISRIC REST API (Keyless).
        Focuses on pH and Soil Organic Carbon (SOC).
        """
        try:
            # SoilGrids v2 REST API
            # Properties: phh2o (pH), soc (Soil Organic Carbon)
            url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&property=soc&depth=0-5cm&value=mean"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = {}
            for layer in data.get("properties", {}).get("layers", []):
                name = layer.get("name")
                depths = layer.get("depths", [])
                if depths:
                    val = depths[0].get("values", {}).get("mean")
                    if val is not None:
                        # SoilGrids often returns values as integers with multipliers (e.g., pH * 10)
                        if name == "phh2o":
                            properties["ph"] = val / 10.0
                        elif name == "soc":
                            properties["soc_dg_kg"] = val / 10.0 # decigrams per kilogram
            
            return properties
        except Exception as e:
            logger.error(f"Failed to fetch soil properties: {e}")
            return None
