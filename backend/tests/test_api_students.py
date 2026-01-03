"""
REST API Tests for Student Endpoints

Tests:
- GET /students/
- GET /students/{student_id}
- GET /students/me
- POST /students/
- PUT /students/{student_id}
- PUT /students/{student_id}/courses
- DELETE /students/{student_id}
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetStudents:
    """Test GET /students/ endpoint."""
    
    def test_get_all_students_empty(self, client):
        """Test getting all students when none exist."""
        response = client.get("/students/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_students_with_pagination(self, client, test_student):
        """Test getting all students with pagination."""
        response = client.get("/students/?skip=0&limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(s["id"] == test_student.id for s in data)
    
    def test_get_all_students_pagination_limit(self, client, db_session):
        """Test pagination limit works correctly."""
        from app import models
        from app.auth_utils import get_password_hash
        
        # Create multiple students
        for i in range(5):
            student = models.Student(
                name=f"student_{i}",
                hashed_password=get_password_hash("pass123")
            )
            db_session.add(student)
        db_session.commit()
        
        response = client.get("/students/?skip=0&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2


@pytest.mark.api
class TestGetStudentById:
    """Test GET /students/{student_id} endpoint."""
    
    def test_get_student_by_id_success(self, client, test_student):
        """Test getting a student by ID."""
        response = client.get(f"/students/{test_student.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_student.id
        assert data["name"] == test_student.name
        assert "hashed_password" not in data
    
    def test_get_student_by_id_not_found(self, client):
        """Test getting non-existent student returns 404."""
        response = client.get("/students/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestGetCurrentStudent:
    """Test GET /students/me endpoint."""
    
    def test_get_current_student_success(self, authenticated_client, test_student):
        """Test getting current authenticated student."""
        response = authenticated_client.get("/students/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_student.id
        assert data["name"] == test_student.name
    
    def test_get_current_student_requires_auth(self, client):
        """Test that /students/me requires authentication."""
        response = client.get("/students/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
class TestCreateStudent:
    """Test POST /students/ endpoint."""
    
    def test_create_student_success(self, client, db_session):
        """Test creating a new student."""
        response = client.post(
            "/students/",
            json={
                "name": "new_student_api",
                "password": "password123",
                "faculty": "Engineering",
                "year": 2,
                "career_goal_id": None,
                "human_skill_ids": [],
                "courses_taken": []
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "new_student_api"
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_create_student_duplicate_name(self, client, test_student):
        """Test creating student with duplicate name fails."""
        response = client.post(
            "/students/",
            json={
                "name": test_student.name,
                "password": "password123",
                "faculty": "CS",
                "year": 1
            }
        )
        
        # Should fail due to unique constraint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.api
class TestUpdateStudent:
    """Test PUT /students/{student_id} endpoint."""
    
    def test_update_student_success(self, client, test_student):
        """Test updating a student."""
        response = client.put(
            f"/students/{test_student.id}",
            json={
                "name": test_student.name,  # Keep same name
                "faculty": "Updated Faculty",
                "year": 3,
                "career_goal_id": None,
                "human_skill_ids": [],
                "courses_taken": []
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["faculty"] == "Updated Faculty"
        assert data["year"] == 3
    
    def test_update_student_not_found(self, client):
        """Test updating non-existent student returns 404."""
        response = client.put(
            "/students/99999",
            json={
                "name": "updated_name",
                "faculty": "CS",
                "year": 1
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestUpdateStudentCourses:
    """Test PUT /students/{student_id}/courses endpoint."""
    
    def test_update_student_courses_success(self, client, test_student, test_course, db_session):
        """Test updating student's courses."""
        # Create another course
        from app import models
        course2 = models.Course(name="Course 2", description="Second course")
        db_session.add(course2)
        db_session.commit()
        
        response = client.put(
            f"/students/{test_student.id}/courses",
            json={
                "courses_taken": [test_course.id, course2.id]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["courses_taken"]) == 2
        assert test_course.id in data["courses_taken"]
        assert course2.id in data["courses_taken"]
    
    def test_update_student_courses_empty_list(self, client, test_student, test_course):
        """Test clearing student's courses."""
        # First add a course
        client.put(
            f"/students/{test_student.id}/courses",
            json={"courses_taken": [test_course.id]}
        )
        
        # Then clear it
        response = client.put(
            f"/students/{test_student.id}/courses",
            json={"courses_taken": []}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["courses_taken"] == []
    
    def test_update_student_courses_not_found(self, client):
        """Test updating courses for non-existent student."""
        response = client.put(
            "/students/99999/courses",
            json={"courses_taken": [1, 2]}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestDeleteStudent:
    """Test DELETE /students/{student_id} endpoint."""
    
    def test_delete_student_success(self, client, db_session):
        """Test deleting a student."""
        from app import models
        from app.auth_utils import get_password_hash
        
        student = models.Student(
            name="to_delete",
            hashed_password=get_password_hash("pass123")
        )
        db_session.add(student)
        db_session.commit()
        student_id = student.id
        
        response = client.delete(f"/students/{student_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify student is deleted
        get_response = client.get(f"/students/{student_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_student_not_found(self, client):
        """Test deleting non-existent student."""
        response = client.delete("/students/99999")
        
        # Should return 404 or 200 with error message
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

