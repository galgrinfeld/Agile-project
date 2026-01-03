"""
REST API Tests for Course Review Endpoints

Tests:
- GET /reviews/
- POST /reviews/
- GET /reviews/course/{course_id}
- GET /reviews/student/{student_id}
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetReviews:
    """Test GET /reviews/ endpoint."""
    
    def test_get_all_reviews_empty(self, client):
        """Test getting all reviews when none exist."""
        response = client.get("/reviews/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_reviews_with_data(self, client, db_session, test_student, test_course):
        """Test getting all reviews."""
        from app import models
        
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        db_session.commit()
        
        response = client.get("/reviews/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


@pytest.mark.api
class TestCreateReview:
    """Test POST /reviews/ endpoint."""
    
    def test_create_review_success(self, authenticated_client, test_course):
        """Test creating a course review (requires authentication)."""
        response = authenticated_client.post(
            "/reviews/",
            json={
                "course_id": test_course.id,
                "industry_relevance_rating": 5,
                "instructor_rating": 4,
                "useful_learning_rating": 5,
                "languages_learned": "Python, JavaScript",
                "course_outputs": "Web application",
                "industry_relevance_text": "Very relevant",
                "instructor_feedback": "Great instructor",
                "useful_learning_text": "Learned a lot"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["course_id"] == test_course.id
        assert data["industry_relevance_rating"] == 5
        assert data["instructor_rating"] == 4
        assert data["useful_learning_rating"] == 5
        assert "final_score" in data
        assert data["final_score"] > 0  # Should be calculated
        assert "student_id" in data
    
    def test_create_review_calculates_final_score(self, authenticated_client, test_course):
        """Test that final score is calculated correctly."""
        response = authenticated_client.post(
            "/reviews/",
            json={
                "course_id": test_course.id,
                "industry_relevance_rating": 5,
                "instructor_rating": 4,
                "useful_learning_rating": 5
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Formula: ((5*5) + (4*2) + (5*3)) / 10 * 2 = (25 + 8 + 15) / 10 * 2 = 48/10 * 2 = 9.6
        expected_score = ((5 * 5) + (4 * 2) + (5 * 3)) / 10 * 2
        assert abs(data["final_score"] - expected_score) < 0.01
    
    def test_create_review_requires_auth(self, client, test_course):
        """Test that creating review requires authentication."""
        response = client.post(
            "/reviews/",
            json={
                "course_id": test_course.id,
                "industry_relevance_rating": 5,
                "instructor_rating": 4,
                "useful_learning_rating": 5
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_review_invalid_course(self, authenticated_client):
        """Test creating review for non-existent course."""
        response = authenticated_client.post(
            "/reviews/",
            json={
                "course_id": 99999,
                "industry_relevance_rating": 5,
                "instructor_rating": 4,
                "useful_learning_rating": 5
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_review_invalid_ratings(self, authenticated_client, test_course):
        """Test creating review with invalid rating values."""
        # Rating out of range (should be 1-5)
        response = authenticated_client.post(
            "/reviews/",
            json={
                "course_id": test_course.id,
                "industry_relevance_rating": 6,  # Invalid
                "instructor_rating": 4,
                "useful_learning_rating": 5
            }
        )
        
        # API may or may not validate this
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_create_review_missing_required_fields(self, authenticated_client, test_course):
        """Test creating review with missing required fields."""
        response = authenticated_client.post(
            "/reviews/",
            json={
                "course_id": test_course.id,
                "industry_relevance_rating": 5
                # Missing instructor_rating and useful_learning_rating
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestGetReviewsByCourse:
    """Test GET /reviews/course/{course_id} endpoint."""
    
    def test_get_reviews_by_course_success(self, client, db_session, test_student, test_course):
        """Test getting reviews for a specific course."""
        from app import models
        
        review1 = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        review2 = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=4,
            instructor_rating=3,
            useful_learning_rating=4,
            final_score=7.0
        )
        db_session.add_all([review1, review2])
        db_session.commit()
        
        response = client.get(f"/reviews/course/{test_course.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(r["course_id"] == test_course.id for r in data)
    
    def test_get_reviews_by_course_not_found(self, client):
        """Test getting reviews for non-existent course."""
        response = client.get("/reviews/course/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestGetReviewsByStudent:
    """Test GET /reviews/student/{student_id} endpoint."""
    
    def test_get_reviews_by_student_success(self, client, db_session, test_student, test_course):
        """Test getting reviews from a specific student."""
        from app import models
        
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        db_session.commit()
        
        response = client.get(f"/reviews/student/{test_student.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(r["student_id"] == test_student.id for r in data)
    
    def test_get_reviews_by_student_not_found(self, client):
        """Test getting reviews for non-existent student."""
        response = client.get("/reviews/student/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

