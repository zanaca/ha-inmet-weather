"""INMET Weather API Client."""
import logging
from typing import Any, Dict, Optional
import math

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://apiprevmet3.inmet.gov.br"
TIMEOUT = 30


class InmetApiClient:
    """INMET API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def get_geocode_from_coordinates(
        self, latitude: float, longitude: float
    ) -> Optional[str]:
        """Get geocode from latitude and longitude.

        Find the nearest location by calculating distance to known geocodes.
        """
        try:
            # List of major Brazilian city geocodes with approximate coordinates
            # Format: (geocode, lat, lon, city_name)
            known_locations = [
                ("3304557", -22.9068, -43.1729, "Rio de Janeiro"),
                ("3550308", -23.5505, -46.6333, "São Paulo"),
                ("5300108", -15.7939, -47.8828, "Brasília"),
                ("4106902", -25.4284, -49.2733, "Curitiba"),
                ("3106200", -19.9167, -43.9345, "Belo Horizonte"),
                ("2304400", -3.7172, -38.5433, "Fortaleza"),
                ("2927408", -12.9714, -38.5014, "Salvador"),
                ("5208707", -16.6869, -49.2648, "Goiânia"),
                ("2611606", -8.0476, -34.8770, "Recife"),
                ("4314902", -30.0346, -51.2177, "Porto Alegre"),
                ("1302603", -3.1019, -60.0250, "Manaus"),
                ("2111300", -2.5387, -44.2825, "São Luís"),
                ("1501402", -1.4558, -48.4902, "Belém"),
                ("2704302", -9.6658, -35.7350, "Maceió"),
                ("2408102", -5.7945, -35.2110, "Natal"),
                ("2800308", -10.9472, -37.0731, "Aracaju"),
                ("1200401", -9.9747, -67.8075, "Rio Branco"),
                ("1400100", 2.8235, -60.6758, "Boa Vista"),
                ("1100205", -8.7619, -63.9039, "Porto Velho"),
                ("1600303", 0.0347, -51.0694, "Macapá"),
                ("1721000", -10.1753, -48.2982, "Palmas"),
                ("1600600", -0.0389, -51.0664, "Amapá"),
                ("4205407", -27.5954, -48.5480, "Florianópolis"),
                ("3205309", -20.3155, -40.3128, "Vitória"),
                ("5103403", -15.5989, -56.0949, "Cuiabá"),
                ("5002704", -20.4428, -54.6464, "Campo Grande"),
                ("1100304", -10.8312, -61.9378, "Ji-Paraná"),
                ("2611507", -7.9386, -34.8721, "Olinda"),
            ]

            min_distance = float("inf")
            closest_geocode = None

            # Find the closest known location
            for geocode, lat, lon, city_name in known_locations:
                distance = self.calculate_distance(latitude, longitude, lat, lon)

                if distance < min_distance:
                    min_distance = distance
                    closest_geocode = geocode

            if closest_geocode:
                _LOGGER.info(
                    "Found closest location: geocode=%s, distance=%.2f km",
                    closest_geocode,
                    min_distance,
                )
                return closest_geocode

            # Fallback to Rio de Janeiro if no close match found
            _LOGGER.warning("No close location found, using Rio de Janeiro as default")
            return "3304557"

        except Exception as err:
            _LOGGER.error("Error getting geocode: %s", err)
            return None

    async def get_nearest_station(
        self, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Get nearest weather station based on coordinates."""
        # First, we need to find the geocode
        # Since we don't have a direct endpoint, we'll use a heuristic approach
        # In a real implementation, you would cache a list of known geocodes and coordinates

        # For now, let's calculate distance to known locations
        # This is a simplified implementation
        geocode = await self.get_geocode_from_coordinates(latitude, longitude)

        if not geocode:
            return None

        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/estacao/proxima/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching station data: %s", response.status
                        )
                        return None

                    return await response.json()

        except Exception as err:
            _LOGGER.error("Error getting nearest station: %s", err)
            return None

    async def get_current_weather(self, geocode: str) -> Optional[Dict[str, Any]]:
        """Get current weather data for a geocode."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/estacao/proxima/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching current weather: %s", response.status
                        )
                        return None

                    data = await response.json()
                    return data

        except Exception as err:
            _LOGGER.error("Error getting current weather: %s", err)
            return None

    async def get_forecast(self, geocode: str) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a geocode."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/previsao/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching forecast: %s", response.status
                        )
                        return None

                    data = await response.json()
                    return data

        except Exception as err:
            _LOGGER.error("Error getting forecast: %s", err)
            return None

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        # Radius of Earth in kilometers
        R = 6371.0

        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
