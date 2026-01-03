"""
REST API Tests for Career Goals Endpoints

Tests:
- GET /career-goals/
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestGetCareerGoals:
    """Test GET /career-goals/ endpoint."""
    
    def test_get_all_career_goals_empty(self, client):
        """Test getting all career goals when none exist."""
        response = client.get("/career-goals/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_career_goals_with_data(self, client, test_career_goal):
        """Test getting all career goals."""
        response = client.get("/career-goals/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(g["id"] == test_career_goal.id for g in data)
    
    def test_get_career_goals_with_skills(self, client, db_session, test_career_goal, test_skill_technical, test_skill_human):
        """Test getting career goals with associated skills."""
        from app import models
        
        # Add skills to career goal
        cg_tech_skill = models.CareerGoalTechnicalSkill(
            career_goal_id=test_career_goal.id,
            skill_id=test_skill_technical.id
        )
        cg_human_skill = models.CareerGoalHumanSkill(
            career_goal_id=test_career_goal.id,
            skill_id=test_skill_human.id
        )
        db_session.add_all([cg_tech_skill, cg_human_skill])
        db_session.commit()
        
        response = client.get("/career-goals/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        goal = next(g for g in data if g["id"] == test_career_goal.id)
        assert "technical_skills" in goal
        assert "human_skills" in goal
        assert len(goal["technical_skills"]) >= 1
        assert len(goal["human_skills"]) >= 1

