"""Simple tests for INMET Weather API client (no HA dependency)."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_components.inmet_weather.api import InmetApiClient  # noqa: E402


@pytest.mark.asyncio
async def test_get_geocode_from_coordinates_error(temp_cache_dir):
    """Test geocode detection handles errors."""
    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock both API call and distance calculation to fail
    mock_response = AsyncMock()
    mock_response.status = 500
    session.get = MagicMock(
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
    )

    with patch.object(
        client, "calculate_distance", side_effect=Exception("Test error")
    ):
        geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)
        assert geocode is None


@pytest.mark.asyncio
async def test_get_current_weather_success():
    """Test successful current weather fetch."""
    session = MagicMock()
    client = InmetApiClient(session)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "dados": {
                "TEM_INS": "29",
                "UMD_INS": "61",
                "PRE_INS": "1008.3",
                "VEN_VEL": "1.7",
                "VEN_RAJ": "5.2",
            }
        }
    )

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
    mock_response.json = AsyncMock(
        return_value={
            "3304557": {
                "17/10/2025": {
                    "manha": {
                        "resumo": "Muitas nuvens",
                        "temp_max": 32,
                    }
                }
            }
        }
    )

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


@pytest.mark.asyncio
async def test_get_nearest_station_success(temp_cache_dir):
    """Test successful nearest station fetch."""
    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(
        return_value={
            "3304557": {
                "centroide": {"lat": -22.9068, "lon": -43.1729},
                "nome": "Rio de Janeiro",
            }
        }
    )

    # Mock station response
    mock_station_response = MagicMock()
    mock_station_response.status = 200
    mock_station_response.json = AsyncMock(
        return_value={
            "estacao": {
                "CODIGO": "A636",
                "NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
                "GEOCODE": "3304557",
            }
        }
    )

    # Create async context managers
    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_station_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)
    session.get = MagicMock(return_value=mock_get_context)

    result = await client.get_nearest_station(-22.9068, -43.1729)

    assert result is not None
    assert result["estacao"]["GEOCODE"] == "3304557"


@pytest.mark.asyncio
async def test_get_nearest_station_cache_hit(temp_cache_dir):
    """Test that cached station data is returned on second call."""

    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(
        return_value={
            "3304557": {
                "centroide": {"lat": -22.9068, "lon": -43.1729},
                "nome": "Rio de Janeiro",
            }
        }
    )

    # Mock station response
    mock_station_response = MagicMock()
    mock_station_response.status = 200
    station_data = {
        "estacao": {
            "CODIGO": "A636",
            "NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
            "GEOCODE": "3304557",
        }
    }
    mock_station_response.json = AsyncMock(return_value=station_data)

    # Create async context managers
    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_station_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)
    session.get = MagicMock(return_value=mock_get_context)

    # First call - should fetch from API
    result1 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result1 is not None
    assert session.get.call_count == 1

    # Second call - should use cache
    result2 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result2 is not None
    assert result2 == result1
    # API should not be called again
    assert session.get.call_count == 1


@pytest.mark.asyncio
async def test_get_nearest_station_cache_expiration(temp_cache_dir):
    """Test that cache expires after 2 hours."""
    import time

    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(
        return_value={
            "3304557": {
                "centroide": {"lat": -22.9068, "lon": -43.1729},
                "nome": "Rio de Janeiro",
            }
        }
    )

    # Mock station response
    mock_station_response = MagicMock()
    mock_station_response.status = 200
    station_data = {
        "estacao": {
            "CODIGO": "A636",
            "NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
            "GEOCODE": "3304557",
        }
    }
    mock_station_response.json = AsyncMock(return_value=station_data)

    # Create async context managers
    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_station_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)
    session.get = MagicMock(return_value=mock_get_context)

    # First call - should fetch from API
    result1 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result1 is not None
    assert session.get.call_count == 1

    # Manually expire the cache by setting timestamp to 3 hours ago
    cache_key = client._get_cache_key(-22.9068, -43.1729)
    client._station_cache[cache_key]["timestamp"] = time.time() - 10800  # 3 hours

    # Second call - cache expired, should fetch from API again
    result2 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result2 is not None
    # API should be called again
    assert session.get.call_count == 2


@pytest.mark.asyncio
async def test_get_nearest_station_no_geocode(temp_cache_dir):
    """Test nearest station fetch when geocode is not found."""
    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock empty geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(return_value={})

    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)

    result = await client.get_nearest_station(-22.9068, -43.1729)

    assert result is None


@pytest.mark.asyncio
async def test_get_nearest_station_error(temp_cache_dir):
    """Test nearest station fetch handles errors."""
    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(
        return_value={
            "3304557": {
                "centroide": {"lat": -22.9068, "lon": -43.1729},
                "nome": "Rio de Janeiro",
            }
        }
    )

    # Mock station error response
    mock_station_response = MagicMock()
    mock_station_response.status = 500

    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_station_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)
    session.get = MagicMock(return_value=mock_get_context)

    result = await client.get_nearest_station(-22.9068, -43.1729)

    assert result is None


@pytest.mark.asyncio
async def test_get_current_weather_fallback_on_error():
    """Test that current weather returns last successful result on error."""
    session = MagicMock()
    client = InmetApiClient(session)

    # First successful response
    mock_success_response = MagicMock()
    mock_success_response.status = 200
    success_data = {
        "dados": {
            "TEM_INS": "29",
            "UMD_INS": "61",
        }
    }
    mock_success_response.json = AsyncMock(return_value=success_data)

    # Second failed response
    mock_error_response = MagicMock()
    mock_error_response.status = 500

    mock_success_context = MagicMock()
    mock_success_context.__aenter__ = AsyncMock(return_value=mock_success_response)
    mock_success_context.__aexit__ = AsyncMock(return_value=None)

    mock_error_context = MagicMock()
    mock_error_context.__aenter__ = AsyncMock(return_value=mock_error_response)
    mock_error_context.__aexit__ = AsyncMock(return_value=None)

    # First call succeeds, second fails
    session.get = MagicMock(side_effect=[mock_success_context, mock_error_context])

    # First call should succeed
    result1 = await client.get_current_weather("3304557")
    assert result1 is not None
    assert result1 == success_data

    # Second call should return cached successful result despite error
    result2 = await client.get_current_weather("3304557")
    assert result2 is not None
    assert result2 == success_data


@pytest.mark.asyncio
async def test_get_forecast_fallback_on_error():
    """Test that forecast returns last successful result on error."""
    session = MagicMock()
    client = InmetApiClient(session)

    # First successful response
    mock_success_response = MagicMock()
    mock_success_response.status = 200
    success_data = {
        "3304557": {
            "17/10/2025": {"manha": {"resumo": "Muitas nuvens", "temp_max": 32}}
        }
    }
    mock_success_response.json = AsyncMock(return_value=success_data)

    # Second failed response
    mock_error_response = MagicMock()
    mock_error_response.status = 500

    mock_success_context = MagicMock()
    mock_success_context.__aenter__ = AsyncMock(return_value=mock_success_response)
    mock_success_context.__aexit__ = AsyncMock(return_value=None)

    mock_error_context = MagicMock()
    mock_error_context.__aenter__ = AsyncMock(return_value=mock_error_response)
    mock_error_context.__aexit__ = AsyncMock(return_value=None)

    # First call succeeds, second fails
    session.get = MagicMock(side_effect=[mock_success_context, mock_error_context])

    # First call should succeed
    result1 = await client.get_forecast("3304557")
    assert result1 is not None
    assert result1 == success_data

    # Second call should return cached successful result despite error
    result2 = await client.get_forecast("3304557")
    assert result2 is not None
    assert result2 == success_data


@pytest.mark.asyncio
async def test_get_nearest_station_fallback_on_error(temp_cache_dir):
    """Test that nearest station returns last successful result on error."""
    session = MagicMock()
    client = InmetApiClient(session, cache_dir=temp_cache_dir)

    # Mock geocode response
    mock_geocode_response = MagicMock()
    mock_geocode_response.status = 200
    mock_geocode_response.json = AsyncMock(
        return_value={
            "3304557": {
                "centroide": {"lat": -22.9068, "lon": -43.1729},
                "nome": "Rio de Janeiro",
            }
        }
    )

    # First successful station response
    mock_success_station = MagicMock()
    mock_success_station.status = 200
    success_data = {
        "estacao": {
            "CODIGO": "A636",
            "NOME": "RIO DE JANEIRO - JACAREPAGUÁ",
            "GEOCODE": "3304557",
        }
    }
    mock_success_station.json = AsyncMock(return_value=success_data)

    # Second failed station response
    mock_error_station = MagicMock()
    mock_error_station.status = 500

    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_geocode_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)

    mock_success_get_context = MagicMock()
    mock_success_get_context.__aenter__ = AsyncMock(return_value=mock_success_station)
    mock_success_get_context.__aexit__ = AsyncMock(return_value=None)

    mock_error_get_context = MagicMock()
    mock_error_get_context.__aenter__ = AsyncMock(return_value=mock_error_station)
    mock_error_get_context.__aexit__ = AsyncMock(return_value=None)

    session.post = MagicMock(return_value=mock_post_context)
    session.get = MagicMock(
        side_effect=[mock_success_get_context, mock_error_get_context]
    )

    # First call should succeed
    result1 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result1 is not None
    assert result1 == success_data

    # Expire the cache to force a new API call
    import time

    cache_key = client._get_cache_key(-22.9068, -43.1729)
    client._station_cache[cache_key]["timestamp"] = time.time() - 10800  # 3 hours ago

    # Second call should return cached successful result despite error
    result2 = await client.get_nearest_station(-22.9068, -43.1729)
    assert result2 is not None
    assert result2 == success_data


@pytest.mark.asyncio
async def test_get_current_weather_fallback_on_exception():
    """Test that current weather returns last successful result on exception."""
    session = MagicMock()
    client = InmetApiClient(session)

    # First successful response
    mock_success_response = MagicMock()
    mock_success_response.status = 200
    success_data = {"dados": {"TEM_INS": "29"}}
    mock_success_response.json = AsyncMock(return_value=success_data)

    mock_success_context = MagicMock()
    mock_success_context.__aenter__ = AsyncMock(return_value=mock_success_response)
    mock_success_context.__aexit__ = AsyncMock(return_value=None)

    # First call succeeds, second raises exception
    session.get = MagicMock(
        side_effect=[mock_success_context, Exception("Network error")]
    )

    # First call should succeed
    result1 = await client.get_current_weather("3304557")
    assert result1 is not None
    assert result1 == success_data

    # Second call should return cached successful result despite exception
    result2 = await client.get_current_weather("3304557")
    assert result2 is not None
    assert result2 == success_data
