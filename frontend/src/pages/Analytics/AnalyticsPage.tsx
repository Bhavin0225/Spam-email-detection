import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { BarChart3, Database, RefreshCw } from 'lucide-react';


export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/analytics');
      setData(res.data);
    } catch (e) {
      console.error('Failed to load analytics details', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Analytics</h2>
          <p className="text-xs text-[#94a3b8]">Review spam trend metrics, false-positive distributions, and threat vectors.</p>
        </div>
        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="p-2 rounded-xl bg-[#0d1424] border border-white/10 text-[#94a3b8] hover:text-white transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading || !data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-80 bg-[#0d1424] rounded-xl animate-pulse" />
          <div className="h-80 bg-[#0d1424] rounded-xl animate-pulse" />
        </div>
      ) : (
        <>
          {/* Top Indicators Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="glass-card p-5 rounded-xl space-y-2">
              <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider block">Total Scanned Volume</span>
              <span className="text-2xl font-black text-white">{data.total_scans}</span>
              <p className="text-[10px] text-[#64748b] font-medium">Scans parsed dynamically from live endpoints</p>
            </div>
            <div className="glass-card p-5 rounded-xl space-y-2">
              <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider block">Average Spam Rate</span>
              <span className="text-2xl font-black text-red-400 font-mono">{Math.round(data.spam_rate * 100)}%</span>
              <p className="text-[10px] text-[#64748b] font-medium">Identified threats/phishing indicators ratio</p>
            </div>
            <div className="glass-card p-5 rounded-xl space-y-2">
              <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider block">False Positive Rate</span>
              <span className="text-2xl font-black text-blue-400 font-mono">{Math.round(data.false_positive_rate * 100)}%</span>
              <p className="text-[10px] text-[#64748b] font-medium">Drift rates calculated from correction audits</p>
            </div>
          </div>

          {/* Charts Grids */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Area Chart: Prediction trends over time */}
            <div className="glass-card p-6 rounded-xl space-y-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Database className="w-4 h-4 text-[#00f5a0]" />
                <span>Classification Counts Over Time</span>
              </h3>
              
              <div className="h-72 w-full text-xs">
                {data.predictions_over_time.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-[#64748b] font-semibold">
                    No time series data logged.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.predictions_over_time} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorSpam" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25}/>
                          <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorHam" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                      <XAxis dataKey="date" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '12px', color: '#f3f4f6' }} />
                      <Legend />
                      <Area type="monotone" dataKey="spam" name="Suspicious" stroke="#ef4444" fillOpacity={1} fill="url(#colorSpam)" />
                      <Area type="monotone" dataKey="ham" name="Legitimate" stroke="#10b981" fillOpacity={1} fill="url(#colorHam)" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Bar Chart: Top suspicious domains */}
            <div className="glass-card p-6 rounded-xl space-y-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <BarChart3 className="w-4 h-4 text-red-400" />
                <span>Top Flagged Domains</span>
              </h3>

              <div className="h-72 w-full text-xs">
                {data.top_suspicious_domains.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-[#64748b] font-semibold">
                    No flagged domain analytics logged.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.top_suspicious_domains} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                      <XAxis dataKey="domain" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '12px', color: '#f3f4f6' }} />
                      <Bar dataKey="count" name="Flagged Scans" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
