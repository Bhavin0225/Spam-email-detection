import { render, screen } from '@testing-library/react';

import { PredictionCard } from '../components/cards/PredictionCard';
import { describe, it, expect } from 'vitest';

describe('PredictionCard', () => {
  it('should render predictions verdict, confidence and risk level badges correctly', () => {
    const mockPrediction = {
      prediction_id: 'pred-123',
      prediction_label: 'suspicious',
      confidence: 0.87,
      risk_level: 'high',
      model_version: 'v1.0.0',
    };

    render(<PredictionCard prediction={mockPrediction} />);

    // Check classification text
    expect(screen.getByText(/Suspicious Phishing E-Mail/i)).toBeInTheDocument();
    
    // Check confidence percentage
    expect(screen.getByText(/87%/i)).toBeInTheDocument();

    // Check risk level badge
    expect(screen.getByText(/high Risk/i)).toBeInTheDocument();

    // Check model version
    expect(screen.getByText(/v1.0.0/i)).toBeInTheDocument();
  });
});
