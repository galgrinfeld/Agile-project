/**
 * Tests for courseService.js
 * Tests course-related API interactions
 */
import {
  getCourse,
  getCourseStats,
  getCourseReviews,
  locateReviewPage
} from '../../services/courseService';

// Mock fetch globally
global.fetch = jest.fn();

describe('courseService', () => {
  const mockToken = 'test_token_123';
  const mockCourseId = 1;

  beforeEach(() => {
    fetch.mockClear();
  });

  describe('getCourse', () => {
    test('getCourse successfully fetches course details', async () => {
      const mockCourse = {
        id: mockCourseId,
        name: 'Introduction to CS',
        description: 'Basic CS concepts',
        prerequisites: [],
        skills: []
      };

      const mockResponse = {
        ok: true,
        json: async () => mockCourse
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await getCourse(mockCourseId, mockToken);

      expect(fetch).toHaveBeenCalledWith(
        `http://localhost:8000/courses/${mockCourseId}`,
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${mockToken}`
          }
        })
      );

      expect(result).toEqual(mockCourse);
    });

    test('getCourse throws error on failed request', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found'
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await expect(getCourse(99999, mockToken)).rejects.toThrow('Failed to fetch course');
    });

    test('getCourse handles network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(getCourse(mockCourseId, mockToken)).rejects.toThrow('Network error');
    });
  });

  describe('getCourseStats', () => {
    test('getCourseStats successfully fetches course statistics', async () => {
      const mockStats = {
        review_count: 10,
        avg_final_score: 8.5,
        avg_industry_relevance: 4.2,
        avg_instructor_quality: 4.0,
        avg_useful_learning: 4.3
      };

      const mockResponse = {
        ok: true,
        json: async () => mockStats
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await getCourseStats(mockCourseId, mockToken);

      expect(fetch).toHaveBeenCalledWith(
        `http://localhost:8000/courses/${mockCourseId}/stats`,
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${mockToken}`
          }
        })
      );

      expect(result).toEqual(mockStats);
    });

    test('getCourseStats throws error on failed request', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found'
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await expect(getCourseStats(99999, mockToken)).rejects.toThrow('Failed to fetch course stats');
    });
  });

  describe('getCourseReviews', () => {
    test('getCourseReviews successfully fetches paginated reviews', async () => {
      const mockReviews = {
        items: [
          { id: 1, student_id: 1, final_score: 9.0 },
          { id: 2, student_id: 2, final_score: 8.5 }
        ],
        page: 1,
        page_size: 10,
        total: 2
      };

      const mockResponse = {
        ok: true,
        json: async () => mockReviews
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await getCourseReviews(mockCourseId, 1, 10, mockToken);

      expect(fetch).toHaveBeenCalledWith(
        `http://localhost:8000/courses/${mockCourseId}/reviews?page=1&page_size=10`,
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${mockToken}`
          }
        })
      );

      expect(result).toEqual(mockReviews);
    });

    test('getCourseReviews uses default pagination values', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({ items: [], page: 1, page_size: 10, total: 0 })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await getCourseReviews(mockCourseId, undefined, undefined, mockToken);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=1&page_size=10'),
        expect.any(Object)
      );
    });

    test('getCourseReviews throws error on failed request', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await expect(getCourseReviews(mockCourseId, 1, 10, mockToken)).rejects.toThrow('Failed to fetch course reviews');
    });
  });

  describe('locateReviewPage', () => {
    test('locateReviewPage returns page number when endpoint exists', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({ page: 3 })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await locateReviewPage(mockCourseId, 123, mockToken);

      expect(result).toEqual({ page: 3 });
    });

    test('locateReviewPage returns null when endpoint not implemented', async () => {
      const mockResponse = {
        ok: false,
        status: 404
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await locateReviewPage(mockCourseId, 123, mockToken);

      expect(result).toBeNull();
    });
  });
});

