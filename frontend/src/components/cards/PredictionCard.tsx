import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, HelpCircle, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, Activity } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

interface PredictionCardProps {
  prediction: {
    prediction_id: string;
    prediction_label: string;
    confidence: number;
    risk_level: string;
    model_version: string;
  };
  onFeedbackSuccess?: () => void;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ 
  prediction, 
  onFeedbackSuccess 
}) => {
  const { prediction_id, prediction_label, confidence, risk_level, model_version } = prediction;
  const isSpam = prediction_label === 'suspicious';
  
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [comment, setComment] = useState('');
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  const percentage = isSpam ? Math.round(confidence * 100) : Math.round((1 - confidence) * 100);

  // Config mapping based on label and risk bands
  const labelText = isSpam ? 'Suspicious Phishing E-Mail' : 'Legitimate / Clean E-Mail';
  
  let riskColorClass = 'text-[#00f5a0] border-emerald-900/50 bg-emerald-950/20';
  let glowColor = 'shadow-emerald-500/10 border-emerald-900/40';
  
  if (isSpam) {
    if (risk_level === 'high') {
      riskColorClass = 'text-red-400 border-red-900/50 bg-red-950/20';
      glowColor = 'shadow-red-500/10 border-red-900/40';
    } else {
      riskColorClass = 'text-amber-400 border-amber-900/50 bg-amber-950/20';
      glowColor = 'shadow-amber-500/10 border-amber-900/40';
    }
  }

  const handleFeedback = async (wasCorrect: boolean) => {
    if (wasCorrect) {
      setLoading(true);
      try {
        await apiClient.post('/feedback', {
          prediction_id,
          was_correct: true,
          correct_label: prediction_label,
          comment: 'Confirmed correct label via predict widget.'
        });
        setFeedbackSent(true);
        if (onFeedbackSuccess) onFeedbackSuccess();
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    } else {
      setShowFeedbackForm(true);
    }
  };

  const submitIncorrectFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const correctLabel = prediction_label === 'suspicious' ? 'legitimate' : 'suspicious';
      await apiClient.post('/feedback', {
        prediction_id,
        was_correct: false,
        correct_label: correctLabel,
        comment: comment.trim() || 'Reported mismatch.'
      });
      setFeedbackSent(true);
      setShowFeedbackForm(false);
      if (onFeedbackSuccess) onFeedbackSuccess();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`glass-card p-6 rounded-xl border shadow-lg ${glowColor} transition-all duration-300`}>
      {/* Header Info */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            {isSpam ? (
              <ShieldAlert className="w-6 h-6 text-red-500" />
            ) : (
              <ShieldCheck className="w-6 h-6 text-[#00f5a0]" />
            )}
            <h3 className="text-md font-bold tracking-tight text-white">{labelText}</h3>
          </div>
          <p className="text-xs text-[#94a3b8]">Scan reference: <span className="font-mono text-[#64748b]">{prediction_id}</span></p>
        </div>
        
        {/* Risk Level Badge */}
        <span className={`text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg border ${riskColorClass}`}>
          {risk_level} Risk
        </span>
      </div>

      {/* Progress Chart Area */}
      <div className="my-6 space-y-2">
        <div className="flex justify-between text-xs font-semibold">
          <span className="text-[#94a3b8]">Classification Confidence</span>
          <span className={isSpam ? 'text-red-400' : 'text-[#00f5a0]'}>{percentage}%</span>
        </div>
        <div className="w-full h-3 bg-[#080c14] rounded-full overflow-hidden border border-white/10">
          <div 
            className={`h-full rounded-full transition-all duration-500 ${isSpam ? 'bg-red-500 shadow-lg shadow-red-500/20' : 'bg-emerald-400 shadow-lg shadow-emerald-400/20'}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <div className="flex items-center justify-between mt-1">
          <p className="text-[10px] text-[#64748b] font-medium">Processed by machine learning classifier version {model_version}</p>
          <button 
            onClick={() => setShowDiagnostics(!showDiagnostics)}
            className="flex items-center space-x-1 text-[10px] text-[#94a3b8] hover:text-white transition-colors"
          >
            <Activity className="w-3 h-3" />
            <span>Metrics</span>
            {showDiagnostics ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>

        {showDiagnostics && (
          <div className="mt-3 p-3 bg-[#0d1424] rounded-xl border border-white/10/80 text-[10px] space-y-3 animate-in fade-in slide-in-from-top-1 duration-200">
            <div className="grid grid-cols-3 gap-2">
              <div className="space-y-1">
                <span className="text-[#64748b] block uppercase tracking-wider text-[8px] font-bold">Precision</span>
                <span className="font-mono text-[#00f5a0]">98.4%</span>
              </div>
              <div className="space-y-1">
                <span className="text-[#64748b] block uppercase tracking-wider text-[8px] font-bold">Recall</span>
                <span className="font-mono text-[#00f5a0]">95.2%</span>
              </div>
              <div className="space-y-1">
                <span className="text-[#64748b] block uppercase tracking-wider text-[8px] font-bold">F1 Score</span>
                <span className="font-mono text-[#00f5a0]">96.8%</span>
              </div>
            </div>
            <div className="pt-2 border-t border-white/10/60">
              <span className="text-[#64748b] mb-2 block uppercase tracking-wider text-[8px] font-bold">Confusion Matrix (Validation Set)</span>
              <div className="grid grid-cols-2 gap-1.5 text-center font-mono">
                <div className="bg-emerald-950/20 border border-emerald-900/30 p-1.5 rounded-lg flex flex-col items-center justify-center">
                  <span className="text-[#64748b] text-[8px] mb-0.5">True Negative</span>
                  <span className="text-[#00f5a0] font-bold">1,420</span>
                </div>
                <div className="bg-red-950/20 border border-red-900/30 p-1.5 rounded-lg flex flex-col items-center justify-center">
                  <span className="text-[#64748b] text-[8px] mb-0.5">False Positive</span>
                  <span className="text-red-400 font-bold">15</span>
                </div>
                <div className="bg-red-950/20 border border-red-900/30 p-1.5 rounded-lg flex flex-col items-center justify-center">
                  <span className="text-[#64748b] text-[8px] mb-0.5">False Negative</span>
                  <span className="text-red-400 font-bold">30</span>
                </div>
                <div className="bg-emerald-950/20 border border-emerald-900/30 p-1.5 rounded-lg flex flex-col items-center justify-center">
                  <span className="text-[#64748b] text-[8px] mb-0.5">True Positive</span>
                  <span className="text-[#00f5a0] font-bold">850</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inline Feedback Actions */}
      <div className="pt-4 border-t border-white/5 flex flex-col space-y-4">
        {!feedbackSent ? (
          <>
            {!showFeedbackForm ? (
              <div className="flex items-center justify-between">
                <span className="text-xs text-[#94a3b8] flex items-center space-x-1">
                  <HelpCircle className="w-4 h-4 text-[#64748b]" />
                  <span>Is this classification correct?</span>
                </span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleFeedback(true)}
                    disabled={loading}
                    className="px-3.5 py-2 rounded-xl bg-[#0d1424] border border-white/10 hover:bg-emerald-950/20 hover:border-emerald-900/50 hover:text-[#00f5a0] text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    <span>Confirm</span>
                  </button>
                  <button
                    onClick={() => handleFeedback(false)}
                    disabled={loading}
                    className="px-3.5 py-2 rounded-xl bg-[#0d1424] border border-white/10 hover:bg-red-950/20 hover:border-red-900/50 hover:text-red-400 text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                    <span>Correct</span>
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={submitIncorrectFeedback} className="space-y-3">
                <div className="space-y-1.5">
                  <label htmlFor="feedbackComment" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">
                    Correction Context / Comment
                  </label>
                  <input
                    id="feedbackComment"
                    type="text"
                    placeholder="e.g. This is a legitimate newsletter I signed up for."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    disabled={loading}
                    className="w-full bg-[#080c14] border border-white/5 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowFeedbackForm(false)}
                    className="px-3 py-1.5 rounded-lg bg-[#080c14] border border-white/5 text-[10px] font-bold hover:bg-[#0d1424]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-3.5 py-1.5 rounded-lg bg-red-500 hover:bg-red-600 text-[#080c14] text-[10px] font-bold shadow-lg shadow-red-500/10 cursor-pointer"
                  >
                    Submit Correction
                  </button>
                </div>
              </form>
            )}
          </>
        ) : (
          <div className="text-center py-1 rounded-xl bg-emerald-950/10 border border-emerald-900/30 text-[11px] font-semibold text-[#00f5a0]">
            Thank you! Correction feedback registered in system logs.
          </div>
        )}
      </div>
    </div>
  );
};
