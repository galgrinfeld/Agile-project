from sqlalchemy.orm import Session
from .. import models
from sqlalchemy import func
from collections import defaultdict


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_all_course_skills(db: Session):
    # returns list of (course_id, skill_id, relevance_score)
    rows = db.query(models.CourseSkill.course_id, models.CourseSkill.skill_id, models.CourseSkill.relevance_score).all()
    return rows


def get_all_skills(db: Session):
    return db.query(models.Skill).all()


def get_career_goal_skills(db: Session, career_goal_id: int):
    tech = db.query(models.CareerGoalTechnicalSkill).filter(models.CareerGoalTechnicalSkill.career_goal_id == career_goal_id).all()
    human = db.query(models.CareerGoalHumanSkill).filter(models.CareerGoalHumanSkill.career_goal_id == career_goal_id).all()
    tech_ids = [r.skill_id for r in tech]
    human_ids = [r.skill_id for r in human]
    return tech_ids, human_ids


def get_all_courses(db: Session):
    return db.query(models.Course).all()


def get_course_clusters_map(db: Session):
    # returns map course_id -> list of cluster objects
    rows = db.query(models.CourseCluster.course_id, models.Cluster).join(models.Cluster, models.CourseCluster.cluster_id == models.Cluster.id).all()
    m = defaultdict(list)
    for course_id, cluster in rows:
        m[course_id].append(cluster)
    return m


def get_course_review_stats(db: Session):
    # per-course avg and count, and global mean
    per = db.query(models.CourseReview.course_id, func.count(models.CourseReview.id).label('n'), func.avg(models.CourseReview.final_score).label('avg')).group_by(models.CourseReview.course_id).all()
    stats = {r.course_id: {'n': int(r.n), 'avg': float(r.avg)} for r in per}
    global_mean_row = db.query(func.avg(models.CourseReview.final_score)).one()
    global_mean = float(global_mean_row[0]) if global_mean_row[0] is not None else None
    return stats, global_mean


def get_course_prereqs(db: Session):
    # returns map course_id -> set(required_course_id)
    rows = db.query(models.CoursePrerequisite.course_id, models.CoursePrerequisite.required_course_id).all()
    m = defaultdict(set)
    for course_id, req_id in rows:
        m[course_id].add(req_id)
    return m
