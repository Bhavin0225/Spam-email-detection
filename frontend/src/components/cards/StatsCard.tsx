import React from 'react';
import type { LucideIcon } from 'lucide-react';


interface StatsCardProps {
  title: string;
  value: string | number;
  description: string;
  icon: LucideIcon;
  iconColor?: string;
  badge?: string;
  badgeColor?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  description,
  icon: Icon,
  iconColor = 'text-blue-400',
  badge,
  badgeColor = 'bg-blue-950/20 text-blue-400 border-blue-900/50',
}) => {
  return (
    <div className="glass-card p-6 rounded-xl flex items-start justify-between relative overflow-hidden group">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/5 to-transparent rounded-full translate-x-12 -translate-y-12 transition-transform duration-300 group-hover:scale-110" />

      <div className="space-y-3">
        <span className="text-[10px] font-bold text-[#64748b] uppercase font-mono tracking-wider">{title}</span>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white tracking-tight">{value}</span>
          {badge && (
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badgeColor}`}>
              {badge}
            </span>
          )}
        </div>
        <p className="text-xs text-[#64748b] font-medium">{description}</p>
      </div>

      <div className={`p-3 rounded-xl bg-[#0d1424] border border-white/10 ${iconColor} shadow-inner`}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
  );
};
