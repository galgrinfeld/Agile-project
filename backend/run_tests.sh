#!/bin/bash
# Backend test runner script

set -e

echo "=========================================="
echo "Running Backend Tests"
echo "=========================================="

# Check if we're in the backend directory
if [ ! -f "pytest.ini" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Run tests with coverage
echo "Running pytest with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html -v

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Coverage report: htmlcov/index.html"
echo "=========================================="

