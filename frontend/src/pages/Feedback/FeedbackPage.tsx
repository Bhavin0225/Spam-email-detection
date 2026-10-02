import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';
import { 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle,
  HelpCircle
} from 'lucide-react';



export const FeedbackPage: React.FC = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Feedback action states
  const [activeFeedbackScan, setActiveFeedbackScan] = useState<any | null>(null);
  const [comment, setComment] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);

  const fetchScans = async () => {
    setLoading(true);
    try {
      // Fetch user's recent scans
      const res = await apiClient.get('/history?limit=20');
      setScans(res.data);
    } catch (e) {
      console.error('Failed to load history for feedback', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  const handleConfirmCorrect = async (scan: any) => {
    try {
      await apiClient.post('/feedback', {
        prediction_id: scan.prediction_id,
        was_correct: true,
        correct_label: scan.prediction_label,
        comment: 'Verified correct classification.'
      });
      // Refresh list to show updated status
      fetchScans();
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenCorrection = (scan: any) => {
    setActiveFeedbackScan(scan);
    setComment('');
  };

  const handleSubmitCorrection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFeedbackScan) return;

    setSubmitLoading(true);
    try {
      const correctLabel = activeFeedbackScan.prediction_label === 'suspicious' ? 'legitimate' : 'suspicious';
      await apiClient.post('/feedback', {
        prediction_id: activeFeedbackScan.prediction_id,
        was_correct: false,
        correct_label: correctLabel,
        comment: comment.trim() || 'Reported classification mismatch.'
      });
      setActiveFeedbackScan(null);
      fetchScans();
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Classification Feedback</h2>
        <p className="text-xs text-[#94a3b8]">Review predictions and log corrections. Feedback is utilized in retraining pipelines to reduce false positives.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left list column */}
        <div className="lg:col-span-2 glass-card rounded-xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-white">Recent Scans Needing Verification</h3>
          
          {loading ? (
            <div className="space-y-3">
              <div className="h-16 bg-[#0d1424] rounded-xl animate-pulse" />
              <div className="h-16 bg-[#0d1424] rounded-xl animate-pulse" />
            </div>
          ) : scans.length === 0 ? (
            <div className="text-center py-12 text-[#64748b] font-semibold text-xs">
              No scans found to submit feedback for.
            </div>
          ) : (
            <div className="space-y-3">
              {scans.map((scan) => {
                const isSpam = scan.prediction_label === 'suspicious';
                return (
                  <div key={scan.prediction_id} className="p-4 bg-[#080c14] border border-white/5/50 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="min-w-0 flex-1 space-y-1">
                      <span className="font-semibold block text-xs text-white truncate">{scan.email?.subject || 'No Subject'}</span>
                      <div className="flex items-center space-x-2 text-[10px] text-[#64748b] font-semibold uppercase tracking-wider">
                        <span className={isSpam ? 'text-red-400' : 'text-[#00f5a0]'}>{scan.prediction_label}</span>
                        <span>•</span>
                        <span className="font-mono">{Math.round(scan.confidence * 100)}% confidence</span>
                      </div>
                    </div>

                    <div className="flex space-x-2 flex-shrink-0">
                      <button
                        onClick={() => handleConfirmCorrect(scan)}
                        className="p-2 rounded-lg bg-[#0d1424] border border-white/10 hover:bg-emerald-950/20 hover:border-emerald-900/50 hover:text-[#00f5a0] text-[10px] font-bold tracking-wide transition-colors cursor-pointer flex items-center space-x-1"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Confirm</span>
                      </button>
                      <button
                        onClick={() => handleOpenCorrection(scan)}
                        className="p-2 rounded-lg bg-[#0d1424] border border-white/10 hover:bg-red-950/20 hover:border-red-900/50 hover:text-red-400 text-[10px] font-bold tracking-wide transition-colors cursor-pointer flex items-center space-x-1"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Correction</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Correction Feedback Submission Form */}
        <div className="lg:col-span-1">
          {activeFeedbackScan ? (
            <form onSubmit={handleSubmitCorrection} className="glass-card p-6 rounded-xl border border-red-900/40 shadow-lg shadow-red-500/5 space-y-4">
              <div className="flex items-center space-x-2 pb-2 border-b border-white/5/40">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <h3 className="text-sm font-bold text-white">Submit Classification Correction</h3>
              </div>

              <div className="space-y-1 bg-[#080c14]/60 p-3 rounded-lg border border-white/5 text-xs">
                <span className="text-[9px] font-bold text-[#64748b] uppercase tracking-wider block">Target Scan Subject</span>
                <span className="font-semibold text-white block truncate">{activeFeedbackScan.email?.subject}</span>
                <span className="text-[10px] text-[#94a3b8] block mt-1">
                  Expected output correction: <span className="font-bold text-[#00f5a0]">
                    {activeFeedbackScan.prediction_label === 'suspicious' ? 'legitimate' : 'suspicious'}
                  </span>
                </span>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="correctionComment" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Comment / Mismatch Context</label>
                <textarea
                  id="correctionComment"
                  placeholder="Explain why the classifier made a mistake (e.g. newsletter, system alert mail, false positive)..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  disabled={submitLoading}
                  rows={4}
                  className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all resize-none"
                />
              </div>

              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setActiveFeedbackScan(null)}
                  disabled={submitLoading}
                  className="flex-1 py-2 rounded-xl bg-[#0d1424] border border-white/10 hover:bg-slate-800 text-[#94a3b8] font-bold text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitLoading}
                  className="flex-1 py-2 rounded-xl bg-red-500 hover:bg-red-600 text-[#080c14] font-bold text-xs shadow-lg shadow-red-500/10 transition-colors cursor-pointer"
                >
                  {submitLoading ? 'Submitting...' : 'Register Correction'}
                </button>
              </div>
            </form>
          ) : (
            <div className="glass-card p-8 rounded-xl border border-white/5 flex flex-col items-center justify-center text-center h-64 text-[#64748b] font-semibold space-y-2">
              <HelpCircle className="w-10 h-10 text-[#64748b]" />
              <p className="text-xs text-[#94a3b8]">Report mismatch details</p>
              <p className="text-[10px] text-[#64748b] max-w-[180px]">Select any scan element on the left to register a classification correction.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
