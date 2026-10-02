import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { vi, describe, it, expect } from 'vitest';
import { apiClient } from '../services/apiClient';

vi.mock('../services/apiClient', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

const TestConsumer: React.FC = () => {
  const { user, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="user-email">{user ? user.email : 'null'}</span>
      <span data-testid="user-role">{user ? user.role : 'null'}</span>
      <button onClick={() => login('test@user.com', 'password123')} data-testid="login-btn">
        Login
      </button>
      <button onClick={logout} data-testid="logout-btn">
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  it('should authenticate users and extract role claims from JWT token', async () => {
    const header = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
    // Expire is 100 seconds in the future
    const payloadVal = { 
      sub: 'test@user.com', 
      role: 'user', 
      exp: Math.floor((Date.now() + 100000) / 1000) 
    };
    const payload = window.btoa(JSON.stringify(payloadVal));
    const fakeToken = `${header}.${payload}.signature`;

    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        access_token: fakeToken,
        refresh_token: 'fake_refresh',
      },
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    expect(screen.getByTestId('user-email')).toHaveTextContent('null');

    await act(async () => {
      fireEvent.click(screen.getByTestId('login-btn'));
    });

    expect(screen.getByTestId('user-email')).toHaveTextContent('test@user.com');
    expect(screen.getByTestId('user-role')).toHaveTextContent('user');

    // Logout
    fireEvent.click(screen.getByTestId('logout-btn'));
    expect(screen.getByTestId('user-email')).toHaveTextContent('null');
  });
});
