"""Simple script to run recommendations for a given student id (dev use)."""
from backend.app.database import SessionLocal
from backend.app.recommendation_engine import service


def run(student_id=1, career_goal_id=None):
    db = SessionLocal()
    try:
        res = service.recommend_courses(db, student_id, career_goal_id or 1, k=5, enforce_prereqs=False)
        print(res)
    finally:
        db.close()


if __name__ == '__main__':
    run()
