/**
 * Integration tests for authService
 * Tests the AuthProvider context and hooks
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../services/authService';

// Mock fetch
global.fetch = jest.fn();

// Test component that uses auth context
const TestComponent = () => {
  const { currentUser, token, loading, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading...' : 'Loaded'}</div>
      <div data-testid="user">{currentUser ? currentUser.name : 'No user'}</div>
      <div data-testid="token">{token || 'No token'}</div>
      <button onClick={() => login('testuser', 'password123')}>Login</button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  );
};

describe('AuthProvider Integration', () => {
  beforeEach(() => {
    localStorage.clear();
    fetch.mockClear();
  });

  test('AuthProvider initializes with no user when no token exists', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
    expect(screen.getByTestId('token')).toHaveTextContent('No token');
  });

  test('AuthProvider loads user from existing token', async () => {
    // Mock a valid JWT token (simplified)
    const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsInN0dWRlbnRfaWQiOjEsImV4cCI6OTk5OTk5OTk5OX0.test';
    localStorage.setItem('userToken', mockToken);

    // Mock parseJwt to return decoded token
    const originalParseJwt = require('../../services/authService').parseJwt;
    jest.spyOn(require('../../services/authService'), 'parseJwt').mockReturnValue({
      sub: 'testuser',
      student_id: 1,
      exp: 9999999999
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser');
    });
  });

  test('login updates user state', async () => {
    const mockToken = 'mock_access_token';
    const mockResponse = {
      ok: true,
      json: async () => ({ access_token: mockToken, token_type: 'bearer' })
    };

    fetch.mockResolvedValueOnce(mockResponse);

    // Mock parseJwt
    jest.spyOn(require('../../services/authService'), 'parseJwt').mockReturnValue({
      sub: 'testuser',
      student_id: 1,
      exp: 9999999999
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    loginButton.click();

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser');
      expect(screen.getByTestId('token')).toHaveTextContent(mockToken);
    });
  });

  test('logout clears user state', async () => {
    const mockToken = 'mock_token';
    localStorage.setItem('userToken', mockToken);

    jest.spyOn(require('../../services/authService'), 'parseJwt').mockReturnValue({
      sub: 'testuser',
      student_id: 1,
      exp: 9999999999
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser');
    });

    const logoutButton = screen.getByText('Logout');
    logoutButton.click();

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('token')).toHaveTextContent('No token');
      expect(localStorage.getItem('userToken')).toBeNull();
    });
  });

  test('useAuth returns default context when used outside provider', () => {
    // Suppress console.warn for this test
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

    const TestOutsideProvider = () => {
      const auth = useAuth();
      return <div data-testid="auth">{auth.currentUser ? 'Has user' : 'No user'}</div>;
    };

    render(<TestOutsideProvider />);

    expect(screen.getByTestId('auth')).toHaveTextContent('No user');
    expect(consoleSpy).toHaveBeenCalled();

    consoleSpy.mockRestore();
  });
});

