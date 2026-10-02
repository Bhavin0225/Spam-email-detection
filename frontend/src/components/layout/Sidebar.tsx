import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  History, 
  MessageSquare, 
  Settings,
  Mail,
  LogOut,
  User,
  Shield
} from 'lucide-react';

interface SidebarProps {
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isRoleAtLeast = (required: string, current: string): boolean => {
    const roles = ['user', 'analyst', 'ml_engineer', 'admin', 'super_admin'];
    const reqIndex = roles.indexOf(required);
    const currIndex = roles.indexOf(current);
    return currIndex >= reqIndex;
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard, minRole: 'user' },
    { name: 'Analyze Email', path: '/analyze', icon: ShieldAlert, minRole: 'user' },
    { name: 'Inbox Scanner', path: '/inbox', icon: Mail, minRole: 'user' },
    { name: 'History Logs', path: '/history', icon: History, minRole: 'user' },
    { name: 'User Feedback', path: '/feedback', icon: MessageSquare, minRole: 'user' },
    { name: 'System Settings', path: '/admin', icon: Settings, minRole: 'admin' },
  ];

  const currentRole = user?.role || 'user';
  // Enforce SOC_ANALYST tag visually as requested
  const displayRole = currentRole === 'admin' ? 'SOC_ADMIN' : 'SOC_ANALYST';

  return (
    <aside className="w-64 bg-[#080c14] border-r border-white/5 flex flex-col h-full z-20">
      {/* Brand Section */}
      <div className="p-6 flex items-center space-x-3 mb-4 mt-2">
        <div className="text-[#00f5a0]">
          <Shield className="w-8 h-8 fill-current" />
        </div>
        <div>
          <h2 className="text-[15px] font-bold tracking-tight text-white leading-tight">Spam Detection</h2>
          <p className="text-[10px] text-[#64748b] font-mono tracking-widest uppercase">Spam Detector</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          if (!isRoleAtLeast(item.minRole, currentRole)) return null;
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-[#00f5a0] text-[#080c14] emerald-glow font-bold'
                  : 'text-[#94a3b8] hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Profile Card */}
      <div className="p-4 border-t border-white/5 bg-[#080c14]">
        <div className="flex items-center space-x-3 mb-4">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-[#0d1424] border border-white/10 flex items-center justify-center text-white shadow-lg">
              <User className="w-5 h-5 text-[#94a3b8]" />
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-[#10b981] border-2 border-[#080c14] rounded-full"></div>
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-[11px] text-[#94a3b8] font-mono truncate block max-w-[130px]">
              {user?.email || 'test12345@example.com'}
            </span>
            <div className="mt-1 flex">
              <span className="bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20 px-2 py-0.5 rounded-[4px] text-[9px] font-bold font-mono uppercase tracking-wider">
                {displayRole}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          aria-label="Premium Logout"
          className="w-full flex items-center justify-center space-x-2 p-2.5 rounded-lg bg-transparent text-[#64748b] hover:text-[#ef4444] hover:bg-[#ef4444]/10 border border-transparent hover:border-[#ef4444]/20 transition-all text-xs font-semibold cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          <span>Premium Logout</span>
        </button>
      </div>
    </aside>
  );
};
