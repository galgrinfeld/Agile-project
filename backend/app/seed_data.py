"""
Seed script to populate the database with sample data.
Run this script to initialize the database with courses, students, and ratings.
"""

from .database import SessionLocal, engine
from . import models
from sqlalchemy import text


def seed_database():
    """Populate the database with sample data."""
    db = SessionLocal()
    
    # Drop all tables with CASCADE to handle dependencies
    try:
        db.execute(text("DROP TABLE IF EXISTS ratings CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS enrollment CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS students CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS courses CASCADE"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning during DROP: {e}")
    
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create sample courses first
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
    
    # Create sample students with courses_taken arrays
    students = [
        models.Student(name="Alice Johnson", faculty="Computer Science", year=1, courses_taken=[1, 2]),
        models.Student(name="Bob Smith", faculty="Computer Science", year=2, courses_taken=[1, 3]),
        models.Student(name="Charlie Brown", faculty="Computer Science", year=3, courses_taken=[2, 4]),
        models.Student(name="Diana Prince", faculty="Engineering", year=1, courses_taken=[1]),
        models.Student(name="Eve Wilson", faculty="Engineering", year=2, courses_taken=[5]),
        models.Student(name="Frank Miller", faculty="Business", year=1, courses_taken=[6]),
    ]
    db.add_all(students)
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


