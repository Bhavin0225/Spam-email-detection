import React, { useState } from 'react';
import { Mail, ChevronDown, ChevronUp, Play } from 'lucide-react';

interface EmailFormProps {
  onSubmit: (data: {
    subject: string;
    body: string;
    sender: string;
    headers?: Record<string, any>;
  }) => Promise<void>;
  loading: boolean;
}

export const EmailForm: React.FC<EmailFormProps> = ({ onSubmit, loading }) => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [sender, setSender] = useState('');
  const [showHeaders, setShowHeaders] = useState(false);
  
  // Advanced security headers state
  const [spf, setSpf] = useState('');
  const [dkim, setDkim] = useState('');
  const [dmarc, setDmarc] = useState('');
  const [replyTo, setReplyTo] = useState('');
  const [hopCount, setHopCount] = useState(0);

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!subject.trim()) {
      setError('Subject line is required.');
      return;
    }
    if (!body.trim()) {
      setError('Email body content is required.');
      return;
    }
    if (!sender.trim()) {
      setError('Sender address is required.');
      return;
    }

    const payload: any = {
      subject: subject.trim(),
      body: body.trim(),
      sender: sender.trim(),
    };

    if (showHeaders) {
      payload.headers = {
        spf: spf.trim(),
        dkim: dkim.trim(),
        dmarc: dmarc.trim(),
        'reply-to': replyTo.trim(),
        hop_count: Number(hopCount),
      };
    }

    try {
      await onSubmit(payload);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze email. Please verify connections.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-card p-6 rounded-xl space-y-6">
      <div className="flex items-center space-x-3 pb-2 border-b border-white/5">
        <Mail className="w-5 h-5 text-[#00f5a0]" />
        <h3 className="text-sm font-semibold text-white">Email Classification Scanner</h3>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-900/50 text-xs font-semibold text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Sender field */}
        <div className="space-y-1.5">
          <label htmlFor="sender" className="text-[10px] font-bold text-[#64748b] uppercase font-mono tracking-wider">Sender</label>
          <input
            id="sender"
            type="text"
            placeholder="e.g. support@netflix.com"
            value={sender}
            onChange={(e) => setSender(e.target.value)}
            disabled={loading}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600 outline-none transition-all"
          />
        </div>

        {/* Subject field */}
        <div className="space-y-1.5">
          <label htmlFor="subject" className="text-[10px] font-bold text-[#64748b] uppercase font-mono tracking-wider">Subject</label>
          <input
            id="subject"
            type="text"
            placeholder="e.g. Action Required: Verify your credentials"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            disabled={loading}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600 outline-none transition-all"
          />
        </div>
      </div>

      {/* Body field */}
      <div className="space-y-1.5">
        <label htmlFor="body" className="text-[10px] font-bold text-[#64748b] uppercase font-mono tracking-wider">Email Content / Body</label>
        <textarea
          id="body"
          placeholder="Paste raw email text content or HTML content here..."
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={loading}
          rows={6}
          className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600 outline-none transition-all resize-none"
        />
      </div>

      {/* Advanced toggle */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => setShowHeaders(!showHeaders)}
          className="text-xs font-bold text-[#94a3b8] hover:text-white uppercase tracking-wider flex items-center space-x-1 transition-colors outline-none cursor-pointer"
        >
          <span>Advanced Security Headers</span>
          {showHeaders ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showHeaders && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 mt-2 border-t border-white/5">
            <div className="space-y-1.5">
              <label htmlFor="spf" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">SPF Status</label>
              <input
                id="spf"
                type="text"
                placeholder="e.g. pass, fail"
                value={spf}
                onChange={(e) => setSpf(e.target.value)}
                disabled={loading}
                className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="dkim" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">DKIM Status</label>
              <input
                id="dkim"
                type="text"
                placeholder="e.g. pass, signature"
                value={dkim}
                onChange={(e) => setDkim(e.target.value)}
                disabled={loading}
                className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="dmarc" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">DMARC Status</label>
              <input
                id="dmarc"
                type="text"
                placeholder="e.g. pass, fail"
                value={dmarc}
                onChange={(e) => setDmarc(e.target.value)}
                disabled={loading}
                className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="replyTo" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Reply-To Address</label>
              <input
                id="replyTo"
                type="text"
                placeholder="e.g. badguy@hacker.com"
                value={replyTo}
                onChange={(e) => setReplyTo(e.target.value)}
                disabled={loading}
                className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="hopCount" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Hop Count (Received Headers)</label>
              <input
                id="hopCount"
                type="number"
                value={hopCount}
                onChange={(e) => setHopCount(Number(e.target.value))}
                disabled={loading}
                className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/25 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none transition-all"
              />
            </div>
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-4 rounded-xl bg-[#00f5a0] hover:bg-[#00f5a0]/80 text-[#080c14] font-bold text-sm tracking-wide shadow-lg emerald-glow disabled:opacity-50 hover:shadow-emerald-500/25 flex items-center justify-center space-x-2 transition-all cursor-pointer"
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
        ) : (
          <>
            <Play className="w-4 h-4 text-[#080c14] fill-current" />
            <span>Classify Suspicious Elements</span>
          </>
        )}
      </button>
    </form>
  );
};
