import { render, screen } from '@testing-library/react';

import { Sidebar } from '../components/layout/Sidebar';
import { vi, describe, it, expect } from 'vitest';
import { useAuth } from '../contexts/AuthContext';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

describe('Sidebar Navigation', () => {
  it('should hide admin and analyst links when user role is regular user', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { email: 'user@test.com', role: 'user' },
      loading: false,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analyze Email')).toBeInTheDocument();
    expect(screen.queryByText('Analytics Dashboard')).not.toBeInTheDocument();
    expect(screen.queryByText('Admin Panel')).not.toBeInTheDocument();
  });

  it('should show all links when user role is admin', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { email: 'admin@test.com', role: 'admin' },
      loading: false,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analyze Email')).toBeInTheDocument();
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Admin Panel')).toBeInTheDocument();
  });
});
