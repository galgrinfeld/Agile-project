"""
Seed script to initialize the database with tables only (no sample data).
This ensures a clean schema is ready for production use.
"""

from .database import SessionLocal, engine
from . import models
from sqlalchemy import text
# auth_utils import is still needed for the student model dependency on startup
from .auth_utils import get_password_hash 


def seed_database():
    """Initialize the database tables without populating sample data."""
    db = SessionLocal()
    
    # --- CRITICAL: Drop all existing tables to apply the new schema ---
    try:
        # Drop all tables with CASCADE to handle dependencies and ensure the new schema is used
        db.execute(text("DROP TABLE IF EXISTS course_reviews CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS ratings CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS students CASCADE")) 
        db.execute(text("DROP TABLE IF EXISTS courses CASCADE"))
        db.commit()
        print("Existing tables dropped successfully.")
    except Exception as e:
        db.rollback()
        # This will still print a warning if a table didn't exist, but it's safe.
        print(f"Warning during DROP (may occur if tables didn't exist): {e}") 
    
    # Create all tables (Now includes 'hashed_password' on the students table)
    models.Base.metadata.create_all(bind=engine)
    print("Database schema created successfully (tables: students, courses, ratings, course_reviews).")
    
    # --- ADD SAMPLE COURSES ---
    sample_courses = [
        models.Course(
            id=10123,
            name="Introduction to Computer Science",
            description="CS101 - Learn fundamental programming concepts and problem-solving techniques",
            difficulty=2,
            workload=4  # credits
        ),
        models.Course(
            id=10124,
            name="Data Structures",
            description="CS201 - Master arrays, linked lists, trees, and algorithms",
            difficulty=4,
            workload=4  # credits
        ),
        models.Course(
            id=10125,
            name="Database Systems",
            description="CS301 - Design and implement relational databases",
            difficulty=3,
            workload=3  # credits
        ),
        models.Course(
            id=10126,
            name="Web Development",
            description="CS302 - Build modern web applications with HTML, CSS, JavaScript",
            difficulty=3,
            workload=3  # credits
        ),
        models.Course(
            id=10127,
            name="Machine Learning",
            description="CS401 - Introduction to ML algorithms and neural networks",
            difficulty=5,
            workload=4  # credits
        ),
    ]
    
    db.add_all(sample_courses)
    db.commit()
    print("Sample courses added successfully.")
    
    # --- ADD DEMO STUDENT ---
    demo_student = models.Student(
        name="demo",
        hashed_password=get_password_hash("demo123"),
        faculty="Computer Science",
        year=3
    )
    db.add(demo_student)
    db.commit()
    print("Demo student created successfully (username: demo, password: demo123).")
    
    # --- ADD SAMPLE COURSE REVIEWS ---
    sample_reviews = [
        models.CourseReview(
            student_id=1,
            course_id=10123,
            languages_learned="HTML, CSS, JavaScript",
            course_outputs="Personal Portfolio Website, Responsive Design",
            industry_relevance_text="Highly relevant for web development careers",
            instructor_feedback="Excellent teaching methodology and clear explanations",
            useful_learning_text="Learned practical skills applicable to real projects",
            industry_relevance_rating=5,
            instructor_rating=5,
            useful_learning_rating=5,
            final_score=10.0
        ),
        models.CourseReview(
            student_id=1,
            course_id=10124,
            languages_learned="Python, Advanced OOP",
            course_outputs="Multiple backend projects, API development",
            industry_relevance_text="Essential for backend development positions",
            instructor_feedback="Great depth of knowledge, challenging assignments",
            useful_learning_text="Very useful for production-level coding",
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=5,
            final_score=9.4
        ),
        models.CourseReview(
            student_id=1,
            course_id=10125,
            languages_learned="React, JavaScript ES6+",
            course_outputs="Interactive React Components, Full App",
            industry_relevance_text="Very relevant for modern frontend development",
            instructor_feedback="Good course content, could use more examples",
            useful_learning_text="Practical knowledge for frontend jobs",
            industry_relevance_rating=5,
            instructor_rating=4,
            useful_learning_rating=4,
            final_score=8.8
        ),
    ]
    
    db.add_all(sample_reviews)
    db.commit()
    print("Sample course reviews added successfully.")
    
    # --- ADD SKILLS (Technical and Human) ---
    technical_skills = [
        models.Skill(name="Python", type="technical", description="Python programming language"),
        models.Skill(name="JavaScript", type="technical", description="JavaScript programming language"),
        models.Skill(name="SQL", type="technical", description="Relational database language"),
        models.Skill(name="React", type="technical", description="React.js for frontend development"),
        models.Skill(name="Node.js", type="technical", description="Node.js for backend development"),
        models.Skill(name="TensorFlow", type="technical", description="ML framework"),
        models.Skill(name="C++", type="technical", description="C++ programming language"),
        models.Skill(name="AWS", type="technical", description="Amazon Web Services"),
        models.Skill(name="Docker", type="technical", description="Containerization"),
        models.Skill(name="Git", type="technical", description="Version control"),
    ]
    human_skills = [
        models.Skill(name="Teamwork", type="human", description="Works well in teams"),
        models.Skill(name="Communication", type="human", description="Clear communicator"),
        models.Skill(name="Self-learner", type="human", description="Able to learn independently"),
        models.Skill(name="Problem-solving", type="human", description="Strong at solving new problems"),
        models.Skill(name="Adaptability", type="human", description="Quick to adjust to change"),
        models.Skill(name="Leadership", type="human", description="Can lead projects or teams"),
    ]
    db.add_all(technical_skills + human_skills)
    db.commit()

    # --- ADD CAREER GOALS ---
    backend = models.CareerGoal(name="Backend Developer", description="Builds server-side logic and APIs.")
    frontend = models.CareerGoal(name="Frontend Developer", description="Develops the user interface of apps.")
    fullstack = models.CareerGoal(name="Full Stack Developer", description="Handles both frontend and backend.")
    mobile = models.CareerGoal(name="Mobile Developer", description="Creates mobile apps for Android/iOS.")
    datascientist = models.CareerGoal(name="Data Scientist", description="Handles data analysis and visualization.")
    dataanalyst = models.CareerGoal(name="Data Analyst", description="Analyzes datasets to find insights.")
    mlengineer = models.CareerGoal(name="Machine Learning Engineer", description="Designs and deploys ML models.")
    devops = models.CareerGoal(name="DevOps Engineer", description="Enables CI/CD and infrastructure as code.")
    cloudarchitect = models.CareerGoal(name="Cloud Architect", description="Designs cloud-based systems.")
    uxdesigner = models.CareerGoal(name="UX Designer", description="Designs user experiences.")
    qaengineer = models.CareerGoal(name="QA Engineer", description="Assures software quality before release.")
    securityengineer = models.CareerGoal(name="Security Engineer", description="Protects systems against threats.")
    productmanager = models.CareerGoal(name="Product Manager", description="Oversees product lifecycle.")
    embeddedsystems = models.CareerGoal(name="Embedded Systems Engineer", description="Works with hardware/firmware.")
    db.add_all([
        backend, frontend, fullstack, mobile, datascientist, dataanalyst, mlengineer,
        devops, cloudarchitect, uxdesigner, qaengineer, securityengineer, productmanager, embeddedsystems
    ])
    db.commit()

    # --- ASSIGN SKILLS TO CAREER GOALS ---
    # Query the ids just inserted
    skill_map = {s.name: s for s in db.query(models.Skill).all()}
    # Assigns for brevity
    def t(name): return skill_map[name] if name in skill_map else None
    def h(name): return skill_map[name] if name in skill_map else None

    backend.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id), models.CareerGoalTechnicalSkill(skill_id=t("SQL").id), models.CareerGoalTechnicalSkill(skill_id=t("Node.js").id), models.CareerGoalTechnicalSkill(skill_id=t("Git").id)]
    backend.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Teamwork").id), models.CareerGoalHumanSkill(skill_id=h("Problem-solving").id)]

    frontend.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("JavaScript").id), models.CareerGoalTechnicalSkill(skill_id=t("React").id), models.CareerGoalTechnicalSkill(skill_id=t("Git").id)]
    frontend.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Communication").id), models.CareerGoalHumanSkill(skill_id=h("Adaptability").id)]

    fullstack.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id), models.CareerGoalTechnicalSkill(skill_id=t("JavaScript").id), models.CareerGoalTechnicalSkill(skill_id=t("SQL").id), models.CareerGoalTechnicalSkill(skill_id=t("React").id)]
    fullstack.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Teamwork").id), models.CareerGoalHumanSkill(skill_id=h("Self-learner").id)]

    mobile.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("JavaScript").id), models.CareerGoalTechnicalSkill(skill_id=t("Git").id)]
    mobile.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Adaptability").id), models.CareerGoalHumanSkill(skill_id=h("Problem-solving").id)]

    datascientist.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id), models.CareerGoalTechnicalSkill(skill_id=t("SQL").id)]
    datascientist.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Problem-solving").id), models.CareerGoalHumanSkill(skill_id=h("Self-learner").id)]

    dataanalyst.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("SQL").id), models.CareerGoalTechnicalSkill(skill_id=t("Python").id)]
    dataanalyst.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Communication").id)]

    mlengineer.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id), models.CareerGoalTechnicalSkill(skill_id=t("TensorFlow").id), models.CareerGoalTechnicalSkill(skill_id=t("SQL").id)]
    mlengineer.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Self-learner").id), models.CareerGoalHumanSkill(skill_id=h("Problem-solving").id)]

    devops.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Docker").id), models.CareerGoalTechnicalSkill(skill_id=t("AWS").id), models.CareerGoalTechnicalSkill(skill_id=t("Python").id)]
    devops.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Teamwork").id), models.CareerGoalHumanSkill(skill_id=h("Communication").id)]

    cloudarchitect.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("AWS").id), models.CareerGoalTechnicalSkill(skill_id=t("Docker").id)]
    cloudarchitect.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Leadership").id), models.CareerGoalHumanSkill(skill_id=h("Adaptability").id)]

    uxdesigner.technical_skills = []
    uxdesigner.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Communication").id)]

    qaengineer.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id)]
    qaengineer.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Problem-solving").id)]

    securityengineer.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("Python").id), models.CareerGoalTechnicalSkill(skill_id=t("C++").id)]
    securityengineer.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Adaptability").id)]

    productmanager.technical_skills = []
    productmanager.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Leadership").id), models.CareerGoalHumanSkill(skill_id=h("Communication").id)]

    embeddedsystems.technical_skills = [models.CareerGoalTechnicalSkill(skill_id=t("C++").id)]
    embeddedsystems.human_skills = [models.CareerGoalHumanSkill(skill_id=h("Self-learner").id)]

    db.commit()
    print("Sample career goals and skills added successfully.")
    db.close()


if __name__ == "__main__":
    seed_database()