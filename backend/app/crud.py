from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from . import models, schemas

# ==================== Student CRUD Operations ====================

def get_student(db: Session, student_id: int):
    """Retrieve a student by their ID."""
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_name(db: Session, name: str):
    """Retrieve a student by their unique name (used for login/registration)."""
    return db.query(models.Student).filter(models.Student.name == name).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of students with pagination."""
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, student_data: Dict[str, Any]):
    """
    Create a new student record.
    The data dictionary contains:
    - 'hashed_password' for auth
    - 'career_goal_id' (optional)
    - 'human_skill_ids' (optional, list of skill IDs)
    """
    # Extract many-to-many fields before creating the student
    human_skill_ids = student_data.pop('human_skill_ids', [])
    
    # Create the student with simple fields
    db_student = models.Student(**student_data)
    db.add(db_student)
    db.flush()  # Flush to get the student ID
    
    # Add human skills (many-to-many)
    if human_skill_ids:
        for skill_id in human_skill_ids:
            # Verify the skill exists before adding
            skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
            if skill:
                db_student.human_skills.append(skill)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: int, student_data: Dict[str, Any]):
    """
    Update an existing student record.
    Handles simple fields and many-to-many relationships.
    """
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    # Extract many-to-many fields
    human_skill_ids = student_data.pop('human_skill_ids', None)
    
    # Update simple fields
    for key, value in student_data.items():
        if hasattr(db_student, key) and key != 'id':
            setattr(db_student, key, value)
    
    # Update human skills if provided
    if human_skill_ids is not None:
        # Clear existing skills
        db_student.human_skills.clear()
        # Add new skills
        for skill_id in human_skill_ids:
            skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
            if skill:
                db_student.human_skills.append(skill)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def add_student_course(db: Session, student_id: int, course_id: int, status: str = "completed"):
    """Add a course to a student's courses (or update status)."""
    # Check if already exists
    existing = db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == student_id,
        models.StudentCourse.course_id == course_id
    ).first()
    
    if existing:
        existing.status = status
    else:
        student_course = models.StudentCourse(
            student_id=student_id,
            course_id=course_id,
            status=status
        )
        db.add(student_course)
    
    db.commit()
    return existing if existing else student_course


def remove_student_course(db: Session, student_id: int, course_id: int):
    """Remove a course from a student's courses."""
    db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == student_id,
        models.StudentCourse.course_id == course_id
    ).delete()
    db.commit()


def get_student_courses(db: Session, student_id: int) -> List[models.StudentCourse]:
    """Get all courses for a student."""
    return db.query(models.StudentCourse).filter(
        models.StudentCourse.student_id == student_id
    ).all()


# ==================== Course CRUD Operations (Example) ====================

def get_course(db: Session, course_id: int):
    """Retrieve a course by its ID."""
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of courses with pagination."""
    return db.query(models.Course).offset(skip).limit(limit).all()

# ... other CRUD functions for update, delete, ratings, etc. would go here