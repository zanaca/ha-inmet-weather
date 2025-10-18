"""Weather platform for INMET Weather integration."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
    Forecast,
    WeatherEntity,
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


class InmetWeatherCoordinator(DataUpdateCoordinator):
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

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API."""
        try:
            current = await self.client.get_current_weather(self.geocode)
            forecast = await self.client.get_forecast(self.geocode)

            if current is None or forecast is None:
                raise UpdateFailed("Error fetching data from INMET API")

            return {"current": current, "forecast": forecast}

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class InmetWeatherEntity(CoordinatorEntity, WeatherEntity):
    """INMET Weather Entity."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

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

    @property
    def native_temperature(self) -> Optional[float]:
        """Return the temperature."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                temp = current["dados"].get("TEM_INS")
                if temp:
                    try:
                        return float(temp)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def humidity(self) -> Optional[float]:
        """Return the humidity."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                humidity = current["dados"].get("UMD_INS")
                if humidity:
                    try:
                        return float(humidity)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def native_pressure(self) -> Optional[float]:
        """Return the pressure."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                pressure = current["dados"].get("PRE_INS")
                if pressure:
                    try:
                        return float(pressure)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def native_wind_speed(self) -> Optional[float]:
        """Return the wind speed in m/s."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                wind_speed = current["dados"].get("VEN_VEL")
                if wind_speed:
                    try:
                        return float(wind_speed)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def native_wind_gust_speed(self) -> Optional[float]:
        """Return the wind gust speed in m/s."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                wind_gust = current["dados"].get("VEN_RAJ")
                if wind_gust:
                    try:
                        return float(wind_gust)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def wind_bearing(self) -> Optional[float]:
        """Return the wind bearing."""
        if self.coordinator.data and "current" in self.coordinator.data:
            current = self.coordinator.data["current"]
            if "dados" in current:
                wind_dir = current["dados"].get("VEN_DIR")
                if wind_dir:
                    try:
                        return float(wind_dir)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def condition(self) -> Optional[str]:
        """Return the current condition."""
        if self.coordinator.data and "forecast" in self.coordinator.data:
            forecast_data = self.coordinator.data["forecast"]

            # Get today's forecast
            today = datetime.now().strftime("%d/%m/%Y")

            for city_data in forecast_data.values():
                if today in city_data:
                    today_data = city_data[today]

                    # Get current hour
                    current_hour = datetime.now().hour

                    # Determine which period we're in
                    if current_hour < 12:
                        period_data = today_data.get("manha", {})
                    elif current_hour < 18:
                        period_data = today_data.get("tarde", {})
                    else:
                        period_data = today_data.get("noite", {})

                    resumo = period_data.get("resumo", "").lower()

                    # Map INMET condition to Home Assistant condition
                    for key, value in CONDITION_MAP.items():
                        if key in resumo:
                            return value

        return None

    @property
    def forecast(self) -> Optional[List[Forecast]]:
        """Return the forecast."""
        if not self.coordinator.data or "forecast" not in self.coordinator.data:
            return None

        forecast_data = self.coordinator.data["forecast"]
        forecasts = []

        try:
            for city_data in forecast_data.values():
                for date_str, date_data in city_data.items():
                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                    except ValueError:
                        continue

                    # Process each period
                    for period_key in ["manha", "tarde", "noite"]:
                        if period_key in date_data:
                            period_data = date_data[period_key]

                            # Determine the time for this period
                            if period_key == "manha":
                                hour = 6
                            elif period_key == "tarde":
                                hour = 12
                            else:
                                hour = 18

                            forecast_time = date_obj.replace(
                                hour=hour, minute=0, second=0
                            )

                            # Get condition
                            resumo = period_data.get("resumo", "").lower()
                            condition = None
                            for key, value in CONDITION_MAP.items():
                                if key in resumo:
                                    condition = value
                                    break

                            forecast_item: Forecast = {
                                ATTR_FORECAST_TIME: forecast_time.isoformat(),
                                ATTR_FORECAST_NATIVE_TEMP: period_data.get("temp_max"),
                                ATTR_FORECAST_NATIVE_TEMP_LOW: period_data.get(
                                    "temp_min"
                                ),
                            }

                            if condition:
                                forecast_item[ATTR_FORECAST_CONDITION] = condition

                            # Add humidity if available
                            if "umidade_max" in period_data:
                                forecast_item[ATTR_FORECAST_HUMIDITY] = period_data[
                                    "umidade_max"
                                ]

                            forecasts.append(forecast_item)

            return forecasts[:15]  # Limit to 15 forecast items

        except Exception as err:
            _LOGGER.error("Error parsing forecast data: %s", err)
            return None
