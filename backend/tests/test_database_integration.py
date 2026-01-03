"""
Database Integration Tests

Tests that validate:
- Database CRUD operations
- Data persistence
- Schema correctness
- Constraints and relationships
- Foreign key constraints
- Cascade deletes
"""
import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app import models
from app.database import Base


@pytest.mark.integration
class TestStudentDatabaseIntegration:
    """Test Student model database operations."""
    
    def test_create_student(self, db_session):
        """Test creating a student in the database."""
        student = models.Student(
            name="john_doe",
            hashed_password="hashed_password_123",
            faculty="Computer Science",
            year=2
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)
        
        assert student.id is not None
        assert student.name == "john_doe"
        assert student.faculty == "Computer Science"
        assert student.year == 2
        assert student.created_at is not None
    
    def test_student_name_unique_constraint(self, db_session):
        """Test that student names must be unique."""
        student1 = models.Student(
            name="unique_user",
            hashed_password="hash1"
        )
        db_session.add(student1)
        db_session.commit()
        
        student2 = models.Student(
            name="unique_user",
            hashed_password="hash2"
        )
        db_session.add(student2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_student_cascade_delete_courses(self, db_session, test_student, test_course):
        """Test that deleting a student cascades to student_courses."""
        # Create student-course relationship
        student_course = models.StudentCourse(
            student_id=test_student.id,
            course_id=test_course.id,
            status="completed"
        )
        db_session.add(student_course)
        db_session.commit()
        
        # Verify relationship exists
        assert db_session.query(models.StudentCourse).filter_by(
            student_id=test_student.id
        ).first() is not None
        
        # Delete student
        db_session.delete(test_student)
        db_session.commit()
        
        # Verify student_course was deleted
        assert db_session.query(models.StudentCourse).filter_by(
            student_id=test_student.id
        ).first() is None
    
    def test_student_cascade_delete_ratings(self, db_session, test_student, test_course):
        """Test that deleting a student cascades to ratings."""
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.5,
            comment="Great!"
        )
        db_session.add(rating)
        db_session.commit()
        
        rating_id = rating.id
        
        # Delete student
        db_session.delete(test_student)
        db_session.commit()
        
        # Verify rating was deleted
        assert db_session.query(models.Rating).filter_by(id=rating_id).first() is None
    
    def test_student_cascade_delete_reviews(self, db_session, test_student, test_course):
        """Test that deleting a student cascades to course reviews."""
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        db_session.commit()
        
        review_id = review.id
        
        # Delete student
        db_session.delete(test_student)
        db_session.commit()
        
        # Verify review was deleted
        assert db_session.query(models.CourseReview).filter_by(id=review_id).first() is None
    
    def test_student_human_skills_relationship(self, db_session, test_student, test_skill_human):
        """Test many-to-many relationship between students and human skills."""
        test_student.human_skills.append(test_skill_human)
        db_session.commit()
        db_session.refresh(test_student)
        
        assert len(test_student.human_skills) == 1
        assert test_student.human_skills[0].id == test_skill_human.id
        
        # Test removal
        test_student.human_skills.remove(test_skill_human)
        db_session.commit()
        db_session.refresh(test_student)
        
        assert len(test_student.human_skills) == 0


@pytest.mark.integration
class TestCourseDatabaseIntegration:
    """Test Course model database operations."""
    
    def test_create_course(self, db_session):
        """Test creating a course in the database."""
        course = models.Course(
            name="Advanced Algorithms",
            description="Complex algorithm design",
            workload=15,
            credits=4.0,
            status="Selective"
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        assert course.id is not None
        assert course.name == "Advanced Algorithms"
        assert course.workload == 15
        assert course.credits == 4.0
        assert course.status == "Selective"
        assert course.created_at is not None
    
    def test_course_name_unique_constraint(self, db_session):
        """Test that course names must be unique."""
        course1 = models.Course(name="Unique Course", description="First")
        course2 = models.Course(name="Unique Course", description="Second")
        
        db_session.add(course1)
        db_session.commit()
        
        db_session.add(course2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_course_cascade_delete_prerequisites(self, db_session):
        """Test that deleting a course cascades to prerequisites."""
        course1 = models.Course(name="Prerequisite Course")
        course2 = models.Course(name="Main Course")
        db_session.add_all([course1, course2])
        db_session.commit()
        
        prerequisite = models.CoursePrerequisite(
            course_id=course2.id,
            required_course_id=course1.id
        )
        db_session.add(prerequisite)
        db_session.commit()
        
        prerequisite_id = prerequisite.id
        
        # Delete main course
        db_session.delete(course2)
        db_session.commit()
        
        # Verify prerequisite was deleted
        assert db_session.query(models.CoursePrerequisite).filter_by(
            id=prerequisite_id
        ).first() is None
    
    def test_course_cascade_delete_ratings(self, db_session, test_course, test_student):
        """Test that deleting a course cascades to ratings."""
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.0
        )
        db_session.add(rating)
        db_session.commit()
        
        rating_id = rating.id
        
        # Delete course
        db_session.delete(test_course)
        db_session.commit()
        
        # Verify rating was deleted
        assert db_session.query(models.Rating).filter_by(id=rating_id).first() is None
    
    def test_course_skills_relationship(self, db_session, test_course, test_skill_technical):
        """Test many-to-many relationship between courses and skills."""
        test_course.skills.append(test_skill_technical)
        db_session.commit()
        db_session.refresh(test_course)
        
        assert len(test_course.skills) == 1
        assert test_course.skills[0].id == test_skill_technical.id


@pytest.mark.integration
class TestRatingDatabaseIntegration:
    """Test Rating model database operations."""
    
    def test_create_rating(self, db_session, test_student, test_course):
        """Test creating a rating."""
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=4.5,
            comment="Excellent course"
        )
        db_session.add(rating)
        db_session.commit()
        db_session.refresh(rating)
        
        assert rating.id is not None
        assert rating.student_id == test_student.id
        assert rating.course_id == test_course.id
        assert rating.score == 4.5
        assert rating.comment == "Excellent course"
        assert rating.created_at is not None
    
    def test_rating_foreign_key_student(self, db_session, test_course):
        """Test that rating requires valid student_id."""
        rating = models.Rating(
            student_id=99999,  # Non-existent student
            course_id=test_course.id,
            score=4.0
        )
        db_session.add(rating)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_rating_foreign_key_course(self, db_session, test_student):
        """Test that rating requires valid course_id."""
        rating = models.Rating(
            student_id=test_student.id,
            course_id=99999,  # Non-existent course
            score=4.0
        )
        db_session.add(rating)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_rating_score_constraint(self, db_session, test_student, test_course):
        """Test that rating score can be any float (validation at API level)."""
        # Database allows any float, but API should validate 1-5 range
        rating = models.Rating(
            student_id=test_student.id,
            course_id=test_course.id,
            score=10.0  # Invalid but DB allows it
        )
        db_session.add(rating)
        db_session.commit()
        
        # Verify it was saved (constraint validation happens at API level)
        assert rating.score == 10.0


@pytest.mark.integration
class TestCourseReviewDatabaseIntegration:
    """Test CourseReview model database operations."""
    
    def test_create_review(self, db_session, test_student, test_course):
        """Test creating a course review."""
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0,
            languages_learned="Python, JavaScript",
            course_outputs="Web app"
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)
        
        assert review.id is not None
        assert review.student_id == test_student.id
        assert review.course_id == test_course.id
        assert review.final_score == 9.0
        assert review.industry_relevance_rating == 5
        assert review.created_at is not None
    
    def test_review_foreign_key_student(self, db_session, test_course):
        """Test that review requires valid student_id."""
        review = models.CourseReview(
            student_id=99999,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_review_foreign_key_course(self, db_session, test_student):
        """Test that review requires valid course_id."""
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=99999,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_review_cascade_delete_on_course(self, db_session, test_student, test_course):
        """Test that deleting a course cascades to reviews."""
        review = models.CourseReview(
            student_id=test_student.id,
            course_id=test_course.id,
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.0
        )
        db_session.add(review)
        db_session.commit()
        
        review_id = review.id
        
        # Delete course
        db_session.delete(test_course)
        db_session.commit()
        
        # Verify review was deleted
        assert db_session.query(models.CourseReview).filter_by(id=review_id).first() is None


@pytest.mark.integration
class TestCareerGoalDatabaseIntegration:
    """Test CareerGoal model database operations."""
    
    def test_create_career_goal(self, db_session):
        """Test creating a career goal."""
        goal = models.CareerGoal(
            name="Data Scientist",
            description="Analyze data and build models"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)
        
        assert goal.id is not None
        assert goal.name == "Data Scientist"
        assert goal.description == "Analyze data and build models"
    
    def test_career_goal_technical_skills_relationship(self, db_session, test_career_goal, test_skill_technical):
        """Test relationship between career goals and technical skills."""
        cg_skill = models.CareerGoalTechnicalSkill(
            career_goal_id=test_career_goal.id,
            skill_id=test_skill_technical.id
        )
        db_session.add(cg_skill)
        db_session.commit()
        
        db_session.refresh(test_career_goal)
        assert len(test_career_goal.technical_skills) == 1
        assert test_career_goal.technical_skills[0].skill_id == test_skill_technical.id
    
    def test_career_goal_cascade_delete_skills(self, db_session, test_career_goal, test_skill_technical):
        """Test that deleting career goal cascades to skill relationships."""
        cg_skill = models.CareerGoalTechnicalSkill(
            career_goal_id=test_career_goal.id,
            skill_id=test_skill_technical.id
        )
        db_session.add(cg_skill)
        db_session.commit()
        
        # Delete career goal
        db_session.delete(test_career_goal)
        db_session.commit()
        
        # Verify relationship was deleted
        assert db_session.query(models.CareerGoalTechnicalSkill).filter_by(
            career_goal_id=test_career_goal.id
        ).first() is None


@pytest.mark.integration
class TestSkillDatabaseIntegration:
    """Test Skill model database operations."""
    
    def test_create_skill(self, db_session):
        """Test creating a skill."""
        skill = models.Skill(
            name="React",
            type="technical",
            description="React framework"
        )
        db_session.add(skill)
        db_session.commit()
        db_session.refresh(skill)
        
        assert skill.id is not None
        assert skill.name == "React"
        assert skill.type == "technical"
    
    def test_skill_type_validation(self, db_session):
        """Test that skill type can be 'technical' or 'human'."""
        # Database doesn't enforce enum, but API should
        skill = models.Skill(
            name="Test Skill",
            type="invalid_type"  # DB allows it, API should validate
        )
        db_session.add(skill)
        db_session.commit()
        
        # Verify it was saved (validation happens at API level)
        assert skill.type == "invalid_type"


@pytest.mark.integration
class TestStudentCourseDatabaseIntegration:
    """Test StudentCourse association model."""
    
    def test_create_student_course(self, db_session, test_student, test_course):
        """Test creating a student-course relationship."""
        student_course = models.StudentCourse(
            student_id=test_student.id,
            course_id=test_course.id,
            status="completed"
        )
        db_session.add(student_course)
        db_session.commit()
        
        assert student_course.student_id == test_student.id
        assert student_course.course_id == test_course.id
        assert student_course.status == "completed"
        assert student_course.created_at is not None
    
    def test_student_course_composite_primary_key(self, db_session, test_student, test_course):
        """Test that student_id + course_id form a composite primary key."""
        sc1 = models.StudentCourse(
            student_id=test_student.id,
            course_id=test_course.id,
            status="completed"
        )
        db_session.add(sc1)
        db_session.commit()
        
        # Try to create duplicate
        sc2 = models.StudentCourse(
            student_id=test_student.id,
            course_id=test_course.id,
            status="in_progress"
        )
        db_session.add(sc2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_student_course_cascade_delete_on_student(self, db_session, test_student, test_course):
        """Test cascade delete when student is deleted."""
        student_course = models.StudentCourse(
            student_id=test_student.id,
            course_id=test_course.id,
            status="completed"
        )
        db_session.add(student_course)
        db_session.commit()
        
        # Delete student
        db_session.delete(test_student)
        db_session.commit()
        
        # Verify student_course was deleted
        assert db_session.query(models.StudentCourse).filter_by(
            student_id=test_student.id
        ).first() is None

