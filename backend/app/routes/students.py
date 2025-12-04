from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=list[schemas.StudentResponse])
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
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Create a new student."""
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Update an existing student."""
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student."""
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}
