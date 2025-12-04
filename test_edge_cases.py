#!/usr/bin/env python3
"""Test edge cases for Brazil boundary validation."""

import asyncio
import sys
import importlib.util

# Load geo_utils directly
spec = importlib.util.spec_from_file_location(
    "geo_utils",
    "./custom_components/inmet_weather/geo_utils.py"
)
geo_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo_utils)

is_in_brazil = geo_utils.is_in_brazil

async def test_edge_cases():
    """Test various edge cases."""
    print("=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)

    test_cases = [
        # (name, lat, lon, expected)
        ("Center of Brazil", -15.0, -50.0, True),
        ("Fernando de Noronha closer", -3.85, -32.42, True),  # Closer to actual island
        ("Near Paraguay border", -22.0, -55.5, True),
        ("Near Iguazu Falls", -25.5, -54.5, True),  # Actually inside Brazil
        ("Near Uruguay border", -30.5, -55.5, True),
        ("Just outside south", -34.0, -55.0, False),
        ("Falkland Islands", -51.7, -59.0, False),
        ("French Guiana", 4.0, -53.0, False),
        ("Suriname", 4.0, -56.0, False),
        ("Guyana", 6.0, -58.5, False),
        ("Bolivia", -16.5, -68.0, False),
        ("Chile", -33.5, -70.5, False),
        ("Atlantic far east", -23.0, -30.0, False),
        ("Pacific far west", -10.0, -75.0, False),
    ]

    passed = 0
    failed = 0

    for name, lat, lon, expected in test_cases:
        result = await is_in_brazil(lat, lon)
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1
        else:
            failed += 1

        expected_str = "inside" if expected else "outside"
        result_str = "inside" if result else "outside"

        print(f"{status} {name:30} ({lat:7.2f}, {lon:7.2f})")
        print(f"   Expected: {expected_str:7} | Got: {result_str:7}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(test_edge_cases()))
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
