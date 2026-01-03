"""
REST API Tests for Recommendations Endpoints

Tests:
- GET /recommendations/courses
- GET /recommendations/courses/for-goal/{career_goal_id}
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetRecommendations:
    """Test GET /recommendations/courses endpoint."""
    
    def test_get_recommendations_requires_auth(self, client):
        """Test that recommendations require authentication."""
        response = client.get("/recommendations/courses")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_recommendations_no_career_goal(self, authenticated_client, test_student):
        """Test getting recommendations when student has no career goal."""
        response = authenticated_client.get("/recommendations/courses")
        
        # Should return 400 if no career goal is set
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "career goal" in response.json()["detail"].lower()
    
    def test_get_recommendations_with_career_goal(self, authenticated_client, db_session, test_student, test_career_goal):
        """Test getting recommendations with career goal set."""
        # Set career goal for student
        test_student.career_goal_id = test_career_goal.id
        db_session.commit()
        
        response = authenticated_client.get("/recommendations/courses?k=5")
        
        # Should return recommendations (may be empty if no courses match)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data or "courses" in data
    
    def test_get_recommendations_with_k_parameter(self, authenticated_client, db_session, test_student, test_career_goal):
        """Test getting recommendations with k parameter."""
        test_student.career_goal_id = test_career_goal.id
        db_session.commit()
        
        response = authenticated_client.get("/recommendations/courses?k=3")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_recommendations_invalid_k(self, authenticated_client, db_session, test_student, test_career_goal):
        """Test getting recommendations with invalid k parameter."""
        test_student.career_goal_id = test_career_goal.id
        db_session.commit()
        
        response = authenticated_client.get("/recommendations/courses?k=0")
        
        # Should return 422 for invalid k (ge=1)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestGetRecommendationsForGoal:
    """Test GET /recommendations/courses/for-goal/{career_goal_id} endpoint."""
    
    def test_get_recommendations_for_goal_requires_auth(self, client, test_career_goal):
        """Test that recommendations for goal require authentication."""
        response = client.get(f"/recommendations/courses/for-goal/{test_career_goal.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_recommendations_for_goal_success(self, authenticated_client, test_career_goal):
        """Test getting recommendations for a specific career goal."""
        response = authenticated_client.get(
            f"/recommendations/courses/for-goal/{test_career_goal.id}?k=5"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data or "courses" in data
    
    def test_get_recommendations_for_goal_not_found(self, authenticated_client):
        """Test getting recommendations for non-existent career goal."""
        response = authenticated_client.get("/recommendations/courses/for-goal/99999?k=5")
        
        # May return 200 with empty results or 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

