"""
Pytest configuration and shared fixtures for all tests.
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db

# Import app but prevent seed_database from running during tests
import os
os.environ['SKIP_SEED'] = 'true'

from app.main import app
from app import models
from app.auth_utils import get_password_hash, create_access_token


# Test database configuration
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_courses_db")
TEST_DB_USER = os.getenv("TEST_DB_USER", "test_admin")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "test_admin")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")

# Use SQLite for faster tests, or PostgreSQL for more realistic testing
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    # SQLite in-memory database for fast tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL test database
    SQLALCHEMY_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Creates tables, yields session, then drops tables.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close session here, handled by fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_student_data():
    """Sample student data for testing."""
    return {
        "name": "test_student",
        "password": "testpass123",
        "faculty": "Computer Science",
        "year": 2,
        "career_goal_id": None,
        "human_skill_ids": [],
        "courses_taken": []
    }


@pytest.fixture
def test_student(db_session: Session, test_student_data):
    """Create a test student in the database."""
    student = models.Student(
        name=test_student_data["name"],
        hashed_password=get_password_hash(test_student_data["password"]),
        faculty=test_student_data["faculty"],
        year=test_student_data["year"],
        career_goal_id=test_student_data["career_goal_id"]
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_student_token(test_student):
    """Generate a JWT token for test student."""
    from datetime import timedelta
    access_token_expires = timedelta(minutes=1440)
    return create_access_token(
        data={"sub": test_student.name, "student_id": test_student.id},
        expires_delta=access_token_expires
    )


@pytest.fixture
def authenticated_client(client, test_student_token):
    """Client with authentication headers."""
    client.headers = {"Authorization": f"Bearer {test_student_token}"}
    return client


@pytest.fixture
def test_course_data():
    """Sample course data for testing."""
    return {
        "name": "Introduction to Computer Science",
        "description": "Basic CS concepts",
        "workload": 10,
        "credits": 3.0,
        "status": "Mandatory"
    }


@pytest.fixture
def test_course(db_session: Session, test_course_data):
    """Create a test course in the database."""
    course = models.Course(**test_course_data)
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def test_career_goal(db_session: Session):
    """Create a test career goal."""
    goal = models.CareerGoal(
        name="Software Engineer",
        description="Build software applications"
    )
    db_session.add(goal)
    db_session.commit()
    db_session.refresh(goal)
    return goal


@pytest.fixture
def test_skill_technical(db_session: Session):
    """Create a test technical skill."""
    skill = models.Skill(
        name="Python",
        type="technical",
        description="Python programming language"
    )
    db_session.add(skill)
    db_session.commit()
    db_session.refresh(skill)
    return skill


@pytest.fixture
def test_skill_human(db_session: Session):
    """Create a test human skill."""
    skill = models.Skill(
        name="Communication",
        type="human",
        description="Effective communication skills"
    )
    db_session.add(skill)
    db_session.commit()
    db_session.refresh(skill)
    return skill


@pytest.fixture
def test_rating_data(test_course):
    """Sample rating data."""
    return {
        "course_id": test_course.id,
        "score": 4.5,
        "comment": "Great course!"
    }


@pytest.fixture
def test_review_data(test_course):
    """Sample course review data."""
    return {
        "course_id": test_course.id,
        "languages_learned": "Python, JavaScript",
        "course_outputs": "Web application",
        "industry_relevance_text": "Very relevant",
        "instructor_feedback": "Excellent instructor",
        "useful_learning_text": "Learned a lot",
        "industry_relevance_rating": 5,
        "instructor_rating": 4,
        "useful_learning_rating": 5
    }

