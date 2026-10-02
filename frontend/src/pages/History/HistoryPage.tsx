import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';
import { 
  ShieldCheck, 
  ShieldAlert, 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  X,
  FileText,
  Calendar,
  AlertCircle
} from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filtering states
  const [label, setLabel] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const limit = 10;
  
  // Selected detail overlay
  const [selectedScan, setSelectedScan] = useState<any | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      let url = `/history?limit=${limit}&skip=${skip}`;
      
      if (label) url += `&label=${label}`;
      if (riskLevel) url += `&risk_level=${riskLevel}`;
      
      if (startDate) {
        const startISO = new Date(startDate).toISOString();
        url += `&start_date=${startISO}`;
      }
      if (endDate) {
        const endISO = new Date(endDate).toISOString();
        url += `&end_date=${endISO}`;
      }
      
      const res = await apiClient.get(url);
      setScans(res.data);
    } catch (e) {
      console.error('Failed to load history logs', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, label, riskLevel, startDate, endDate]);

  const handleClearFilters = () => {
    setLabel('');
    setRiskLevel('');
    setStartDate('');
    setEndDate('');
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Audit Logs & History</h2>
          <p className="text-xs text-[#94a3b8]">Search and audit prediction verdicts across past operations.</p>
        </div>
      </div>

      {/* Filters Panel */}
      <div className="glass-card p-5 rounded-xl grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
        {/* Label */}
        <div className="space-y-1.5">
          <label htmlFor="filterLabel" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Classification</label>
          <select
            id="filterLabel"
            value={label}
            onChange={(e) => { setLabel(e.target.value); setPage(1); }}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none cursor-pointer"
          >
            <option value="">All Classifications</option>
            <option value="suspicious">Suspicious</option>
            <option value="legitimate">Legitimate</option>
          </select>
        </div>

        {/* Risk Level */}
        <div className="space-y-1.5">
          <label htmlFor="filterRisk" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Risk Band</label>
          <select
            id="filterRisk"
            value={riskLevel}
            onChange={(e) => { setRiskLevel(e.target.value); setPage(1); }}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none cursor-pointer"
          >
            <option value="">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>

        {/* Start Date */}
        <div className="space-y-1.5">
          <label htmlFor="filterStart" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Start Date</label>
          <input
            id="filterStart"
            type="date"
            value={startDate}
            onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 rounded-xl px-3.5 py-2 text-xs text-white outline-none cursor-pointer"
          />
        </div>

        {/* End Date */}
        <div className="space-y-1.5">
          <label htmlFor="filterEnd" className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">End Date</label>
          <input
            id="filterEnd"
            type="date"
            value={endDate}
            onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
            className="w-full bg-[#0d1424] border border-white/10 focus:border-emerald-500/50 rounded-xl px-3.5 py-2 text-xs text-white outline-none cursor-pointer"
          />
        </div>

        {/* Clear filters button */}
        <button
          onClick={handleClearFilters}
          className="w-full py-2.5 rounded-xl bg-[#0d1424] border border-white/10 hover:bg-slate-800 text-[#94a3b8] font-bold text-xs flex items-center justify-center space-x-1 transition-all cursor-pointer h-[38px]"
        >
          <X className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>

      {/* Scans list */}
      <div className="glass-card rounded-xl p-6 space-y-4">
        {loading ? (
          <div className="space-y-3 py-6">
            <div className="h-10 bg-[#0d1424] rounded-xl animate-pulse" />
            <div className="h-10 bg-[#0d1424] rounded-xl animate-pulse" />
            <div className="h-10 bg-[#0d1424] rounded-xl animate-pulse" />
          </div>
        ) : scans.length === 0 ? (
          <div className="py-12 text-center text-[#64748b] font-semibold flex flex-col items-center space-y-2">
            <Search className="w-8 h-8 text-[#64748b]" />
            <p className="text-xs text-[#94a3b8]">No scans matched your query.</p>
            <p className="text-[10px] text-[#64748b]">Try modifying your filters or clear them above.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/5 text-[#94a3b8] font-bold uppercase tracking-wider">
                  <th className="pb-3 pl-2">Subject / Sender</th>
                  <th className="pb-3">Verdict</th>
                  <th className="pb-3">Confidence</th>
                  <th className="pb-3">Risk Level</th>
                  <th className="pb-3">Date</th>
                  <th className="pb-3 pr-2 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/30 text-[#94a3b8]">
                {scans.map((scan) => {
                  const isSpam = scan.prediction_label === 'suspicious';
                  return (
                    <tr key={scan.prediction_id} className="hover:bg-[#0d1424]/15 transition-colors">
                      <td className="py-3.5 pl-2 max-w-xs truncate">
                        <span className="font-semibold block text-white truncate">{scan.email?.subject || 'No Subject'}</span>
                        <span className="text-[10px] text-[#64748b] block truncate mt-0.5">{scan.email?.sender}</span>
                      </td>
                      <td className="py-3.5 font-bold">
                        <span className={`inline-flex items-center space-x-1 ${isSpam ? 'text-red-400' : 'text-[#00f5a0]'}`}>
                          {isSpam ? <ShieldAlert className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                          <span>{scan.prediction_label}</span>
                        </span>
                      </td>
                      <td className="py-3.5 font-semibold font-mono">
                        {Math.round(scan.confidence * 100)}%
                      </td>
                      <td className="py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          scan.risk_level === 'high' 
                            ? 'bg-red-950/20 border-red-900/40 text-red-400'
                            : scan.risk_level === 'medium'
                              ? 'bg-amber-950/20 border-amber-900/40 text-amber-400'
                              : 'bg-emerald-950/20 border-emerald-900/40 text-[#00f5a0]'
                        }`}>
                          {scan.risk_level}
                        </span>
                      </td>
                      <td className="py-3.5 text-[#64748b] font-medium">
                        {new Date(scan.created_at).toLocaleDateString()} {new Date(scan.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="py-3.5 pr-2 text-right">
                        <button
                          onClick={() => setSelectedScan(scan)}
                          className="px-2.5 py-1 rounded-lg bg-[#0d1424] border border-white/10 hover:bg-slate-800 text-[10px] font-bold tracking-wide transition-colors cursor-pointer"
                        >
                          Review EML
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination controls */}
        <div className="flex items-center justify-between pt-4 border-t border-white/5/40">
          <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider">Page {page}</span>
          <div className="flex space-x-1">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg bg-[#0d1424] border border-white/10 text-[#94a3b8] hover:text-white disabled:opacity-30 transition-opacity cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={scans.length < limit}
              className="p-1.5 rounded-lg bg-[#0d1424] border border-white/10 text-[#94a3b8] hover:text-white disabled:opacity-30 transition-opacity cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Expandable detail overlay modal */}
      {selectedScan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setSelectedScan(null)} />
          
          <div className="relative glass-card w-full max-w-2xl rounded-xl overflow-hidden shadow-2xl z-10 flex flex-col max-h-[85vh]">
            {/* Header */}
            <div className="p-6 border-b border-white/5 flex items-center justify-between bg-[#080c14]">
              <div className="flex items-center space-x-2.5">
                <FileText className="w-5 h-5 text-[#00f5a0]" />
                <h3 className="text-sm font-bold text-white">Parsed E-Mail Details & Auditing</h3>
              </div>
              <button 
                onClick={() => setSelectedScan(null)}
                className="p-1.5 rounded-lg bg-[#0d1424] border border-white/10 text-[#94a3b8] hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Scrollable details */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Envelope details */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs bg-[#080c14]/60 p-4 rounded-xl border border-white/5">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Sender Address</span>
                  <span className="font-semibold text-white">{selectedScan.email?.sender}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Sender Domain</span>
                  <span className="font-semibold text-[#94a3b8] font-mono">{selectedScan.email?.sender_domain || 'unknown'}</span>
                </div>
                <div className="sm:col-span-2 space-y-1">
                  <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Subject Line</span>
                  <span className="font-semibold text-white">{selectedScan.email?.subject}</span>
                </div>
              </div>

              {/* Classification metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                <div className="bg-[#080c14]/30 border border-white/5 p-3 rounded-xl">
                  <span className="text-[9px] font-bold text-[#64748b] uppercase tracking-wider block">Scan Verdict</span>
                  <span className={`text-xs font-bold block mt-1 ${selectedScan.prediction_label === 'suspicious' ? 'text-red-400' : 'text-[#00f5a0]'}`}>
                    {selectedScan.prediction_label}
                  </span>
                </div>
                <div className="bg-[#080c14]/30 border border-white/5 p-3 rounded-xl">
                  <span className="text-[9px] font-bold text-[#64748b] uppercase tracking-wider block">Spam Confidence</span>
                  <span className="text-xs font-bold text-white block mt-1 font-mono">{Math.round(selectedScan.confidence * 100)}%</span>
                </div>
                <div className="bg-[#080c14]/30 border border-white/5 p-3 rounded-xl">
                  <span className="text-[9px] font-bold text-[#64748b] uppercase tracking-wider block">Assigned Risk</span>
                  <span className="text-xs font-bold text-amber-400 block mt-1 uppercase tracking-wide">{selectedScan.risk_level}</span>
                </div>
              </div>

              {/* Body Text */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Email Text Content</span>
                <div className="bg-[#080c14]/60 border border-white/5 p-4 rounded-xl text-xs text-[#94a3b8] font-mono whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed border-l-2 border-l-emerald-500/30">
                  {selectedScan.email?.body || 'Empty content'}
                </div>
              </div>

              {/* Security headers summary */}
              {selectedScan.email?.headers && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Security validation headers</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-[#080c14]/30 border border-white/5/40 p-4 rounded-xl text-[11px] font-semibold">
                    <div className="flex justify-between border-b border-white/5 pb-1.5">
                      <span className="text-[#64748b]">SPF alignment:</span>
                      <span className="text-[#94a3b8] font-mono">{selectedScan.email.headers.spf || 'None'}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-1.5">
                      <span className="text-[#64748b]">DKIM alignment:</span>
                      <span className="text-[#94a3b8] font-mono truncate max-w-[120px]">{selectedScan.email.headers.dkim ? 'Present' : 'None'}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-1.5 sm:border-0 sm:pb-0">
                      <span className="text-[#64748b]">DMARC alignment:</span>
                      <span className="text-[#94a3b8] font-mono">{selectedScan.email.headers.dmarc || 'None'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#64748b]">Hop routing count:</span>
                      <span className="text-[#94a3b8] font-mono">{selectedScan.email.headers.hop_count ?? 0}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/5 bg-[#080c14] flex items-center justify-between text-[10px] font-medium text-[#64748b]">
              <span className="flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Audited on {new Date(selectedScan.created_at).toLocaleString()}</span>
              </span>
              <span className="flex items-center space-x-1 text-[#64748b]">
                <AlertCircle className="w-3.5 h-3.5 text-[#64748b]" />
                <span>Model v{selectedScan.model_version}</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
