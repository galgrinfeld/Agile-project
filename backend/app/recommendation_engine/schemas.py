from pydantic import BaseModel
from typing import List, Optional, Dict


class SkillMatch(BaseModel):
    skill_id: int
    name: str
    relevance_score: float


class CourseExplain(BaseModel):
    course_id: int
    name: str
    final_score: float
    s_role: float
    s_affinity: float
    soft_readiness: float
    s_cluster: int
    q_smoothed: float
    avg_score_raw: Optional[float]
    review_count: int
    matched_technical_skills: List[SkillMatch] = []
    missing_technical_skills: List[int] = []
    course_clusters: List[Dict] = []


class RecommendationsResponse(BaseModel):
    soft_readiness: float
    inferred_goal_clusters: List[Dict] = []
    recommendations: List[CourseExplain] = []
    blocked_courses: Optional[List[Dict]] = []
