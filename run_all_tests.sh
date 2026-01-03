#!/bin/bash
# Run all tests (backend and frontend)

set -e

echo "=========================================="
echo "Running All Tests"
echo "=========================================="

# Backend tests
echo ""
echo "--- Backend Tests ---"
cd backend
if [ -f "run_tests.sh" ]; then
    bash run_tests.sh
else
    pytest --cov=app --cov-report=term-missing -v
fi
cd ..

# Frontend tests
echo ""
echo "--- Frontend Tests ---"
cd frontend
if [ -f "run_tests.sh" ]; then
    bash run_tests.sh
else
    npm test -- --coverage --watchAll=false
fi
cd ..

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="

