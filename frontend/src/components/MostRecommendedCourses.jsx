import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Typography,
  Box,
  IconButton,
  Collapse,
  Button,
  Alert,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useAuth } from '../services/authService';
import { getCourseRecommendations } from '../services/recommendationService';
import { useNavigate } from 'react-router-dom';

const MostRecommendedCourses = () => {
  const { token, currentUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [openMap, setOpenMap] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getCourseRecommendations({ k: 10, enforce_prereqs: true });
        setData(res);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to fetch recommendations');
      } finally {
        setLoading(false);
      }
    };

    if (token) fetchData();
  }, [token]);

  if (!token) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Most Recommended Courses" />
        <CardContent>
          <Typography>Please log in to view personalized recommendations.</Typography>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Most Recommended Courses" />
        <CardContent sx={{ display: 'flex', justifyContent: 'center', minHeight: 180 }}>
          <CircularProgress />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Most Recommended Courses" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.recommendations || data.recommendations.length === 0) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Most Recommended Courses" />
        <CardContent>
          <Typography>No recommendations available. Complete your profile or add completed courses to get recommendations.</Typography>
        </CardContent>
      </Card>
    );
  }

  const toggle = (id) => {
    setOpenMap((m) => ({ ...m, [id]: !m[id] }));
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardHeader title="Most Recommended Courses" action={<Button onClick={() => window.location.reload()}>Refresh</Button>} />
      <CardContent>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Final Score</TableCell>
                <TableCell>Avg (count)</TableCell>
                <TableCell>Career Fit</TableCell>
                <TableCell>Affinity</TableCell>
                <TableCell>Cluster Match</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Explain</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.recommendations.map((rec, idx) => (
                <React.Fragment key={rec.course_id}>
                  <TableRow hover>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell>
                      <Typography
                        onClick={() => navigate(`/courses/${rec.course_id}`)}
                        sx={{ cursor: 'pointer', color: '#1976d2' }}
                      >
                        {rec.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{(rec.final_score * 100).toFixed(2)}%</TableCell>
                    <TableCell>{rec.avg_score_raw ? `${rec.avg_score_raw.toFixed(1)} (${rec.review_count})` : `- (${rec.review_count})`}</TableCell>
                    <TableCell>{rec.s_role.toFixed(2)}</TableCell>
                    <TableCell>{rec.s_affinity.toFixed(2)}</TableCell>
                    <TableCell>{rec.s_cluster ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{rec.q_smoothed.toFixed(2)}</TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => toggle(rec.course_id)}>
                        <ExpandMoreIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={9} sx={{ p: 0, borderBottom: '1px solid #eee' }}>
                      <Collapse in={openMap[rec.course_id]} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2, backgroundColor: '#fafafa' }}>
                          <Typography variant="subtitle2">Matched Technical Skills</Typography>
                          <Box sx={{ mb: 1 }}>{rec.matched_technical_skills.length ? rec.matched_technical_skills.map(s => (<Typography key={s.skill_id} sx={{ display: 'inline-block', mr: 2 }}>{s.skill_id} ({s.relevance_score})</Typography>)) : <Typography>-</Typography>}</Box>
                          <Typography variant="subtitle2">Missing Technical Skills</Typography>
                          <Box sx={{ mb: 1 }}>{rec.missing_technical_skills.length ? rec.missing_technical_skills.join(', ') : <Typography>-</Typography>}</Box>
                          <Typography variant="subtitle2">Course Clusters</Typography>
                          <Box sx={{ mb: 1 }}>{rec.course_clusters.length ? rec.course_clusters.map(c => (<Typography key={c.id} sx={{ display: 'inline-block', mr: 2 }}>{c.name}</Typography>)) : <Typography>-</Typography>}</Box>
                          <Typography variant="body2">Soft readiness: {(rec.soft_readiness * 100).toFixed(1)}%</Typography>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default MostRecommendedCourses;
