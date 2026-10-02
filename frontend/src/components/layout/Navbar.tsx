import React, { useEffect, useState } from 'react';
import { Menu, Plus, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiClient } from '../../services/apiClient';

interface NavbarProps {
  onToggleMobileMenu: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileMenu }) => {
  const [health, setHealth] = useState<{ database: string; version?: string } | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await apiClient.get('/health');
        setHealth(res.data);
      } catch (e) {
        setHealth({ database: 'disconnected' });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const dbConnected = health?.database === 'connected';

  return (
    <header className="h-[72px] bg-[#080c14] border-b border-white/5 flex items-center justify-between px-8 z-10">
      {/* Mobile Toggle & Title */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onToggleMobileMenu}
          aria-label="Toggle Menu"
          className="md:hidden p-2 rounded-lg text-[#94a3b8] hover:bg-white/5 hover:text-white"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-base font-bold text-white tracking-tight hidden md:block">
          Security Operations Console
        </h1>
      </div>

      {/* Right Cluster */}
      <div className="flex items-center space-x-5">
        {/* Model Version Pill */}
        <div className="hidden md:flex items-center px-3 py-1.5 rounded-lg bg-[#0d1424] border border-white/10 text-xs font-mono text-[#94a3b8]">
          <span>[Model: <span className="text-[#00f5a0]">{health?.version || 'v1.0.0'}</span>]</span>
        </div>

        {/* Database Status Indicator */}
        <div className="flex items-center space-x-2 text-xs font-mono font-medium text-[#94a3b8]">
          <div className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dbConnected ? 'bg-[#00f5a0]' : 'bg-[#ef4444]'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${dbConnected ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`}></span>
          </div>
          <span className="hidden sm:inline-block">({dbConnected ? '●' : '!'}) {dbConnected ? 'Database Connected' : 'DB Offline'}</span>
        </div>

        {/* Primary CTA Button */}
        <Link
          to="/analyze"
          className="flex items-center space-x-1.5 bg-[#0d1424] hover:bg-[#00f5a0]/10 border border-[#00f5a0]/30 text-[#00f5a0] hover:text-[#00f5a0] hover:emerald-glow px-4 py-2 rounded-xl text-sm font-semibold transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Analysis Scan</span>
        </Link>

        {/* Quick Action Icon */}
        <button className="text-[#64748b] hover:text-white transition-colors p-1.5">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
