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
  AlertCircle,
  Menu,
  X,
  Sparkles
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
  onToggleMobileMenu?: () => void;
  mobileMenuOpen?: boolean;
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
  onToggleMobileMenu,
  mobileMenuOpen = false,
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
    <header className="h-16 bg-navy-900/95 backdrop-blur-md border-b border-navy-700/60 px-4 sm:px-6 flex items-center justify-between shrink-0 z-30 select-none sticky top-0">
      {/* Left: Mobile Menu Trigger + Active Pursuit Selector & Value Pill */}
      <div className="flex items-center gap-2 sm:gap-3 overflow-hidden">
        {/* Mobile Hamburger Button */}
        {onToggleMobileMenu && (
          <button
            onClick={onToggleMobileMenu}
            className="p-1.5 rounded-lg lg:hidden text-slate-400 hover:text-white hover:bg-navy-800 transition"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5 text-cyan-400" /> : <Menu className="w-5 h-5" />}
          </button>
        )}

        {/* Pursuit Capsule */}
        <div className="flex items-center gap-2 bg-navy-950/90 border border-navy-700/80 hover:border-cyan-500/40 rounded-full px-3 py-1.5 shadow-inner transition max-w-[260px] sm:max-w-none">
          <Briefcase className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="hidden sm:inline text-xs text-slate-400 font-medium whitespace-nowrap">Active Pursuit:</span>

          <select
            value={activeTenderId || ''}
            onChange={(e) => onSelectTender(e.target.value)}
            className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer max-w-[150px] sm:max-w-[260px] md:max-w-[320px] truncate pr-1"
          >
            {tenders.length === 0 && <option value="">No Active Pursuits</option>}
            {tenders.map((t) => (
              <option key={t.id} value={t.id} className="bg-navy-900 text-white py-1">
                {t.reference_number ? `${t.reference_number} – ` : ''}
                {t.title}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none shrink-0" />
        </div>

        {/* Dynamic Estimated Value Pill */}
        {activeTender && activeTender.estimated_value ? (
          <div className="hidden md:flex items-center px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium font-mono shrink-0 shadow-sm">
            Est. Value: {formatCurrency(activeTender.estimated_value, activeTender.currency)}
          </div>
        ) : (
          <div className="hidden md:flex items-center px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-medium font-mono shrink-0 shadow-sm">
            Tender Active • Pipeline Verified
          </div>
        )}
      </div>

      {/* Right Controls: Global Search, Notifications, Profile */}
      <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
        {/* Global Search Input with Shortcut Badge */}
        <div className="relative hidden md:block">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search tenders, clauses, evidence..."
            className="w-48 lg:w-64 pl-8 pr-12 py-1.5 bg-navy-950/80 border border-navy-700/80 hover:border-navy-600 focus:border-cyan-500/70 rounded-full text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/40 transition shadow-inner"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-500 bg-navy-900 border border-navy-700/80 rounded px-1.5 py-0.2 pointer-events-none">
            Ctrl+K
          </kbd>
        </div>

        {/* Notification Bell with Badge */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="relative p-2 rounded-full bg-navy-950/80 hover:bg-navy-800 border border-navy-700/80 hover:border-navy-600 text-slate-300 hover:text-white transition shadow-sm active:scale-95"
            title="Notifications & Alerts"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center ring-2 ring-navy-900 animate-pulse-subtle">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Panel */}
          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-navy-850/95 backdrop-blur-xl border border-navy-700 rounded-2xl shadow-dropdown p-3.5 z-50 animate-fade-in">
              <div className="flex items-center justify-between pb-2.5 border-b border-navy-700/80 mb-2.5">
                <div className="flex items-center gap-1.5">
                  <Bell className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="text-xs font-bold text-white">System Notifications</span>
                </div>
                <span className="text-[10px] font-mono font-semibold text-cyan-400 bg-cyan-500/15 border border-cyan-500/30 px-2 py-0.5 rounded-full">
                  {unreadCount} Unread
                </span>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                <div className="p-2.5 bg-navy-900/90 rounded-xl border border-navy-700/50 flex items-start gap-2.5 text-xs hover:border-emerald-500/30 transition">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">Proposal Approved</div>
                    <div className="text-[11px] text-slate-400 leading-tight">Formal sign-off completed for JADC2 Cloud Integration</div>
                    <div className="text-[10px] text-slate-500 mt-1 font-mono">2h ago</div>
                  </div>
                </div>
                <div className="p-2.5 bg-navy-900/90 rounded-xl border border-navy-700/50 flex items-start gap-2.5 text-xs hover:border-amber-500/30 transition">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">Addendum Published</div>
                    <div className="text-[11px] text-slate-400 leading-tight">TND-2026-0410 updated with 2 clarification docs</div>
                    <div className="text-[10px] text-slate-500 mt-1 font-mono">4h ago</div>
                  </div>
                </div>
                <div className="p-2.5 bg-navy-900/90 rounded-xl border border-navy-700/50 flex items-start gap-2.5 text-xs hover:border-cyan-500/30 transition">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">ProofLink Synchronized</div>
                    <div className="text-[11px] text-slate-400 leading-tight">Evidence vault indexed 8 new past performance assets</div>
                    <div className="text-[10px] text-slate-500 mt-1 font-mono">6h ago</div>
                  </div>
                </div>
              </div>
              <div className="pt-2.5 border-t border-navy-700/80 mt-2.5 text-center">
                <button
                  onClick={() => {
                    setNotificationsOpen(false);
                    if (onOpenNotifications) onOpenNotifications();
                  }}
                  className="text-[11px] text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center gap-1 transition"
                >
                  View All Deadlines & Alerts →
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Authenticated User Profile */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1 rounded-full hover:bg-navy-800/90 border border-transparent hover:border-navy-700/70 transition active:scale-95"
          >
            {/* Initials Avatar Badge */}
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 border border-cyan-400/40 flex items-center justify-center text-white text-xs font-bold tracking-wider shadow-md">
              {initials}
            </div>

            {/* User Name & Role */}
            <div className="hidden lg:block text-left pr-1">
              <div className="text-xs font-bold text-white leading-tight">
                {user.full_name || 'Enterprise User'}
              </div>
              <div className="text-[10px] text-slate-400 leading-tight">
                {user.role || 'Bid Manager'}
              </div>
            </div>

            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden lg:block" />
          </button>

          {/* Profile Dropdown */}
          {profileOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-navy-850/95 backdrop-blur-xl border border-navy-700 rounded-2xl shadow-dropdown p-3.5 z-50 animate-fade-in">
              <div className="pb-3 border-b border-navy-700/80 mb-2.5">
                <div className="font-bold text-sm text-white">{user.full_name}</div>
                <div className="text-xs text-cyan-400 font-mono truncate">{user.email}</div>
                <div className="text-[11px] text-slate-300 mt-2 flex items-center gap-1.5 bg-navy-900/80 px-2 py-1 rounded-lg border border-navy-700/60">
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Role: <span className="text-emerald-400 font-semibold">{user.role}</span>
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
                    className="w-full bg-navy-950 border border-navy-700/80 hover:border-cyan-500/50 rounded-lg text-xs text-white p-2 focus:outline-none focus:border-cyan-500 transition"
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
                className="w-full flex items-center gap-2 p-2 rounded-xl text-xs font-semibold text-rose-300 hover:text-rose-200 hover:bg-rose-950/40 border border-transparent hover:border-rose-800/40 transition"
              >
                <LogOut className="w-3.5 h-3.5 text-rose-400" />
                Sign Out of Workspace
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

