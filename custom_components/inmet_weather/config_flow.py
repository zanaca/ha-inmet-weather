"""Config flow for INMET Weather integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import config_validation as cv

from .api import InmetApiClient
from .const import DOMAIN
from .geo_utils import is_in_brazil

_LOGGER = logging.getLogger(__name__)


class InmetWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for INMET Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Use Home Assistant's configured latitude and longitude by default
            latitude = user_input.get(CONF_LATITUDE, self.hass.config.latitude)
            longitude = user_input.get(CONF_LONGITUDE, self.hass.config.longitude)
            name = user_input.get(CONF_NAME, "INMET Weather")

            # First, check if coordinates are within Brazil
            if not await is_in_brazil(latitude, longitude):
                errors["base"] = "outside_brazil"
                _LOGGER.warning(
                    "Coordinates (%.4f, %.4f) are outside Brazil's boundaries",
                    latitude,
                    longitude,
                )
            else:
                # Validate the coordinates by trying to fetch data
                try:
                    session = aiohttp_client.async_get_clientsession(self.hass)
                    client = InmetApiClient(session)

                    # Try to get the geocode
                    geocode = await client.get_geocode_from_coordinates(
                        latitude, longitude
                    )

                    if geocode:
                        # Create a unique ID based on coordinates
                        await self.async_set_unique_id(f"{latitude}_{longitude}")
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=name,
                            data={
                                CONF_NAME: name,
                                CONF_LATITUDE: latitude,
                                CONF_LONGITUDE: longitude,
                                "geocode": geocode,
                            },
                        )
                    else:
                        errors["base"] = "cannot_connect"

                except Exception as err:
                    _LOGGER.exception("Unexpected exception: %s", err)
                    errors["base"] = "unknown"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default="INMET Weather"): cv.string,
                    vol.Optional(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                }
            ),
            errors=errors,
        )
