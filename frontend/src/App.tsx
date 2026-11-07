import React, { useState, useEffect } from 'react';
import { apiRequest } from './api/client';
import { User, Tender, Requirement, ComplianceItem, Organization } from './types';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { BrandLogo } from './components/common/BrandLogo';

// Views
import { DashboardView } from './components/views/DashboardView';
import { PortfolioView } from './components/views/PortfolioView';
import { OpportunitiesView } from './components/views/OpportunitiesView';
import { IntelligenceView } from './components/views/IntelligenceView';
import { RequirementsView } from './components/views/RequirementsView';
import { BidStrategyView } from './components/views/BidStrategyView';
import { ComplianceView } from './components/views/ComplianceView';
import { EvidenceLibraryView } from './components/views/EvidenceLibraryView';
import { ProofLinkView } from './components/views/ProofLinkView';
import { ProposalStudioView } from './components/views/ProposalStudioView';
import { FinancialBOQView } from './components/views/FinancialBOQView';
import { BidAuditView } from './components/views/BidAuditView';
import { RisksView } from './components/views/RisksView';
import { HumanApprovalView } from './components/views/HumanApprovalView';
import { DeliverablesView } from './components/views/DeliverablesView';
import { SwitchWarRoomView } from './components/views/SwitchWarRoomView';
import { AgentActivityView } from './components/views/AgentActivityView';
import { WorkflowHistoryView } from './components/views/WorkflowHistoryView';
import { ProcurementSourcesView } from './components/views/ProcurementSourcesView';
import { TenderMonitoringView } from './components/views/TenderMonitoringView';
import { AmendmentsView } from './components/views/AmendmentsView';
import { MarketIntelligenceView } from './components/views/MarketIntelligenceView';
import { CompetitorBenchmarksView } from './components/views/CompetitorBenchmarksView';
import { BidLearningView } from './components/views/BidLearningView';
import { KnowledgeLibraryView } from './components/views/KnowledgeLibraryView';
import { DeadlinesView } from './components/views/DeadlinesView';
import { AnalyticsView } from './components/views/AnalyticsView';
import { OrgProfileView } from './components/views/OrgProfileView';
import { TeamPermissionsView } from './components/views/TeamPermissionsView';
import { SettingsView } from './components/views/SettingsView';

import {
  Lock,
  Mail,
  UserCheck,
  AlertCircle,
  CheckCircle2,
  Building,
  Shield
} from 'lucide-react';

export default function App() {
  // Authentication State
  const [user, setUser] = useState<User | null>(null);
  const [, setToken] = useState<string>(localStorage.getItem('tf_token') || '');
  const [authLoading, setAuthLoading] = useState(true);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authError, setAuthError] = useState<string | null>(null);

  // Form Fields
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState<'Viewer' | 'Author' | 'Reviewer' | 'Approver' | 'Admin'>('Author');
  const [regOrg, setRegOrg] = useState('Apex Global Defense');

  // Switch Subsystem Status
  const [switchStatus, setSwitchStatus] = useState<any>({
    status: 'connected',
    message: 'Switch Local Broker Active',
    mesh_connected: false,
    internal_broker_active: true,
    agents_registered: 5,
    tools_registered: 31,
  });

  // Navigation & Workspace State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Primary Data State
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [activeTenderId, setActiveTenderId] = useState<string | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>([]);

  // Enterprise Procurement State
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [marketTrends, setMarketTrends] = useState<any>(null);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [bidLearning, setBidLearning] = useState<any>(null);
  const [knowledgeAssets, setKnowledgeAssets] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null);

  // Toast System
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  useEffect(() => {
    checkSession();
    checkSwitchHealth();
  }, []);

  useEffect(() => {
    if (user) {
      loadTenders();
      loadProcurementData();
    }
  }, [user]);

  useEffect(() => {
    if (activeTenderId) {
      loadTenderDetails(activeTenderId);
    }
  }, [activeTenderId]);

  async function checkSession() {
    const storedToken = localStorage.getItem('tf_token');
    if (!storedToken) {
      setUser(null);
      setAuthLoading(false);
      return;
    }
    try {
      const res = await apiRequest<User>('/auth/me');
      if (res.success && res.data) {
        setUser(res.data);
      } else {
        localStorage.removeItem('tf_token');
        setToken('');
        setUser(null);
      }
    } catch {
      localStorage.removeItem('tf_token');
      setToken('');
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  }

  async function checkSwitchHealth() {
    try {
      const res = (await apiRequest<any>('/switch/status')) as any;
      if (res && res.status) {
        setSwitchStatus(res);
      }
    } catch {
      setSwitchStatus({
        status: 'disconnected',
        message: 'Switch offline',
        internal_broker_active: true,
      });
    }
  }

  async function handleLogin(email?: string, password?: string) {
    setAuthLoading(true);
    setAuthError(null);
    const e = email || loginEmail;
    const p = password || loginPassword;
    try {
      const res = await apiRequest<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: e, password: p }),
      });
      if (res.success && res.data && res.data.access_token) {
        localStorage.setItem('tf_token', res.data.access_token);
        setToken(res.data.access_token);
        setUser(res.data.user);
        showToast(`Welcome back, ${res.data.user.full_name}!`);
      } else {
        setAuthError(res.message || 'Authentication failed. Please verify credentials.');
      }
    } catch (err: any) {
      setAuthError(err.message || 'Login failed.');
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleRegister() {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await apiRequest<any>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: regEmail,
          password: regPassword,
          full_name: regFullName,
          role: regRole,
          organization_name: regOrg,
        }),
      });
      if (res.success && res.data && res.data.access_token) {
        localStorage.setItem('tf_token', res.data.access_token);
        setToken(res.data.access_token);
        setUser(res.data.user);
        showToast(`Account registered for ${res.data.user.full_name}!`);
      } else {
        setAuthError(res.message || 'Registration failed.');
      }
    } catch (err: any) {
      setAuthError(err.message || 'Registration failed.');
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch {}
    localStorage.removeItem('tf_token');
    setToken('');
    setUser(null);
    showToast('Signed out of TenderForge.');
  }

  async function loadTenders() {
    const res = await apiRequest<any>('/tenders');
    if (res.success && res.data) {
      const items = res.data.items || [];
      setTenders(items);
      if (items.length > 0 && !activeTenderId) {
        const preferred =
          items.find((t: any) => t.title && t.title.includes('Joint Multi-Domain')) ||
          items[0];
        setActiveTenderId(preferred.id);
      }
    }
  }

  async function loadTenderDetails(tenderId: string) {
    try {
      const [reqRes, compRes] = await Promise.all([
        apiRequest<any>(`/tenders/${tenderId}/analysis`),
        apiRequest<any>(`/tenders/${tenderId}/compliance`),
      ]);

      if (reqRes.success && reqRes.data) {
        const groups = reqRes.data;
        const allReqs: Requirement[] = [];
        Object.keys(groups).forEach((cat) => {
          if (Array.isArray(groups[cat])) {
            allReqs.push(...groups[cat]);
          }
        });
        if (allReqs.length > 0) setRequirements(allReqs);
      }

      if (compRes.success && compRes.data && compRes.data.items) {
        setComplianceItems(compRes.data.items);
      }
    } catch (e) {
      console.error('Error loading tender details', e);
    }
  }

  async function loadProcurementData() {
    try {
      const [oppRes, recRes, srcRes, mktRes, compRes, learnRes, knRes, orgRes] = await Promise.all([
        apiRequest<any>('/opportunities'),
        apiRequest<any>('/opportunities/recommendations'),
        apiRequest<any>('/sources'),
        apiRequest<any>('/market/trends'),
        apiRequest<any>('/market/competitors'),
        apiRequest<any>('/analytics/bid-learning'),
        apiRequest<any>('/knowledge/assets'),
        apiRequest<any>('/organizations'),
      ]);

      if (oppRes.success && oppRes.data) setOpportunities(oppRes.data.opportunities || []);
      if (recRes.success && recRes.data) setRecommendations(recRes.data.recommendations || []);
      if (srcRes.success && srcRes.data) setSources(srcRes.data.sources || []);
      if (mktRes.success && mktRes.data) setMarketTrends(mktRes.data);
      if (compRes.success && compRes.data) setCompetitors(compRes.data.competitors || []);
      if (learnRes.success && learnRes.data) setBidLearning(learnRes.data);
      if (knRes.success && knRes.data) setKnowledgeAssets(knRes.data.assets || []);
      if (orgRes.success && orgRes.data) {
        const orgList = orgRes.data.organizations || orgRes.data || [];
        setOrganizations(orgList);
        if (orgList.length > 0 && !selectedOrgId) {
          setSelectedOrgId(orgList[0].id);
        }
      }
    } catch (e) {
      console.error('Procurement data load error', e);
    }
  }

  async function handleSendWarRoomCommand(cmd: string) {
    if (!activeTenderId) return null;
    const res = await apiRequest<any>(`/switch/rooms/${activeTenderId}/command`, {
      method: 'POST',
      body: JSON.stringify({
        command_line: cmd,
        user_id: user?.id || 'admin_user',
        user_role: user?.role || 'Bid Director',
      }),
    });
    return res.data || res;
  }

  // 1. Loading State
  if (authLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-navy-950 text-white font-sans">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-mono">
            Verifying TenderForge Cryptographic Session...
          </p>
        </div>
      </div>
    );
  }

  // 2. Unauthenticated Login / Register Canvas (NO EMOJIS)
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy-950 p-6 text-slate-100 font-sans">
        <div className="w-full max-w-md bg-navy-900 border border-navy-700/80 rounded-2xl p-8 shadow-2xl space-y-6">
          <div className="flex flex-col items-center text-center space-y-3">
            <BrandLogo />
            <p className="text-xs text-slate-400 max-w-xs">
              Enterprise Bid Intelligence & Trustworthy Proposal Preparation Platform
            </p>
          </div>

          {authError && (
            <div className="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          <div className="flex border-b border-navy-700 text-xs">
            <button
              onClick={() => setAuthMode('login')}
              className={`flex-1 py-2.5 font-medium border-b-2 transition ${
                authMode === 'login'
                  ? 'border-cyan-400 text-white font-bold'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setAuthMode('register')}
              className={`flex-1 py-2.5 font-medium border-b-2 transition ${
                authMode === 'register'
                  ? 'border-cyan-400 text-white font-bold'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Register Organization
            </button>
          </div>

          {authMode === 'login' ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleLogin();
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Work Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="email"
                    required
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                    placeholder="user@organization.com"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                    placeholder="••••••••••••"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl transition shadow-lg shadow-blue-950 flex items-center justify-center gap-1.5"
              >
                Authenticate Session
              </button>
            </form>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleRegister();
              }}
              className="space-y-3"
            >
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  className="w-full px-3 py-1.5 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white"
                  placeholder="Elena Vance"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Work Email</label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full px-3 py-1.5 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white font-mono"
                  placeholder="elena@defense.com"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full px-3 py-1.5 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white font-mono"
                  placeholder="••••••••••••"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Role</label>
                  <select
                    value={regRole}
                    onChange={(e: any) => setRegRole(e.target.value)}
                    className="w-full px-2 py-1.5 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white"
                  >
                    <option value="Author">Author</option>
                    <option value="Reviewer">Reviewer</option>
                    <option value="Approver">Approver</option>
                    <option value="Admin">Admin</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Organization</label>
                  <input
                    type="text"
                    required
                    value={regOrg}
                    onChange={(e) => setRegOrg(e.target.value)}
                    className="w-full px-3 py-1.5 bg-navy-950 border border-navy-700 rounded-xl text-xs text-white"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl transition mt-2 shadow-lg shadow-blue-950"
              >
                Register Account
              </button>
            </form>
          )}

          <div className="pt-4 border-t border-navy-700/80">
            <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-2 font-mono">
              Verified Enterprise Demo Profiles:
            </p>
            <div className="space-y-1.5">
              <button
                onClick={() => handleLogin('admin@tenderforge.com', 'TenderForgeAdmin2026!')}
                className="w-full text-left px-3 py-2 bg-navy-950 hover:bg-navy-800 border border-navy-700/80 rounded-xl text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-cyan-400">Administrator</span>
                <span className="text-slate-400 font-mono text-[11px]">admin@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('author@tenderforge.com', 'TenderForgeAuthor2026!')}
                className="w-full text-left px-3 py-2 bg-navy-950 hover:bg-navy-800 border border-navy-700/80 rounded-xl text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-blue-400">Proposal Architect</span>
                <span className="text-slate-400 font-mono text-[11px]">author@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('reviewer@tenderforge.com', 'TenderForgeReviewer2026!')}
                className="w-full text-left px-3 py-2 bg-navy-950 hover:bg-navy-800 border border-navy-700/80 rounded-xl text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-purple-400">Compliance Auditor</span>
                <span className="text-slate-400 font-mono text-[11px]">reviewer@tenderforge.com</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const activeTender = tenders.find((t) => t.id === activeTenderId) || tenders[0];

  return (
    <div className="min-h-screen flex bg-navy-950 text-slate-100 font-sans">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded-xl text-xs font-medium shadow-2xl flex items-center gap-2 border animate-fade-in ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-700 text-emerald-200'
              : 'bg-rose-950/90 border-rose-700 text-rose-200'
          }`}
        >
          {toast.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{toast.message}</span>
        </div>
      )}

      {/* 1. Left Collapsible Sidebar (Grouped A-F with Brand Logo & Bottom Cards) */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          setMobileMenuOpen(false);
        }}
        switchStatus={switchStatus}
        organizationName={organizations[0]?.name || 'Apex Global Defense'}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        mobileOpen={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      {/* 2. Main Content Canvas */}
      <div className="flex-1 flex flex-col overflow-hidden bg-navy-950">
        {/* Top Header Bar (Active pursuit selector, est value badge, search, notifications, profile) */}
        <Header
          user={user}
          tenders={tenders}
          activeTenderId={activeTenderId}
          onSelectTender={setActiveTenderId}
          organizations={organizations}
          selectedOrgId={selectedOrgId}
          onSelectOrg={setSelectedOrgId}
          onLogout={handleLogout}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onOpenNotifications={() => setActiveTab('deadlines')}
          onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
          mobileMenuOpen={mobileMenuOpen}
        />

        {/* Dynamic View Canvas */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-navy-950">
          {/* GROUP A: OVERVIEW */}
          {activeTab === 'dashboard' && (
            <DashboardView
              user={user}
              tenders={tenders}
              opportunities={opportunities}
              recommendations={recommendations}
              switchStatus={switchStatus}
              marketTrends={marketTrends}
              bidLearning={bidLearning}
              onSelectTender={setActiveTenderId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'portfolio' && (
            <PortfolioView
              tenders={tenders}
              activeTenderId={activeTenderId}
              onSelectTender={setActiveTenderId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'opportunities' && (
            <OpportunitiesView
              opportunities={opportunities}
              onPromoteOpportunity={(opp) => {
                showToast(`Opportunity ${opp.external_id || opp.title} promoted to pursuit.`);
              }}
              onNavigateTab={setActiveTab}
            />
          )}

          {/* GROUP B: TENDER INTELLIGENCE */}
          {activeTab === 'intelligence' && (
            <IntelligenceView
              activeTender={activeTender}
              requirements={requirements}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'requirements' && (
            <RequirementsView
              activeTender={activeTender}
              requirements={requirements}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'bid_decision' && (
            <BidStrategyView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'compliance' && (
            <ComplianceView
              activeTender={activeTender}
              complianceItems={complianceItems}
              onNavigateTab={setActiveTab}
            />
          )}

          {/* GROUP C: EVIDENCE & PROPOSALS */}
          {activeTab === 'evidence' && (
            <EvidenceLibraryView />
          )}

          {activeTab === 'prooflink' && (
            <ProofLinkView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'proposal' && (
            <ProposalStudioView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'financial' && (
            <FinancialBOQView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'bid_audit' && (
            <BidAuditView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'risks' && (
            <RisksView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'human_approval' && (
            <HumanApprovalView
              user={user}
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'deliverables' && (
            <DeliverablesView
              activeTender={activeTender}
            />
          )}

          {/* GROUP D: COLLABORATION */}
          {activeTab === 'war_room' && (
            <SwitchWarRoomView
              user={user}
              activeTender={activeTender}
              switchStatus={switchStatus}
              onSendCommand={handleSendWarRoomCommand}
            />
          )}

          {activeTab === 'agent_activity' && (
            <AgentActivityView
              switchStatus={switchStatus}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'workflow_history' && (
            <WorkflowHistoryView
              activeTender={activeTender}
            />
          )}

          {/* GROUP E: PROCUREMENT INTELLIGENCE */}
          {activeTab === 'sources' && (
            <ProcurementSourcesView
              sources={sources}
            />
          )}

          {activeTab === 'monitoring' && (
            <TenderMonitoringView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'amendments' && (
            <AmendmentsView
              activeTender={activeTender}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'market' && (
            <MarketIntelligenceView
              marketTrends={marketTrends}
            />
          )}

          {activeTab === 'competitors' && (
            <CompetitorBenchmarksView
              competitors={competitors}
            />
          )}

          {activeTab === 'bid_learning' && (
            <BidLearningView
              bidLearning={bidLearning}
            />
          )}

          {activeTab === 'knowledge' && (
            <KnowledgeLibraryView
              knowledgeAssets={knowledgeAssets}
            />
          )}

          {/* GROUP F: MANAGEMENT */}
          {activeTab === 'deadlines' && (
            <DeadlinesView
              tenders={tenders}
              onSelectTender={setActiveTenderId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsView />
          )}

          {activeTab === 'org_profile' && (
            <OrgProfileView
              user={user}
              organizations={organizations}
            />
          )}

          {activeTab === 'team' && (
            <TeamPermissionsView
              currentUser={user}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              switchStatus={switchStatus}
            />
          )}
        </main>
      </div>
    </div>
  );
}
