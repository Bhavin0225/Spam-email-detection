import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Mail, Lock, Shield } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Please provide email and password.');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080c14] flex items-center justify-center px-4 relative overflow-hidden font-sans">
      {/* Visual background glows */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#00f5a0]/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-[#10b981]/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md space-y-8 relative z-10">
        {/* Brand Header */}
        <div className="flex flex-col items-center justify-center space-y-4 mb-8">
          <div className="text-[#00f5a0] bg-[#0d1424] p-4 rounded-2xl border border-white/10 shadow-[0_0_30px_rgba(0,245,160,0.15)]">
            <Shield className="w-10 h-10 fill-current" />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-bold tracking-tight text-white leading-tight">Spam Detection</h2>
            <p className="text-xs text-[#00f5a0] font-mono tracking-widest uppercase mt-1">SOC Authentication</p>
          </div>
        </div>

        {/* Form Container */}
        <div className="glass-card p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3.5 rounded-xl bg-[#ef4444]/10 border border-[#ef4444]/30 text-xs font-mono font-bold text-[#ef4444] text-center uppercase tracking-wider">
                {error}
              </div>
            )}

            {/* Email input */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-[10px] font-bold text-[#64748b] font-mono uppercase tracking-widest">Operator Email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[#64748b]">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email"
                  type="email"
                  placeholder="operator@soc.local"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  className="w-full bg-[#080c14] border border-white/10 focus:border-[#00f5a0]/50 focus:ring-1 focus:ring-[#00f5a0]/25 rounded-xl pl-11 pr-4 py-3.5 text-sm font-mono text-white placeholder-[#64748b] outline-none transition-all"
                />
              </div>
            </div>

            {/* Password input */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-[10px] font-bold text-[#64748b] font-mono uppercase tracking-widest">Access Code</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[#64748b]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  className="w-full bg-[#080c14] border border-white/10 focus:border-[#00f5a0]/50 focus:ring-1 focus:ring-[#00f5a0]/25 rounded-xl pl-11 pr-4 py-3.5 text-sm font-mono text-white placeholder-[#64748b] outline-none transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 px-4 rounded-xl bg-[#00f5a0] hover:bg-white text-[#080c14] font-bold text-sm tracking-wide emerald-glow transition-all flex items-center justify-center space-x-2 cursor-pointer mt-4"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-[#080c14] border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>Initialize Console Session</span>
              )}
            </button>
          </form>
        </div>

        {/* Footer signup redirect link */}
        <p className="text-center text-xs font-mono text-[#64748b]">
          Unregistered operator?{' '}
          <Link to="/signup" className="text-[#00f5a0] hover:text-white font-bold transition-colors ml-1 border-b border-[#00f5a0]/30 hover:border-white pb-0.5">
            Request Access
          </Link>
        </p>
      </div>
    </div>
  );
};
