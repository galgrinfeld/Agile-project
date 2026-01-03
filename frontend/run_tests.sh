#!/bin/bash
# Frontend test runner script

set -e

echo "=========================================="
echo "Running Frontend Tests"
echo "=========================================="

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "Error: Please run this script from the frontend directory"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run tests with coverage
echo "Running Jest tests with coverage..."
npm test -- --coverage --watchAll=false

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Coverage report: coverage/index.html"
echo "=========================================="

