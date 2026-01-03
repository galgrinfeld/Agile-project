/**
 * Tests for authService.js
 * Tests authentication logic, token management, and API interactions
 */
import { 
  loginUser, 
  register, 
  setToken, 
  getToken, 
  removeToken 
} from '../../services/authService';

// Mock fetch globally
global.fetch = jest.fn();

describe('authService', () => {
  beforeEach(() => {
    // Clear localStorage and fetch mocks before each test
    localStorage.clear();
    fetch.mockClear();
  });

  describe('Token Management', () => {
    test('setToken stores token in localStorage', () => {
      const token = 'test_token_123';
      setToken(token);
      expect(localStorage.getItem('userToken')).toBe(token);
    });

    test('getToken retrieves token from localStorage', () => {
      const token = 'test_token_123';
      localStorage.setItem('userToken', token);
      expect(getToken()).toBe(token);
    });

    test('getToken returns null when no token exists', () => {
      expect(getToken()).toBeNull();
    });

    test('removeToken removes token from localStorage', () => {
      localStorage.setItem('userToken', 'test_token');
      removeToken();
      expect(localStorage.getItem('userToken')).toBeNull();
    });
  });

  describe('loginUser', () => {
    test('loginUser successfully logs in and stores token', async () => {
      const mockToken = 'mock_access_token';
      const mockResponse = {
        ok: true,
        json: async () => ({ access_token: mockToken, token_type: 'bearer' })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const token = await loginUser('testuser', 'password123');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })
      );

      expect(token).toBe(mockToken);
      expect(localStorage.getItem('userToken')).toBe(mockToken);
    });

    test('loginUser throws error on failed login', async () => {
      const mockResponse = {
        ok: false,
        json: async () => ({ detail: 'Incorrect username or password' })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await expect(loginUser('wronguser', 'wrongpass')).rejects.toThrow();
      expect(localStorage.getItem('userToken')).toBeNull();
    });

    test('loginUser handles network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(loginUser('testuser', 'password123')).rejects.toThrow('Network error');
    });
  });

  describe('register', () => {
    test('register successfully creates new user', async () => {
      const mockUser = {
        id: 1,
        name: 'newuser',
        faculty: 'Engineering',
        year: 1
      };

      const mockResponse = {
        ok: true,
        json: async () => mockUser
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const result = await register({
        name: 'newuser',
        password: 'password123',
        faculty: 'Engineering',
        year: 1
      });

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/auth/register',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: 'newuser',
            password: 'password123',
            faculty: 'Engineering',
            year: 1,
            courses_taken: []
          })
        })
      );

      expect(result).toEqual(mockUser);
    });

    test('register throws error on duplicate user', async () => {
      const mockResponse = {
        ok: false,
        json: async () => ({ detail: 'User with this name already exists' })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      const error = await register({
        name: 'existinguser',
        password: 'password123'
      }).catch(e => e);

      expect(error.detail).toContain('already exists');
    });

    test('register handles network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(register({
        name: 'newuser',
        password: 'password123'
      })).rejects.toThrow();
    });

    test('register uses default values for optional fields', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({ id: 1, name: 'newuser' })
      };

      fetch.mockResolvedValueOnce(mockResponse);

      await register({
        name: 'newuser',
        password: 'password123'
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({
            name: 'newuser',
            password: 'password123',
            faculty: 'Undeclared',
            year: 1,
            courses_taken: []
          })
        })
      );
    });
  });
});

