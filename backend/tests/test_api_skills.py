"""
REST API Tests for Skills Endpoints

Tests:
- GET /skills/
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetSkills:
    """Test GET /skills/ endpoint."""
    
    def test_get_all_skills_empty(self, client):
        """Test getting all skills when none exist."""
        response = client.get("/skills/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_skills(self, client, test_skill_technical, test_skill_human):
        """Test getting all skills."""
        response = client.get("/skills/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_skills_filter_by_type_technical(self, client, test_skill_technical, test_skill_human):
        """Test filtering skills by type (technical)."""
        response = client.get("/skills/?type=technical")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(skill["type"] == "technical" for skill in data)
        assert any(skill["id"] == test_skill_technical.id for skill in data)
    
    def test_get_skills_filter_by_type_human(self, client, test_skill_technical, test_skill_human):
        """Test filtering skills by type (human)."""
        response = client.get("/skills/?type=human")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(skill["type"] == "human" for skill in data)
        assert any(skill["id"] == test_skill_human.id for skill in data)
    
    def test_get_skills_invalid_type(self, client):
        """Test filtering with invalid type (should return empty or all)."""
        response = client.get("/skills/?type=invalid")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return empty list or handle gracefully
        assert isinstance(data, list)

