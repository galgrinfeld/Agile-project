// frontend/src/components/ProfilePage.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../services/authService';
import CourseSelection from './CourseSelection';
import CoursesGrid from './CoursesGrid';
import JobRolesGrid from './JobRolesGrid';
import { JobRoles } from '../utils';

const API_URL = 'http://localhost:8000';
const DEPARTMENTS = ['Computer Science'];
const YEARS = [1, 2, 3, 4];

const ProfilePage = ({ onBack }) => {
    const [allStudents, setAllStudents] = useState([]);
    const { currentUser, token } = useAuth();
    const [loading, setLoading] = useState(true);
    const [editMode, setEditMode] = useState(false);
    const [profile, setProfile] = useState(null);
    const [formData, setFormData] = useState({});
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [nameError, setNameError] = useState(null);
    const [selectedGoals, setSelectedGoals] = useState([]);
    const [showCourseSelector, setShowCourseSelector] = useState(false);
    const [showGoalsSelector, setShowGoalsSelector] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [courses, setCourses] = useState([]);

    // Logic to disable global scroll when not editing
    useEffect(() => {
        if (!editMode) {
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        }

        return () => {
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        };
    }, [editMode]);

    useEffect(() => {
        async function fetchProfile() {
            setLoading(true);
            setError(null);
            setNameError(null);
            try {
                const authToken = token;
                if (!authToken || !currentUser) throw new Error('Not authenticated');
                const res = await fetch(`${API_URL}/students/${currentUser.id}`);
                if (!res.ok) throw new Error('Failed to fetch profile');
                const data = await res.json();
                setProfile(data);
                setFormData({
                    name: data.name || '',
                    faculty: data.faculty || '',
                    year: data.year || '',
                    courses_taken: data.courses_taken || [],
                    career_goals: data.career_goals || [],
                });
            } catch(e) {
                setError(e.message);
            }
            setLoading(false);
        }
        async function fetchCourses() {
            try {
                const response = await fetch(`${API_URL}/courses/`);
                if (!response.ok) {
                    throw new Error('Failed to fetch courses');
                }
                const data = await response.json();
                setCourses(data);
            } catch (e) {
                setError(e.message || 'Failed to load courses');
            }
        }
        fetchProfile();
        fetchCourses();
        fetch('http://localhost:8000/students/?skip=0&limit=100')
            .then(res => res.json())
            .then(data => setAllStudents(data));
    }, [currentUser, token]);

    function handleChange(e) {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (name === 'name' && allStudents) {
            const exists = allStudents.some(s => s.name?.toLowerCase() === value.toLowerCase() && s.id !== currentUser.id);
            setNameError(exists ? 'This name is already taken. Please choose another.' : null);
        }
    }

    function handleCoursesChange(newCourses) {
        setFormData(prev => ({ ...prev, courses_taken: newCourses }));
        setShowCourseSelector(false);
    }

    function handleGoalsChange(newGoals) {
        setFormData(prev => ({ ...prev, career_goals: newGoals }));
        setShowGoalsSelector(false);
    }

    const handleToggleCourse = (courseId) => {
        const isSelected = formData.courses_taken?.includes(courseId);
        if (isSelected) {
            handleCoursesChange(formData.courses_taken.filter(id => id !== courseId));
        } else {
            handleCoursesChange([...(formData.courses_taken || []), courseId]);
        }
    };

    const getCourseCode = (description) => {
        if (!description) return '';
        const match = description.match(/^([A-Z]+\d+)/);
        return match ? match[1] : '';
    };

    const filteredCourses = (searchQuery && searchQuery.length > 0)
        ? courses.filter(course => {
            const searchLower = searchQuery.toLowerCase();
            const courseName = course.name.toLowerCase();
            const courseCode = getCourseCode(course.description).toLowerCase();
            return courseName.includes(searchLower) || courseCode.includes(searchLower);
        })
        : courses;

    const handleToggleGoal = (goalId) => {
        let newGoals;
        if (selectedGoals.includes(goalId)) {
            newGoals = selectedGoals.filter(id => id !== goalId);
        } else {
            newGoals = [...selectedGoals, goalId];
        }
        setSelectedGoals(newGoals);
        handleGoalsChange(newGoals);
    };

    async function handleSave(e) {
        e.preventDefault();
        setError(null);
        setNameError(null);
        setLoading(true);
        setSuccess(false);
        try {
            const authToken = token;
            if (!authToken || !currentUser) throw new Error('Not authenticated');
            const res = await fetch(`${API_URL}/students/${currentUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(formData),
            });
            if (!res.ok) {
                let msg = 'Failed to update profile';
                try {
                    const errResp = await res.json();
                    if (errResp.detail && errResp.detail.toLowerCase().includes('name') && errResp.detail.toLowerCase().includes('exist')) {
                        setNameError('This name is already taken. Please choose another.');
                        msg = errResp.detail;
                    } else {
                        setError(errResp.detail || msg);
                    }
                } catch {
                    setError(msg);
                }
                setLoading(false);
                return;
            }
            const updated = await res.json();
            setProfile(updated);
            setEditMode(false);
            setSuccess(true);
        } catch(e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) return <div style={styles.loading}>Loading profile...</div>;
    if (error) return <div style={styles.error}>{error}</div>;
    if (!profile) return <div style={styles.error}>No profile data found.</div>;

    const goalIdToName = (id) => {
        const MAP = {
            backend: 'Backend Developer',
            frontend: 'Frontend Developer',
            fullstack: 'Full Stack Developer',
            mobile: 'Mobile Developer',
            datascientist: 'Data Scientist',
            dataanalyst: 'Data Analyst',
            mlengineer: 'Machine Learning Engineer',
            devops: 'DevOps Engineer',
            cloudarchitect: 'Cloud Architect',
            uxdesigner: 'UX Designer',
            qaengineer: 'QA Engineer',
            securityengineer: 'Security Engineer',
            productmanager: 'Product Manager',
            embeddedsystems: 'Embedded Systems Engineer',
        };
        return MAP[id] || id;
    };

    return (
        <div style={styles.container}>
            <div style={styles.profileCard}>
                <div style={styles.cardHeader}>
                    <h2 style={styles.header}>My Profile</h2>
                    {!editMode ? (
                        <button
                            style={styles.editButton}
                            onClick={() => setEditMode(true)}
                            title="Edit Profile"
                        >
                            Edit
                        </button>
                    ) : (
                        <button
                            style={styles.doneButton}
                            onClick={() => { 
                                setEditMode(false); 
                                setFormData(profile); 
                                setSelectedGoals(profile.career_goals || []); 
                            }}
                            title="Done Editing"
                        >
                            Done
                        </button>
                    )}
                </div>
                <form onSubmit={handleSave} style={styles.form}>
                    <label style={styles.label}>
                        Name:
                        {editMode ? (
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                style={styles.input}
                                onChange={handleChange}
                                autoFocus
                            />
                        ) : (
                            <div style={styles.readValue}>{profile.name}</div>
                        )}
                        {editMode && nameError && <span style={styles.fieldError}>{nameError}</span>}
                    </label>
                    <label style={styles.label}>
                        Department/Faculty:
                        {editMode ? (
                            <select
                                name="faculty"
                                value={formData.faculty}
                                style={styles.input}
                                onChange={handleChange}
                            >
                                {DEPARTMENTS.map(opt => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        ) : (
                            <div style={styles.readValue}>{profile.faculty}</div>
                        )}
                    </label>
                    <label style={styles.label}>
                        Year:
                        {editMode ? (
                            <select
                                name="year"
                                value={formData.year}
                                style={styles.input}
                                onChange={handleChange}
                            >
                                {YEARS.map(y => (
                                    <option key={y} value={y}>{y}</option>
                                ))}
                            </select>
                        ) : (
                            <div style={styles.readValue}>{profile.year}</div>
                        )}
                    </label>
                    <label style={styles.label}>
                        Courses Taken:
                        {editMode ? (
                            <div>
                                <button type="button" style={styles.inlineEditBtn} onClick={()=>setShowCourseSelector(s=>!s)}>
                                    {showCourseSelector ? 'Hide' : 'Edit Courses'}
                                </button>
                                {showCourseSelector && (
                                    <div style={styles.selectorWrapper}>
                                        <CoursesGrid
                                            filteredCourses={filteredCourses}
                                            selectedCourses={formData.courses_taken}
                                            handleToggleCourse={handleToggleCourse}
                                            getCourseCode={getCourseCode}
                                            styles={styles}
                                        />
                                    </div>
                                )}
                                {!showCourseSelector && (
                                    <div style={styles.tagList}>
                                        {Array.isArray(formData.courses_taken) && formData.courses_taken.length === 0
                                            ? <span style={styles.hint}>Select your completed courses.</span>
                                            : formData.courses_taken.map(courseId => {
                                                let courseObj = null;
                                                if (Array.isArray(courses) && courses.length > 0) {
                                                    courseObj = courses.find(c => c.id === (typeof courseId === 'object' ? courseId.id : courseId));
                                                }
                                                if (!courseObj && Array.isArray(profile?.course_catalog)) {
                                                    courseObj = profile.course_catalog.find(c => c.id === (typeof courseId === 'object' ? courseId.id : courseId));
                                                }
                                                return (
                                                    <span style={styles.tag} key={courseObj?.id || courseId}>
                                                        {courseObj && courseObj.name ? courseObj.name : courseId}
                                                    </span>
                                                );
                                            })}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div style={styles.tagList}>
                                {Array.isArray(profile.courses_taken) && profile.courses_taken.length === 0
                                    ? <span style={styles.hint}>No courses selected.</span>
                                    : profile.courses_taken.map(courseId => {
                                        let courseObj = null;
                                        if (Array.isArray(courses) && courses.length > 0) {
                                            courseObj = courses.find(c => c.id === (typeof courseId === 'object' ? courseId.id : courseId));
                                        }
                                        if (!courseObj && Array.isArray(profile.course_catalog)) {
                                            courseObj = profile.course_catalog.find(c => c.id === (typeof courseId === 'object' ? courseId.id : courseId));
                                        }
                                        return (
                                            <span style={styles.tag} key={courseObj?.id || courseId}>
                                                {courseObj && courseObj.name ? courseObj.name : courseId}
                                            </span>
                                        );
                                    })
                                }
                            </div>
                        )}
                    </label>
                    <label style={styles.label}>
                        Career Goals:
                        {editMode ? (
                            <div>
                                <button type="button" style={styles.inlineEditBtn} onClick={() => {
                                    setSelectedGoals(formData.career_goals || []);
                                    setShowGoalsSelector(s => !s);
                                }}>
                                    {showGoalsSelector ? 'Hide' : 'Edit Goals'}
                                </button>
                                {showGoalsSelector && (
                                    <div style={styles.selectorWrapper}>
                                       <JobRolesGrid
                                            jobRoles={JobRoles}
                                            selectedGoals={selectedGoals}
                                            handleToggleGoal={handleToggleGoal}
                                            styles={styles}
                                        />
                                    </div>
                                )}
                                {!showGoalsSelector && (
                                    <div style={styles.tagList}>
                                        {Array.isArray(formData.career_goals) && formData.career_goals.length === 0
                                            ? <span style={styles.hint}>Select your career goals.</span>
                                            : formData.career_goals.map(id => (
                                                <span style={styles.tag} key={id}>{goalIdToName(id)}</span>
                                            ))}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div style={styles.tagList}>
                                {Array.isArray(profile.career_goals) && profile.career_goals.length === 0
                                    ? <span style={styles.hint}>No career goals set.</span>
                                    : profile.career_goals.map(id => (
                                        <span style={styles.tag} key={id}>{goalIdToName(id)}</span>
                                    ))}
                            </div>
                        )}
                    </label>
                    {editMode && (
                        <div style={styles.buttonRowCenter}>
                            <button type="submit" style={styles.applyButton} disabled={loading}>Apply</button>
                        </div>
                    )}
                    {success && <div style={styles.success}>Profile updated successfully!</div>}
                </form>
            </div>
        </div>
    );
};

const styles = {
    container: {
        fontFamily: 'Roboto, Helvetica, Arial, sans-serif',
        fontSize: 16,
        height: '100vh',
        width: '100vw',
        backgroundColor: '#f5f5f5',
        padding: '20px', // Reduced padding to allow the card to sit higher
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start', // Ensures card starts at the top
        overflow: 'hidden',
        boxSizing: 'border-box',
    },
    profileCard: {
        background: 'white',
        padding: 32,
        borderRadius: 12,
        maxWidth: 540,
        width: '100%',
        boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        position: 'relative',
        margin: '20px 0', // Fixed margin instead of 'auto' to position higher
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
    },
    input: {
        width: '100%',
        padding: 8,
        marginTop: 4,
        marginBottom: 10,
        fontSize: 16,
        borderRadius: 6,
        border: '1px solid #ccc',
    },
    label: {
        fontWeight: 500,
        marginBottom: 2,
        display: 'flex',
        flexDirection: 'column',
        fontSize: 15,
    },
    buttonRowCenter: {
        display: 'flex',
        justifyContent: 'center',
        marginTop: 16,
    },
    applyButton: {
        background: '#00D9A3',
        color: 'white',
        border: 'none',
        borderRadius: 6,
        padding: '10px 36px',
        fontWeight: 600,
        cursor: 'pointer',
        fontSize: 16,
        minWidth: 120,
        alignSelf: 'center',
    },
    editButton: {
        padding: '7px 18px',
        background: '#006cff',
        color: 'white',
        border: 'none',
        borderRadius: 6,
        fontWeight: 600,
        fontSize: 15,
        cursor: 'pointer',
        marginLeft: 8,
        boxShadow: '0 2px 8px rgba(0,108,255,0.07)',
        transition: 'background 0.2s',
    },
    doneButton: {
        padding: '7px 18px',
        background: '#00D9A3',
        color: 'white',
        border: 'none',
        borderRadius: 6,
        fontWeight: 600,
        fontSize: 15,
        cursor: 'pointer',
        marginLeft: 8,
    },
    loading: {
        textAlign: 'center',
        padding: 32,
        fontSize: 18,
        color: '#666',
    },
    error: {
        color: '#dc3545',
        padding: 16,
        textAlign: 'center',
        background: '#faebeb',
        borderRadius: 6,
        marginBottom: 12,
    },
    success: {
        color: '#008800',
        marginTop: 12,
        textAlign: 'center',
    },
    fieldError: {
        color: '#dc3545',
        fontSize: '13px',
        marginTop: '-8px',
        marginBottom: '6px',
    },
    header: {
        fontWeight: 700,
        fontSize: 24,
        marginBottom: 16,
        textAlign: 'left',
    },
    cardHeader: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    readValue: {
        color: '#444',
        padding: '6px 0 8px 2px',
        fontSize: 15,
        fontWeight: 500,
    },
    tagList: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        margin: '6px 0',
    },
    tag: {
        border: '1px solid #00D9A3',
        backgroundColor: '#e4faee',
        color: '#008a63',
        padding: '3px 10px',
        borderRadius: '12px',
        fontWeight: 500,
        fontSize: 13,
        letterSpacing: 0.3,
    },
    hint: {
        fontSize: '12px',
        color: '#888',
        margin: 0,
    },
    inlineEditBtn: {
        background: '#f5f5f5',
        color: '#006',
        border: '1px solid #ccc',
        borderRadius: 8,
        fontSize: 13,
        padding: '4px 12px',
        cursor: 'pointer',
        marginBottom: 6,
        marginLeft: 0,
        marginTop: 2,
    },
    selectorWrapper: {
        background: '#f9f9f9',
        border: '1px solid #e0e0e0',
        borderRadius: 10,
        margin: '10px 0 4px 0',
        padding: '16px 10px',
        maxHeight: '280px', // Slightly smaller to ensure fit
        overflowY: 'auto',
    },
};

export default ProfilePage;