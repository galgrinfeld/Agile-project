from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CareerGoal, CareerGoalTechnicalSkill, CareerGoalHumanSkill, Skill
from typing import List, Dict

router = APIRouter(prefix="/career-goals", tags=["career-goals"])

@router.get("/", response_model=List[Dict])
def get_all_career_goals(db: Session = Depends(get_db)):
    try:
        goals = db.query(CareerGoal).all()
        # Gather technical/human skills as list-of-names for each goal
        def skill_names(goal, relation_attr):
            names = []
            for rel in getattr(goal, relation_attr):
                # Use Session.get to fetch by PK and handle missing skills gracefully
                skill = db.get(Skill, rel.skill_id)
                if skill is not None:
                    names.append(skill.name)
            return names

        seen_names = set()
        filtered = []
        for goal in goals:
            if goal.name not in seen_names:
                seen_names.add(goal.name)
                filtered.append(goal)

        return [
            {
                "id": goal.id,
                "name": goal.name,
                "description": goal.description,
                "technical_skills": skill_names(goal, 'technical_skills'),
                "human_skills": skill_names(goal, 'human_skills'),
            }
            for goal in filtered
        ]
    except Exception as e:
        # Ensure we return a proper HTTP error instead of None (which
        # causes FastAPI response validation to fail with 'Input should
        # be a valid list'). Raise an HTTPException so the client gets
        # a clear 500 response and the exception is logged by the server.
        print(f"Exception {e}")
        raise HTTPException(status_code=500, detail=str(e))

    

