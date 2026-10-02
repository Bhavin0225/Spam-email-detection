import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';
import { 
  Users, 
  Terminal, 
  RefreshCw, 
  Shield, 
  Activity
} from 'lucide-react';


export const UserManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'logs'>('users');
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/admin/users');
      setUsers(res.data);
    } catch (e) {
      console.error('Failed to load user list', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/admin/logs');
      setLogs(res.data);
    } catch (e) {
      console.error('Failed to load audit logs', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers();
    } else {
      fetchLogs();
    }
  }, [activeTab]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Admin Operations Desk</h2>
          <p className="text-xs text-[#94a3b8]">Manage operator authorizations and review system access logs.</p>
        </div>
        <button
          onClick={activeTab === 'users' ? fetchUsers : fetchLogs}
          disabled={loading}
          className="p-2.5 rounded-xl bg-[#0d1424] border border-white/10 text-[#94a3b8] hover:text-white transition-all flex items-center justify-center cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Tabs Switcher */}
      <div className="flex space-x-2 border-b border-white/5/40 pb-px">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition-all cursor-pointer ${
            activeTab === 'users'
              ? 'border-emerald-500 text-[#00f5a0] font-bold'
              : 'border-transparent text-[#64748b] hover:text-[#94a3b8]'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Operator Directory</span>
        </button>
        <button
          onClick={() => setActiveTab('logs')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition-all cursor-pointer ${
            activeTab === 'logs'
              ? 'border-emerald-500 text-[#00f5a0] font-bold'
              : 'border-transparent text-[#64748b] hover:text-[#94a3b8]'
          }`}
        >
          <Terminal className="w-4 h-4" />
          <span>System Audit Logs</span>
        </button>
      </div>

      {/* Content Panels */}
      <div className="glass-card rounded-xl p-6">
        {loading ? (
          <div className="space-y-3 py-6">
            <div className="h-10 bg-[#0d1424] rounded-xl animate-pulse" />
            <div className="h-10 bg-[#0d1424] rounded-xl animate-pulse" />
          </div>
        ) : activeTab === 'users' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/5 text-[#94a3b8] font-bold uppercase tracking-wider">
                  <th className="pb-3 pl-2">Name / Email</th>
                  <th className="pb-3">User ID</th>
                  <th className="pb-3">Role</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 pr-2 text-right">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/30 text-[#94a3b8]">
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-[#64748b] font-semibold">
                      No users registered.
                    </td>
                  </tr>
                ) : (
                  users.map((item) => (
                    <tr key={item.user_id} className="hover:bg-[#0d1424]/10 transition-colors">
                      <td className="py-3.5 pl-2">
                        <span className="font-semibold block text-white">{item.full_name || 'N/A'}</span>
                        <span className="text-[10px] text-[#64748b] block mt-0.5">{item.email}</span>
                      </td>
                      <td className="py-3.5 font-mono text-[#94a3b8]">
                        {item.user_id}
                      </td>
                      <td className="py-3.5 font-semibold text-[#00f5a0]">
                        <span className="flex items-center space-x-1">
                          <Shield className="w-3.5 h-3.5" />
                          <span>{item.role}</span>
                        </span>
                      </td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold border bg-emerald-950/20 border-emerald-900/40 text-[#00f5a0]">
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3.5 pr-2 text-right text-[#64748b] font-medium">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/5 text-[#94a3b8] font-bold uppercase tracking-wider">
                  <th className="pb-3 pl-2">Event Type</th>
                  <th className="pb-3">Details / Metadata</th>
                  <th className="pb-3">Severity</th>
                  <th className="pb-3">Operator ID</th>
                  <th className="pb-3 pr-2 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/30 text-[#94a3b8] font-mono">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-[#64748b] font-semibold font-sans">
                      No system audit events recorded.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => {
                    const isWarn = log.severity === 'warning' || log.severity === 'critical';
                    return (
                      <tr key={log.log_id} className="hover:bg-[#0d1424]/10 transition-colors">
                        <td className="py-3.5 pl-2 font-bold text-white">
                          <span className="flex items-center space-x-1">
                            <Activity className="w-3.5 h-3.5 text-blue-400" />
                            <span>{log.event_type}</span>
                          </span>
                        </td>
                        <td className="py-3.5 max-w-sm truncate text-[#94a3b8] text-[10px]">
                          {JSON.stringify(log.details)}
                        </td>
                        <td className="py-3.5">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                            isWarn
                              ? 'bg-red-950/20 border-red-900/40 text-red-400'
                              : 'bg-[#0d1424] border-white/10 text-[#94a3b8]'
                          }`}>
                            {log.severity}
                          </span>
                        </td>
                        <td className="py-3.5 text-[#64748b] truncate max-w-[120px]">
                          {log.user_id || 'anonymous'}
                        </td>
                        <td className="py-3.5 pr-2 text-right text-[#64748b] font-medium">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
