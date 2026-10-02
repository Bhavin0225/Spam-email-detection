import React, { useState } from 'react';
import { EmailForm } from '../../components/forms/EmailForm';
import { PredictionCard } from '../../components/cards/PredictionCard';
import { apiClient } from '../../services/apiClient';

export const AnalyzeEmailPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<any | null>(null);

  const handleAnalyze = async (data: {
    subject: string;
    body: string;
    sender: string;
    headers?: Record<string, any>;
  }) => {
    setLoading(true);
    setPrediction(null);
    try {
      const res = await apiClient.post('/predict', data);
      setPrediction(res.data);
    } catch (e) {
      console.error(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Threat Analysis Engine</h2>
        <p className="text-sm text-[#94a3b8] mt-1">Scan incoming subjects, bodies, and headers to predict classification flags.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Input Form Column (spanning 2 cols on lg screens) */}
        <div className="lg:col-span-2">
          <EmailForm onSubmit={handleAnalyze} loading={loading} />
        </div>

        {/* Prediction Results Card */}
        <div className="lg:col-span-1">
          {prediction ? (
            <PredictionCard prediction={prediction} />
          ) : (
            <div className="glass-card p-8 border border-white/5 flex flex-col items-center justify-center text-center h-64 text-[#94a3b8] font-semibold space-y-3">
              <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center bg-[#0d1424] text-[#64748b]">
                ?
              </div>
              <p className="text-sm text-[#64748b] font-mono">Waiting for classification...</p>
              <p className="text-xs text-[#64748b] max-w-[180px]">Submit an email text on the left to review prediction reports here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
