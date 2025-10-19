"""Constants for the INMET Weather integration."""

DOMAIN = "inmet_weather"
DEFAULT_NAME = "INMET Weather"

# Update interval in seconds (every 30 minutes)
UPDATE_INTERVAL = 1800

# Geocode cache settings
GEOCODE_CACHE_FILE = ".inmet_geocode_cache.json"

# Conditions
CONDITION_SUNNY = "sunny"
CONDITION_CLEAR_NIGHT = "clear-night"

# Condition mapping from INMET to Home Assistant
CONDITION_MAP = {
    "poucas nuvens": "partlycloudy",
    "muitas nuvens": "cloudy",
    "pancadas de chuva": "pouring",
    "pancada de chuva": "pouring",
    "trovoada": "lightning-rainy",
    "tempestade": "lightning-rainy",
    "céu claro": CONDITION_SUNNY,
    "parcialmente nublado": "partlycloudy",
    "ceu claro": CONDITION_SUNNY,
    "claro": CONDITION_SUNNY,
    "neblina": "fog",
    "nevoeiro": "fog",
    "névoa": "fog",
    "nuvens": "partlycloudy",
    "chuva": "rainy",
    "nublado": "cloudy",
    "encoberto": "cloudy",
    "neve": "snowy",
    "limpo": CONDITION_SUNNY,
    "ensolarado": CONDITION_SUNNY,
    "sol": CONDITION_SUNNY,
}
