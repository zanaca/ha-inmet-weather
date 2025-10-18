"""Constants for the INMET Weather integration."""

DOMAIN = "inmet_weather"
DEFAULT_NAME = "INMET Weather"

# Update interval in seconds (every 30 minutes)
UPDATE_INTERVAL = 1800

# Condition mapping from INMET to Home Assistant
CONDITION_MAP = {
    "poucas nuvens": "partlycloudy",
    "muitas nuvens": "cloudy",
    "nublado": "cloudy",
    "encoberto": "cloudy",
    "chuva": "rainy",
    "pancadas de chuva": "pouring",
    "pancada de chuva": "pouring",
    "trovoada": "lightning-rainy",
    "tempestade": "lightning-rainy",
    "neve": "snowy",
    "limpo": "sunny",
    "ensolarado": "sunny",
    "sol": "sunny",
    "céu claro": "sunny",
    "ceu claro": "sunny",
    "neblina": "fog",
    "nevoeiro": "fog",
    "névoa": "fog",
    "nuvens": "partlycloudy",
    "parcialmente nublado": "partlycloudy",
}
