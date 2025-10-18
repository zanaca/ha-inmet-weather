#!/bin/bash
# Quick test runner for INMET Weather integration

set -e

echo "================================================"
echo "INMET Weather Integration - Test Suite"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3.13 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    python3.13 -m pip  install -r requirements-test.txt --break-system-packages
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

echo ""
echo "================================================"
echo "Step 1: Validating JSON files"
echo "================================================"

# Validate manifest.json
if python3.13 -c "import json; json.load(open('custom_components/inmet_weather/manifest.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ manifest.json is valid${NC}"
else
    echo -e "${RED}✗ manifest.json is invalid${NC}"
    exit 1
fi

# Validate strings.json
if python3.13 -c "import json; json.load(open('custom_components/inmet_weather/strings.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ strings.json is valid${NC}"
else
    echo -e "${RED}✗ strings.json is invalid${NC}"
    exit 1
fi

# Validate hacs.json
if python3.13 -c "import json; json.load(open('hacs.json'))" 2>/dev/null; then
    echo -e "${GREEN}✓ hacs.json is valid${NC}"
else
    echo -e "${RED}✗ hacs.json is invalid${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "Step 2: Testing INMET API connectivity"
echo "================================================"

if curl -s --connect-timeout 5 "https://apiprevmet3.inmet.gov.br/previsao/3304557" | python3.13 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓ INMET API is accessible${NC}"
else
    echo -e "${YELLOW}⚠ INMET API may not be accessible (this is OK for offline testing)${NC}"
fi

echo ""
echo "================================================"
echo "Step 3: Running unit tests"
echo "================================================"
echo ""

# Run pytest with coverage
pytest --cov=custom_components.inmet_weather \
       --cov-report=term-missing \
       --cov-report=html \
       -v

PYTEST_EXIT_CODE=$?

echo ""
echo "================================================"
echo "Step 4: Code quality checks"
echo "================================================"
echo ""

# Check code formatting with black
echo "Checking code formatting (black)..."
if black --check custom_components tests 2>/dev/null; then
    echo -e "${GREEN}✓ Code formatting is correct${NC}"
else
    echo -e "${YELLOW}⚠ Code needs formatting (run: black custom_components tests)${NC}"
fi

echo ""

# Check import sorting with isort
echo "Checking import sorting (isort)..."
if isort --check-only custom_components tests 2>/dev/null; then
    echo -e "${GREEN}✓ Imports are correctly sorted${NC}"
else
    echo -e "${YELLOW}⚠ Imports need sorting (run: isort custom_components tests)${NC}"
fi

echo ""

# Check with flake8
echo "Running linter (flake8)..."
if flake8 custom_components tests --max-line-length=100 --ignore=E203,W503 2>/dev/null; then
    echo -e "${GREEN}✓ No linting issues found${NC}"
else
    echo -e "${YELLOW}⚠ Linting issues found${NC}"
fi

echo ""
echo "================================================"
echo "Summary"
echo "================================================"

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Coverage report: htmlcov/index.html"
    echo "To view: open htmlcov/index.html"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    exit 1
fi
