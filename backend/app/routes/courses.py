from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[schemas.CourseResponse])
def get_all_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all courses with pagination."""
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=schemas.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.put("/{course_id}", response_model=schemas.CourseResponse)
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Update an existing course."""
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for key, value in course.dict().items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course."""
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted successfully"}
