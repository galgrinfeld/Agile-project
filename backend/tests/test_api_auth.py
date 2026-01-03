"""
REST API Tests for Authentication Endpoints

Tests:
- Registration
- Login
- Token validation
- Error handling
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestAuthRegistration:
    """Test /auth/register endpoint."""
    
    def test_register_success(self, client, db_session):
        """Test successful student registration."""
        response = client.post(
            "/auth/register",
            json={
                "name": "new_student",
                "password": "securepass123",
                "faculty": "Engineering",
                "year": 1,
                "career_goal_id": None,
                "human_skill_ids": [],
                "courses_taken": []
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "new_student"
        assert data["faculty"] == "Engineering"
        assert data["year"] == 1
        assert "id" in data
        assert "hashed_password" not in data  # Security: password should not be in response
    
    def test_register_duplicate_name(self, client, test_student):
        """Test registration with duplicate name fails."""
        response = client.post(
            "/auth/register",
            json={
                "name": test_student.name,
                "password": "password123",
                "faculty": "CS",
                "year": 1
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_short_password(self, client):
        """Test registration with password shorter than 6 characters fails."""
        response = client.post(
            "/auth/register",
            json={
                "name": "short_pass_user",
                "password": "12345",  # Less than 6 characters
                "faculty": "CS",
                "year": 1
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post(
            "/auth/register",
            json={
                "name": "incomplete_user"
                # Missing password
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestAuthLogin:
    """Test /auth/login endpoint."""
    
    def test_login_success(self, client, test_student, test_student_data):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            data={
                "username": test_student_data["name"],
                "password": test_student_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent_user",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self, client, test_student):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            data={
                "username": test_student.name,
                "password": "wrong_password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post(
            "/auth/login",
            data={},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestAuthTokenValidation:
    """Test token validation in protected endpoints."""
    
    def test_protected_endpoint_with_valid_token(self, authenticated_client, test_student):
        """Test accessing protected endpoint with valid token."""
        response = authenticated_client.get("/students/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_student.id
        assert data["name"] == test_student.name
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/students/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/students/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_expired_token(self, client, test_student):
        """Test accessing protected endpoint with expired token."""
        from datetime import timedelta
        from app.auth_utils import create_access_token
        
        # Create expired token
        expired_token = create_access_token(
            data={"sub": test_student.name, "student_id": test_student.id},
            expires_delta=timedelta(minutes=-1)  # Expired 1 minute ago
        )
        
        response = client.get(
            "/students/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

