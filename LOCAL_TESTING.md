# Local Testing Guide

This guide will help you test the INMET Weather integration locally on your machine.

## Prerequisites

- Python 3.11 or 3.12
- Home Assistant installed locally (or running in Docker)
- Git

## Method 1: Link to Existing Home Assistant Installation

### Step 1: Locate Your Home Assistant Config Directory

Common locations:
- **Linux**: `~/.homeassistant/`
- **macOS**: `~/.homeassistant/`
- **Windows**: `%APPDATA%\.homeassistant\`
- **Docker**: Your mapped config volume

### Step 2: Create Symbolic Link

```bash
# Navigate to your Home Assistant config directory
cd ~/.homeassistant

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Create symbolic link to the integration
ln -s /Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather custom_components/inmet_weather

# Verify the link was created
ls -la custom_components/
```

### Step 3: Restart Home Assistant

```bash
# If running Home Assistant Core
hass --restart

# If running as a service
sudo systemctl restart home-assistant@homeassistant

# If running in Docker
docker restart homeassistant
```

### Step 4: Add Integration via UI

1. Open Home Assistant in your browser
2. Go to **Settings** → **Devices & Services**
3. Click **"+ Add Integration"**
4. Search for **"INMET Weather"**
5. Follow the configuration steps:
   - Enter a name (or use default)
   - Enter latitude/longitude (or use Home Assistant's default)
6. Click **Submit**

The integration should now appear in your integrations list!

## Method 2: Run Home Assistant Core Locally

### Step 1: Create a Test Environment

```bash
# Create a directory for testing
mkdir -p ~/ha-test
cd ~/ha-test

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Home Assistant
pip install homeassistant

# Create config directory
mkdir -p config
cd config
```

### Step 2: Install the Integration

```bash
# Create custom_components directory
mkdir -p custom_components

# Copy or link the integration
cp -r /Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather custom_components/

# OR create symbolic link
ln -s /Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather custom_components/inmet_weather
```

### Step 3: Create Basic Configuration

Create `configuration.yaml`:

```yaml
# Minimal Home Assistant configuration
homeassistant:
  name: Test Home
  latitude: -22.9068
  longitude: -43.1729
  elevation: 0
  unit_system: metric
  time_zone: America/Sao_Paulo

# Enable the frontend
frontend:

# Enable configuration UI
config:

# HTTP configuration
http:
  server_port: 8123
```

### Step 4: Run Home Assistant

```bash
# From the config directory
cd ~/ha-test/config

# Run Home Assistant
hass -c .
```

### Step 5: Access Home Assistant

1. Open browser to http://localhost:8123
2. Complete the onboarding process
3. Add the INMET Weather integration as described in Method 1

## Method 3: Run Unit Tests Locally

### Step 1: Install Test Dependencies

```bash
cd /Users/zanaca/dev/ha-inmet-weather

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install test dependencies
pip install -r requirements-test.txt
```

### Step 2: Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=custom_components.inmet_weather --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_get_geocode_from_coordinates_rio -v

# Run tests and stop on first failure
pytest -x

# Run tests with output (see print statements)
pytest -s
```

### Step 3: View Coverage Report

```bash
# After running tests with coverage, open the HTML report
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

## Method 4: Test with Docker

### Step 1: Create Docker Compose File

Create `docker-compose.yml` in your test directory:

```yaml
version: '3'
services:
  homeassistant:
    container_name: ha-inmet-test
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - /Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather:/config/custom_components/inmet_weather
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```

### Step 2: Create Configuration

```bash
mkdir -p config
# Copy your configuration.yaml to ./config/
```

### Step 3: Run Docker Container

```bash
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

## Debugging Tips

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.inmet_weather: debug
```

### Check Logs

```bash
# View Home Assistant logs
tail -f ~/.homeassistant/home-assistant.log

# Or in Docker
docker logs -f homeassistant
```

### Common Issues

1. **Integration not showing up**
   - Verify the symbolic link or copy was successful
   - Check file permissions
   - Restart Home Assistant completely
   - Check logs for import errors

2. **Import errors**
   - Make sure all files are present in custom_components/inmet_weather/
   - Check manifest.json is valid
   - Verify Python version compatibility

3. **API errors**
   - Check your internet connection
   - Verify INMET API is accessible: `curl https://apiprevmet3.inmet.gov.br/previsao/3304557`
   - Check logs for specific error messages

## Quick Test Script

Create a test script `test_integration.sh`:

```bash
#!/bin/bash

echo "Testing INMET Weather Integration..."

# Check if files exist
echo "Checking files..."
if [ -d "/Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather" ]; then
    echo "✓ Integration directory found"
else
    echo "✗ Integration directory not found"
    exit 1
fi

# Check manifest
echo "Validating manifest..."
python3 -c "import json; json.load(open('/Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather/manifest.json'))" && echo "✓ manifest.json valid" || echo "✗ manifest.json invalid"

# Check strings
echo "Validating strings..."
python3 -c "import json; json.load(open('/Users/zanaca/dev/ha-inmet-weather/custom_components/inmet_weather/strings.json'))" && echo "✓ strings.json valid" || echo "✗ strings.json invalid"

# Test API connection
echo "Testing INMET API..."
curl -s "https://apiprevmet3.inmet.gov.br/previsao/3304557" | python3 -m json.tool > /dev/null && echo "✓ API accessible" || echo "✗ API not accessible"

echo "Done!"
```

Make it executable and run:

```bash
chmod +x test_integration.sh
./test_integration.sh
```

## Next Steps

After testing locally:

1. Make changes to the code
2. Restart Home Assistant to reload the integration
3. Test your changes
4. Run unit tests: `pytest`
5. Commit your changes

For development workflow, see [CONTRIBUTING.md](CONTRIBUTING.md).
