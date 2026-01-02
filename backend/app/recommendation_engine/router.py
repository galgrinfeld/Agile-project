from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth_utils import get_current_student
from . import service, schemas

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/courses", response_model=schemas.RecommendationsResponse)
def get_recommendations_for_current_student(
    k: int = Query(10, ge=1),
    enforce_prereqs: bool = Query(True),
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student),
):
    # Determine career goal id from student
    student = current_student
    career_goal_id = getattr(student, 'career_goal_id', None)
    # fallback: student.career_goals array may contain a string name or id
    if career_goal_id is None:
        cg_list = getattr(student, 'career_goals', []) or []
        if len(cg_list) == 0:
            raise HTTPException(status_code=400, detail="Student has no career goal set")
        try:
            career_goal_id = int(cg_list[0])
        except Exception:
            # try lookup by name
            from .. import models
            cg = db.query(models.CareerGoal).filter(models.CareerGoal.name == cg_list[0]).first()
            if not cg:
                raise HTTPException(status_code=400, detail="Cannot resolve student's career goal")
            career_goal_id = cg.id

    res = service.recommend_courses(db, student.id, career_goal_id, k=k, enforce_prereqs=enforce_prereqs)
    return res


@router.get("/courses/for-goal/{career_goal_id}", response_model=schemas.RecommendationsResponse)
def get_recommendations_for_goal(
    career_goal_id: int,
    k: int = Query(10, ge=1),
    enforce_prereqs: bool = Query(True),
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student),
):
    res = service.recommend_courses(db, current_student.id, career_goal_id, k=k, enforce_prereqs=enforce_prereqs)
    return res
