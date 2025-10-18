"""Tests for INMET Weather integration initialization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

from custom_components.inmet_weather import (DOMAIN, async_setup,
                                             async_setup_entry,
                                             async_unload_entry)


@pytest.mark.asyncio
async def test_async_setup():
    """Test the async_setup function."""
    hass = MagicMock()
    config = {}

    result = await async_setup(hass, config)

    assert result is True


@pytest.mark.asyncio
async def test_async_setup_entry(mock_config_entry):
    """Test setting up the integration from a config entry."""
    hass = MagicMock()
    hass.data = {}

    entry = MagicMock(spec=ConfigEntry)
    entry.data = mock_config_entry

    # Create an AsyncMock that returns None when awaited
    mock_forward = AsyncMock(return_value=None)
    hass.config_entries.async_forward_entry_setups = mock_forward

    result = await async_setup_entry(hass, entry)

    assert result is True
    assert DOMAIN in hass.data
    mock_forward.assert_called_once_with(entry, ["weather"])


@pytest.mark.asyncio
async def test_async_setup_entry_creates_domain_data():
    """Test that async_setup_entry creates domain data structure."""
    hass = MagicMock()
    hass.data = {}

    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        CONF_NAME: "Test Weather",
        CONF_LATITUDE: -22.9068,
        CONF_LONGITUDE: -43.1729,
        "geocode": "3304557",
    }

    # Create an AsyncMock that returns None when awaited
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    await async_setup_entry(hass, entry)

    assert DOMAIN in hass.data
    assert isinstance(hass.data[DOMAIN], dict)


@pytest.mark.asyncio
async def test_async_unload_entry_success():
    """Test successful unloading of config entry."""
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_entry_id": {}}}

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"

    # Create an AsyncMock that returns True when awaited
    mock_unload = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = mock_unload

    result = await async_unload_entry(hass, entry)

    assert result is True
    assert "test_entry_id" not in hass.data[DOMAIN]
    mock_unload.assert_called_once_with(entry, ["weather"])


@pytest.mark.asyncio
async def test_async_unload_entry_failure():
    """Test failed unloading of config entry."""
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_entry_id": {}}}

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"

    # Create an AsyncMock that returns False when awaited
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    result = await async_unload_entry(hass, entry)

    assert result is False
    # Data should still be present since unload failed
    assert "test_entry_id" in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_missing_data():
    """Test unloading when entry data is not in hass.data."""
    hass = MagicMock()
    hass.data = {DOMAIN: {}}

    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "missing_entry_id"

    # Create an AsyncMock that returns True when awaited
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)

    # Should still return True even if entry wasn't in data
    assert result is True


@pytest.mark.asyncio
async def test_platforms_loaded():
    """Test that weather platform is loaded."""
    hass = MagicMock()
    hass.data = {}

    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        CONF_NAME: "Test Weather",
        CONF_LATITUDE: -22.9068,
        CONF_LONGITUDE: -43.1729,
        "geocode": "3304557",
    }

    # Create an AsyncMock that returns None when awaited
    mock_forward = AsyncMock(return_value=None)
    hass.config_entries.async_forward_entry_setups = mock_forward

    await async_setup_entry(hass, entry)

    # Verify weather platform was loaded
    call_args = mock_forward.call_args[0]
    assert "weather" in call_args[1]
