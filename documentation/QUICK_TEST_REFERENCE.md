# Quick Test Reference

## Quick Start

### Backend Tests

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_auth.py
```

### Frontend Tests

```bash
# Install dependencies
cd frontend
npm install

# Run all tests
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage --watchAll=false
```

## Test Files Overview

### Backend Tests (`backend/tests/`)

| File | Description | Test Count |
|------|-------------|------------|
| `test_database_integration.py` | Database CRUD, relationships, constraints | 30+ |
| `test_api_auth.py` | Authentication endpoints | 15+ |
| `test_api_students.py` | Student endpoints | 15+ |
| `test_api_courses.py` | Course endpoints | 20+ |
| `test_api_ratings.py` | Rating endpoints | 15+ |
| `test_api_reviews.py` | Course review endpoints | 10+ |
| `test_api_career_goals.py` | Career goal endpoints | 5+ |
| `test_api_skills.py` | Skill endpoints | 5+ |
| `test_api_recommendations.py` | Recommendation endpoints | 5+ |

### Frontend Tests (`frontend/src/__tests__/`)

| File | Description | Test Count |
|------|-------------|------------|
| `services/authService.test.js` | Auth service unit tests | 10+ |
| `services/authService.integration.test.js` | Auth context integration | 5+ |
| `services/courseService.test.js` | Course service tests | 10+ |
| `components/AuthForm.test.jsx` | Auth form component | 10+ |
| `components/CourseDetailsPage.test.jsx` | Course details component | 5+ |

## Common Commands

### Run Tests by Category

```bash
# Backend: Integration tests only
pytest -m integration

# Backend: API tests only
pytest -m api

# Backend: Specific endpoint
pytest tests/test_api_auth.py::TestAuthLogin
```

### Coverage Reports

```bash
# Backend coverage
cd backend && pytest --cov=app --cov-report=html
# Open: htmlcov/index.html

# Frontend coverage
cd frontend && npm test -- --coverage --watchAll=false
# Open: coverage/index.html
```

## Test Markers

Backend tests use markers for categorization:

- `@pytest.mark.integration` - Database integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.unit` - Unit tests (if any)

## Troubleshooting

**Backend: Import errors**
```bash
# Make sure you're in backend directory
cd backend
# Install dependencies
pip install -r requirements.txt
```

**Frontend: Module not found**
```bash
# Install dependencies
cd frontend
npm install
```

**Backend: Database errors**
- Tests use SQLite in-memory by default
- For PostgreSQL: `export USE_SQLITE=false`

## Test Structure

```
backend/tests/
├── conftest.py              # Fixtures and config
├── test_database_integration.py
└── test_api_*.py            # API endpoint tests

frontend/src/__tests__/
├── services/                # Service tests
└── components/              # Component tests
```

## Key Features

✅ **Idempotent** - Tests can run multiple times safely
✅ **Isolated** - Each test is independent
✅ **Fast** - SQLite in-memory for backend
✅ **Comprehensive** - 130+ backend, 35+ frontend tests
✅ **CI/CD Ready** - No manual intervention needed

For detailed documentation, see `TESTING_GUIDE.md`.

