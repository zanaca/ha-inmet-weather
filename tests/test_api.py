"""Tests for INMET Weather API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession

from custom_components.inmet_weather.api import InmetApiClient


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_rio(temp_cache_dir):
    """Test geocode detection for Rio de Janeiro using real API response."""
    session = MagicMock(spec=ClientSession)

    # Mock real Previsao_Portal API response with multiple cities
    mock_api_data = {
        "3304557": {
            "nome": "Rio de Janeiro",
            "uf": "RJ",
            "centroide": {"lat": -22.9068, "lon": -43.1729},
        },
        "3550308": {
            "nome": "São Paulo",
            "uf": "SP",
            "centroide": {"lat": -23.5505, "lon": -46.6333},
        },
        "5300108": {
            "nome": "Brasília",
            "uf": "DF",
            "centroide": {"lat": -15.7939, "lon": -47.8828},
        },
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_api_data)
    session.get = MagicMock(
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
    )

    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Test coordinates near Rio de Janeiro
    geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)

    assert geocode == "3304557"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_sao_paulo(temp_cache_dir):
    """Test geocode detection for São Paulo using real API response."""
    session = MagicMock(spec=ClientSession)

    # Mock real Previsao_Portal API response
    mock_api_data = {
        "3304557": {
            "nome": "Rio de Janeiro",
            "uf": "RJ",
            "centroide": {"lat": -22.9068, "lon": -43.1729},
        },
        "3550308": {
            "nome": "São Paulo",
            "uf": "SP",
            "centroide": {"lat": -23.5505, "lon": -46.6333},
        },
        "5300108": {
            "nome": "Brasília",
            "uf": "DF",
            "centroide": {"lat": -15.7939, "lon": -47.8828},
        },
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_api_data)
    session.get = MagicMock(
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
    )

    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Test coordinates near São Paulo
    geocode = await client.get_geocode_from_coordinates(-23.5505, -46.6333)

    assert geocode == "3550308"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_brasilia(temp_cache_dir):
    """Test geocode detection for Brasília using real API response."""
    session = MagicMock(spec=ClientSession)

    # Mock real Previsao_Portal API response
    mock_api_data = {
        "3304557": {
            "nome": "Rio de Janeiro",
            "uf": "RJ",
            "centroide": {"lat": -22.9068, "lon": -43.1729},
        },
        "3550308": {
            "nome": "São Paulo",
            "uf": "SP",
            "centroide": {"lat": -23.5505, "lon": -46.6333},
        },
        "5300108": {
            "nome": "Brasília",
            "uf": "DF",
            "centroide": {"lat": -15.7939, "lon": -47.8828},
        },
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_api_data)
    session.get = MagicMock(
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
    )

    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Test coordinates near Brasília
    geocode = await client.get_geocode_from_coordinates(-15.7939, -47.8828)

    assert geocode == "5300108"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_fallback(temp_cache_dir):
    """Test geocode detection falls back to distance calculation when API fails."""
    session = MagicMock(spec=ClientSession)

    # Mock API failure to test fallback mechanism
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_response)

    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Test coordinates in the middle of the ocean (0,0 - Gulf of Guinea)
    # Algorithm should find Natal as it's the closest Brazilian city to the equator
    geocode = await client.get_geocode_from_coordinates(0, 0)

    # Should return Natal (2408102) as it's closest to equator
    assert geocode == "2408102"


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_error(temp_cache_dir):
    """Test geocode detection handles errors."""
    session = MagicMock(spec=ClientSession)

    # Mock API failure
    mock_response = AsyncMock()
    mock_response.status = 500
    session.get = MagicMock(
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
    )

    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    with patch.object(
        client, "calculate_distance", side_effect=Exception("Test error")
    ):
        geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)
        assert geocode is None


@pytest.mark.asyncio
async def test_get_current_weather_success(mock_current_weather_response):
    """Test successful current weather fetch."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_current_weather_response)

    with patch.object(session, "get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await client.get_current_weather("3304557")

        assert result is not None
        assert result["dados"]["TEM_INS"] == "29"
        assert result["dados"]["UMD_INS"] == "61"
        assert result["dados"]["PRE_INS"] == "1008.3"
        assert result["dados"]["VEN_VEL"] == "1.7"
        assert result["dados"]["VEN_RAJ"] == "5.2"


@pytest.mark.asyncio
async def test_get_current_weather_error():
    """Test current weather fetch handles errors."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    mock_response = AsyncMock()
    mock_response.status = 404

    with patch.object(session, "get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await client.get_current_weather("3304557")

        assert result is None


@pytest.mark.asyncio
async def test_get_current_weather_timeout():
    """Test current weather fetch handles timeout."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    with patch.object(session, "get", side_effect=Exception("Timeout")):
        result = await client.get_current_weather("3304557")
        assert result is None


@pytest.mark.asyncio
async def test_get_forecast_success(mock_forecast_response):
    """Test successful forecast fetch."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_forecast_response)

    with patch.object(session, "get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await client.get_forecast("3304557")

        assert result is not None
        assert "3304557" in result
        assert "17/10/2025" in result["3304557"]
        assert "manha" in result["3304557"]["17/10/2025"]
        assert result["3304557"]["17/10/2025"]["manha"]["resumo"] == "Muitas nuvens"


@pytest.mark.asyncio
async def test_get_forecast_error():
    """Test forecast fetch handles errors."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    mock_response = AsyncMock()
    mock_response.status = 500

    with patch.object(session, "get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await client.get_forecast("3304557")

        assert result is None


@pytest.mark.asyncio
async def test_get_forecast_timeout():
    """Test forecast fetch handles timeout."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    with patch.object(session, "get", side_effect=Exception("Timeout")):
        result = await client.get_forecast("3304557")
        assert result is None


def test_calculate_distance():
    """Test distance calculation using Haversine formula."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    # Distance between Rio de Janeiro and São Paulo (approximately 360 km)
    distance = client.calculate_distance(-22.9068, -43.1729, -23.5505, -46.6333)

    # Should be approximately 360 km
    assert 350 < distance < 370


def test_calculate_distance_same_point():
    """Test distance calculation for the same point."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    distance = client.calculate_distance(-22.9068, -43.1729, -22.9068, -43.1729)

    assert distance == 0.0


def test_calculate_distance_equator():
    """Test distance calculation across equator."""
    session = MagicMock(spec=ClientSession)
    client = InmetApiClient(session)

    # Distance from equator at 0,0 to equator at 1,0 (approximately 111 km)
    distance = client.calculate_distance(0, 0, 1, 0)

    # Should be approximately 111 km (1 degree of latitude)
    assert 110 < distance < 112
