"""Simple tests for INMET Weather API client (no HA dependency)."""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch, ANY

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from custom_components.inmet_weather.api import InmetApiClient


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_rio():
    """Test geocode detection for Rio de Janeiro."""
    session = MagicMock()
    client = InmetApiClient(session)

    # Test coordinates near Rio de Janeiro
    geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)

    assert geocode == "3304557"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_sao_paulo():
    """Test geocode detection for São Paulo."""
    session = MagicMock()
    client = InmetApiClient(session)

    # Test coordinates near São Paulo
    geocode = await client.get_geocode_from_coordinates(-23.5505, -46.6333)

    assert geocode == "3550308"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_brasilia():
    """Test geocode detection for Brasília."""
    session = MagicMock()
    client = InmetApiClient(session)

    # Test coordinates near Brasília
    geocode = await client.get_geocode_from_coordinates(-15.7939, -47.8828)

    assert geocode == "5300108"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_error():
    """Test geocode detection handles errors."""
    session = MagicMock()
    client = InmetApiClient(session)

    with patch.object(client, "calculate_distance", side_effect=Exception("Test error")):
        geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)
        assert geocode is None


@pytest.mark.asyncio
async def test_get_current_weather_success():
    """Test successful current weather fetch."""
    session = MagicMock()
    client = InmetApiClient(session)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "dados": {
            "TEM_INS": "29",
            "UMD_INS": "61",
            "PRE_INS": "1008.3",
            "VEN_VEL": "1.7",
            "VEN_RAJ": "5.2",
        }
    })

    # Create a proper async context manager
    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_context)

    result = await client.get_current_weather("3304557")

    assert result is not None
    assert result["dados"]["TEM_INS"] == "29"
    assert result["dados"]["UMD_INS"] == "61"


@pytest.mark.asyncio
async def test_get_current_weather_error():
    """Test current weather fetch handles errors."""
    session = MagicMock()
    client = InmetApiClient(session)

    mock_response = MagicMock()
    mock_response.status = 404

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_context)

    result = await client.get_current_weather("3304557")

    assert result is None


@pytest.mark.asyncio
async def test_get_forecast_success():
    """Test successful forecast fetch."""
    session = MagicMock()
    client = InmetApiClient(session)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "3304557": {
            "17/10/2025": {
                "manha": {
                    "resumo": "Muitas nuvens",
                    "temp_max": 32,
                }
            }
        }
    })

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_context)

    result = await client.get_forecast("3304557")

    assert result is not None
    assert "3304557" in result
    assert "17/10/2025" in result["3304557"]


@pytest.mark.asyncio
async def test_get_forecast_error():
    """Test forecast fetch handles errors."""
    session = MagicMock()
    client = InmetApiClient(session)

    mock_response = MagicMock()
    mock_response.status = 500

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_context)

    result = await client.get_forecast("3304557")

    assert result is None


def test_calculate_distance():
    """Test distance calculation using Haversine formula."""
    session = MagicMock()
    client = InmetApiClient(session)

    # Distance between Rio de Janeiro and São Paulo (approximately 360 km)
    distance = client.calculate_distance(-22.9068, -43.1729, -23.5505, -46.6333)

    # Should be approximately 360 km
    assert 350 < distance < 370


def test_calculate_distance_same_point():
    """Test distance calculation for the same point."""
    session = MagicMock()
    client = InmetApiClient(session)

    distance = client.calculate_distance(-22.9068, -43.1729, -22.9068, -43.1729)

    assert distance == 0.0


def test_calculate_distance_equator():
    """Test distance calculation across equator."""
    session = MagicMock()
    client = InmetApiClient(session)

    # Distance from equator at 0,0 to equator at 1,0 (approximately 111 km)
    distance = client.calculate_distance(0, 0, 1, 0)

    # Should be approximately 111 km (1 degree of latitude)
    assert 110 < distance < 112
