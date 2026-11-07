import React, { useState } from 'react';
import {
  Bell,
  Search,
  Briefcase,
  ChevronDown,
  LogOut,
  UserCheck,
  Building,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Tender, User, Organization } from '../../types';

interface HeaderProps {
  user: User;
  tenders: Tender[];
  activeTenderId: string | null;
  onSelectTender: (id: string) => void;
  organizations: Organization[];
  selectedOrgId: string | null;
  onSelectOrg: (id: string) => void;
  unreadCount?: number;
  onLogout: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onOpenNotifications?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  tenders,
  activeTenderId,
  onSelectTender,
  organizations,
  selectedOrgId,
  onSelectOrg,
  unreadCount = 3,
  onLogout,
  searchQuery,
  onSearchChange,
  onOpenNotifications,
}) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const activeTender = tenders.find((t) => t.id === activeTenderId) || tenders[0];

  // Derive initials from full name
  const initials = user.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'JD';

  const formatCurrency = (val?: number, currency = 'USD') => {
    if (val === undefined || val === null) return 'N/A';
    return `$${val.toLocaleString()} ${currency}`;
  };

  return (
    <header className="h-16 bg-navy-900 border-b border-navy-700/60 px-6 flex items-center justify-between shrink-0 z-30 select-none">
      {/* Left: Active Pursuit Selector & Value Pill */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-navy-950/80 border border-navy-700/80 rounded-full px-3.5 py-1.5 shadow-inner">
          <Briefcase className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="text-xs text-slate-400 font-medium whitespace-nowrap">Active Pursuit:</span>

          <select
            value={activeTenderId || ''}
            onChange={(e) => onSelectTender(e.target.value)}
            className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer max-w-[280px] md:max-w-[340px] truncate pr-2"
          >
            {tenders.length === 0 && <option value="">No Active Pursuits</option>}
            {tenders.map((t) => (
              <option key={t.id} value={t.id} className="bg-navy-900 text-white py-1">
                {t.reference_number ? `${t.reference_number} – ` : ''}
                {t.title}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none" />
        </div>

        {/* Dynamic Estimated Value Pill (Styled exactly like reference design) */}
        {activeTender && activeTender.estimated_value ? (
          <div className="hidden sm:flex items-center px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium font-mono">
            Est. Value: {formatCurrency(activeTender.estimated_value, activeTender.currency)}
          </div>
        ) : (
          <div className="hidden sm:flex items-center px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-medium font-mono">
            Tender Active • Pipeline Verified
          </div>
        )}
      </div>

      {/* Right Controls: Global Search, Notifications, Profile */}
      <div className="flex items-center gap-4">
        {/* Global Search Input */}
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search tenders, clauses, evidence..."
            className="w-56 lg:w-72 pl-9 pr-3 py-1.5 bg-navy-950/70 border border-navy-700/70 rounded-full text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition"
          />
        </div>

        {/* Notification Bell with Badge */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="relative p-2 rounded-full bg-navy-950/70 hover:bg-navy-800 border border-navy-700/70 text-slate-300 hover:text-white transition"
            title="Notifications & Alerts"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center ring-2 ring-navy-900">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Panel */}
          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-navy-850 border border-navy-700 rounded-xl shadow-2xl p-3 z-50 animate-fade-in">
              <div className="flex items-center justify-between pb-2 border-b border-navy-700/80 mb-2">
                <span className="text-xs font-bold text-white">System Notifications</span>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">
                  {unreadCount} Unread
                </span>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                <div className="p-2 bg-navy-900/80 rounded-lg border border-navy-700/50 flex items-start gap-2 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">Proposal Approved</div>
                    <div className="text-[11px] text-slate-400">Formal sign-off completed for JADC2 Cloud Integration</div>
                    <div className="text-[9px] text-slate-500 mt-1 font-mono">2h ago</div>
                  </div>
                </div>
                <div className="p-2 bg-navy-900/80 rounded-lg border border-navy-700/50 flex items-start gap-2 text-xs">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">Addendum Published</div>
                    <div className="text-[11px] text-slate-400">TND-2026-0410 updated with 2 clarification docs</div>
                    <div className="text-[9px] text-slate-500 mt-1 font-mono">4h ago</div>
                  </div>
                </div>
                <div className="p-2 bg-navy-900/80 rounded-lg border border-navy-700/50 flex items-start gap-2 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">ProofLink Synchronized</div>
                    <div className="text-[11px] text-slate-400">Evidence vault indexed 8 new past performance assets</div>
                    <div className="text-[9px] text-slate-500 mt-1 font-mono">6h ago</div>
                  </div>
                </div>
              </div>
              <div className="pt-2 border-t border-navy-700/80 mt-2 text-center">
                <button
                  onClick={() => {
                    setNotificationsOpen(false);
                    if (onOpenNotifications) onOpenNotifications();
                  }}
                  className="text-[11px] text-cyan-400 hover:text-cyan-300 font-medium"
                >
                  View All Deadlines & Alerts →
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Authenticated User Profile (Matches JD circle + Name + Role) */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2.5 p-1 rounded-full hover:bg-navy-800 transition"
          >
            {/* Initials Avatar Badge */}
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-600 border border-blue-400/40 flex items-center justify-center text-white text-xs font-bold tracking-wider shadow-md shadow-black/40">
              {initials}
            </div>

            {/* User Name & Role */}
            <div className="hidden lg:block text-left pr-1">
              <div className="text-xs font-bold text-white leading-tight">
                {user.full_name || 'Enterprise User'}
              </div>
              <div className="text-[11px] text-slate-400 leading-tight">
                {user.role || 'Bid Manager'}
              </div>
            </div>

            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden lg:block" />
          </button>

          {/* Profile Dropdown */}
          {profileOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-navy-850 border border-navy-700 rounded-xl shadow-2xl p-3 z-50 animate-fade-in">
              <div className="pb-3 border-b border-navy-700/80 mb-2">
                <div className="font-bold text-sm text-white">{user.full_name}</div>
                <div className="text-xs text-cyan-400 font-mono">{user.email}</div>
                <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Role: <span className="text-white font-medium">{user.role}</span>
                </div>
              </div>

              {/* Organization Switcher inside profile */}
              {organizations.length > 0 && (
                <div className="mb-3">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <Building className="w-3 h-3 text-cyan-400" />
                    Active Organization
                  </div>
                  <select
                    value={selectedOrgId || organizations[0]?.id || ''}
                    onChange={(e) => onSelectOrg(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-700 rounded-lg text-xs text-white p-2 focus:outline-none focus:border-cyan-500"
                  >
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <button
                onClick={() => {
                  setProfileOpen(false);
                  onLogout();
                }}
                className="w-full flex items-center gap-2 p-2 rounded-lg text-xs font-medium text-rose-300 hover:text-rose-200 hover:bg-rose-950/40 border border-transparent hover:border-rose-800/40 transition"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out of Workspace
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
