import { render, screen, fireEvent, act } from '@testing-library/react';

import { EmailForm } from '../components/forms/EmailForm';
import { vi, describe, it, expect } from 'vitest';

describe('EmailForm', () => {
  it('should display validation error if required fields are missing', async () => {
    const mockSubmit = vi.fn();
    render(<EmailForm onSubmit={mockSubmit} loading={false} />);

    // Click submit button on empty form
    const btn = screen.getByRole('button', { name: /Classify Suspicious/i });
    
    await act(async () => {
      fireEvent.click(btn);
    });

    // Expect validation error message
    expect(screen.getByText(/Subject line is required/i)).toBeInTheDocument();
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('should submit successfully when all values are populated', async () => {
    const mockSubmit = vi.fn().mockResolvedValue(null);
    render(<EmailForm onSubmit={mockSubmit} loading={false} />);

    // Fill fields
    fireEvent.change(screen.getByPlaceholderText(/support@netflix.com/i), {
      target: { value: 'sender@site.com' },
    });
    fireEvent.change(screen.getByPlaceholderText(/Action Required/i), {
      target: { value: 'Verification' },
    });
    fireEvent.change(screen.getByPlaceholderText(/Paste raw email text/i), {
      target: { value: 'Please log in now.' },
    });

    const btn = screen.getByRole('button', { name: /Classify Suspicious/i });
    
    await act(async () => {
      fireEvent.click(btn);
    });

    expect(screen.queryByText(/required/i)).not.toBeInTheDocument();
    expect(mockSubmit).toHaveBeenCalledWith({
      sender: 'sender@site.com',
      subject: 'Verification',
      body: 'Please log in now.',
    });
  });
});
