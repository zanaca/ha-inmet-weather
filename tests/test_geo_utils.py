"""Tests for geographic utilities."""

import pytest

from custom_components.inmet_weather.geo_utils import (
    get_geojson_file_path,
    is_geojson_available,
    is_in_brazil,
)


@pytest.mark.asyncio
async def test_is_in_brazil_valid_coordinates():
    """Test coordinates that are within Brazil."""
    # Rio de Janeiro
    assert await is_in_brazil(-22.9068, -43.1729) is True

    # São Paulo
    assert await is_in_brazil(-23.5505, -46.6333) is True

    # Brasília
    assert await is_in_brazil(-15.7939, -47.8828) is True

    # Porto Alegre (Rio Grande do Sul - southern Brazil)
    assert await is_in_brazil(-30.0346, -51.2177) is True

    # Boa Vista (Roraima - northern Brazil)
    assert await is_in_brazil(2.8235, -60.6758) is True

    # Manaus (Amazonas - western Brazil)
    assert await is_in_brazil(-3.1190, -60.0217) is True

    # Recife (Pernambuco - eastern Brazil)
    assert await is_in_brazil(-8.0476, -34.8770) is True


@pytest.mark.asyncio
async def test_is_in_brazil_boundary_coordinates():
    """Test coordinates near Brazil's boundaries."""
    # Test coordinates near southern boundary (Rio Grande do Sul)
    assert await is_in_brazil(-33.0, -53.0) is True  # Inside southern Brazil

    # Test coordinates near northern boundary (Roraima)
    assert await is_in_brazil(4.0, -60.0) is True  # Inside northern Brazil

    # Test coordinates in center of Brazil
    assert await is_in_brazil(-15.0, -50.0) is True  # Central Brazil


@pytest.mark.asyncio
async def test_is_in_brazil_outside_coordinates():
    """Test coordinates that are outside Brazil."""
    # Argentina (Buenos Aires)
    assert await is_in_brazil(-34.6037, -58.3816) is False

    # Uruguay (Montevideo)
    assert await is_in_brazil(-34.9011, -56.1645) is False

    # Paraguay (Asunción)
    assert await is_in_brazil(-25.2637, -57.5759) is False

    # Colombia (Bogotá)
    assert await is_in_brazil(4.7110, -74.0721) is False

    # Venezuela (Caracas)
    assert await is_in_brazil(10.4806, -66.9036) is False

    # Peru (Lima)
    assert await is_in_brazil(-12.0464, -77.0428) is False

    # Atlantic Ocean (too far east)
    assert await is_in_brazil(-23.5505, -20.0) is False

    # Pacific Ocean (too far west)
    assert await is_in_brazil(-15.0, -80.0) is False

    # North of Brazil
    assert await is_in_brazil(10.0, -50.0) is False

    # South of Brazil
    assert await is_in_brazil(-40.0, -50.0) is False


@pytest.mark.asyncio
async def test_is_in_brazil_slightly_outside():
    """Test coordinates just outside Brazil's boundaries."""
    # Far south of Brazil
    assert await is_in_brazil(-35.0, -50.0) is False

    # Far north of Brazil
    assert await is_in_brazil(10.0, -50.0) is False

    # Far west of Brazil
    assert await is_in_brazil(-15.0, -80.0) is False

    # Far east of Brazil (Atlantic Ocean)
    assert await is_in_brazil(-15.0, -20.0) is False


@pytest.mark.asyncio
async def test_is_in_brazil_edge_cases():
    """Test edge cases for coordinate validation."""
    # Test with coordinates near actual Brazilian borders
    # These are approximations - exact borders follow complex coastlines and rivers

    # Near Uruguay border (should be just inside)
    assert await is_in_brazil(-30.0, -57) is True

    # Deep in Amazon (should be inside)
    assert await is_in_brazil(-2.0, -60.0) is True


def test_geojson_file_exists():
    """Test that the GeoJSON file exists and is accessible."""
    import os

    geojson_path = get_geojson_file_path()
    assert os.path.exists(geojson_path), f"GeoJSON file not found at {geojson_path}"
    assert os.path.isfile(geojson_path), f"GeoJSON path is not a file: {geojson_path}"


@pytest.mark.asyncio
async def test_geojson_available():
    """Test that the GeoJSON can be loaded."""
    assert await is_geojson_available() is True, "GeoJSON should be available and valid"


def test_geojson_file_path():
    """Test getting the GeoJSON file path."""
    geojson_path = get_geojson_file_path()
    assert geojson_path.endswith(
        "gadm41_BRA_0.json"
    ), "Path should end with correct filename"
    assert (
        "custom_components/inmet_weather" in geojson_path
    ), "Path should contain integration directory"
