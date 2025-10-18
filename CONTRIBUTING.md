# Contributing to INMET Weather for Home Assistant

Thank you for your interest in contributing to this project! This guide will help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/zanaca/ha-inmet-weather.git
   cd ha-inmet-weather
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-test.txt
   ```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=custom_components.inmet_weather --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_api.py
```

### Run specific test
```bash
pytest tests/test_api.py::test_get_geocode_from_coordinates_rio
```

## Code Quality

### Format code with Black
```bash
black custom_components tests
```

### Sort imports with isort
```bash
isort custom_components tests
```

### Lint with flake8
```bash
flake8 custom_components tests --max-line-length=100
```

### Type checking with mypy
```bash
mypy custom_components
```

## Testing Your Changes

1. **Link the integration to your Home Assistant config**
   ```bash
   ln -s $(pwd)/custom_components/inmet_weather ~/.homeassistant/custom_components/
   ```

2. **Restart Home Assistant**

3. **Add the integration through the UI**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "INMET Weather"

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests for new functionality
   - Update documentation if needed

3. **Ensure all tests pass**
   ```bash
   pytest
   black custom_components tests
   isort custom_components tests
   flake8 custom_components tests --max-line-length=100
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

## Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep lines under 100 characters
- Use descriptive variable names

## Testing Guidelines

- Write tests for all new functionality
- Aim for at least 80% code coverage
- Use meaningful test names that describe what is being tested
- Mock external API calls
- Test both success and failure scenarios

## Commit Message Guidelines

- Use clear and descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add detailed description if needed

Examples:
```
Add support for wind gust speed
Fix temperature parsing for invalid values
Update README with installation instructions
```

## Questions?

If you have any questions, feel free to:
- Open an issue on GitHub
- Ask in the pull request comments
- Check existing issues for similar questions

Thank you for contributing!
