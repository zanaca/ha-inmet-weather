#!/usr/bin/env python3
"""Standalone test for Brazil boundary validation."""

import asyncio
import sys
import importlib.util

# Load geo_utils directly without going through __init__.py
spec = importlib.util.spec_from_file_location(
    "geo_utils",
    "./custom_components/inmet_weather/geo_utils.py"
)
geo_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo_utils)

is_in_brazil = geo_utils.is_in_brazil
is_geojson_available = geo_utils.is_geojson_available
get_geojson_file_path = geo_utils.get_geojson_file_path


async def test_boundaries():
    """Test boundary validation with various coordinates."""
    print("=" * 60)
    print("Testing Brazil Boundary Validation (GeoJSON)")
    print("=" * 60)

    # Check if GeoJSON is available
    print(f"\nGeoJSON file: {get_geojson_file_path()}")
    geojson_available = await is_geojson_available()
    print(f"GeoJSON available: {geojson_available}")

    if not geojson_available:
        print("ERROR: GeoJSON file not available!")
        return 1

    # Test valid coordinates (inside Brazil)
    print("\n✓ Testing valid coordinates (inside Brazil):")
    test_cases_valid = [
        ("Rio de Janeiro", -22.9068, -43.1729),
        ("São Paulo", -23.5505, -46.6333),
        ("Brasília", -15.7939, -47.8828),
        ("Porto Alegre", -30.0346, -51.2177),
        ("Manaus", -3.1190, -60.0217),
    ]

    all_valid_passed = True
    for name, lat, lon in test_cases_valid:
        result = await is_in_brazil(lat, lon)
        status = "✓" if result else "✗"
        if not result:
            all_valid_passed = False
        print(f"  {status} {name:20} ({lat:7.4f}, {lon:7.4f}) -> {result}")

    # Test invalid coordinates (outside Brazil)
    print("\n✓ Testing invalid coordinates (outside Brazil):")
    test_cases_invalid = [
        ("Buenos Aires, Argentina", -34.6037, -58.3816),
        ("Lima, Peru", -12.0464, -77.0428),
        ("Caracas, Venezuela", 10.4806, -66.9036),
        ("Atlantic Ocean", -23.5505, -20.0),
        ("Pacific Ocean", -15.0, -80.0),
    ]

    all_invalid_passed = True
    for name, lat, lon in test_cases_invalid:
        result = await is_in_brazil(lat, lon)
        status = "✓" if not result else "✗"
        if result:
            all_invalid_passed = False
        print(f"  {status} {name:30} ({lat:7.4f}, {lon:7.4f}) -> {result}")

    # Summary
    print("\n" + "=" * 60)
    if all_valid_passed and all_invalid_passed:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(test_boundaries()))
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
