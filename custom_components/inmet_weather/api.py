"""INMET Weather API Client."""

import json
import logging
import math
import os
import time
from typing import Any, Dict, Optional

import aiohttp
import async_timeout

from .const import GEOCODE_CACHE_EXPIRY, GEOCODE_CACHE_FILE

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://apiprevmet3.inmet.gov.br"
TIMEOUT = 30


class InmetApiClient:
    """INMET API Client."""

    def __init__(
        self, session: aiohttp.ClientSession, cache_dir: Optional[str] = None
    ) -> None:
        """Initialize the API client.

        Args:
            session: aiohttp client session
            cache_dir: Directory to store cache file (defaults to temp directory for tests)
        """
        self._session = session
        if cache_dir is None:
            # Use temp directory by default (good for tests)
            import tempfile

            cache_dir = tempfile.gettempdir()
        self._cache_dir = cache_dir
        self._cache_file = os.path.join(self._cache_dir, GEOCODE_CACHE_FILE)
        self._geocode_cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load geocode cache from file."""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, "r") as f:
                    self._geocode_cache = json.load(f)
                _LOGGER.debug("Loaded geocode cache from %s", self._cache_file)
        except Exception as err:
            _LOGGER.warning("Failed to load geocode cache: %s", err)
            self._geocode_cache = {}

    def _save_cache(self) -> None:
        """Save geocode cache to file."""
        try:
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)

            with open(self._cache_file, "w") as f:
                json.dump(self._geocode_cache, f, indent=2)
            _LOGGER.debug("Saved geocode cache to %s", self._cache_file)
        except Exception as err:
            _LOGGER.warning("Failed to save geocode cache: %s", err)

    def _get_cache_key(self, latitude: float, longitude: float) -> str:
        """Generate cache key from coordinates (rounded to 2 decimal places)."""
        return f"{round(latitude, 2)},{round(longitude, 2)}"

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if "timestamp" not in cache_entry:
            return False

        age = time.time() - cache_entry["timestamp"]
        return age < GEOCODE_CACHE_EXPIRY

    async def get_geocode_from_coordinates(
        self, latitude: float, longitude: float
    ) -> Optional[str]:
        """Get geocode from latitude and longitude using live API.

        Queries the Previsao_Portal API and caches the result for 2 days.
        Falls back to distance-based calculation if API fails.
        """
        # Check cache first
        cache_key = self._get_cache_key(latitude, longitude)
        if cache_key in self._geocode_cache:
            cache_entry = self._geocode_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                _LOGGER.debug(
                    "Using cached geocode %s for coordinates (%.2f, %.2f)",
                    cache_entry["geocode"],
                    latitude,
                    longitude,
                )
                return cache_entry["geocode"]
            else:
                _LOGGER.debug(
                    "Cache entry expired for coordinates (%.2f, %.2f)",
                    latitude,
                    longitude,
                )

        # Try to get geocode from live API
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/Previsao_Portal"
                async with self._session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Find the nearest location from API response
                        geocode = self._find_nearest_from_api_data(
                            data, latitude, longitude
                        )

                        if geocode:
                            # Cache the result
                            self._geocode_cache[cache_key] = {
                                "geocode": geocode,
                                "timestamp": time.time(),
                                "latitude": latitude,
                                "longitude": longitude,
                            }
                            self._save_cache()

                            _LOGGER.info(
                                "Found geocode %s from API for coordinates (%.2f, %.2f)",
                                geocode,
                                latitude,
                                longitude,
                            )
                            return geocode
                    else:
                        _LOGGER.warning(
                            "API returned status %s, falling back to distance calculation",
                            response.status,
                        )

        except Exception as err:
            _LOGGER.warning(
                "Failed to get geocode from API: %s, falling back to distance calculation",
                err,
            )

        # Fallback: use distance-based calculation with hardcoded locations
        geocode = await self._get_geocode_by_distance(latitude, longitude)

        if geocode:
            # Cache the fallback result
            self._geocode_cache[cache_key] = {
                "geocode": geocode,
                "timestamp": time.time(),
                "latitude": latitude,
                "longitude": longitude,
                "source": "fallback",
            }
            self._save_cache()

        return geocode

    def _find_nearest_from_api_data(
        self, data: Dict[str, Any], latitude: float, longitude: float
    ) -> Optional[str]:
        """Find nearest location from Previsao_Portal API data."""
        try:
            min_distance = float("inf")
            closest_geocode = None

            # The API returns a dictionary with geocodes as keys
            # Each entry should have centroide with lat/lon
            for geocode, location_data in data.items():
                if isinstance(location_data, dict) and "centroide" in location_data:
                    centroide = location_data["centroide"]

                    # Extract coordinates from centroide
                    if "lat" in centroide and "lon" in centroide:
                        loc_lat = float(centroide["lat"])
                        loc_lon = float(centroide["lon"])

                        distance = self.calculate_distance(
                            latitude, longitude, loc_lat, loc_lon
                        )

                        if distance < min_distance:
                            min_distance = distance
                            closest_geocode = geocode

            if closest_geocode:
                _LOGGER.debug(
                    "Found closest location from API: geocode=%s, distance=%.2f km",
                    closest_geocode,
                    min_distance,
                )

            return closest_geocode

        except Exception as err:
            _LOGGER.error("Error parsing API data: %s", err)
            return None

    async def _get_geocode_by_distance(
        self, latitude: float, longitude: float
    ) -> Optional[str]:
        """Fallback method: Get geocode by calculating distance to known locations."""
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
                    "Found closest location (fallback): geocode=%s, distance=%.2f km",
                    closest_geocode,
                    min_distance,
                )
                return closest_geocode

            # Fallback to Rio de Janeiro if no close match found
            _LOGGER.warning("No close location found, using Rio de Janeiro as default")
            return "3304557"

        except Exception as err:
            _LOGGER.error("Error getting geocode by distance: %s", err)
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
                        _LOGGER.error("Error fetching forecast: %s", response.status)
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
