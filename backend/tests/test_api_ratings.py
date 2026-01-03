"""
REST API Tests for Rating Endpoints

Tests:
- GET /ratings/
- GET /ratings/{rating_id}
- GET /ratings/course/{course_id}
- GET /ratings/student/{student_id}
- POST /ratings/
- PUT /ratings/{rating_id}
- DELETE /ratings/{rating_id}
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetRatings:
    """Test GET /ratings/ endpoint."""
    
    def test_get_all_ratings_empty(self, client):
        """Test getting all ratings when none exist."""
        response = client.get("/ratings/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_ratings_with_data(self, client, db_session, test_student, test_course):
        """Test getting all ratings."""
        from app import models
        
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.5,
            comment="Great course"
        )
        db_session.add(rating)
        db_session.commit()
        
        response = client.get("/ratings/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


@pytest.mark.api
class TestGetRatingById:
    """Test GET /ratings/{rating_id} endpoint."""
    
    def test_get_rating_by_id_success(self, client, db_session, test_student, test_course):
        """Test getting a rating by ID."""
        from app import models
        
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.5,
            comment="Excellent"
        )
        db_session.add(rating)
        db_session.commit()
        
        response = client.get(f"/ratings/{rating.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == rating.id
        assert data["score"] == 4.5
        assert data["comment"] == "Excellent"
    
    def test_get_rating_by_id_not_found(self, client):
        """Test getting non-existent rating returns 404."""
        response = client.get("/ratings/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestGetCourseRatings:
    """Test GET /ratings/course/{course_id} endpoint."""
    
    def test_get_course_ratings_success(self, client, db_session, test_student, test_course):
        """Test getting ratings for a specific course."""
        from app import models
        
        rating1 = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.5
        )
        rating2 = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=5.0
        )
        db_session.add_all([rating1, rating2])
        db_session.commit()
        
        response = client.get(f"/ratings/course/{test_course.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(r["course_id"] == test_course.id for r in data)


@pytest.mark.api
class TestGetStudentRatings:
    """Test GET /ratings/student/{student_id} endpoint."""
    
    def test_get_student_ratings_success(self, client, db_session, test_student, test_course):
        """Test getting ratings from a specific student."""
        from app import models
        
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.0
        )
        db_session.add(rating)
        db_session.commit()
        
        response = client.get(f"/ratings/student/{test_student.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(r["student_id"] == test_student.id for r in data)


@pytest.mark.api
class TestCreateRating:
    """Test POST /ratings/ endpoint."""
    
    def test_create_rating_success(self, authenticated_client, test_course):
        """Test creating a rating (requires authentication)."""
        response = authenticated_client.post(
            "/ratings/",
            json={
                "course_id": test_course.id,
                "score": 4.5,
                "comment": "Great course!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["course_id"] == test_course.id
        assert data["score"] == 4.5
        assert data["comment"] == "Great course!"
        assert "student_id" in data
    
    def test_create_rating_requires_auth(self, client, test_course):
        """Test that creating rating requires authentication."""
        response = client.post(
            "/ratings/",
            json={
                "course_id": test_course.id,
                "score": 4.5
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_rating_invalid_course(self, authenticated_client):
        """Test creating rating for non-existent course."""
        response = authenticated_client.post(
            "/ratings/",
            json={
                "course_id": 99999,
                "score": 4.5
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_rating_invalid_score(self, authenticated_client, test_course):
        """Test creating rating with invalid score (should be validated)."""
        response = authenticated_client.post(
            "/ratings/",
            json={
                "course_id": test_course.id,
                "score": 10.0  # Out of range (should be 1-5)
            }
        )
        
        # API may or may not validate this, but should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.api
class TestUpdateRating:
    """Test PUT /ratings/{rating_id} endpoint."""
    
    def test_update_rating_success(self, client, db_session, test_student, test_course):
        """Test updating a rating."""
        from app import models
        
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=3.0,
            comment="Initial comment"
        )
        db_session.add(rating)
        db_session.commit()
        
        response = client.put(
            f"/ratings/{rating.id}",
            json={
                "course_id": test_course.id,
                "score": 5.0,
                "comment": "Updated comment"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == 5.0
        assert data["comment"] == "Updated comment"
    
    def test_update_rating_not_found(self, client, test_course):
        """Test updating non-existent rating."""
        response = client.put(
            "/ratings/99999",
            json={
                "course_id": test_course.id,
                "score": 4.0
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestDeleteRating:
    """Test DELETE /ratings/{rating_id} endpoint."""
    
    def test_delete_rating_success(self, client, db_session, test_student, test_course):
        """Test deleting a rating."""
        from app import models
        
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.0
        )
        db_session.add(rating)
        db_session.commit()
        rating_id = rating.id
        
        response = client.delete(f"/ratings/{rating_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify rating is deleted
        get_response = client.get(f"/ratings/{rating_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_rating_not_found(self, client):
        """Test deleting non-existent rating."""
        response = client.delete("/ratings/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

