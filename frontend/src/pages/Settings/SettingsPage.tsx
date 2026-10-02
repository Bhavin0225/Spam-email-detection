import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Settings, Shield, HardDrive } from 'lucide-react';



export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Console Settings</h2>
        <p className="text-xs text-[#94a3b8]">Manage profile specifications and operations details.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
        {/* User Card */}
        <div className="md:col-span-1 glass-card p-6 rounded-xl flex flex-col items-center text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-[#0d1424] border border-white/10 flex items-center justify-center text-[#94a3b8] text-2xl font-bold shadow-inner">
            {user?.email?.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">{user?.email}</h3>
            <span className="text-[10px] font-bold text-[#00f5a0] uppercase tracking-wider mt-1 block">
              {user?.role} Role
            </span>
          </div>
        </div>

        {/* Profile details */}
        <div className="md:col-span-2 glass-card p-6 rounded-xl space-y-6">
          <div className="flex items-center space-x-3 pb-2 border-b border-white/5">
            <Settings className="w-5 h-5 text-[#00f5a0]" />
            <h3 className="text-sm font-bold text-white">Operator Details</h3>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Email Address</span>
                <div className="p-3 bg-[#0d1424] border border-white/10/80 rounded-xl text-xs font-semibold text-[#94a3b8]">
                  {user?.email}
                </div>
              </div>
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Role Authorization</span>
                <div className="p-3 bg-[#0d1424] border border-white/10/80 rounded-xl text-xs font-semibold text-[#94a3b8] flex items-center space-x-1.5">
                  <Shield className="w-3.5 h-3.5 text-[#00f5a0]" />
                  <span className="capitalize">{user?.role}</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-1.5">
              <span className="text-[10px] font-bold text-[#64748b] uppercase tracking-wider block">Console Version Info</span>
              <div className="p-3 bg-[#0d1424] border border-white/10/80 rounded-xl text-xs font-semibold text-[#94a3b8] flex items-center space-x-1.5">
                <HardDrive className="w-3.5 h-3.5 text-[#64748b]" />
                <span>Spam Detection Dashboard v1.0.0 (FastAPI Core + React TS Client)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
