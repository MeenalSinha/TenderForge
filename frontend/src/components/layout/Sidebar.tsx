import React, { useState } from 'react';
import {
  LayoutDashboard,
  Briefcase,
  Compass,
  FileSearch,
  CheckSquare,
  Crosshair,
  ShieldAlert,
  Library,
  Link2,
  FileText,
  DollarSign,
  Scale,
  AlertTriangle,
  FileCheck,
  PackageCheck,
  Zap,
  Bot,
  History,
  Share2,
  Activity,
  FileDiff,
  TrendingUp,
  Award,
  GraduationCap,
  BookOpen,
  Bell,
  BarChart3,
  Building,
  Users,
  Settings,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { BrandLogo } from '../common/BrandLogo';

export interface NavGroup {
  id: string;
  label: string;
  items: {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }[];
}

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tabId: string) => void;
  switchStatus: {
    status?: string;
    message?: string;
    mesh_connected?: boolean;
    internal_broker_active?: boolean;
    agents_registered?: number;
    tools_registered?: number;
  };
  organizationName?: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const NAV_GROUPS: NavGroup[] = [
  {
    id: 'overview',
    label: 'Overview',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'portfolio', label: 'Tender Portfolio', icon: Briefcase },
      { id: 'opportunities', label: 'Opportunity Discovery', icon: Compass },
    ],
  },
  {
    id: 'tender_intelligence',
    label: 'Tender Intelligence',
    items: [
      { id: 'intelligence', label: 'Tender Analysis', icon: FileSearch },
      { id: 'requirements', label: 'Requirements & Criteria', icon: CheckSquare },
      { id: 'bid_decision', label: 'Bid Strategy (Bid/No-Bid)', icon: Crosshair },
      { id: 'compliance', label: 'Compliance Center', icon: ShieldAlert },
    ],
  },
  {
    id: 'evidence_proposals',
    label: 'Evidence & Proposals',
    items: [
      { id: 'evidence', label: 'Evidence Library', icon: Library },
      { id: 'prooflink', label: 'ProofLink Traceability', icon: Link2 },
      { id: 'proposal', label: 'Proposal Studio', icon: FileText },
      { id: 'financial', label: 'Financial BOQ Workspace', icon: DollarSign },
      { id: 'bid_audit', label: 'Independent Bid Audit', icon: Scale },
      { id: 'risks', label: 'Risk Management', icon: AlertTriangle },
      { id: 'human_approval', label: 'Human Approval Gate', icon: FileCheck },
      { id: 'deliverables', label: 'Final Deliverables', icon: PackageCheck },
    ],
  },
  {
    id: 'collaboration',
    label: 'Collaboration',
    items: [
      { id: 'war_room', label: 'Switch War Room', icon: Zap },
      { id: 'agent_activity', label: 'AI Agent Activity', icon: Bot },
      { id: 'workflow_history', label: 'Workflow & History', icon: History },
    ],
  },
  {
    id: 'procurement_intelligence',
    label: 'Procurement Intelligence',
    items: [
      { id: 'sources', label: 'Procurement Connectors', icon: Share2 },
      { id: 'monitoring', label: 'Tender Monitoring', icon: Activity },
      { id: 'amendments', label: 'Amendment Intelligence', icon: FileDiff },
      { id: 'market', label: 'Market Intelligence', icon: TrendingUp },
      { id: 'competitors', label: 'Competitor Benchmarks', icon: Award },
      { id: 'bid_learning', label: 'Closed-Loop Learning', icon: GraduationCap },
      { id: 'knowledge', label: 'Knowledge Library', icon: BookOpen },
    ],
  },
  {
    id: 'management',
    label: 'Management',
    items: [
      { id: 'deadlines', label: 'Deadlines & Alerts', icon: Bell },
      { id: 'analytics', label: 'Analytics & Reports', icon: BarChart3 },
      { id: 'org_profile', label: 'Organization Profile', icon: Building },
      { id: 'team', label: 'Team & Permissions', icon: Users },
      { id: 'settings', label: 'Settings', icon: Settings },
    ],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  switchStatus,
  organizationName = 'Apex Global Defense',
  collapsed = false,
  mobileOpen = false,
  onCloseMobile,
}) => {
  // Track expanded groups (all open by default for effortless discoverability)
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    overview: true,
    tender_intelligence: true,
    evidence_proposals: true,
    collaboration: true,
    procurement_intelligence: true,
    management: true,
  });

  const toggleGroup = (groupId: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [groupId]: !prev[groupId],
    }));
  };

  const handleItemClick = (itemId: string) => {
    onSelectTab(itemId);
    if (onCloseMobile) {
      onCloseMobile();
    }
  };

  // Determine true Switch connection status
  const isSwitchOnline = switchStatus.status === 'connected' || switchStatus.mesh_connected;
  const isBrokerActive = switchStatus.internal_broker_active || switchStatus.status === 'connected';

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden transition-opacity"
        />
      )}

      <aside
        className={`bg-navy-900 border-r border-navy-700/60 flex flex-col justify-between shrink-0 transition-all duration-300 z-50 select-none ${
          collapsed ? 'w-20' : 'w-64 lg:w-72'
        } ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } fixed lg:static inset-y-0 left-0 shadow-2xl lg:shadow-none`}
      >
        {/* Top Brand Header */}
        <div>
          <div className="h-16 px-5 border-b border-navy-700/60 flex items-center justify-between">
            <BrandLogo collapsed={collapsed} />
          </div>

          {/* Scrollable Navigation Area */}
          <div className="p-3 space-y-4 overflow-y-auto max-h-[calc(100vh-190px)] text-xs">
            {NAV_GROUPS.map((group) => {
              const isExpanded = expandedGroups[group.id] !== false;
              const hasActiveChild = group.items.some((i) => i.id === activeTab);

              return (
                <div key={group.id} className="space-y-1">
                  {/* Group Heading with Collapsible Toggle */}
                  {!collapsed && (
                    <button
                      onClick={() => toggleGroup(group.id)}
                      className="w-full flex items-center justify-between px-2.5 py-1 text-[11px] font-semibold text-slate-400 hover:text-slate-200 uppercase tracking-wider transition group"
                    >
                      <span className={hasActiveChild ? 'text-cyan-400 font-bold' : ''}>{group.label}</span>
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300 transition-transform" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300 transition-transform" />
                      )}
                    </button>
                  )}

                  {/* Group Navigation Items */}
                  {(isExpanded || collapsed) && (
                    <div className="space-y-0.5">
                      {group.items.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeTab === item.id;

                        return (
                          <button
                            key={item.id}
                            onClick={() => handleItemClick(item.id)}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs transition duration-150 text-left relative ${
                              isActive
                                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold shadow-md shadow-blue-900/40 border border-blue-400/30'
                                : 'text-slate-400 hover:text-slate-100 hover:bg-navy-800/80 border border-transparent'
                            }`}
                            title={collapsed ? item.label : undefined}
                          >
                            <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                            {!collapsed && (
                              <span className="truncate flex-1">{item.label}</span>
                            )}
                            {!collapsed && !isActive && (
                              <ChevronRight className="w-3 h-3 text-slate-600 opacity-0 group-hover:opacity-100" />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom Fixed Panels: Switch Status Card & Organization Card (Reference Design) */}
        <div className="p-3 border-t border-navy-700/60 space-y-2 bg-navy-900/95 shrink-0">
          {/* Switch War Room Quick Launcher Card */}
          <button
            onClick={() => handleItemClick('war_room')}
            className={`w-full p-2.5 rounded-xl border transition text-left flex items-center justify-between group ${
              activeTab === 'war_room'
                ? 'bg-navy-800 border-cyan-500/50 shadow-sm'
                : 'bg-navy-950/80 hover:bg-navy-800/80 border-navy-700/60'
            }`}
          >
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="relative shrink-0">
                <span
                  className={`w-2.5 h-2.5 rounded-full inline-block ${
                    isSwitchOnline
                      ? 'bg-emerald-400 shadow-glow-emerald animate-pulse-slow'
                      : isBrokerActive
                      ? 'bg-cyan-400 shadow-glow-cyan'
                      : 'bg-amber-400'
                  }`}
                />
              </div>
              {!collapsed && (
                <div className="overflow-hidden">
                  <div className="font-semibold text-xs text-white truncate">
                    Switch War Room
                  </div>
                  <div className="text-[10px] text-emerald-400 font-mono truncate">
                    {isSwitchOnline
                      ? 'Connected (Mesh)'
                      : isBrokerActive
                      ? 'Local Broker Active'
                      : 'Offline'}
                  </div>
                </div>
              )}
            </div>
            {!collapsed && (
              <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition group-hover:translate-x-0.5" />
            )}
          </button>

          {/* Organization Card (e.g., Acme Enterprises / Apex Global Defense) */}
          <button
            onClick={() => handleItemClick('org_profile')}
            className={`w-full p-2.5 rounded-xl border transition text-left flex items-center justify-between group ${
              activeTab === 'org_profile'
                ? 'bg-navy-800 border-blue-500/50 shadow-sm'
                : 'bg-navy-950/80 hover:bg-navy-800/80 border-navy-700/60'
            }`}
          >
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-7 h-7 rounded-lg bg-navy-850 border border-navy-700/80 flex items-center justify-center shrink-0 text-cyan-400 group-hover:border-cyan-500/40 transition">
                <Building className="w-3.5 h-3.5" />
              </div>
              {!collapsed && (
                <div className="overflow-hidden">
                  <div className="font-semibold text-xs text-white truncate">
                    {organizationName}
                  </div>
                  <div className="text-[10px] text-slate-400 font-sans truncate">
                    Enterprise Workspace
                  </div>
                </div>
              )}
            </div>
            {!collapsed && (
              <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition group-hover:translate-x-0.5" />
            )}
          </button>
        </div>
      </aside>
    </>
  );
};

