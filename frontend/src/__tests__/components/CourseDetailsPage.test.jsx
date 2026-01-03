/**
 * Tests for CourseDetailsPage component
 * Tests course details display, stats, reviews, and API interactions
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CourseDetailsPage from '../../components/CourseDetailsPage';
import * as courseService from '../../services/courseService';

// Mock courseService
jest.mock('../../services/courseService');

// Mock useAuth
jest.mock('../../services/authService', () => ({
  useAuth: () => ({
    currentUser: { id: 1, name: 'testuser' },
    token: 'mock_token',
    loading: false
  })
}));

describe('CourseDetailsPage', () => {
  const mockCourse = {
    id: 1,
    name: 'Introduction to CS',
    description: 'Basic CS concepts',
    workload: 10,
    credits: 3.0,
    status: 'Mandatory',
    prerequisites: [],
    skills: [],
    clusters: []
  };

  const mockStats = {
    review_count: 10,
    avg_final_score: 8.5,
    avg_industry_relevance: 4.2,
    avg_instructor_quality: 4.0,
    avg_useful_learning: 4.3
  };

  const mockReviews = {
    items: [
      {
        id: 1,
        student_id: 1,
        student_name: 'Student 1',
        final_score: 9.0,
        industry_relevance_rating: 5,
        instructor_rating: 4,
        useful_learning_rating: 5
      }
    ],
    page: 1,
    page_size: 10,
    total: 1
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    courseService.getCourse.mockReturnValue(new Promise(() => {})); // Never resolves

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays course details after loading', async () => {
    courseService.getCourse.mockResolvedValueOnce(mockCourse);
    courseService.getCourseStats.mockResolvedValueOnce(mockStats);
    courseService.getCourseReviews.mockResolvedValueOnce(mockReviews);

    // Mock useParams to return courseId
    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ courseId: '1' });

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(mockCourse.name)).toBeInTheDocument();
      expect(screen.getByText(mockCourse.description)).toBeInTheDocument();
    });
  });

  test('displays course statistics', async () => {
    courseService.getCourse.mockResolvedValueOnce(mockCourse);
    courseService.getCourseStats.mockResolvedValueOnce(mockStats);
    courseService.getCourseReviews.mockResolvedValueOnce(mockReviews);

    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ courseId: '1' });

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/review count|reviews/i)).toBeInTheDocument();
      expect(screen.getByText(mockStats.avg_final_score.toString())).toBeInTheDocument();
    });
  });

  test('displays course reviews', async () => {
    courseService.getCourse.mockResolvedValueOnce(mockCourse);
    courseService.getCourseStats.mockResolvedValueOnce(mockStats);
    courseService.getCourseReviews.mockResolvedValueOnce(mockReviews);

    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ courseId: '1' });

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(mockReviews.items[0].student_name)).toBeInTheDocument();
    });
  });

  test('handles error when course not found', async () => {
    courseService.getCourse.mockRejectedValueOnce(new Error('Course not found'));

    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ courseId: '999' });

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/error|not found/i)).toBeInTheDocument();
    });
  });

  test('handles pagination for reviews', async () => {
    courseService.getCourse.mockResolvedValueOnce(mockCourse);
    courseService.getCourseStats.mockResolvedValueOnce(mockStats);
    courseService.getCourseReviews.mockResolvedValueOnce(mockReviews);

    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ courseId: '1' });

    render(
      <BrowserRouter>
        <CourseDetailsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(courseService.getCourseReviews).toHaveBeenCalledWith(1, 1, 10, 'mock_token');
    });
  });
});

