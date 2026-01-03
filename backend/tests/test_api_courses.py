"""
REST API Tests for Course Endpoints

Tests:
- GET /courses/
- GET /courses/{course_id}
- GET /courses/{course_id}/stats
- GET /courses/{course_id}/reviews
- POST /courses/
- PUT /courses/{course_id}
- DELETE /courses/{course_id}
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetCourses:
    """Test GET /courses/ endpoint."""
    
    def test_get_all_courses_empty(self, client):
        """Test getting all courses when none exist."""
        response = client.get("/courses/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_courses_with_data(self, client, test_course):
        """Test getting all courses."""
        response = client.get("/courses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(c["id"] == test_course.id for c in data)
    
    def test_get_all_courses_pagination(self, client, db_session):
        """Test pagination for courses."""
        from app import models
        
        # Create multiple courses
        for i in range(5):
            course = models.Course(name=f"Course {i}", description=f"Description {i}")
            db_session.add(course)
        db_session.commit()
        
        response = client.get("/courses/?skip=0&limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3


@pytest.mark.api
class TestGetCourseById:
    """Test GET /courses/{course_id} endpoint."""
    
    def test_get_course_details_success(self, client, test_course):
        """Test getting course details."""
        response = client.get(f"/courses/{test_course.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_course.id
        assert data["name"] == test_course.name
        assert "prerequisites" in data
        assert "skills" in data
        assert "clusters" in data
    
    def test_get_course_details_not_found(self, client):
        """Test getting non-existent course returns 404."""
        response = client.get("/courses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestGetCourseStats:
    """Test GET /courses/{course_id}/stats endpoint."""
    
    def test_get_course_stats_no_reviews(self, client, test_course):
        """Test getting stats for course with no reviews."""
        response = client.get(f"/courses/{test_course.id}/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review_count"] == 0
        assert data["avg_final_score"] == 0.0
    
    def test_get_course_stats_with_reviews(self, client, db_session, test_course, test_student):
        """Test getting stats for course with reviews."""
        from app import models
        
        # Create reviews
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
        
        response = client.get(f"/courses/{test_course.id}/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review_count"] == 2
        assert data["avg_final_score"] == 8.0  # (9.0 + 7.0) / 2
        assert data["avg_industry_relevance"] == 4.5
        assert data["avg_instructor_quality"] == 3.5
    
    def test_get_course_stats_not_found(self, client):
        """Test getting stats for non-existent course."""
        response = client.get("/courses/99999/stats")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestGetCourseReviews:
    """Test GET /courses/{course_id}/reviews endpoint."""
    
    def test_get_course_reviews_empty(self, client, test_course):
        """Test getting reviews for course with no reviews."""
        response = client.get(f"/courses/{test_course.id}/reviews")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
    
    def test_get_course_reviews_pagination(self, client, db_session, test_course, test_student):
        """Test paginated course reviews."""
        from app import models
        
        # Create multiple reviews
        for i in range(5):
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
        
        response = client.get(f"/courses/{test_course.id}/reviews?page=1&page_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] == 5
        assert len(data["items"]) == 2
    
    def test_get_course_reviews_invalid_page(self, client, test_course):
        """Test pagination with invalid page number."""
        response = client.get(f"/courses/{test_course.id}/reviews?page=0&page_size=10")
        
        # Should return 422 for invalid page (ge=1)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_course_reviews_not_found(self, client):
        """Test getting reviews for non-existent course."""
        response = client.get("/courses/99999/reviews")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestCreateCourse:
    """Test POST /courses/ endpoint."""
    
    def test_create_course_success(self, client):
        """Test creating a new course."""
        response = client.post(
            "/courses/",
            json={
                "name": "New Course",
                "description": "Course description",
                "workload": 10,
                "credits": 3.0,
                "status": "Mandatory"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Course"
        assert data["description"] == "Course description"
        assert "id" in data
    
    def test_create_course_duplicate_name(self, client, test_course):
        """Test creating course with duplicate name fails."""
        response = client.post(
            "/courses/",
            json={
                "name": test_course.name,
                "description": "Duplicate"
            }
        )
        
        # Should fail due to unique constraint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.api
class TestUpdateCourse:
    """Test PUT /courses/{course_id} endpoint."""
    
    def test_update_course_success(self, client, test_course):
        """Test updating a course."""
        response = client.put(
            f"/courses/{test_course.id}",
            json={
                "name": test_course.name,  # Keep same name
                "description": "Updated description",
                "workload": 15,
                "credits": 4.0,
                "status": "Selective"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["workload"] == 15
    
    def test_update_course_not_found(self, client):
        """Test updating non-existent course returns 404."""
        response = client.put(
            "/courses/99999",
            json={
                "name": "Updated Course",
                "description": "New description"
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestDeleteCourse:
    """Test DELETE /courses/{course_id} endpoint."""
    
    def test_delete_course_success(self, client, db_session):
        """Test deleting a course."""
        from app import models
        
        course = models.Course(name="To Delete", description="Will be deleted")
        db_session.add(course)
        db_session.commit()
        course_id = course.id
        
        response = client.delete(f"/courses/{course_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify course is deleted
        get_response = client.get(f"/courses/{course_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_course_not_found(self, client):
        """Test deleting non-existent course."""
        response = client.delete("/courses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

