# Testing Guide

This document provides comprehensive information about running and maintaining tests for the Agile Project.

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Running Tests](#running-tests)
5. [Test Structure](#test-structure)
6. [CI/CD Integration](#cicd-integration)

## Overview

The project includes three types of tests:

1. **Backend Database Integration Tests** - Test database operations, relationships, and constraints
2. **Backend REST API Tests** - Test all API endpoints, authentication, and error handling
3. **Frontend Tests** - Test React components, services, and business logic

## Backend Testing

### Test Framework

- **Framework**: pytest
- **Test Client**: FastAPI TestClient (httpx)
- **Database**: SQLite (in-memory) for fast tests, PostgreSQL for realistic testing

### Test Structure

Backend tests are located in `backend/tests/`:

```
backend/tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_database_integration.py  # Database CRUD and relationship tests
├── test_api_auth.py              # Authentication endpoint tests
├── test_api_students.py          # Student endpoint tests
├── test_api_courses.py           # Course endpoint tests
├── test_api_ratings.py           # Rating endpoint tests
├── test_api_reviews.py           # Course review endpoint tests
├── test_api_career_goals.py      # Career goal endpoint tests
├── test_api_skills.py            # Skill endpoint tests
└── test_api_recommendations.py   # Recommendation endpoint tests
```

### Running Backend Tests

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Run All Tests

```bash
# From backend directory
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_auth.py

# Run specific test class
pytest tests/test_api_auth.py::TestAuthLogin

# Run specific test
pytest tests/test_api_auth.py::TestAuthLogin::test_login_success
```

#### Run Tests by Marker

```bash
# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only unit tests
pytest -m unit
```

#### Test Configuration

The test configuration is in `backend/pytest.ini`. Key settings:

- **Test Database**: Uses SQLite in-memory by default (fast)
- **Coverage**: Enabled with HTML report generation
- **Markers**: `integration`, `api`, `unit` for test categorization

#### Using PostgreSQL for Tests

To use PostgreSQL instead of SQLite (more realistic but slower):

```bash
# Set environment variable
export USE_SQLITE=false

# Or set in pytest.ini or conftest.py
```

Make sure PostgreSQL test database is running and accessible.

### Test Coverage

Backend tests cover:

- ✅ All database models and relationships
- ✅ All REST API endpoints
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling
- ✅ Pagination
- ✅ Foreign key constraints
- ✅ Cascade deletes

## Frontend Testing

### Test Framework

- **Framework**: Jest (via react-scripts)
- **Testing Library**: @testing-library/react
- **Utilities**: @testing-library/jest-dom, @testing-library/user-event

### Test Structure

Frontend tests are located in `frontend/src/__tests__/`:

```
frontend/src/__tests__/
├── services/
│   ├── authService.test.js
│   ├── authService.integration.test.js
│   └── courseService.test.js
├── components/
│   ├── AuthForm.test.jsx
│   └── CourseDetailsPage.test.jsx
└── utils.test.js
```

### Running Frontend Tests

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Run All Tests

```bash
# From frontend directory
npm test

# Run in watch mode (default)
npm test

# Run once and exit
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage --watchAll=false
```

#### Run Specific Tests

```bash
# Run specific test file
npm test -- authService.test.js

# Run tests matching pattern
npm test -- --testNamePattern="login"
```

### Test Configuration

Frontend test configuration:

- **Setup File**: `frontend/src/setupTests.js` - Configures jest-dom and mocks
- **Jest Config**: Inherited from react-scripts (in package.json)

### Test Coverage

Frontend tests cover:

- ✅ Authentication service (login, register, token management)
- ✅ Course service (API interactions)
- ✅ Auth context provider
- ✅ Component rendering
- ✅ User interactions
- ✅ Error handling
- ✅ Loading states

## Running Tests

### Run All Tests

#### Backend Only

```bash
cd backend
pytest
```

#### Frontend Only

```bash
cd frontend
npm test -- --watchAll=false
```

#### Both (from project root)

```bash
# Backend
cd backend && pytest && cd ..

# Frontend
cd frontend && npm test -- --watchAll=false && cd ..
```

### Test Scripts

#### Backend Test Script

Create `backend/run_tests.sh`:

```bash
#!/bin/bash
set -e

echo "Running backend tests..."
pytest --cov=app --cov-report=term-missing --cov-report=html

echo "Test coverage report generated in htmlcov/index.html"
```

#### Frontend Test Script

Create `frontend/run_tests.sh`:

```bash
#!/bin/bash
set -e

echo "Running frontend tests..."
npm test -- --coverage --watchAll=false

echo "Test coverage report generated in coverage/"
```

## Test Structure

### Backend Test Patterns

#### Database Integration Test Example

```python
@pytest.mark.integration
def test_create_student(db_session):
    student = models.Student(
        name="test_user",
        hashed_password="hash123"
    )
    db_session.add(student)
    db_session.commit()
    
    assert student.id is not None
    assert student.name == "test_user"
```

#### API Test Example

```python
@pytest.mark.api
def test_login_success(client, test_student, test_student_data):
    response = client.post(
        "/auth/login",
        data={
            "username": test_student_data["name"],
            "password": test_student_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
```

### Frontend Test Patterns

#### Service Test Example

```javascript
test('loginUser successfully logs in', async () => {
  const mockToken = 'mock_token';
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ access_token: mockToken })
  });

  const token = await loginUser('user', 'pass');
  expect(token).toBe(mockToken);
});
```

#### Component Test Example

```javascript
test('renders login form', () => {
  render(<AuthForm onAuthSuccess={jest.fn()} />);
  expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
});
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
```

### Docker Compose Test Setup

You can run tests in Docker:

```bash
# Backend tests
docker-compose run --rm backend pytest

# Frontend tests
docker-compose run --rm frontend npm test -- --watchAll=false
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Tests should clean up after themselves (handled by fixtures)
3. **Naming**: Use descriptive test names that explain what is being tested
4. **Coverage**: Aim for high coverage but focus on critical paths
5. **Speed**: Keep tests fast (use mocks where appropriate)
6. **Readability**: Tests should be easy to understand and maintain

## Troubleshooting

### Backend Tests

**Issue**: Database connection errors
- **Solution**: Check database configuration in `conftest.py` and ensure test database is accessible

**Issue**: Import errors
- **Solution**: Ensure you're running tests from the correct directory and PYTHONPATH is set

### Frontend Tests

**Issue**: Module not found errors
- **Solution**: Run `npm install` to ensure all dependencies are installed

**Issue**: Tests timing out
- **Solution**: Increase timeout in test or use `waitFor` for async operations

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/docs/getting-started)

