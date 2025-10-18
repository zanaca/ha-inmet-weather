#!/usr/bin/env python3
"""Standalone test script for INMET Weather API (no pytest required)."""
import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock

# Add current directory to path
sys.path.insert(0, '.')

from custom_components.inmet_weather.api import InmetApiClient


def test_calculate_distance():
    """Test distance calculation."""
    print("Test: Calculate distance between Rio and São Paulo...")
    session = MagicMock()
    client = InmetApiClient(session)

    distance = client.calculate_distance(-22.9068, -43.1729, -23.5505, -46.6333)

    assert 350 < distance < 370, f"Distance should be ~360km, got {distance}km"
    print(f"✓ Distance calculated correctly: {distance:.2f}km")


async def test_geocode_detection():
    """Test geocode detection for major cities."""
    print("\nTest: Geocode detection...")
    session = MagicMock()
    client = InmetApiClient(session)

    # Test Rio de Janeiro
    geocode = await client.get_geocode_from_coordinates(-22.9068, -43.1729)
    assert geocode == "3304557", f"Expected 3304557, got {geocode}"
    print("✓ Rio de Janeiro: 3304557")

    # Test São Paulo
    geocode = await client.get_geocode_from_coordinates(-23.5505, -46.6333)
    assert geocode == "3550308", f"Expected 3550308, got {geocode}"
    print("✓ São Paulo: 3550308")

    # Test Brasília
    geocode = await client.get_geocode_from_coordinates(-15.7939, -47.8828)
    assert geocode == "5300108", f"Expected 5300108, got {geocode}"
    print("✓ Brasília: 5300108")


async def test_api_structure():
    """Test API client structure and methods."""
    print("\nTest: API client structure...")
    session = MagicMock()
    client = InmetApiClient(session)

    assert hasattr(client, 'get_geocode_from_coordinates')
    assert hasattr(client, 'get_current_weather')
    assert hasattr(client, 'get_forecast')
    assert hasattr(client, 'calculate_distance')
    print("✓ All required methods present")


async def test_current_weather_api():
    """Test current weather API call structure."""
    print("\nTest: Current weather API...")
    session = MagicMock()
    client = InmetApiClient(session)

    # Mock the response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "dados": {
            "TEM_INS": "29",
            "UMD_INS": "61",
            "VEN_VEL": "1.7",
        }
    })

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    session.get = MagicMock(return_value=mock_context)

    result = await client.get_current_weather("3304557")

    assert result is not None
    assert "dados" in result
    print("✓ Current weather API works correctly")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("INMET Weather API - Standalone Tests")
    print("=" * 60)

    try:
        # Sync tests
        test_calculate_distance()

        # Async tests
        await test_geocode_detection()
        await test_api_structure()
        await test_current_weather_api()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
