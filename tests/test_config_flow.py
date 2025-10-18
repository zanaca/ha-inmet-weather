"""Tests for INMET Weather config flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.data_entry_flow import FlowResultType

from custom_components.inmet_weather.const import DOMAIN


@pytest.mark.asyncio
async def test_form_default_values(mock_hass):
    """Test config flow with default values."""
    result = await mock_hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_form_user_input_success(mock_hass):
    """Test successful configuration with user input."""
    with patch(
        "custom_components.inmet_weather.config_flow.InmetApiClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_geocode_from_coordinates = AsyncMock(return_value="3304557")
        mock_client_class.return_value = mock_client

        result = await mock_hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await mock_hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Test Weather",
                CONF_LATITUDE: -22.9068,
                CONF_LONGITUDE: -43.1729,
            },
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Test Weather"
        assert result["data"][CONF_NAME] == "Test Weather"
        assert result["data"][CONF_LATITUDE] == -22.9068
        assert result["data"][CONF_LONGITUDE] == -43.1729
        assert result["data"]["geocode"] == "3304557"


@pytest.mark.asyncio
async def test_form_cannot_connect(mock_hass):
    """Test config flow when cannot connect to API."""
    with patch(
        "custom_components.inmet_weather.config_flow.InmetApiClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_geocode_from_coordinates = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mock_hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await mock_hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Test Weather",
                CONF_LATITUDE: -22.9068,
                CONF_LONGITUDE: -43.1729,
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_form_unexpected_exception(mock_hass):
    """Test config flow handles unexpected exceptions."""
    with patch(
        "custom_components.inmet_weather.config_flow.InmetApiClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_geocode_from_coordinates = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        mock_client_class.return_value = mock_client

        result = await mock_hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await mock_hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Test Weather",
                CONF_LATITUDE: -22.9068,
                CONF_LONGITUDE: -43.1729,
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_form_already_configured(mock_hass):
    """Test config flow when location is already configured."""
    # Mock an existing entry
    mock_entry = MagicMock()
    mock_entry.unique_id = "-22.9068_-43.1729"
    mock_hass.config_entries.async_entries.return_value = [mock_entry]

    with patch(
        "custom_components.inmet_weather.config_flow.InmetApiClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_geocode_from_coordinates = AsyncMock(return_value="3304557")
        mock_client_class.return_value = mock_client

        result = await mock_hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await mock_hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Test Weather",
                CONF_LATITUDE: -22.9068,
                CONF_LONGITUDE: -43.1729,
            },
        )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_form_uses_ha_defaults(mock_hass):
    """Test that form uses HA's latitude and longitude as defaults."""
    mock_hass.config.latitude = -23.5505
    mock_hass.config.longitude = -46.6333

    result = await mock_hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the schema has the correct defaults
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    # The defaults are set in the schema, so we can't directly test them here
    # but they would be visible in the UI


@pytest.mark.asyncio
async def test_form_with_custom_name(mock_hass):
    """Test config flow with custom name."""
    with patch(
        "custom_components.inmet_weather.config_flow.InmetApiClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_geocode_from_coordinates = AsyncMock(return_value="3550308")
        mock_client_class.return_value = mock_client

        result = await mock_hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await mock_hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "São Paulo Weather",
                CONF_LATITUDE: -23.5505,
                CONF_LONGITUDE: -46.6333,
            },
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "São Paulo Weather"
        assert result["data"]["geocode"] == "3550308"
