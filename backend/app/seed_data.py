"""
Seed script to populate the database with sample data.
Run this script to initialize the database with courses, students, enrollments, and ratings.
"""

from .database import SessionLocal, engine
from . import models


def seed_database():
    """Populate the database with sample data."""
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(models.Student).first():
        print("Database already seeded. Skipping...")
        db.close()
        return
    
    # Create sample students
    students = [
        models.Student(faculty="Computer Science", year=1),
        models.Student(faculty="Computer Science", year=2),
        models.Student(faculty="Computer Science", year=3),
        models.Student(faculty="Engineering", year=1),
        models.Student(faculty="Engineering", year=2),
        models.Student(faculty="Business", year=1),
    ]
    db.add_all(students)
    db.commit()
    
    # Create sample courses
    courses = [
        models.Course(
            name="Introduction to Python",
            description="Learn the basics of Python programming",
            difficulty=2,
            workload=5
        ),
        models.Course(
            name="Data Structures and Algorithms",
            description="Master essential data structures and algorithmic thinking",
            difficulty=4,
            workload=8
        ),
        models.Course(
            name="Web Development with FastAPI",
            description="Build modern web applications with FastAPI",
            difficulty=3,
            workload=6
        ),
        models.Course(
            name="Database Design",
            description="Learn SQL and relational database design principles",
            difficulty=3,
            workload=5
        ),
        models.Course(
            name="Machine Learning Fundamentals",
            description="Introduction to machine learning concepts and algorithms",
            difficulty=4,
            workload=8
        ),
        models.Course(
            name="Cloud Computing with AWS",
            description="Deploy and manage applications on AWS cloud",
            difficulty=3,
            workload=6
        ),
    ]
    db.add_all(courses)
    db.commit()
    
    # Create sample enrollments
    enrollments = [
        models.Enrollment(student_id=1, course_id=1),
        models.Enrollment(student_id=1, course_id=2),
        models.Enrollment(student_id=2, course_id=1),
        models.Enrollment(student_id=2, course_id=3),
        models.Enrollment(student_id=3, course_id=2),
        models.Enrollment(student_id=3, course_id=4),
        models.Enrollment(student_id=4, course_id=1),
        models.Enrollment(student_id=5, course_id=5),
        models.Enrollment(student_id=6, course_id=6),
    ]
    db.add_all(enrollments)
    db.commit()
    
    # Create sample ratings
    ratings = [
        models.Rating(student_id=1, course_id=1, score=5.0, comment="Excellent course!"),
        models.Rating(student_id=1, course_id=2, score=4.5, comment="Challenging but rewarding"),
        models.Rating(student_id=2, course_id=1, score=4.0, comment="Good introduction"),
        models.Rating(student_id=2, course_id=3, score=4.8, comment="Very practical and useful"),
        models.Rating(student_id=3, course_id=2, score=4.2, comment="Comprehensive content"),
        models.Rating(student_id=3, course_id=4, score=4.5, comment="Clear explanations"),
        models.Rating(student_id=4, course_id=1, score=3.8, comment="Could use more examples"),
        models.Rating(student_id=5, course_id=5, score=4.7, comment="Great instructor"),
        models.Rating(student_id=6, course_id=6, score=4.3, comment="Hands-on and practical"),
    ]
    db.add_all(ratings)
    db.commit()
    
    print("Database seeded successfully!")
    db.close()


if __name__ == "__main__":
    seed_database()
