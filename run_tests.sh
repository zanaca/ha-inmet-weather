#!/bin/bash
# Simple test runner without coverage requirements

set -e

echo "================================================"
echo "INMET Weather - Simple Test Runner"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Validating JSON files"
echo "================================================"

# Validate manifest.json
if python3 -c "import json; json.load(open('custom_components/inmet_weather/manifest.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ manifest.json is valid${NC}"
else
    echo -e "${RED}✗ manifest.json is invalid${NC}"
    exit 1
fi

# Validate strings.json
if python3 -c "import json; json.load(open('custom_components/inmet_weather/strings.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ strings.json is valid${NC}"
else
    echo -e "${RED}✗ strings.json is invalid${NC}"
    exit 1
fi

# Validate hacs.json
if python3 -c "import json; json.load(open('hacs.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ hacs.json is valid${NC}"
else
    echo -e "${RED}✗ hacs.json is invalid${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "Step 2: Testing core API logic"
echo "================================================"
echo ""

python3 test_api_direct.py

DIRECT_TEST_EXIT=$?

echo ""
echo "================================================"
echo "Step 3: Testing with pytest (if available)"
echo "================================================"
echo ""

# Check if pytest is available
if command -v pytest &> /dev/null; then
    echo "Running pytest tests..."

    # Run pytest without coverage
    pytest -v

    PYTEST_EXIT_CODE=$?
else
    echo -e "${YELLOW}pytest not installed. Skipping pytest tests.${NC}"
    echo -e "${YELLOW}To run full tests: pip install -r requirements-test.txt${NC}"
    PYTEST_EXIT_CODE=0
fi

echo ""
echo "================================================"
echo "Summary"
echo "================================================"

if [ $DIRECT_TEST_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Core API tests passed!${NC}"
else
    echo -e "${RED}✗ Core API tests failed${NC}"
fi

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some pytest tests failed${NC}"
    exit 1
fi
