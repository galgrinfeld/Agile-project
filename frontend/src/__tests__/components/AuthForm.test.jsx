/**
 * Tests for AuthForm component
 * Tests login, registration, error handling, and UI states
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AuthForm from '../../components/AuthForm';

// Mock authService
jest.mock('../../services/authService', () => ({
  loginUser: jest.fn(),
  register: jest.fn(),
  useAuth: () => ({
    currentUser: null,
    loading: false,
    login: jest.fn(),
    logout: jest.fn()
  })
}));

import { loginUser, register } from '../../services/authService';

describe('AuthForm', () => {
  const mockOnAuthSuccess = jest.fn();
  const mockOnRegisterSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form by default', () => {
    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test('switches to registration form', () => {
    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    const switchButton = screen.getByText(/sign up|register/i);
    fireEvent.click(switchButton);

    expect(screen.getByText(/register|sign up/i)).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    loginUser.mockResolvedValueOnce('mock_token');

    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login|submit/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledWith('testuser', 'password123');
      expect(mockOnAuthSuccess).toHaveBeenCalled();
    });
  });

  test('handles login error', async () => {
    const errorMessage = 'Invalid credentials';
    loginUser.mockRejectedValueOnce(new Error(errorMessage));

    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login|submit/i });

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/error|invalid|incorrect/i)).toBeInTheDocument();
    });

    expect(mockOnAuthSuccess).not.toHaveBeenCalled();
  });

  test('handles successful registration', async () => {
    const mockUser = { id: 1, name: 'newuser' };
    register.mockResolvedValueOnce(mockUser);

    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    // Switch to registration
    const switchButton = screen.getByText(/sign up|register/i);
    fireEvent.click(switchButton);

    const usernameInput = screen.getByLabelText(/username|name/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /register|sign up|submit/i });

    fireEvent.change(usernameInput, { target: { value: 'newuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(register).toHaveBeenCalled();
      expect(mockOnRegisterSuccess).toHaveBeenCalled();
    });
  });

  test('handles registration error', async () => {
    const error = new Error('User already exists');
    error.detail = 'User with this name already exists';
    register.mockRejectedValueOnce(error);

    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    // Switch to registration
    const switchButton = screen.getByText(/sign up|register/i);
    fireEvent.click(switchButton);

    const usernameInput = screen.getByLabelText(/username|name/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /register|sign up|submit/i });

    fireEvent.change(usernameInput, { target: { value: 'existinguser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/error|already exists/i)).toBeInTheDocument();
    });

    expect(mockOnRegisterSuccess).not.toHaveBeenCalled();
  });

  test('validates required fields', async () => {
    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    const submitButton = screen.getByRole('button', { name: /login|submit/i });
    fireEvent.click(submitButton);

    // Form validation should prevent submission
    await waitFor(() => {
      expect(loginUser).not.toHaveBeenCalled();
    });
  });

  test('shows loading state during submission', async () => {
    let resolveLogin;
    const loginPromise = new Promise((resolve) => {
      resolveLogin = resolve;
    });
    loginUser.mockReturnValueOnce(loginPromise);

    render(
      <AuthForm
        onAuthSuccess={mockOnAuthSuccess}
        onRegisterSuccess={mockOnRegisterSuccess}
      />
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login|submit/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Check for loading state (button disabled or loading text)
    expect(submitButton).toBeDisabled();

    resolveLogin('mock_token');

    await waitFor(() => {
      expect(mockOnAuthSuccess).toHaveBeenCalled();
    });
  });
});

