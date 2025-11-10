"""INMET Weather API Client."""

import asyncio
from datetime import datetime
import json
import logging
import math
import os
import tempfile
import time
from typing import Any, Dict, Optional, List

import aiohttp
import async_timeout

from .const import GEOCODE_CACHE_FILE

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://apiprevmet3.inmet.gov.br"
TIMEOUT = 30
LOG_MESSAGE_USING_LAST_SUCCESSFUL_STATION = (
    "Using last successful station data for coordinates (%.2f, %.2f) due to exception"
)


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
        self._cache_content = {}
        self._geocode_cache: Dict[str, Dict[str, Any]] = {}
        # Cache will be loaded on first use to avoid blocking I/O in __init__
        self._cache_loaded = False
        # Cache for nearest station data (2 hours expiration)
        self._station_cache: Dict[str, Dict[str, Any]] = {}
        # Fallback cache for last successful API responses (no expiration)
        self._last_successful_current_weather: Dict[str, Any] = {}
        self._last_successful_forecast: Dict[str, Any] = {}
        self._last_successful_station: Dict[str, Any] = {}

    def _get_cache_key(self, latitude: float, longitude: float) -> str:
        """Generate cache key from coordinates (rounded to 2 decimal places)."""
        return f"{round(latitude, 2)},{round(longitude, 2)}"

    def _is_cache_valid(
        self, cache_entry: Dict[str, Any], max_age_seconds: int
    ) -> bool:
        """Check if a cache entry is still valid based on timestamp."""
        if "timestamp" not in cache_entry:
            return False
        age = time.time() - cache_entry["timestamp"]
        return age < max_age_seconds

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
            _LOGGER.debug(
                "Using cached geocode %s for coordinates (%.2f, %.2f)",
                cache_entry["geocode"],
                latitude,
                longitude,
            )
            return cache_entry["geocode"]

        # Try to get geocode from live API
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/Previsao_Portal"
                async with self._session.post(
                    url,
                    json={
                        "data": datetime.now().astimezone().isoformat().split("T")[0],
                        "tipo": "turno",
                        "turno": "tarde",
                    },
                ) as response:
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

    def _find_nearest_from_api_data(
        self, data: List[Dict[str, Any]], latitude: float, longitude: float
    ) -> Optional[str]:
        """Find nearest location from Previsao_Portal API data."""
        try:
            min_distance = float("inf")
            closest_geocode = None

            # The API returns a list of dictionaries, each with a 'geocode' field and
            # a 'centroide' field as a comma-separated "lon,lat" string.
            for location_data in data:
                if isinstance(location_data, dict) and "centroide" in location_data:
                    centroide: List[str] = location_data["centroide"].split(",")
                    geocode = location_data["geocode"]

                    # Extract coordinates from centroide
                    if len(centroide) == 2:
                        loc_lat = float(centroide[1])
                        loc_lon = float(centroide[0])

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

    async def get_nearest_station(
        self, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Get nearest weather station based on coordinates.

        Results are cached for 2 hours to reduce API calls.
        Returns last successful result if current request fails.
        """
        # Check cache first (2 hours = 7200 seconds)
        cache_key = self._get_cache_key(latitude, longitude)
        if cache_key in self._station_cache:
            cache_entry = self._station_cache[cache_key]
            if self._is_cache_valid(cache_entry, 7200):
                _LOGGER.debug(
                    "Using cached station data for coordinates (%.2f, %.2f)",
                    latitude,
                    longitude,
                )
                return cache_entry["data"]
            else:
                _LOGGER.debug(
                    "Cache expired for station data at (%.2f, %.2f)",
                    latitude,
                    longitude,
                )

        # First, we need to find the geocode
        # Since we don't have a direct endpoint, we'll use a heuristic approach
        # In a real implementation, you would cache a list of known geocodes and coordinates

        # For now, let's calculate distance to known locations
        # This is a simplified implementation
        geocode = await self.get_geocode_from_coordinates(latitude, longitude)

        if not geocode:
            # Return last successful result if available
            if cache_key in self._last_successful_station:
                _LOGGER.warning(
                    "Using last successful station data for coordinates (%.2f, %.2f) - no geocode",
                    latitude,
                    longitude,
                )
                return self._last_successful_station[cache_key]
            return None

        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/estacao/proxima/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching station data: %s", response.status
                        )
                        # Return last successful result if available
                        if cache_key in self._last_successful_station:
                            _LOGGER.warning(
                                "Using last successful station data for coordinates (%.2f, %.2f)",
                                latitude,
                                longitude,
                            )
                            return self._last_successful_station[cache_key]
                        return None

                    station_data = await response.json()

                    # Cache the result with timestamp
                    self._station_cache[cache_key] = {
                        "data": station_data,
                        "timestamp": time.time(),
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                    # Store successful result as fallback
                    self._last_successful_station[cache_key] = station_data
                    _LOGGER.debug(
                        "Cached station data for coordinates (%.2f, %.2f)",
                        latitude,
                        longitude,
                    )

                    return station_data

        except Exception as err:
            _LOGGER.error("Error getting nearest station: %s", err)
            # Return last successful result if available
            if cache_key in self._last_successful_station:
                _LOGGER.warning(
                    LOG_MESSAGE_USING_LAST_SUCCESSFUL_STATION,
                    latitude,
                    longitude,
                )
                return self._last_successful_station[cache_key]
            return None

    async def get_current_weather(self, geocode: str) -> Optional[Dict[str, Any]]:
        """Get current weather data for a geocode.

        Returns last successful result if current request fails.
        """
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/estacao/proxima/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching current weather: %s", response.status
                        )
                        # Return last successful result if available
                        if geocode in self._last_successful_current_weather:
                            _LOGGER.warning(
                                "Using last successful current weather data for %s",
                                geocode,
                            )
                            return self._last_successful_current_weather[geocode]
                        return None

                    data = await response.json()
                    # Store successful result as fallback
                    self._last_successful_current_weather[geocode] = data
                    return data

        except Exception as err:
            _LOGGER.error("Error getting current weather: %s", err)
            # Return last successful result if available
            if geocode in self._last_successful_current_weather:
                _LOGGER.warning(
                    "Using last successful current weather data for %s due to exception",
                    geocode,
                )
                return self._last_successful_current_weather[geocode]
            return None

    async def get_forecast(self, geocode: str) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a geocode.

        Returns last successful result if current request fails.
        """
        try:
            async with async_timeout.timeout(TIMEOUT):
                url = f"{API_BASE_URL}/previsao/{geocode}"
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error("Error fetching forecast: %s", response.status)
                        # Return last successful result if available
                        if geocode in self._last_successful_forecast:
                            _LOGGER.warning(
                                "Using last successful forecast data for %s", geocode
                            )
                            return self._last_successful_forecast[geocode]
                        return None

                    data = await response.json()
                    # Store successful result as fallback
                    self._last_successful_forecast[geocode] = data
                    return data

        except Exception as err:
            _LOGGER.error("Error getting forecast: %s", err)
            # Return last successful result if available
            if geocode in self._last_successful_forecast:
                _LOGGER.warning(
                    "Using last successful forecast data for %s due to exception",
                    geocode,
                )
                return self._last_successful_forecast[geocode]
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
