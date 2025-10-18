# INMET Weather for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that provides weather data from INMET (Instituto Nacional de Meteorologia - Brazilian National Institute of Meteorology).

## Quick Start (Local Testing)

Want to test the integration locally right now?

```bash
# Test core API logic (no installation needed!)
python test_api_direct.py
```

**Having issues with pytest?** See [QUICK_START.md](QUICK_START.md) for solutions to common problems.

For complete testing options and troubleshooting, see:

- **[QUICK_START.md](QUICK_START.md)** - Quick testing guide & troubleshooting
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Complete testing documentation
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Run in real Home Assistant

## Features

- Current weather conditions from the nearest INMET weather station
- Weather forecast for the next days
- Automatic location detection based on Home Assistant's configured latitude and longitude
- Support for multiple locations
- Updates every 30 minutes

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/zanaca/ha-inmet-weather`
6. Select category "Integration"
7. Click "Add"
8. Find "INMET Weather" in the integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/inmet_weather` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "INMET Weather"
4. Follow the configuration steps:
   - **Name**: Give your weather entity a name (default: "INMET Weather")
   - **Latitude**: The latitude of your location (default: your Home Assistant's latitude)
   - **Longitude**: The longitude of your location (default: your Home Assistant's longitude)

The integration will automatically find the nearest INMET weather station based on your coordinates.

## How It Works

The integration uses INMET's public API endpoints:

1. **Geocode Detection**: The integration has a built-in list of major Brazilian cities with their geocodes and coordinates. It calculates the distance between your configured location and these known locations to find the nearest one.

2. **Current Weather API** (`/estacao/proxima/{geocode}`): Provides real-time weather conditions from the nearest INMET weather station, including:
   - Temperature, humidity, pressure
   - Wind speed, gusts, and direction
   - Rain accumulation
   - Solar radiation and dew point

3. **Forecast API** (`/previsao/{geocode}`): Provides detailed weather forecast data with three periods per day (morning, afternoon, evening) for multiple days ahead.

The integration automatically:
- Finds the nearest Brazilian city/municipality based on your coordinates
- Fetches current weather from the nearest INMET station
- Retrieves forecast data for your region
- Updates every 30 minutes to provide fresh data

## Data Provided

### Current Conditions
- Temperature (°C)
- Humidity (%)
- Atmospheric Pressure (hPa)
- Wind speed (m/s)
- Wind gusts (m/s)
- Wind direction (degrees)
- Weather condition (sunny, cloudy, rainy, etc.)
- Dew point
- Solar radiation

### Forecast
- Temperature (high/low in °C)
- Weather condition with detailed descriptions
- Humidity (max/min %)
- Wind direction and intensity
- Temperature trends (rising, stable, falling)
- Up to 15 forecast periods covering the next 5 days
  - Morning (manha): 6:00 AM
  - Afternoon (tarde): 12:00 PM
  - Evening (noite): 6:00 PM

## API Information

This integration uses the INMET public API:
- Base URL: `https://apiprevmet3.inmet.gov.br`
- No API key required
- Free to use

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run tests with coverage
pytest --cov=custom_components.inmet_weather --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code
black custom_components tests

# Sort imports
isort custom_components tests

# Lint
flake8 custom_components tests --max-line-length=100
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more detailed development guidelines.

## Support

If you encounter any issues or have suggestions, please [open an issue](https://github.com/zanaca/ha-inmet-weather/issues) on GitHub.

## Credits

Weather data provided by [INMET - Instituto Nacional de Meteorologia](https://portal.inmet.gov.br/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
