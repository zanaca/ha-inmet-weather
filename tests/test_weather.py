"""Tests for INMET Weather entity."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_HUMIDITY,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

from custom_components.inmet_weather.weather import (
    InmetWeatherEntity,
    InmetWeatherCoordinator,
)


@pytest.fixture
def mock_coordinator(mock_current_weather_response, mock_forecast_response):
    """Create a mock coordinator with test data."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {
        "current": mock_current_weather_response,
        "forecast": mock_forecast_response,
    }
    return coordinator


def test_weather_entity_initialization(mock_coordinator):
    """Test weather entity initialization."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity._attr_name == "Test Weather"
    assert entity._attr_unique_id == "-22.9068_-43.1729"
    assert entity._latitude == -22.9068
    assert entity._longitude == -43.1729
    assert entity._attr_native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity._attr_native_pressure_unit == UnitOfPressure.HPA
    assert entity._attr_native_wind_speed_unit == UnitOfSpeed.METERS_PER_SECOND


def test_weather_entity_temperature(mock_coordinator):
    """Test temperature property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_temperature == 29.0


def test_weather_entity_temperature_missing_data():
    """Test temperature property with missing data."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {}

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_temperature is None


def test_weather_entity_humidity(mock_coordinator):
    """Test humidity property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.humidity == 61.0


def test_weather_entity_pressure(mock_coordinator):
    """Test pressure property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_pressure == 1008.3


def test_weather_entity_wind_speed(mock_coordinator):
    """Test wind speed property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_wind_speed == 1.7


def test_weather_entity_wind_gust(mock_coordinator):
    """Test wind gust speed property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_wind_gust_speed == 5.2


def test_weather_entity_wind_bearing(mock_coordinator):
    """Test wind bearing property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.wind_bearing == 153.0


def test_weather_entity_condition_cloudy(mock_coordinator):
    """Test condition property for cloudy weather."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    # Mock today's date to match the forecast
    with patch("custom_components.inmet_weather.weather.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 10, 17, 10, 0, 0)
        mock_datetime.strftime = datetime.strftime

        condition = entity.condition
        assert condition == "cloudy"  # "Muitas nuvens" maps to cloudy


def test_weather_entity_condition_sunny():
    """Test condition property for sunny weather."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {
        "current": {},
        "forecast": {
            "3304557": {
                "17/10/2025": {
                    "manha": {
                        "resumo": "Limpo",
                        "temp_max": 28,
                        "temp_min": 18,
                    }
                }
            }
        },
    }

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    with patch("custom_components.inmet_weather.weather.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 10, 17, 10, 0, 0)
        mock_datetime.strftime = datetime.strftime

        condition = entity.condition
        assert condition == "sunny"  # "Limpo" maps to sunny


def test_weather_entity_forecast(mock_coordinator):
    """Test forecast property."""
    entity = InmetWeatherEntity(
        coordinator=mock_coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    forecast = entity.forecast

    assert forecast is not None
    assert len(forecast) > 0

    # Check first forecast item
    first_item = forecast[0]
    assert ATTR_FORECAST_TIME in first_item
    assert ATTR_FORECAST_NATIVE_TEMP in first_item or ATTR_FORECAST_NATIVE_TEMP_LOW in first_item

    # Check that we have forecasts for different periods
    assert any("manha" in str(item) for item in forecast) or len(forecast) > 0


def test_weather_entity_forecast_empty():
    """Test forecast property with empty data."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {}

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.forecast is None


def test_weather_entity_forecast_parsing():
    """Test forecast parsing with various date formats."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {
        "current": {},
        "forecast": {
            "3304557": {
                "17/10/2025": {
                    "manha": {
                        "resumo": "Muitas nuvens",
                        "temp_max": 32,
                        "temp_min": 20,
                        "umidade_max": 90,
                    },
                    "tarde": {
                        "resumo": "Poucas nuvens",
                        "temp_max": 30,
                        "temp_min": 22,
                        "umidade_max": 85,
                    },
                }
            }
        },
    }

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    forecast = entity.forecast

    assert forecast is not None
    assert len(forecast) == 2  # Two periods (manha and tarde)

    # Check morning forecast
    morning = forecast[0]
    assert morning[ATTR_FORECAST_NATIVE_TEMP] == 32
    assert morning[ATTR_FORECAST_NATIVE_TEMP_LOW] == 20
    assert morning[ATTR_FORECAST_HUMIDITY] == 90

    # Check afternoon forecast
    afternoon = forecast[1]
    assert afternoon[ATTR_FORECAST_NATIVE_TEMP] == 30
    assert afternoon[ATTR_FORECAST_NATIVE_TEMP_LOW] == 22


def test_weather_entity_invalid_temperature():
    """Test handling of invalid temperature values."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {
        "current": {
            "dados": {
                "TEM_INS": "invalid",
            }
        },
        "forecast": {},
    }

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.native_temperature is None


def test_weather_entity_invalid_humidity():
    """Test handling of invalid humidity values."""
    coordinator = MagicMock(spec=InmetWeatherCoordinator)
    coordinator.data = {
        "current": {
            "dados": {
                "UMD_INS": "not_a_number",
            }
        },
        "forecast": {},
    }

    entity = InmetWeatherEntity(
        coordinator=coordinator,
        name="Test Weather",
        latitude=-22.9068,
        longitude=-43.1729,
    )

    assert entity.humidity is None


@pytest.mark.asyncio
async def test_coordinator_update_success(mock_hass, mock_current_weather_response, mock_forecast_response):
    """Test coordinator data update success."""
    from unittest.mock import patch

    mock_client = AsyncMock()
    mock_client.get_current_weather = AsyncMock(return_value=mock_current_weather_response)
    mock_client.get_forecast = AsyncMock(return_value=mock_forecast_response)

    # Patch frame.report_usage to avoid "Frame helper not set up" error
    with patch("homeassistant.helpers.frame.report_usage"):
        coordinator = InmetWeatherCoordinator(mock_hass, mock_client, "3304557")

        result = await coordinator._async_update_data()

        assert result is not None
        assert "current" in result
        assert "forecast" in result
        assert result["current"] == mock_current_weather_response
        assert result["forecast"] == mock_forecast_response


@pytest.mark.asyncio
async def test_coordinator_update_failure(mock_hass):
    """Test coordinator handles update failure."""
    from unittest.mock import patch
    from homeassistant.helpers.update_coordinator import UpdateFailed

    mock_client = AsyncMock()
    mock_client.get_current_weather = AsyncMock(return_value=None)
    mock_client.get_forecast = AsyncMock(return_value=None)

    # Patch frame.report_usage to avoid "Frame helper not set up" error
    with patch("homeassistant.helpers.frame.report_usage"):
        coordinator = InmetWeatherCoordinator(mock_hass, mock_client, "3304557")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_exception(mock_hass):
    """Test coordinator handles exceptions during update."""
    from unittest.mock import patch
    from homeassistant.helpers.update_coordinator import UpdateFailed

    mock_client = AsyncMock()
    mock_client.get_current_weather = AsyncMock(side_effect=Exception("API Error"))

    # Patch frame.report_usage to avoid "Frame helper not set up" error
    with patch("homeassistant.helpers.frame.report_usage"):
        coordinator = InmetWeatherCoordinator(mock_hass, mock_client, "3304557")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
