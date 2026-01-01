from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, crud
from ..database import get_db
from typing import List

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=List[schemas.StudentResponse])
def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all students with pagination."""
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreateAuth, db: Session = Depends(get_db)):
    """Create a new student."""
    from ..auth_utils import get_password_hash
    student_data = student.model_dump()
    student_data['hashed_password'] = get_password_hash(student_data.pop('password'))
    db_student = crud.create_student(db, student_data)
    return db_student


@router.put("/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Update an existing student."""
    student_data = student.model_dump()
    db_student = crud.update_student(db, student_id, student_data)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@router.put("/{student_id}/courses", response_model=schemas.StudentResponse)
def update_student_courses(student_id: int, enrollment: schemas.EnrollmentUpdate, db: Session = Depends(get_db)):
    """Update the list of courses a student has taken (status='completed')."""
    db_student = crud.get_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Clear existing courses and add new ones with 'completed' status
    db.query(models.StudentCourse).filter(models.StudentCourse.student_id == student_id).delete()
    db.commit()
    
    for course_id in enrollment.courses_taken:
        crud.add_student_course(db, student_id, course_id, status="completed")
    
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student."""
    db_student = crud.get_student(db, student_id)
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}

