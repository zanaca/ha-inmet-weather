"""Geographic utilities for INMET Weather integration."""

import json
import logging
import os
from functools import lru_cache
from typing import List, Tuple

_LOGGER = logging.getLogger(__name__)

# Path to the GeoJSON file containing Brazil's boundaries
_GEOJSON_FILE = os.path.join(os.path.dirname(__file__), "gadm41_BRA_0.json")


def _point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Check if a point is inside a polygon using ray casting algorithm.

    Args:
        point: Tuple of (longitude, latitude)
        polygon: List of [lon, lat] coordinate pairs forming the polygon

    Returns:
        True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    xinters = float(
                        "inf"
                    )  # Handles degenerate case when edge is horizontal (p1y == p2y)
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def _point_in_multipolygon(
    point: Tuple[float, float], multipolygon: List[List[List[List[float]]]]
) -> bool:
    """Check if a point is inside any polygon in a MultiPolygon.

    Args:
        point: Tuple of (longitude, latitude)
        multipolygon: GeoJSON MultiPolygon coordinates structure

    Returns:
        True if point is inside any polygon, False otherwise
    """
    for polygon_group in multipolygon:
        # Each polygon_group is a list of rings (exterior + holes)
        # First ring is exterior, rest are holes
        if not polygon_group:
            continue

        # Check if point is in exterior ring
        exterior_ring = polygon_group[0]
        if _point_in_polygon(point, exterior_ring):
            # Check if point is in any hole
            in_hole = False
            for i in range(1, len(polygon_group)):
                if _point_in_polygon(point, polygon_group[i]):
                    in_hole = True
                    break

            if not in_hole:
                return True

    return False


@lru_cache(maxsize=1)
def _load_brazil_geometry():
    """Load and cache Brazil's geometry from GeoJSON file.

    Returns:
        Dictionary with geometry type and coordinates,
        or None if file cannot be loaded
    """
    try:
        with open(_GEOJSON_FILE, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        # Extract the first feature (Brazil's geometry)
        if geojson_data.get("type") == "FeatureCollection" and geojson_data.get(
            "features"
        ):
            feature = geojson_data["features"][0]
            geometry = feature.get("geometry")
            if geometry:
                _LOGGER.debug("Successfully loaded Brazil geometry from GeoJSON")
                return geometry
            else:
                _LOGGER.error("No geometry found in feature")
                return None
        else:
            _LOGGER.error("Invalid GeoJSON structure in %s", _GEOJSON_FILE)
            return None

    except FileNotFoundError:
        _LOGGER.error("GeoJSON file not found: %s", _GEOJSON_FILE)
        return None
    except json.JSONDecodeError as err:
        _LOGGER.error("Failed to parse GeoJSON file: %s", err)
        return None
    except Exception as err:
        _LOGGER.error("Unexpected error loading GeoJSON: %s", err)
        return None


def is_in_brazil(latitude: float, longitude: float) -> bool:
    """Check if the given coordinates are within Brazil's boundaries.

    Uses the official GADM boundary data for accurate point-in-polygon testing.
    Implements ray casting algorithm for pure Python point-in-polygon test.

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)

    Returns:
        True if coordinates are within Brazil's boundaries, False otherwise
    """
    geometry = _load_brazil_geometry()

    if geometry is None:
        _LOGGER.warning(
            "Could not load Brazil geometry, falling back to bounding box check"
        )
        # Fallback to simple bounding box check
        return _is_in_brazil_bbox(latitude, longitude)

    try:
        point = (longitude, latitude)  # GeoJSON uses (lon, lat)
        geometry_type = geometry.get("type")

        if geometry_type == "MultiPolygon":
            coordinates = geometry.get("coordinates", [])
            return _point_in_multipolygon(point, coordinates)
        elif geometry_type == "Polygon":
            coordinates = geometry.get("coordinates", [])
            if coordinates:
                # Check exterior ring (first element)
                if _point_in_polygon(point, coordinates[0]):
                    # Check if in any holes
                    for i in range(1, len(coordinates)):
                        if _point_in_polygon(point, coordinates[i]):
                            return False
                    return True
            return False
        else:
            _LOGGER.error("Unsupported geometry type: %s", geometry_type)
            return _is_in_brazil_bbox(latitude, longitude)

    except Exception as err:
        _LOGGER.error("Error checking if point is in Brazil: %s", err)
        return False


def _is_in_brazil_bbox(latitude: float, longitude: float) -> bool:
    """Fallback bounding box check for Brazil.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        True if within Brazil's approximate bounding box
    """
    # Brazil's approximate bounding box
    # Source: IBGE (Instituto Brasileiro de Geografia e Estatística)
    return (
        -33.75 <= latitude <= 5.27  # Southern to Northern boundary
        and -73.99 <= longitude <= -28.83  # Western to Eastern boundary
    )


def get_geojson_file_path() -> str:
    """Get the path to the GeoJSON file.

    Returns:
        Absolute path to the gadm41_BRA_0.json file
    """
    return os.path.abspath(_GEOJSON_FILE)


def is_geojson_available() -> bool:
    """Check if the GeoJSON file is available and valid.

    Returns:
        True if GeoJSON file exists and can be loaded, False otherwise
    """
    geometry = _load_brazil_geometry()
    return geometry is not None
