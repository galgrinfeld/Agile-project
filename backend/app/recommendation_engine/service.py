from . import config
from . import queries
import numpy as np
from typing import List, Dict, Any


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def recommend_courses(db, student_id: int, career_goal_id: int, k: int = 10, enforce_prereqs: bool = True):
    # Bulk fetch
    student = queries.get_student(db, student_id)
    if not student:
        raise ValueError("Student not found")

    all_courses = queries.get_all_courses(db)
    course_skills_rows = queries.get_all_course_skills(db)
    skills = queries.get_all_skills(db)
    course_clusters_map = queries.get_course_clusters_map(db)
    review_stats, global_mean = queries.get_course_review_stats(db)
    prereq_map = queries.get_course_prereqs(db)

    # Normalize global mean
    C = (global_mean / 10.0) if global_mean is not None else 0.5

    # Build skill id list
    skill_ids = [s.id for s in skills]
    skill_index = {sid: i for i, sid in enumerate(skill_ids)}
    dim = len(skill_ids)

    # Build course vectors
    course_vectors = {}
    for course in all_courses:
        vec = np.zeros(dim, dtype=float)
        course_vectors[course.id] = vec

    for course_id, skill_id, relevance in course_skills_rows:
        if relevance is None:
            relevance = 0.0
        if skill_id in skill_index:
            course_vectors[course_id][skill_index[skill_id]] = float(relevance)

    # Student completed courses - project to model
    completed_courses = []
    try:
        completed_courses = list(student.courses_taken or [])
    except Exception:
        completed_courses = []

    # Candidate filtering: exclude completed
    candidate_courses = [c for c in all_courses if c.id not in completed_courses]

    # If enforce_prereqs True, separate blocked courses
    blocked_courses = []
    if enforce_prereqs:
        filtered = []
        for c in candidate_courses:
            reqs = prereq_map.get(c.id, set())
            missing = [r for r in reqs if r not in completed_courses]
            if missing:
                blocked_courses.append({'course_id': c.id, 'missing_prereqs': missing})
            else:
                filtered.append(c)
        candidate_courses = filtered

    # Get career goal skills
    tech_ids, human_ids = queries.get_career_goal_skills(db, career_goal_id)
    R_tech = set(tech_ids)
    R_human = set(human_ids)

    # Compute S_role for all courses (use completeness over candidate set and blocked for inference)
    s_role_map = {}
    for c in all_courses:
        if not R_tech:
            s_role_map[c.id] = 0.0
            continue
        scores = []
        for sid in R_tech:
            # find relevance in vector
            if sid in skill_index:
                scores.append(float(course_vectors[c.id][skill_index[sid]]))
            else:
                scores.append(0.0)
        s_role_map[c.id] = float(sum(scores) / len(scores)) if scores else 0.0

    # Infer clusters: top N by S_role across all courses
    top_by_role = sorted(all_courses, key=lambda x: s_role_map.get(x.id, 0.0), reverse=True)[:config.TOP_N_ROLE]
    inferred_cluster_ids = set()
    inferred_clusters = []
    for c in top_by_role:
        clusters = course_clusters_map.get(c.id, [])
        for cl in clusters:
            inferred_cluster_ids.add(cl.id)
            inferred_clusters.append({'id': cl.id, 'name': cl.name})

    # Compute soft_readiness
    if not R_human:
        soft_readiness = 1.0
    else:
        try:
            user_human = set(student.human_skills or [])
        except Exception:
            user_human = set()
        missing = R_human - user_human
        soft_readiness = 1.0 - (len(missing) / len(R_human))

    # Prepare completed course vectors for affinity
    completed_vectors = [course_vectors[cid] for cid in completed_courses if cid in course_vectors]

    results = []
    for c in candidate_courses:
        # S_role
        s_role = float(s_role_map.get(c.id, 0.0))

        # S_affinity: average of top K cosine similarities to completed courses
        if not completed_vectors:
            s_affinity = 0.0
        else:
            sims = [_cosine_sim(course_vectors[c.id], v) for v in completed_vectors]
            sims_sorted = sorted(sims, reverse=True)[:config.TOP_K_SIMILAR]
            s_affinity = float(sum(sims_sorted) / len(sims_sorted)) if sims_sorted else 0.0

        # S_cluster
        course_cluster_ids = set([cl.id for cl in course_clusters_map.get(c.id, [])])
        s_cluster = 1 if (course_cluster_ids & inferred_cluster_ids) else 0

        # Review quality smoothing
        stats = review_stats.get(c.id)
        if stats:
            n_reviews = stats['n']
            avg_raw = stats['avg']
            q_raw = (avg_raw / 10.0) if avg_raw is not None else C
        else:
            n_reviews = 0
            q_raw = C

        m = config.PRIOR_M
        q_smoothed = float((m * C + n_reviews * q_raw) / (m + n_reviews)) if (m + n_reviews) > 0 else C

        # Final score
        final = (config.W1 * s_role) + (config.W2 * s_affinity) + (config.W3 * soft_readiness) + (config.W4 * s_cluster) + (config.W5 * q_smoothed)

        # Explain matched and missing technical skills
        matched = []
        missing_skills = []
        for sid in R_tech:
            if sid in skill_index:
                rel = float(course_vectors[c.id][skill_index[sid]])
                if rel > 0:
                    # fetch skill name lazily
                    matched.append({'skill_id': sid, 'relevance_score': rel})
                else:
                    missing_skills.append(sid)
            else:
                missing_skills.append(sid)

        # avg_score raw and count for explainability
        avg_score_raw = (stats['avg'] if stats and stats.get('avg') is not None else None)

        results.append({
            'course_id': c.id,
            'name': c.name,
            'final_score': float(final),
            's_role': float(s_role),
            's_affinity': float(s_affinity),
            'soft_readiness': float(soft_readiness),
            's_cluster': int(s_cluster),
            'q_smoothed': float(q_smoothed),
            'avg_score_raw': (float(avg_score_raw) if avg_score_raw is not None else None),
            'review_count': int(n_reviews),
            'matched_technical_skills': matched,
            'missing_technical_skills': missing_skills,
            'course_clusters': [{'id': cl.id, 'name': cl.name} for cl in course_clusters_map.get(c.id, [])],
        })

    # Sort by final_score desc and return top k
    sorted_res = sorted(results, key=lambda x: x['final_score'], reverse=True)[:k]

    # Format response
    recommendations = sorted_res

    return {
        'soft_readiness': float(soft_readiness),
        'inferred_goal_clusters': inferred_clusters,
        'recommendations': recommendations,
        'blocked_courses': blocked_courses,
    }
