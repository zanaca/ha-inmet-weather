"""Weather platform for INMET Weather integration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import InmetApiClient
from .const import CONDITION_MAP, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

# Period time mappings for forecasts
PERIOD_HOURS = {
    "manha": 6,
    "tarde": 12,
    "noite": 18,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up INMET Weather weather entity."""
    name = config_entry.data[CONF_NAME]
    latitude = config_entry.data[CONF_LATITUDE]
    longitude = config_entry.data[CONF_LONGITUDE]
    geocode = config_entry.data["geocode"]

    session = aiohttp_client.async_get_clientsession(hass)
    client = InmetApiClient(session, cache_dir=hass.config.config_dir)

    coordinator = InmetWeatherCoordinator(hass, client, geocode)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([InmetWeatherEntity(coordinator, name, latitude, longitude)])


class InmetWeatherCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """INMET Weather data coordinator."""

    def __init__(
        self, hass: HomeAssistant, client: InmetApiClient, geocode: str
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.client = client
        self.geocode = geocode

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            current = await self.client.get_current_weather(self.geocode)
            forecast = await self.client.get_forecast(self.geocode)

            if current is None or forecast is None:
                raise UpdateFailed("Error fetching data from INMET API")

            return {"current": current, "forecast": forecast}

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class InmetWeatherEntity(CoordinatorEntity[InmetWeatherCoordinator], WeatherEntity):
    """INMET Weather Entity."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_attribution = "Data provided by INMET (Instituto Nacional de Meteorologia)"

    def __init__(
        self,
        coordinator: InmetWeatherCoordinator,
        name: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{latitude}_{longitude}"
        self._latitude = latitude
        self._longitude = longitude

    def _get_current_data(self, key: str) -> float | None:
        """Get current weather data value safely."""
        if not self.coordinator.data or "current" not in self.coordinator.data:
            return None

        current = self.coordinator.data["current"]
        if "dados" not in current:
            return None

        value = current["dados"].get(key)
        return self._safe_float(value)

    @staticmethod
    def _safe_float(val: Any) -> float | None:
        """Convert value safely to float."""
        if val is None:
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self._get_current_data("TEM_INS")

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self._get_current_data("UMD_INS")

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self._get_current_data("PRE_INS")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in m/s."""
        return self._get_current_data("VEN_VEL")

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed in m/s."""
        return self._get_current_data("VEN_RAJ")

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return self._get_current_data("VEN_DIR")

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the feels-like temperature."""
        return self._get_current_data("TEM_SEN")

    @property
    def native_precipitation(self) -> float | None:
        """Return the accumulated rainfall in mm."""
        return self._get_current_data("CHUVA")

    @property
    def native_temperature_low(self) -> float | None:
        """Return the min temperature for the day."""
        return self._get_current_data("TEM_MIN")

    @property
    def native_temperature_high(self) -> float | None:
        """Return the max temperature for the day."""
        return self._get_current_data("TEM_MAX")

    def _get_current_period(self) -> str:
        """Determine the current time period (manha, tarde, noite)."""
        current_hour = datetime.now().hour
        if current_hour < 12:
            return "manha"
        if current_hour < 18:
            return "tarde"
        return "noite"

    def _map_condition(self, resumo: str) -> str | None:
        """Map INMET condition to Home Assistant condition."""
        resumo_lower = resumo.lower()
        for key, value in CONDITION_MAP.items():
            if key in resumo_lower:
                return value
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data or "forecast" not in self.coordinator.data:
            return None

        forecast_data = self.coordinator.data["forecast"]
        today = datetime.now().strftime("%d/%m/%Y")

        for city_data in forecast_data.values():
            if today not in city_data:
                continue

            today_data = city_data[today]
            period = self._get_current_period()
            period_data = today_data.get(period, {})
            resumo = period_data.get("resumo", "")

            if resumo:
                return self._map_condition(resumo)

        return None

    def _generate_forecast_item(
        self, date_obj: datetime, data: dict[str, Any], period: str | None = None
    ) -> Forecast | None:
        """Generate a forecast item from data."""
        if not data:
            return None

        # Determine hour based on period
        hour = PERIOD_HOURS.get(period, 6) if period else 6
        forecast_time = date_obj.replace(hour=hour, minute=0, second=0)

        # Build forecast item
        forecast_item: Forecast = {
            ATTR_FORECAST_TIME: forecast_time.isoformat(),
            ATTR_FORECAST_NATIVE_TEMP: data.get("temp_max"),
            ATTR_FORECAST_NATIVE_TEMP_LOW: data.get("temp_min"),
            ATTR_FORECAST_WIND_BEARING: data.get("dir-vento"),
        }

        # Add condition if available
        resumo = data.get("resumo", "")
        if resumo:
            condition = self._map_condition(resumo)
            if condition:
                forecast_item[ATTR_FORECAST_CONDITION] = condition

        # Add humidity if available
        if "umidade_max" in data:
            forecast_item[ATTR_FORECAST_HUMIDITY] = data["umidade_max"]

        return forecast_item

    def _parse_forecast_data(
        self, forecast_data: dict[str, Any], max_items: int, periods: list[str] | None = None
    ) -> list[Forecast]:
        """Parse forecast data and return list of forecast items.

        Args:
            forecast_data: Raw forecast data from API
            max_items: Maximum number of forecast items to return
            periods: List of periods to include (e.g., ["manha", "tarde", "noite"]).
                    If None, uses "tarde" as default for daily forecast.
        """
        forecasts: list[Forecast] = []

        try:
            for city_data in forecast_data.values():
                for date_str, date_data in city_data.items():
                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                    except ValueError:
                        continue

                    # Check if this is single-period data (has "uf" field)
                    if "uf" in date_data:
                        item = self._generate_forecast_item(date_obj, date_data)
                        if item:
                            forecasts.append(item)
                    else:
                        # Multi-period data
                        if periods is None:
                            # Default to afternoon for daily forecast
                            item = self._generate_forecast_item(
                                date_obj, date_data.get("tarde", {}), "tarde"
                            )
                            if item:
                                forecasts.append(item)
                        else:
                            # Process specified periods
                            for period_key in periods:
                                if period_key in date_data:
                                    item = self._generate_forecast_item(
                                        date_obj, date_data[period_key], period=period_key
                                    )
                                    if item:
                                        forecasts.append(item)

            return forecasts[:max_items]

        except Exception as err:
            _LOGGER.error("Error parsing forecast data: %s", err)
            return []

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        if not self.coordinator.data or "forecast" not in self.coordinator.data:
            return None

        forecast_data = self.coordinator.data["forecast"]
        return self._parse_forecast_data(
            forecast_data, max_items=15, periods=["manha", "tarde", "noite"]
        )

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the twice daily forecast."""
        if not self.coordinator.data or "forecast" not in self.coordinator.data:
            return None

        forecast_data = self.coordinator.data["forecast"]
        return self._parse_forecast_data(
            forecast_data, max_items=14, periods=["manha", "tarde", "noite"]
        )

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        if not self.coordinator.data or "forecast" not in self.coordinator.data:
            return None

        forecast_data = self.coordinator.data["forecast"]
        return self._parse_forecast_data(forecast_data, max_items=7, periods=None)
