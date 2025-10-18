"""Tests for INMET Weather constants."""

from custom_components.inmet_weather.const import (CONDITION_MAP, DEFAULT_NAME,
                                                   DOMAIN, UPDATE_INTERVAL)


def test_domain():
    """Test domain constant."""
    assert DOMAIN == "inmet_weather"


def test_default_name():
    """Test default name constant."""
    assert DEFAULT_NAME == "INMET Weather"


def test_update_interval():
    """Test update interval constant."""
    assert UPDATE_INTERVAL == 1800  # 30 minutes in seconds


def test_condition_map_exists():
    """Test that condition map is defined."""
    assert CONDITION_MAP is not None
    assert isinstance(CONDITION_MAP, dict)
    assert len(CONDITION_MAP) > 0


def test_condition_map_cloudy():
    """Test cloudy conditions mapping."""
    assert CONDITION_MAP.get("muitas nuvens") == "cloudy"
    assert CONDITION_MAP.get("nublado") == "cloudy"
    assert CONDITION_MAP.get("encoberto") == "cloudy"


def test_condition_map_sunny():
    """Test sunny conditions mapping."""
    assert CONDITION_MAP.get("limpo") == "sunny"
    assert CONDITION_MAP.get("ensolarado") == "sunny"
    assert CONDITION_MAP.get("sol") == "sunny"
    assert CONDITION_MAP.get("céu claro") == "sunny"
    assert CONDITION_MAP.get("ceu claro") == "sunny"


def test_condition_map_rainy():
    """Test rainy conditions mapping."""
    assert CONDITION_MAP.get("chuva") == "rainy"
    assert CONDITION_MAP.get("pancadas de chuva") == "pouring"
    assert CONDITION_MAP.get("pancada de chuva") == "pouring"


def test_condition_map_stormy():
    """Test stormy conditions mapping."""
    assert CONDITION_MAP.get("trovoada") == "lightning-rainy"
    assert CONDITION_MAP.get("tempestade") == "lightning-rainy"


def test_condition_map_fog():
    """Test foggy conditions mapping."""
    assert CONDITION_MAP.get("neblina") == "fog"
    assert CONDITION_MAP.get("nevoeiro") == "fog"
    assert CONDITION_MAP.get("névoa") == "fog"


def test_condition_map_partly_cloudy():
    """Test partly cloudy conditions mapping."""
    assert CONDITION_MAP.get("poucas nuvens") == "partlycloudy"
    assert CONDITION_MAP.get("nuvens") == "partlycloudy"
    assert CONDITION_MAP.get("parcialmente nublado") == "partlycloudy"


def test_condition_map_snowy():
    """Test snowy conditions mapping."""
    assert CONDITION_MAP.get("neve") == "snowy"


def test_condition_map_values():
    """Test that all condition map values are valid Home Assistant conditions."""
    valid_conditions = [
        "clear-night",
        "cloudy",
        "exceptional",
        "fog",
        "hail",
        "lightning",
        "lightning-rainy",
        "partlycloudy",
        "pouring",
        "rainy",
        "snowy",
        "snowy-rainy",
        "sunny",
        "windy",
        "windy-variant",
    ]

    for condition in CONDITION_MAP.values():
        assert condition in valid_conditions, f"Invalid condition: {condition}"


def test_condition_map_case_sensitivity():
    """Test that condition map keys are lowercase."""
    for key in CONDITION_MAP.keys():
        assert key == key.lower(), f"Key should be lowercase: {key}"
