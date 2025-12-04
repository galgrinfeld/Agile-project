from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ==================== STUDENT SCHEMAS ====================
class StudentBase(BaseModel):
    """Base schema for Student."""
    faculty: Optional[str] = None
    year: Optional[int] = None


class StudentCreate(StudentBase):
    """Schema for creating a Student."""
    pass


class StudentResponse(StudentBase):
    """Schema for Student response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== COURSE SCHEMAS ====================
class CourseBase(BaseModel):
    """Base schema for Course."""
    name: str
    description: Optional[str] = None
    difficulty: Optional[int] = None
    workload: Optional[int] = None


class CourseCreate(CourseBase):
    """Schema for creating a Course."""
    pass


class CourseResponse(CourseBase):
    """Schema for Course response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== ENROLLMENT SCHEMAS ====================
class EnrollmentBase(BaseModel):
    """Base schema for Enrollment."""
    student_id: int
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating an Enrollment."""
    pass


class EnrollmentResponse(EnrollmentBase):
    """Schema for Enrollment response."""
    id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True


# ==================== RATING SCHEMAS ====================
class RatingBase(BaseModel):
    """Base schema for Rating."""
    student_id: int
    course_id: int
    score: float
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    """Schema for creating a Rating."""
    pass


class RatingResponse(RatingBase):
    """Schema for Rating response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
