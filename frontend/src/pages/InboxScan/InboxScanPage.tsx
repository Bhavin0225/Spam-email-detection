import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiClient } from '../../services/apiClient';
import { 
  Mail, 
  ShieldAlert, 
  ShieldCheck, 
  RefreshCw, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  Server, 
  Lock,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Trash2
} from 'lucide-react';

interface ScanResultItem {
  subject: string;
  sender: string;
  prediction_label: string;
  confidence: number;
  risk_level: string;
  prediction_id: string;
  date_sent?: string;
  has_attachments: boolean;
}

interface ScanReport {
  scan_id: string;
  provider: string;
  total_scanned: number;
  spam_count: number;
  legitimate_count: number;
  high_risk_count: number;
  scan_duration_seconds: number;
  results: ScanResultItem[];
  created_at: string;
}

interface GmailStatus {
  connected: boolean;
  email?: string;
  connected_at?: string;
}

export const InboxScanPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<'gmail' | 'imap'>('gmail');
  
  // Gmail Connection States
  const [gmailStatus, setGmailStatus] = useState<GmailStatus>({ connected: false });
  const [gmailLoading, setGmailLoading] = useState<boolean>(true);
  
  // Scan Form States
  const [limit, setLimit] = useState<number>(100);
  const [imapHost, setImapHost] = useState<string>('imap.gmail.com');
  const [imapPort, setImapPort] = useState<number>(993);
  const [imapEmail, setImapEmail] = useState<string>('');
  const [imapPassword, setImapPassword] = useState<string>('');
  const [imapFolder, setImapFolder] = useState<string>('INBOX');
  const [imapProvider, setImapProvider] = useState<string>('gmail');
  
  // Action/Scanning States
  const [scanning, setScanning] = useState<boolean>(false);
  const [scanReport, setScanReport] = useState<ScanReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  
  // Table States
  const [filter, setFilter] = useState<'all' | 'suspicious' | 'legitimate' | 'high_risk'>('all');
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [explainData, setExplainData] = useState<Record<string, any>>({});
  const [loadingExplain, setLoadingExplain] = useState<Record<string, boolean>>({});

  // IMAP Provider preset configurations
  const providerPresets: Record<string, { host: string; port: number }> = {
    gmail: { host: 'imap.gmail.com', port: 993 },
    outlook: { host: 'outlook.office365.com', port: 993 },
    yahoo: { host: 'imap.mail.yahoo.com', port: 993 },
    custom: { host: '', port: 993 }
  };

  useEffect(() => {
    fetchGmailStatus();
    checkOAuthCallback();
  }, []);

  const handleProviderPresetChange = (prov: string) => {
    setImapProvider(prov);
    if (providerPresets[prov]) {
      setImapHost(providerPresets[prov].host);
      setImapPort(providerPresets[prov].port);
    }
  };

  const fetchGmailStatus = async () => {
    setGmailLoading(true);
    try {
      const res = await apiClient.get<GmailStatus>('/inbox/gmail/status');
      setGmailStatus(res.data);
    } catch (err) {
      console.error('Failed to fetch Gmail OAuth status', err);
    } finally {
      setGmailLoading(false);
    }
  };

  const checkOAuthCallback = async () => {
    const code = searchParams.get('code');
    if (code) {
      setGmailLoading(true);
      setError(null);
      // Remove query parameters from URL clean-up
      setSearchParams({}, { replace: true });
      try {
        const redirectUri = window.location.origin + '/inbox';
        await apiClient.post('/inbox/gmail/callback', { code, redirect_uri: redirectUri });
        setSuccessMsg('Successfully connected Gmail account!');
        fetchGmailStatus();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to authorize Gmail OAuth connection.');
      } finally {
        setGmailLoading(false);
      }
    }
  };

  const connectGmail = async () => {
    setError(null);
    setSuccessMsg(null);
    try {
      const redirectUri = window.location.origin + '/inbox';
      const res = await apiClient.get(`/inbox/gmail/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      if (res.data?.auth_url) {
        window.location.href = res.data.auth_url;
      } else {
        throw new Error('OAuth URL not returned by server');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start Gmail connection flow.');
    }
  };

  const disconnectGmail = async () => {
    if (!window.confirm('Are you sure you want to disconnect Gmail?')) return;
    setError(null);
    setSuccessMsg(null);
    try {
      await apiClient.delete('/inbox/gmail/disconnect');
      setGmailStatus({ connected: false });
      setSuccessMsg('Disconnected Gmail account successfully.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect Gmail account.');
    }
  };

  const startScan = async (provider: 'gmail' | 'imap') => {
    setError(null);
    setScanReport(null);
    setScanning(true);
    setExpandedRows({});
    
    try {
      let res;
      if (provider === 'gmail') {
        res = await apiClient.post<ScanReport>('/inbox/gmail/scan', { limit });
      } else {
        if (!imapHost || !imapEmail || !imapPassword) {
          throw new Error('Please fill in all host, email, and app password fields.');
        }
        res = await apiClient.post<ScanReport>('/inbox/imap/scan', {
          host: imapHost,
          port: imapPort,
          email: imapEmail,
          password: imapPassword,
          folder: imapFolder,
          limit,
          provider: imapProvider !== 'custom' ? imapProvider : undefined
        });
      }
      setScanReport(res.data);
      setSuccessMsg(`Inbox scan completed! Scanned ${res.data.total_scanned} emails.`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during inbox scanning.');
    } finally {
      setScanning(false);
    }
  };

  const toggleRow = async (predId: string) => {
    setExpandedRows(prev => ({ ...prev, [predId]: !prev[predId] }));
    
    if (!explainData[predId] && !loadingExplain[predId]) {
      setLoadingExplain(prev => ({ ...prev, [predId]: true }));
      try {
        const res = await apiClient.get(`/history/${predId}`);
        if (res.data) {
          setExplainData(prev => ({ ...prev, [predId]: res.data }));
        }
      } catch (err) {
        console.error('Failed to load explainability factors', err);
      } finally {
        setLoadingExplain(prev => ({ ...prev, [predId]: false }));
      }
    }
  };

  const exportCSV = () => {
    if (!scanReport || !scanReport.results.length) return;
    
    const headers = ['Subject', 'Sender', 'Verdict', 'Confidence', 'Risk Level', 'Date Sent', 'Has Attachments'];
    const rows = scanReport.results.map(r => [
      `"${r.subject.replace(/"/g, '""')}"`,
      `"${r.sender.replace(/"/g, '""')}"`,
      r.prediction_label,
      `${Math.round(r.confidence * 100)}%`,
      r.risk_level,
      r.date_sent ? new Date(r.date_sent).toLocaleString() : 'N/A',
      r.has_attachments ? 'Yes' : 'No'
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `inbox_scan_${scanReport.scan_id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredResults = scanReport?.results.filter(r => {
    if (filter === 'all') return true;
    if (filter === 'suspicious') return r.prediction_label === 'suspicious';
    if (filter === 'legitimate') return r.prediction_label === 'legitimate';
    if (filter === 'high_risk') return r.risk_level === 'high';
    return true;
  }) || [];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Mail className="w-5 h-5 text-[#00f5a0]" />
            <span>Automated Inbox Scanner</span>
          </h2>
          <p className="text-xs text-[#94a3b8]">Scan real mail logs from your inbox in bulk and segregate spam threats.</p>
        </div>
      </div>

      {/* Alert Notices */}
      {error && (
        <div className="p-4 bg-red-950/20 border border-red-900/50 rounded-xl flex items-start space-x-3 text-red-400 text-xs">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-4 bg-emerald-950/20 border border-emerald-900/50 rounded-xl flex items-start space-x-3 text-[#00f5a0] text-xs">
          <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Tabs Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Connection Setup Side Panel */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card rounded-xl p-6 space-y-6">
            <div className="flex border-b border-white/5 pb-1">
              <button
                onClick={() => { setActiveTab('gmail'); setError(null); }}
                className={`flex-1 pb-3 text-xs font-bold uppercase tracking-wider transition-colors ${
                  activeTab === 'gmail' ? 'text-[#00f5a0] border-b-2 border-emerald-500' : 'text-[#94a3b8] hover:text-white'
                }`}
              >
                Gmail Integration
              </button>
              <button
                onClick={() => { setActiveTab('imap'); setError(null); }}
                className={`flex-1 pb-3 text-xs font-bold uppercase tracking-wider transition-colors ${
                  activeTab === 'imap' ? 'text-[#00f5a0] border-b-2 border-emerald-500' : 'text-[#94a3b8] hover:text-white'
                }`}
              >
                Universal IMAP
              </button>
            </div>

            {/* TAB: Gmail (OAuth2) */}
            {activeTab === 'gmail' && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wide">Gmail Connection Status</h3>
                  {gmailLoading ? (
                    <div className="h-12 bg-[#0d1424]/20 rounded-xl animate-pulse" />
                  ) : gmailStatus.connected ? (
                    <div className="p-4 bg-emerald-950/10 border border-emerald-900/30 rounded-xl space-y-3">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-[#00f5a0]" />
                        <span className="text-xs text-white font-semibold truncate">{gmailStatus.email}</span>
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-[#64748b]">
                        <span>Connected: {new Date(gmailStatus.connected_at || '').toLocaleDateString()}</span>
                        <button
                          onClick={disconnectGmail}
                          className="flex items-center space-x-1 text-red-400 hover:text-red-300 font-bold"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Disconnect</span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 bg-[#0d1424] border border-white/10 rounded-xl space-y-4">
                      <p className="text-[11px] text-[#94a3b8] leading-relaxed">
                        Connect your Gmail account via secure Google OAuth2 login to scan your inbox directly.
                      </p>
                      <button
                        onClick={connectGmail}
                        className="w-full flex items-center justify-center space-x-2 bg-[#0d1424] hover:bg-slate-800 text-white border border-slate-700/60 py-2.5 rounded-xl font-bold text-xs transition-colors cursor-pointer"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-[#00f5a0]" />
                        <span>Link Gmail Account</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Limit Slider */}
                <div className="space-y-3">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold text-[#94a3b8]">Scan Volume Limit</span>
                    <span className="font-mono text-[#00f5a0] font-bold">{limit} emails</span>
                  </div>
                  <input
                    type="range"
                    min={10}
                    max={200}
                    step={10}
                    value={limit}
                    onChange={(e) => setLimit(parseInt(e.target.value))}
                    disabled={scanning}
                    className="w-full accent-emerald-500 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-[#64748b]">
                    <span>10</span>
                    <span>100</span>
                    <span>200 (Max)</span>
                  </div>
                </div>

                <button
                  onClick={() => startScan('gmail')}
                  disabled={scanning || !gmailStatus.connected}
                  className={`w-full flex items-center justify-center space-x-2 py-3 rounded-xl font-bold text-xs transition-all ${
                    scanning 
                      ? 'bg-slate-800 text-[#64748b] cursor-not-allowed'
                      : !gmailStatus.connected
                        ? 'bg-[#0d1424] text-[#64748b] border border-white/10/80 cursor-not-allowed'
                        : 'bg-[#00f5a0] hover:bg-[#00f5a0]/80 text-[#080c14] shadow-lg shadow-emerald-500/10 cursor-pointer'
                  }`}
                >
                  {scanning ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Scanning Mailbox...</span>
                    </>
                  ) : (
                    <>
                      <Mail className="w-4 h-4" />
                      <span>Start Inbox Scan</span>
                    </>
                  )}
                </button>
              </div>
            )}

            {/* TAB: IMAP Form */}
            {activeTab === 'imap' && (
              <div className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Email Provider Preset</label>
                  <select
                    value={imapProvider}
                    onChange={(e) => handleProviderPresetChange(e.target.value)}
                    disabled={scanning}
                    className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  >
                    <option value="gmail">Gmail (IMAP)</option>
                    <option value="outlook">Outlook / Office365</option>
                    <option value="yahoo">Yahoo Mail</option>
                    <option value="custom">Custom IMAP Configuration</option>
                  </select>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div className="col-span-2 space-y-1">
                    <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">IMAP Server Host</label>
                    <input
                      type="text"
                      placeholder="imap.example.com"
                      value={imapHost}
                      onChange={(e) => setImapHost(e.target.value)}
                      disabled={scanning || imapProvider !== 'custom'}
                      className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                    />
                  </div>
                  <div className="col-span-1 space-y-1">
                    <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Port</label>
                    <input
                      type="number"
                      value={imapPort}
                      onChange={(e) => setImapPort(parseInt(e.target.value) || 993)}
                      disabled={scanning || imapProvider !== 'custom'}
                      className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Email Address</label>
                  <input
                    type="email"
                    placeholder="user@example.com"
                    value={imapEmail}
                    onChange={(e) => setImapEmail(e.target.value)}
                    disabled={scanning}
                    className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">App Password</label>
                    <span className="text-[9px] text-[#64748b] font-semibold flex items-center gap-0.5">
                      <Lock className="w-3 h-3" />
                      Not stored persistently
                    </span>
                  </div>
                  <input
                    type="password"
                    placeholder="••••••••••••••••"
                    value={imapPassword}
                    onChange={(e) => setImapPassword(e.target.value)}
                    disabled={scanning}
                    className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Folder</label>
                    <input
                      type="text"
                      value={imapFolder}
                      onChange={(e) => setImapFolder(e.target.value)}
                      disabled={scanning}
                      className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">Max Emails</label>
                    <input
                      type="number"
                      min={10}
                      max={200}
                      value={limit}
                      onChange={(e) => setLimit(Math.max(10, Math.min(200, parseInt(e.target.value) || 100)))}
                      disabled={scanning}
                      className="w-full bg-[#0d1424] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                    />
                  </div>
                </div>

                <button
                  onClick={() => startScan('imap')}
                  disabled={scanning}
                  className={`w-full flex items-center justify-center space-x-2 py-3 rounded-xl font-bold text-xs transition-all ${
                    scanning 
                      ? 'bg-slate-800 text-[#64748b] cursor-not-allowed'
                      : 'bg-[#00f5a0] hover:bg-[#00f5a0]/80 text-[#080c14] shadow-lg shadow-emerald-500/10 cursor-pointer'
                  }`}
                >
                  {scanning ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Connecting & Scanning...</span>
                    </>
                  ) : (
                    <>
                      <Server className="w-4 h-4" />
                      <span>Start IMAP Scan</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Scan Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {scanning ? (
            <div className="glass-card rounded-xl p-12 flex flex-col items-center justify-center space-y-4">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 border-4 border-white/10 rounded-full" />
                <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              </div>
              <h3 className="text-sm font-bold text-white tracking-wide">Scanning Your Mailbox</h3>
              <p className="text-xs text-[#94a3b8] text-center max-w-sm leading-relaxed">
                Ingesting the latest headers, analyzing email age, verifying security records (SPF/DKIM/DMARC), scoring attachments, and evaluating spam triggers...
              </p>
            </div>
          ) : scanReport ? (
            <div className="space-y-6">
              {/* Metrics Summary Blocks */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-[#0d1424]/30 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-[#94a3b8] font-bold uppercase tracking-wider block">Total Scanned</span>
                  <span className="text-2xl font-black text-white font-mono block mt-1">{scanReport.total_scanned}</span>
                </div>
                <div className="p-4 bg-red-950/10 border border-red-950/20 rounded-xl">
                  <span className="text-[10px] text-red-400/80 font-bold uppercase tracking-wider block">Suspicious / Spam</span>
                  <span className="text-2xl font-black text-red-400 font-mono block mt-1">{scanReport.spam_count}</span>
                </div>
                <div className="p-4 bg-emerald-950/10 border border-emerald-950/20 rounded-xl">
                  <span className="text-[10px] text-[#00f5a0]/80 font-bold uppercase tracking-wider block">Legitimate</span>
                  <span className="text-2xl font-black text-[#00f5a0] font-mono block mt-1">{scanReport.legitimate_count}</span>
                </div>
                <div className="p-4 bg-purple-950/10 border border-purple-950/20 rounded-xl">
                  <span className="text-[10px] text-purple-400/80 font-bold uppercase tracking-wider block">High Threat Risk</span>
                  <span className="text-2xl font-black text-purple-400 font-mono block mt-1">{scanReport.high_risk_count}</span>
                </div>
              </div>

              {/* filter table and results */}
              <div className="glass-card rounded-xl p-6 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex gap-1.5 overflow-x-auto pb-1">
                    {(['all', 'suspicious', 'legitimate', 'high_risk'] as const).map(f => (
                      <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer ${
                          filter === f 
                            ? 'bg-slate-800 text-[#00f5a0] border border-slate-700/50' 
                            : 'text-[#94a3b8] hover:bg-[#0d1424] hover:text-white'
                        }`}
                      >
                        {f.replace('_', ' ')}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={exportCSV}
                    className="inline-flex items-center space-x-2 bg-[#0d1424] hover:bg-slate-800 text-white border border-white/10 px-3.5 py-2 rounded-xl text-xs font-bold transition-colors cursor-pointer self-start"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export CSV</span>
                  </button>
                </div>

                {/* Results Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-white/5 text-[#94a3b8] font-bold uppercase tracking-wider">
                        <th className="pb-3 pl-2">Subject / Sender</th>
                        <th className="pb-3">Verdict</th>
                        <th className="pb-3">Confidence</th>
                        <th className="pb-3">Risk</th>
                        <th className="pb-3 pr-2 text-right">Details</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900/30 text-[#94a3b8]">
                      {filteredResults.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-8 text-center text-[#64748b] font-semibold">
                            No match scan results for this filter.
                          </td>
                        </tr>
                      ) : (
                        filteredResults.map((item) => {
                          const isSpam = item.prediction_label === 'suspicious';
                          const isExpanded = expandedRows[item.prediction_id];
                          const exp = explainData[item.prediction_id];
                          const loadingExp = loadingExplain[item.prediction_id];

                          return (
                            <React.Fragment key={item.prediction_id}>
                              <tr className="hover:bg-[#0d1424]/20 transition-colors">
                                <td className="py-3.5 pl-2 max-w-xs truncate">
                                  <span className="font-semibold block text-white truncate">{item.subject || '(No Subject)'}</span>
                                  <span className="text-[10px] text-[#64748b] block truncate mt-0.5">{item.sender}</span>
                                </td>
                                <td className="py-3.5 font-bold">
                                  <span className={`inline-flex items-center space-x-1 ${isSpam ? 'text-red-400' : 'text-[#00f5a0]'}`}>
                                    {isSpam ? <ShieldAlert className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                                    <span>{item.prediction_label}</span>
                                  </span>
                                </td>
                                <td className="py-3.5 font-semibold font-mono">
                                  {Math.round(item.confidence * 100)}%
                                </td>
                                <td className="py-3.5">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                    item.risk_level === 'high' 
                                      ? 'bg-red-950/20 border-red-900/40 text-red-400'
                                      : item.risk_level === 'medium'
                                        ? 'bg-amber-950/20 border-amber-900/40 text-amber-400'
                                        : 'bg-emerald-950/20 border-emerald-900/40 text-[#00f5a0]'
                                  }`}>
                                    {item.risk_level}
                                  </span>
                                </td>
                                <td className="py-3.5 pr-2 text-right">
                                  <button
                                    onClick={() => toggleRow(item.prediction_id)}
                                    className="p-1 rounded hover:bg-slate-800 text-[#94a3b8] hover:text-white transition-colors cursor-pointer"
                                  >
                                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                  </button>
                                </td>
                              </tr>

                              {/* Expandable explainability factors details */}
                              {isExpanded && (
                                <tr>
                                  <td colSpan={5} className="py-3 px-4 bg-[#080c14] border-y border-white/5/40">
                                    {loadingExp ? (
                                      <div className="py-4 flex flex-col items-center justify-center space-y-2 text-[#64748b]">
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                        <span>Retrieving threat details...</span>
                                      </div>
                                    ) : exp ? (
                                      <div className="space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                          <div>
                                            <h4 className="text-[10px] font-bold text-red-400 uppercase tracking-wide mb-2">Spam Indicators</h4>
                                            <ul className="space-y-1">
                                              {exp.explainability?.top_spam_factors?.map((f: any, idx: number) => (
                                                <li key={idx} className="text-[11px] text-[#94a3b8] flex justify-between">
                                                  <span>• {f.feature}</span>
                                                  <span className="font-mono text-red-400">+{Math.round(f.score * 100)}</span>
                                                </li>
                                              ))}
                                              {(!exp.explainability?.top_spam_factors || exp.explainability.top_spam_factors.length === 0) && (
                                                <li className="text-[11px] text-[#64748b] italic">None</li>
                                              )}
                                            </ul>
                                          </div>
                                          <div>
                                            <h4 className="text-[10px] font-bold text-[#00f5a0] uppercase tracking-wide mb-2">Clean Signals</h4>
                                            <ul className="space-y-1">
                                              {exp.explainability?.top_clean_factors?.map((f: any, idx: number) => (
                                                <li key={idx} className="text-[11px] text-[#94a3b8] flex justify-between">
                                                  <span>• {f.feature}</span>
                                                  <span className="font-mono text-[#00f5a0]">-{Math.round(f.score * 100)}</span>
                                                </li>
                                              ))}
                                              {(!exp.explainability?.top_clean_factors || exp.explainability.top_clean_factors.length === 0) && (
                                                <li className="text-[11px] text-[#64748b] italic">None</li>
                                              )}
                                            </ul>
                                          </div>
                                        </div>

                                        {/* Security Headers summary */}
                                        <div className="pt-2 border-t border-white/5/30 grid grid-cols-3 gap-2 text-[10px]">
                                          <div>
                                            <span className="text-[#64748b] block">SPF Auth:</span>
                                            <span className={`font-bold uppercase ${exp.email?.headers?.spf === 'pass' ? 'text-[#00f5a0]' : 'text-red-400'}`}>
                                              {exp.email?.headers?.spf || 'fail'}
                                            </span>
                                          </div>
                                          <div>
                                            <span className="text-[#64748b] block">DKIM Signature:</span>
                                            <span className={`font-bold uppercase ${exp.email?.headers?.dkim === 'pass' ? 'text-[#00f5a0]' : 'text-red-400'}`}>
                                              {exp.email?.headers?.dkim || 'fail'}
                                            </span>
                                          </div>
                                          <div>
                                            <span className="text-[#64748b] block">DMARC Alignment:</span>
                                            <span className={`font-bold uppercase ${exp.email?.headers?.dmarc === 'pass' ? 'text-[#00f5a0]' : 'text-red-400'}`}>
                                              {exp.email?.headers?.dmarc || 'fail'}
                                            </span>
                                          </div>
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="text-center py-4 text-[#64748b] italic">
                                        Could not resolve feature details for this prediction record.
                                      </div>
                                    )}
                                  </td>
                                </tr>
                              )}
                            </React.Fragment>
                          );
                        })
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card rounded-xl p-12 flex flex-col items-center justify-center space-y-4 text-[#64748b]">
              <Mail className="w-10 h-10 text-slate-700 animate-pulse" />
              <h3 className="text-sm font-bold text-[#94a3b8]">No Scan session compiled</h3>
              <p className="text-xs text-[#64748b] text-center max-w-xs">
                Select your email provider, adjust the scan volume limit, and trigger the scan to fetch emails.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
