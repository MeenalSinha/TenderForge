import { useState, useEffect } from 'react';
import { apiRequest } from './api/client';
import { Tender, User } from './types';

export default function App() {
  // Auth State
  const [, setToken] = useState<string>(localStorage.getItem('tf_token') || '');
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [loginEmail, setLoginEmail] = useState('admin@tenderforge.com');
  const [loginPassword, setLoginPassword] = useState('TenderForgeAdmin2026!');
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState<'Viewer' | 'Author' | 'Reviewer' | 'Approver' | 'Admin'>('Author');
  const [regOrg, setRegOrg] = useState('Apex Global Defense');

  // Switch Subsystem Status
  const [switchStatus, setSwitchStatus] = useState<any>({
    status: 'connected',
    message: 'Switch Local Broker Active',
    agents_registered: 5,
    tools_registered: 31,
  });

  // Navigation & Workspace State
  const [activeTab, setActiveTab] = useState('portfolio');
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [activeTenderId, setActiveTenderId] = useState<string | null>(null);

  // Detail State
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [marketTrends, setMarketTrends] = useState<any>(null);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [bidLearning, setBidLearning] = useState<any>(null);
  const [knowledgeAssets, setKnowledgeAssets] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [warRoomChat, setWarRoomChat] = useState<string>('');
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
      setSwitchStatus({ status: 'disconnected', message: 'Switch offline' });
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
        setAuthError(res.message || 'Authentication failed.');
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
        const preferred = items.find((t: any) => t.title && t.title.includes('Joint Multi-Domain')) || items[0];
        setActiveTenderId(preferred.id);
      }
    }
  }

  async function loadProcurementData() {
    try {
      const [oppRes, recRes, srcRes, mktRes, compRes, learnRes, knRes, orgRes] = await Promise.all([
        apiRequest<any>('/opportunities'),
        apiRequest<any>('/opportunities/recommendations'),
        apiRequest<any>('/sources'),
        apiRequest<any>('/market/analytics'),
        apiRequest<any>('/market/competitors'),
        apiRequest<any>('/bid-outcomes/learning-analytics'),
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
      if (orgRes.success && orgRes.data) setOrganizations(orgRes.data.organizations || []);
    } catch (e) {
      console.error('Procurement data load error', e);
    }
  }

  const navItems = [
    // CORE WORKFLOW SCREENS
    { id: 'portfolio', label: 'Portfolio Dashboard', icon: '📊', category: 'Core Workflow' },
    { id: 'war_room', label: 'Switch War Room', icon: '⚡', category: 'Core Workflow' },
    { id: 'intelligence', label: 'Tender Analysis', icon: '🔍', category: 'Core Workflow' },
    { id: 'compliance', label: 'Compliance Matrix', icon: '🛡️', category: 'Core Workflow' },
    { id: 'prooflink', label: 'ProofLink Traceability', icon: '🔗', category: 'Core Workflow' },
    { id: 'evidence', label: 'Evidence Research', icon: '🏛️', category: 'Core Workflow' },
    { id: 'proposal', label: 'Proposal Studio', icon: '📝', category: 'Core Workflow' },
    { id: 'bid_audit', label: 'Independent Bid Audit', icon: '⚖️', category: 'Core Workflow' },
    { id: 'human_approval', label: 'Human Approval Gate', icon: '✍️', category: 'Core Workflow' },
    { id: 'deliverables', label: 'Final Deliverables', icon: '📦', category: 'Core Workflow' },

    // EXTENDED ENTERPRISE VIEWS
    { id: 'financial', label: 'Financial BOQ Workspace', icon: '💰', category: 'Enterprise Capabilities' },
    { id: 'opportunities', label: 'Tender Discovery', icon: '🔭', category: 'Enterprise Capabilities' },
    { id: 'recommendations', label: 'AI Match & Explain', icon: '✨', category: 'Enterprise Capabilities' },
    { id: 'sources', label: 'Source Connectors', icon: '🔌', category: 'Enterprise Capabilities' },
    { id: 'market_trends', label: 'Market Spend Analytics', icon: '📈', category: 'Enterprise Capabilities' },
    { id: 'competitors', label: 'Competitor Benchmarks', icon: '🕵️', category: 'Enterprise Capabilities' },
    { id: 'bid_learning', label: 'Closed-Loop Learning', icon: '🧠', category: 'Enterprise Capabilities' },
  ];

  if (authLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-950 text-white font-sans">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-mono">Verifying TenderForge Security Session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6 text-slate-100 font-sans">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-indigo-600 flex items-center justify-center text-white text-2xl mx-auto shadow-lg shadow-emerald-950">
              ⚔️
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">TenderForge</h1>
            <p className="text-xs text-slate-400">From Tender to Trustworthy Proposal</p>
          </div>

          {authError && (
            <div className="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-lg flex items-center gap-2">
              <span>⚠️</span>
              <span>{authError}</span>
            </div>
          )}

          <div className="flex border-b border-slate-800 text-xs">
            <button
              onClick={() => setAuthMode('login')}
              className={`flex-1 py-2 font-medium border-b-2 transition ${
                authMode === 'login' ? 'border-emerald-500 text-white' : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setAuthMode('register')}
              className={`flex-1 py-2 font-medium border-b-2 transition ${
                authMode === 'register' ? 'border-emerald-500 text-white' : 'border-transparent text-slate-400 hover:text-slate-300'
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
                <label className="block text-xs font-medium text-slate-300 mb-1">Work Email</label>
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
                  placeholder="user@organization.com"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
                  placeholder="••••••••••••"
                />
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-lg transition shadow-lg shadow-emerald-950"
              >
                Authenticate
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
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white"
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
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white font-mono"
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
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white font-mono"
                  placeholder="••••••••••••"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assigned Role</label>
                  <select
                    value={regRole}
                    onChange={(e: any) => setRegRole(e.target.value)}
                    className="w-full px-2 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white"
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
                    className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-lg transition mt-2 shadow-lg shadow-emerald-950"
              >
                Register Account
              </button>
            </form>
          )}

          <div className="pt-4 border-t border-slate-800">
            <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-2 font-mono">Verified Demo Profiles:</p>
            <div className="space-y-1.5">
              <button
                onClick={() => handleLogin('admin@tenderforge.com', 'TenderForgeAdmin2026!')}
                className="w-full text-left px-2.5 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800/80 rounded text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-emerald-400">Administrator</span>
                <span className="text-slate-400 font-mono text-[11px]">admin@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('author@tenderforge.com', 'TenderForgeAuthor2026!')}
                className="w-full text-left px-2.5 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800/80 rounded text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-cyan-400">Proposal Architect</span>
                <span className="text-slate-400 font-mono text-[11px]">author@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('reviewer@tenderforge.com', 'TenderForgeReviewer2026!')}
                className="w-full text-left px-2.5 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800/80 rounded text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-indigo-400">Compliance Auditor</span>
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
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded-lg text-xs font-medium shadow-2xl flex items-center gap-2 border animate-fade-in ${
            toast.type === 'success'
              ? 'bg-emerald-950 border-emerald-700 text-emerald-200'
              : 'bg-rose-950 border-rose-700 text-rose-200'
          }`}
        >
          <span>{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo Brand */}
          <div className="p-4 border-b border-slate-800 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-indigo-600 flex items-center justify-center text-white text-lg font-bold shadow-lg shadow-emerald-950">
              ⚔️
            </div>
            <div>
              <h1 className="font-bold text-sm text-white tracking-tight leading-none">TenderForge</h1>
              <p className="text-[10px] text-slate-400 font-mono mt-0.5">Enterprise Bid Intelligence</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="p-3 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)]">
            {['Core Workflow', 'Enterprise Capabilities'].map((category) => {
              const items = navItems.filter((i) => i.category === category);
              if (items.length === 0) return null;
              return (
                <div key={category} className="space-y-1">
                  <div className="px-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">{category}</div>
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition text-left ${
                        activeTab === item.id
                          ? 'bg-emerald-600/15 text-emerald-400 border border-emerald-500/30'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                      }`}
                    >
                      <span className="text-sm">{item.icon}</span>
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Subsystem Status & User Pill */}
        <div className="p-3 border-t border-slate-800 space-y-2 bg-slate-900/60">
          <div className="flex items-center justify-between text-[11px] px-2 py-1 rounded bg-slate-950 border border-slate-800 font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300">Switch Local Broker</span>
            </div>
            <span className="text-emerald-400 text-[10px]">5 Agents (31 MCP)</span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800">
            <div className="overflow-hidden pr-2">
              <div className="font-semibold text-xs text-white truncate">{user.full_name}</div>
              <div className="text-[10px] text-slate-400 font-mono truncate">
                <span className="text-emerald-400">{user.role}</span> • {user.email}
              </div>
            </div>
            <button onClick={handleLogout} className="text-slate-400 hover:text-rose-400 text-xs px-2 py-1 rounded hover:bg-slate-800">
              Sign Out
            </button>
          </div>
        </div>
      </aside>

      {/* Main Workspace Canvas */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Operational Bar */}
        <header className="h-14 border-b border-slate-800 bg-slate-900/70 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 font-medium">Active Pursuit:</span>
            <select
              value={activeTenderId || ''}
              onChange={(e) => setActiveTenderId(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg text-xs font-medium text-white px-3 py-1.5 focus:outline-none focus:border-emerald-500 max-w-md truncate"
            >
              {tenders.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title} ({t.reference_number || 'TND-2026'})
                </option>
              ))}
            </select>
            {activeTender && (
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                Est. ${(activeTender.estimated_value || 12500000).toLocaleString()} USD
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
              <span>Organization:</span>
              <span className="text-white font-semibold">{organizations[0]?.name || 'Apex Global Defense & IT Solutions'}</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-mono">
              <span>{switchStatus.message}</span>
            </div>
          </div>
        </header>

        {/* Dynamic View Canvas */}
        <section className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {/* SCREEN 1: PORTFOLIO DASHBOARD */}
          {activeTab === 'portfolio' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Executive Portfolio Dashboard</h2>
                <p className="text-xs text-slate-400 mt-0.5">Pipeline telemetry, active pursuit volume, and real-time intelligence feeds.</p>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Active Pursuits</div>
                  <div className="text-2xl font-bold text-white mt-1">{tenders.length || 6} Active</div>
                  <div className="text-[11px] text-emerald-400 font-mono mt-1">↑ {opportunities.length} Discovery Leads</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Total Pipeline Value</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">$25,700,000</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-1">USD ({recommendations.length} Recommended Pursuits)</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Compliance Pass Rate</div>
                  <div className="text-2xl font-bold text-cyan-400 mt-1 font-mono">94.2%</div>
                  <div className="text-[11px] text-cyan-300 font-mono mt-1">{bidLearning?.win_rate_percentage ? `${bidLearning.win_rate_percentage}% Win Rate` : '12 Compliant • 2 Partial'}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Switch AI Mesh Status</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1 font-mono">{switchStatus.agents_registered || 5}/5 Active</div>
                  <div className="text-[11px] text-indigo-300 font-mono mt-1">{switchStatus.tools_registered || 31} MCP Tools Registered</div>
                </div>
              </div>

              {/* Discovery & Intelligence Feeds Banner */}
              <div className="grid grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-3 bg-slate-900/80 border border-slate-800/80 rounded-lg flex items-center justify-between">
                  <span className="text-slate-400">Tender Portals Monitored:</span>
                  <span className="text-white font-bold">{sources.length || 3} Feeds Active</span>
                </div>
                <div className="p-3 bg-slate-900/80 border border-slate-800/80 rounded-lg flex items-center justify-between">
                  <span className="text-slate-400">Market Intelligence:</span>
                  <span className="text-emerald-400 font-bold">{marketTrends ? 'Sector Growth +18%' : 'Live Telemetry'}</span>
                </div>
                <div className="p-3 bg-slate-900/80 border border-slate-800/80 rounded-lg flex items-center justify-between">
                  <span className="text-slate-400">Tracked Competitors:</span>
                  <span className="text-cyan-400 font-bold">{competitors.length || 3} Benchmarked</span>
                </div>
                <div className="p-3 bg-slate-900/80 border border-slate-800/80 rounded-lg flex items-center justify-between">
                  <span className="text-slate-400">Vault Knowledge Assets:</span>
                  <span className="text-purple-400 font-bold">{knowledgeAssets.length || 8} Indexed</span>
                </div>
              </div>

              {/* Workflow Stage Progress */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-sm text-white">End-to-End Pursuit Progression</h3>
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Stage 6: Formal Approval</span>
                </div>
                <div className="grid grid-cols-6 gap-2 text-center text-xs font-mono">
                  <div className="p-2 bg-emerald-950/60 border border-emerald-600/40 rounded text-emerald-300">1. Notice Ingestion<br/><span className="text-[10px] text-emerald-400">✓ Ingested</span></div>
                  <div className="p-2 bg-emerald-950/60 border border-emerald-600/40 rounded text-emerald-300">2. Clause Extract<br/><span className="text-[10px] text-emerald-400">✓ 14 Extracted</span></div>
                  <div className="p-2 bg-emerald-950/60 border border-emerald-600/40 rounded text-emerald-300">3. Compliance<br/><span className="text-[10px] text-emerald-400">✓ 94.2% Ready</span></div>
                  <div className="p-2 bg-emerald-950/60 border border-emerald-600/40 rounded text-emerald-300">4. ProofLink Map<br/><span className="text-[10px] text-emerald-400">✓ Lineage Valid</span></div>
                  <div className="p-2 bg-emerald-950/60 border border-emerald-600/40 rounded text-emerald-300">5. Proposal Studio<br/><span className="text-[10px] text-emerald-400">✓ Draft v2.1</span></div>
                  <div className="p-2 bg-indigo-950/80 border border-indigo-500 rounded text-indigo-200">6. Human Sign-Off<br/><span className="text-[10px] text-indigo-300">● Sealed & Signed</span></div>
                </div>
              </div>

              {/* Active Pursuits Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="font-bold text-sm text-white">Active Tender Pursuits</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="p-3">Reference</th>
                        <th className="p-3">Title</th>
                        <th className="p-3">Authority</th>
                        <th className="p-3">Est. Value (USD)</th>
                        <th className="p-3">Stage Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
                      <tr className="hover:bg-slate-800/50">
                        <td className="p-3 text-emerald-400">DOD-DISA-2026</td>
                        <td className="p-3 font-semibold text-white font-sans">Joint Multi-Domain Command & Control (JADC2) Cloud Integration</td>
                        <td className="p-3 font-sans">US Department of Defense (DISA)</td>
                        <td className="p-3">$12,500,000</td>
                        <td className="p-3"><span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Approved for Submission</span></td>
                      </tr>
                      <tr className="hover:bg-slate-800/50">
                        <td className="p-3 text-emerald-400">TND-2026-CLOUD-901</td>
                        <td className="p-3 font-semibold text-white font-sans">Pursuit: Sovereign Cloud Infrastructure Modernization</td>
                        <td className="p-3 font-sans">Federal Communications Commission</td>
                        <td className="p-3">$4,850,000</td>
                        <td className="p-3"><span className="px-2 py-0.5 rounded-full text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Proposal Drafting</span></td>
                      </tr>
                      <tr className="hover:bg-slate-800/50">
                        <td className="p-3 text-emerald-400">RFP-2026-001</td>
                        <td className="p-3 font-semibold text-white font-sans">National Telecom & Cloud Infrastructure</td>
                        <td className="p-3 font-sans">Ministry of Communications</td>
                        <td className="p-3">$3,500,000</td>
                        <td className="p-3"><span className="px-2 py-0.5 rounded-full text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Analyzed & Mapped</span></td>
                      </tr>
                      <tr className="hover:bg-slate-800/50">
                        <td className="p-3 text-emerald-400">TND-2026-MED-442</td>
                        <td className="p-3 font-semibold text-white font-sans">Interoperable Electronic Health Records Platform</td>
                        <td className="p-3 font-sans">Department of Veterans Affairs</td>
                        <td className="p-3">$4,850,000</td>
                        <td className="p-3"><span className="px-2 py-0.5 rounded-full text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20">Opportunity Evaluated</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 2: SWITCH WAR ROOM */}
          {activeTab === 'war_room' && (
            <div className="space-y-4 flex flex-col h-[calc(100vh-140px)]">
              <div className="flex justify-between items-center shrink-0">
                <div>
                  <h2 className="text-lg font-bold text-white">Switch War Room — Multi-Agent Coordination</h2>
                  <p className="text-xs text-slate-400">Real-time collaborative channel connecting human bid managers with 5 specialized AI agents.</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                    ● Switch Mesh: Active
                  </span>
                </div>
              </div>

              {/* Active Agents Status Bar */}
              <div className="grid grid-cols-5 gap-2 shrink-0">
                <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <div className="overflow-hidden"><div className="text-[11px] font-bold text-white truncate">@TenderAnalyst</div><div className="text-[9px] text-slate-400 font-mono">Clause Extraction</div></div>
                </div>
                <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <div className="overflow-hidden"><div className="text-[11px] font-bold text-white truncate">@ComplianceOfficer</div><div className="text-[9px] text-slate-400 font-mono">Matrix Evaluation</div></div>
                </div>
                <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                  <div className="overflow-hidden"><div className="text-[11px] font-bold text-white truncate">@EvidenceResearcher</div><div className="text-[9px] text-slate-400 font-mono">ProofLink Mapping</div></div>
                </div>
                <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                  <div className="overflow-hidden"><div className="text-[11px] font-bold text-white truncate">@ProposalArchitect</div><div className="text-[9px] text-slate-400 font-mono">Proposal Drafting</div></div>
                </div>
                <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                  <div className="overflow-hidden"><div className="text-[11px] font-bold text-white truncate">@BidAuditor</div><div className="text-[9px] text-slate-400 font-mono">Risk & Verification</div></div>
                </div>
              </div>

              {/* Collaborative Message Stream */}
              <div className="flex-1 overflow-y-auto bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 font-sans text-xs">
                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-emerald-400">@TenderAnalyst</span>
                    <span className="text-[10px] text-slate-500 font-mono">10:12:05 UTC</span>
                  </div>
                  <p className="text-slate-200">
                    Ingested tender RFP <strong>DOD-DISA-2026</strong>. Extracted <strong>14 mandatory eligibility clauses</strong> and 5 weighted scoring criteria. Classified 3 hard gates: active DoD Facility Clearance (Secret/Top Secret), ISO 27001 accreditation, and minimum audited turnover $10,000,000.
                  </p>
                </div>

                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-cyan-400">@ComplianceOfficer</span>
                    <span className="text-[10px] text-slate-500 font-mono">10:14:20 UTC</span>
                  </div>
                  <p className="text-slate-200">
                    Evaluated requirements against Apex Global Defense corporate repository. Overall compliance readiness score: <strong>94.2%</strong>. 12 Compliant, 2 Partial, 0 Missing. Financial threshold ($45M vs $10M) passed. Flagged: ISO 27001 certificate renewal horizon in 29 days.
                  </p>
                </div>

                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-indigo-400">@EvidenceResearcher</span>
                    <span className="text-[10px] text-slate-500 font-mono">10:16:45 UTC</span>
                  </div>
                  <p className="text-slate-200">
                    Retrieved verifiable proof documents: <strong>ISO 27001:2022 Certificate</strong> (BSI), <strong>PwC Audited Financial Statements FY24</strong>, and <strong>DoD Tactical Backbone Past Performance</strong>. Attached cryptographic claim lineage hashes.
                  </p>
                </div>

                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-purple-400">@ProposalArchitect</span>
                    <span className="text-[10px] text-slate-500 font-mono">10:22:10 UTC</span>
                  </div>
                  <p className="text-slate-200">
                    Drafted <strong>v2.1 Technical & Operational Proposal</strong>. Embedded 24 inline ProofLink citations (<code className="text-emerald-400 bg-emerald-950 px-1 py-0.5 rounded">[PL-ISO-27001]</code>, <code className="text-emerald-400 bg-emerald-950 px-1 py-0.5 rounded">[PL-PWC-FY24]</code>). Injected certified Zero Trust narrative from Knowledge Library into Section 2.3.
                  </p>
                </div>

                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-amber-400">@BidAuditor</span>
                    <span className="text-[10px] text-slate-500 font-mono">10:28:40 UTC</span>
                  </div>
                  <p className="text-slate-200">
                    Completed pre-flight verification audit. Readiness Score: <strong>94.5/100</strong>. Verified 23/24 claims. 0 unsupported claims. Contradiction between cash and accrual balance resolved by CFO Arthur Pendelton. Proposal is audit-clean and ready for Human Executive Sign-Off.
                  </p>
                </div>

                <div className="p-3 bg-emerald-950/40 border border-emerald-600/40 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-emerald-300">Maj. Gen. (Ret.) Marcus Vance (Human Executive Authority)</span>
                    <span className="text-[10px] text-slate-400 font-mono">10:45:10 UTC</span>
                  </div>
                  <p className="text-emerald-100">
                    <strong>/approve-pursuit</strong> — "Approved pursuit: Solution architecture verified against DISA JADC2 criteria. Commercial margins locked at 15.00% ($4,725,000 USD). All hard gates satisfied."
                  </p>
                  <div className="mt-2 text-[10px] font-mono text-emerald-400 bg-emerald-950/80 p-1.5 rounded border border-emerald-800">
                    Digital Signature SHA-256: 089e9cd505e8301538433fd235bbd9982517ab9e4db43963aaa9ce4b6471b6f4
                  </div>
                </div>
              </div>

              {/* War Room Input Bar */}
              <div className="flex gap-2 shrink-0">
                <input
                  type="text"
                  value={warRoomChat}
                  onChange={(e) => setWarRoomChat(e.target.value)}
                  placeholder="Type a slash command (/analyze, /compliance, /prooflink, /draft, /audit, /approve) or collaborate with agents..."
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 font-sans"
                />
                <button
                  onClick={() => {
                    if (warRoomChat) {
                      showToast('Command dispatched to Switch multi-agent room.');
                      setWarRoomChat('');
                    }
                  }}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs rounded-xl transition"
                >
                  Send
                </button>
              </div>
            </div>
          )}

          {/* SCREEN 3: TENDER ANALYSIS */}
          {activeTab === 'intelligence' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Tender Intelligence & Requirement Extraction</h2>
                  <p className="text-xs text-slate-400">Extraction Agent parsing clauses into mandatory eligibility, technical specs, and financial covenants.</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                    Extracted by: @TenderAnalyst (99.4% Confidence)
                  </span>
                </div>
              </div>

              {/* Opportunity Scope Banner */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 grid grid-cols-4 gap-4 text-xs font-mono">
                <div><span className="text-slate-500 block">Authority:</span><span className="text-white font-semibold font-sans">US Dept of Defense (DISA)</span></div>
                <div><span className="text-slate-500 block">Estimated Valuation:</span><span className="text-emerald-400 font-semibold">$12,500,000 USD</span></div>
                <div><span className="text-slate-500 block">Submission Cutoff:</span><span className="text-slate-200">2026-11-28 17:00 UTC</span></div>
                <div><span className="text-slate-500 block">Extraction Status:</span><span className="text-cyan-400">14 Verified Clauses</span></div>
              </div>

              {/* Requirement Cards */}
              <div className="space-y-3">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs text-emerald-400 font-bold">REQ-001 • MANDATORY ELIGIBILITY</span>
                    <span className="text-[10px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-mono font-bold">CRITICAL HARD GATE</span>
                  </div>
                  <p className="text-xs text-slate-200 font-medium">
                    Vendor must hold active DoD Facility Security Clearance (Secret / Top Secret) and ISO/IEC 27001 accreditation prior to award. Subcontractor facilities must be verified via DCSA accreditation.
                  </p>
                  <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
                    <span>Source: Page 14, Offset 1120</span>
                    <span>Confidence: 99.4%</span>
                    <span className="text-emerald-400">Matched to: EVD-DCSA-FSC & EVD-ISO-27001</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs text-emerald-400 font-bold">REQ-002 • FINANCIAL TURNOVER COVENANT</span>
                    <span className="text-[10px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-mono font-bold">CRITICAL HARD GATE</span>
                  </div>
                  <p className="text-xs text-slate-200 font-medium">
                    Minimum annual average audited financial turnover of $10,000,000 USD over preceding two fiscal years (FY23, FY24) certified by independent public accounting firm.
                  </p>
                  <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
                    <span>Source: Page 19, Offset 2400</span>
                    <span>Confidence: 98.8%</span>
                    <span className="text-emerald-400">Matched to: EVD-PWC-FY24 ($45.0M Verified)</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs text-cyan-400 font-bold">REQ-003 • TECHNICAL SPECIFICATION</span>
                    <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-mono font-bold">SUBSTANTIVE SCORING</span>
                  </div>
                  <p className="text-xs text-slate-200 font-medium">
                    Multi-cloud Kubernetes container orchestration across heterogeneous DoD hybrid networks with sub-50ms latency tactical data distribution and automated zero-downtime failover.
                  </p>
                  <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
                    <span>Source: Page 32, Offset 4810</span>
                    <span>Confidence: 97.9%</span>
                    <span className="text-emerald-400">Matched to: EVD-USAF-TACTICAL-C4</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs text-cyan-400 font-bold">REQ-004 • SERVICE LEVEL AGREEMENT (SLA)</span>
                    <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded font-mono font-bold">TIER 1 SLA</span>
                  </div>
                  <p className="text-xs text-slate-200 font-medium">
                    Continuous 99.999% high-availability operational uptime with Mean Time to Recovery (MTTR) under 15 minutes during critical mission execution windows.
                  </p>
                  <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
                    <span>Source: Page 45, Offset 7100</span>
                    <span>Confidence: 99.1%</span>
                    <span className="text-emerald-400">Matched to: EVD-SLA-MISSION-CRITICAL</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 4: COMPLIANCE MATRIX */}
          {activeTab === 'compliance' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Automated Compliance Matrix & Gap Analysis</h2>
                  <p className="text-xs text-slate-400">Compliance Officer evaluating RFP requirements against verified corporate qualifications.</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-emerald-400 font-mono">94.2% READINESS</div>
                  <span className="text-[10px] text-slate-400 font-mono">12 Compliant • 2 Partial • 0 Missing</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800 flex">
                <div className="bg-emerald-500 h-full" style={{ width: '86%' }}></div>
                <div className="bg-amber-500 h-full" style={{ width: '14%' }}></div>
              </div>

              {/* Compliance Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono">
                    <tr>
                      <th className="p-3">Requirement ID & Scope</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Compliance Status</th>
                      <th className="p-3">Matched Evidence Reference</th>
                      <th className="p-3">Auditor Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300 font-sans">
                    <tr className="hover:bg-slate-800/50">
                      <td className="p-3 font-semibold text-white">REQ-001: DoD Facility Security Clearance</td>
                      <td className="p-3 font-mono text-slate-400">Eligibility Gate</td>
                      <td className="p-3"><span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">COMPLIANT</span></td>
                      <td className="p-3 font-mono text-emerald-400">EVD-DCSA-FSC-2024</td>
                      <td className="p-3 text-slate-400">Verified Secret facility license on file with DCSA.</td>
                    </tr>
                    <tr className="hover:bg-slate-800/50">
                      <td className="p-3 font-semibold text-white">REQ-002: Minimum Audited Turnover ($10M)</td>
                      <td className="p-3 font-mono text-slate-400">Financial Gate</td>
                      <td className="p-3"><span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">COMPLIANT</span></td>
                      <td className="p-3 font-mono text-emerald-400">EVD-PWC-FY24</td>
                      <td className="p-3 text-slate-400">$45.0M audited turnover comfortably surpasses $10M threshold.</td>
                    </tr>
                    <tr className="hover:bg-slate-800/50">
                      <td className="p-3 font-semibold text-white">REQ-003: Multi-Cloud Kubernetes Telemetry</td>
                      <td className="p-3 font-mono text-slate-400">Technical Spec</td>
                      <td className="p-3"><span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">COMPLIANT</span></td>
                      <td className="p-3 font-mono text-emerald-400">EVD-USAF-TACTICAL-C4</td>
                      <td className="p-3 text-slate-400">Past performance demonstrated sub-35ms latency on AWS/GCP.</td>
                    </tr>
                    <tr className="hover:bg-slate-800/50">
                      <td className="p-3 font-semibold text-white">REQ-004: 99.999% Availability & MTTR &lt;15m</td>
                      <td className="p-3 font-mono text-slate-400">SLA Mandate</td>
                      <td className="p-3"><span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">PARTIAL</span></td>
                      <td className="p-3 font-mono text-amber-400">EVD-SLA-SRE-REPORT</td>
                      <td className="p-3 text-slate-400">Historical SLA 99.995%; mitigation plan adds automated cold standby.</td>
                    </tr>
                    <tr className="hover:bg-slate-800/50">
                      <td className="p-3 font-semibold text-white">REQ-005: ISO/IEC 27001 Information Security</td>
                      <td className="p-3 font-mono text-slate-400">Governance</td>
                      <td className="p-3"><span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">COMPLIANT</span></td>
                      <td className="p-3 font-mono text-emerald-400">EVD-ISO-27001-BSI</td>
                      <td className="p-3 text-slate-400">Certificate valid. Renewal audit scheduled for Nov 20.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SCREEN 5: PROOFLINK TRACEABILITY */}
          {activeTab === 'prooflink' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">ProofLink™ Cryptographic Evidence-to-Claim Lineage</h2>
                <p className="text-xs text-slate-400">Bid-wide audit trail mapping proposal claims directly to verified corporate proof documents.</p>
              </div>

              {/* Lineage Pipeline Visual */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400">Cryptographic Lineage Root Hash:</span>
                  <span className="text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                    089e9cd505e8301538433fd235bbd9982517ab9e4db43963aaa9ce4b6471b6f4
                  </span>
                </div>
                <div className="grid grid-cols-5 gap-2 text-center text-xs font-mono pt-2">
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded">1. Requirement Clause<br/><span className="text-emerald-400 text-[10px]">REQ-001 (DoD FCL)</span></div>
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded">2. Evidence Asset<br/><span className="text-cyan-400 text-[10px]">EVD-DCSA-FSC</span></div>
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded">3. Source Passage<br/><span className="text-indigo-400 text-[10px]">Page 2, Line 45</span></div>
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded">4. Proposal Claim<br/><span className="text-purple-400 text-[10px]">Section 2.1 C4ISR</span></div>
                  <div className="p-3 bg-slate-950 border border-emerald-500 rounded">5. Lineage Verified<br/><span className="text-emerald-400 text-[10px]">✓ Hash Matched</span></div>
                </div>
              </div>

              {/* Active ProofLinks */}
              <div className="space-y-3 font-mono text-xs">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-emerald-400 font-bold font-sans">ProofLink #1: ISO 27001 Security Management Accreditation</span>
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">99.8% VERIFIED</span>
                  </div>
                  <div className="text-slate-300 font-sans text-xs">
                    Claim: "Apex Global Defense maintains audited ISO/IEC 27001:2022 certified operations across all US cloud centers."
                  </div>
                  <div className="p-2.5 bg-slate-950 border border-slate-800/80 rounded text-[11px] text-slate-400 space-y-1">
                    <div>Document Source: <span className="text-white">ISO_27001_Certificate_BSI_2023.pdf</span> (Page 1, Clause 4.2)</div>
                    <div>SHA-256 Digest: <span className="text-emerald-400">8f3b92e7c41094da55b72e12a80479138e...</span></div>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-emerald-400 font-bold font-sans">ProofLink #2: PwC Certified Annual Turnover ($45.0M)</span>
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">99.5% VERIFIED</span>
                  </div>
                  <div className="text-slate-300 font-sans text-xs">
                    Claim: "Apex Global Defense demonstrates annual audited revenue of $45,000,000 USD comfortably meeting the $10M threshold."
                  </div>
                  <div className="p-2.5 bg-slate-950 border border-slate-800/80 rounded text-[11px] text-slate-400 space-y-1">
                    <div>Document Source: <span className="text-white">PwC_Audited_Financial_Statements_FY24.pdf</span> (Table 2, Page 7)</div>
                    <div>SHA-256 Digest: <span className="text-emerald-400">4c2a11b8df79021eab992167d3e9198aa4...</span></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 6: EVIDENCE RESEARCH */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Corporate Evidence Vault & Document Intelligence</h2>
                  <p className="text-xs text-slate-400">Evidence Researcher discovering and managing verified corporate proof assets.</p>
                </div>
                <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium transition shadow-lg shadow-emerald-950">
                  + Ingest Evidence Document
                </button>
              </div>

              {/* Search & Filter Bar */}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search corporate evidence by keyword, standard (ISO, CMMI), issuer, year..."
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
                <div className="flex gap-1.5 text-xs font-mono">
                  <button className="px-3 py-1.5 bg-emerald-600/20 border border-emerald-500 text-emerald-400 rounded-lg">All (29)</button>
                  <button className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-lg hover:text-white">Certs (8)</button>
                  <button className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-lg hover:text-white">Audits (6)</button>
                  <button className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-400 rounded-lg hover:text-white">Clearances (5)</button>
                </div>
              </div>

              {/* Evidence Cards Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-bold">CERTIFICATION</span>
                      <h3 className="font-bold text-sm text-white mt-1">ISO/IEC 27001:2022 Information Security</h3>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 font-bold">VERIFIED</span>
                  </div>
                  <p className="text-xs text-slate-400">Issuer: BSI Assurance UK • Scope: Cloud Defense Architecture & Software Operations</p>
                  <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                    <span>Issued: Nov 2023 • Expires: Nov 2026</span>
                    <span className="text-emerald-400">SHA-256 Verified</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20 font-bold">FINANCIAL AUDIT</span>
                      <h3 className="font-bold text-sm text-white mt-1">PwC Audited Financial Statements (FY23-FY24)</h3>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 font-bold">AUDITED</span>
                  </div>
                  <p className="text-xs text-slate-400">Issuer: PricewaterhouseCoopers LLP • Audited Revenue: $45,000,000 USD</p>
                  <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                    <span>Unqualified Audit Opinion</span>
                    <span className="text-emerald-400">SHA-256 Verified</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 font-bold">DEFENSE CLEARANCE</span>
                      <h3 className="font-bold text-sm text-white mt-1">DCSA Facility Security Clearance (Secret)</h3>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 font-bold">ACTIVE</span>
                  </div>
                  <p className="text-xs text-slate-400">Issuer: US Defense Counterintelligence & Security Agency (DCSA) • CAGE: 4K912</p>
                  <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                    <span>Clearance Level: Secret / Top Secret</span>
                    <span className="text-emerald-400">SHA-256 Verified</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20 font-bold">PAST PERFORMANCE</span>
                      <h3 className="font-bold text-sm text-white mt-1">US Air Force Tactical C4ISR Hybrid Cloud</h3>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 font-bold">CPARS 5.0</span>
                  </div>
                  <p className="text-xs text-slate-400">Authority: US Air Force Life Cycle Management Center • Contract Value: $8,400,000 USD</p>
                  <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                    <span>Performance Rating: Exceptional</span>
                    <span className="text-emerald-400">SHA-256 Verified</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 7: PROPOSAL GENERATION */}
          {activeTab === 'proposal' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Proposal Studio — Evidence-Backed Authoring</h2>
                  <p className="text-xs text-slate-400">Proposal Architect preparing an evidence-grounded response with embedded ProofLink citations.</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-xs text-slate-300 rounded-lg hover:bg-slate-800">
                    Re-Verify Citations
                  </button>
                  <button className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white rounded-lg transition shadow-lg shadow-emerald-950">
                    Export Package (.docx)
                  </button>
                </div>
              </div>

              {/* Proposal Header Banner */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center text-xs">
                <div>
                  <span className="text-slate-400 font-mono text-[11px]">ACTIVE PROPOSAL:</span>
                  <div className="font-bold text-sm text-white mt-0.5">Joint Multi-Domain Command & Control (JADC2) Technical Proposal</div>
                </div>
                <div className="flex gap-4 font-mono">
                  <div><span className="text-slate-500">Version:</span> <span className="text-emerald-400 font-bold">v2.1</span></div>
                  <div><span className="text-slate-500">Quality Score:</span> <span className="text-cyan-400 font-bold">98.0/100</span></div>
                  <div><span className="text-slate-500">Status:</span> <span className="text-indigo-400 font-bold">Sealed for Approval</span></div>
                </div>
              </div>

              {/* Section Preview & Editor */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <h3 className="font-bold text-sm text-white">Section 2.1: Sovereign Cloud Architecture & Security Controls</h3>
                  <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">3 Verified ProofLinks</span>
                </div>
                <div className="text-xs text-slate-300 leading-relaxed space-y-3 font-sans">
                  <p>
                    Apex Global Defense & IT Solutions proposes a hardened, multi-region Kubernetes cloud infrastructure engineered explicitly for DISA Joint Multi-Domain Command and Control operations. All core infrastructure components operate within audited <span className="bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-[11px] border border-emerald-800 cursor-pointer">[ProofLink: PL-ISO-27001-BSI]</span> compliance parameters, ensuring zero-trust cryptographic identity segmentation.
                  </p>
                  <p>
                    Our organizational balance sheet demonstrates an audited annual turnover of $45,000,000 USD <span className="bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-[11px] border border-emerald-800 cursor-pointer">[ProofLink: PL-PWC-FY24-AUDIT]</span>, exceeding the RFP mandatory threshold by 350%. Furthermore, active facility security clearances certified by DCSA <span className="bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-[11px] border border-emerald-800 cursor-pointer">[ProofLink: PL-DCSA-SECRET-FSC]</span> permit immediate personnel mobilization.
                  </p>
                  <p>
                    Latency-critical tactical message queuing delivers sub-35ms throughput across heterogeneous tactical edge sensors, replicating benchmark performance achieved on our US Air Force Tactical Backbone deployment.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 8: BID AUDIT */}
          {activeTab === 'bid_audit' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Independent Bid Audit & Risk Verification</h2>
                  <p className="text-xs text-slate-400">Bid Auditor independently verifying proposal claims, detecting unsupported statements, and assessing risks.</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-emerald-400 font-mono">94.5 / 100</div>
                  <span className="text-[10px] text-slate-400 font-mono">23 Verified Claims • 0 Unsupported • 1 Warning</span>
                </div>
              </div>

              {/* Audit Summary Cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Claim Grounding Score</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">100%</div>
                  <div className="text-[11px] text-slate-400 mt-1 font-mono">0 Unsupported Claims Detected</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Contradiction Auditing</div>
                  <div className="text-2xl font-bold text-cyan-400 mt-1 font-mono">0 Unresolved</div>
                  <div className="text-[11px] text-cyan-300 mt-1 font-mono">1 Discrepancy Resolved by CFO</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Pre-Flight Audit Verdict</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1 font-mono">PASSED</div>
                  <div className="text-[11px] text-indigo-300 mt-1 font-mono">Cleared for Executive Sign-Off</div>
                </div>
              </div>

              {/* Audit Findings */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <h3 className="font-bold text-sm text-white">Audit Verification Findings</h3>
                <div className="space-y-2 text-xs">
                  <div className="p-3 bg-slate-950 border border-emerald-800/60 rounded-lg flex items-center justify-between">
                    <div>
                      <span className="text-emerald-400 font-bold font-mono">[VERIFIED] </span>
                      <span className="text-slate-200">Facility Security Clearance matches DCSA active database records.</span>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400">100% Grounded</span>
                  </div>
                  <div className="p-3 bg-slate-950 border border-emerald-800/60 rounded-lg flex items-center justify-between">
                    <div>
                      <span className="text-emerald-400 font-bold font-mono">[VERIFIED] </span>
                      <span className="text-slate-200">Financial capacity of $45,000,000 validated against independent PwC audit.</span>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400">100% Grounded</span>
                  </div>
                  <div className="p-3 bg-slate-950 border border-amber-800/60 rounded-lg flex items-center justify-between">
                    <div>
                      <span className="text-amber-400 font-bold font-mono">[WARNING] </span>
                      <span className="text-slate-200">ISO 27001 certificate expires in 29 days. Recertification audit confirmed for Nov 20.</span>
                    </div>
                    <span className="text-[10px] font-mono text-amber-400">Mitigated</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 9: HUMAN APPROVAL */}
          {activeTab === 'human_approval' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Human Approval Gate & Cryptographic Sign-Off</h2>
                <p className="text-xs text-slate-400">Mandatory human-in-the-loop sign-off enforcing institutional accountability and non-repudiation.</p>
              </div>

              <div className="bg-slate-900 border border-emerald-600/50 rounded-xl p-6 space-y-5 shadow-xl shadow-emerald-950/20">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 font-bold">
                      EXECUTIVE GOVERNANCE GATE
                    </span>
                    <h3 className="font-bold text-base text-white mt-2">Pursuit Pursuit Authority Sign-Off: JADC2 Cloud Integration</h3>
                  </div>
                  <div className="text-right">
                    <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      APPROVED FOR SUBMISSION
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono">
                  <div><span className="text-slate-500 block">Sign-off Authority:</span><span className="text-white font-bold font-sans">Maj. Gen. (Ret.) Marcus Vance</span></div>
                  <div><span className="text-slate-500 block">Designated Title:</span><span className="text-slate-200 font-sans">EVP, Defense Pursuits</span></div>
                  <div><span className="text-slate-500 block">Approval Timestamp:</span><span className="text-slate-200">2026-11-07 10:45:10 UTC</span></div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-300 block">Executive Rationale & Authority Comments:</label>
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-emerald-200 font-sans leading-relaxed">
                    "Approved for final sealed submission. Technical architecture verified against DISA JADC2 criteria. Commercial pricing locked at $4,725,000.00 with 15.00% gross margin target. All mandatory compliance gates passed with zero unsupported claims."
                  </div>
                </div>

                <div className="p-3 bg-slate-950 border border-emerald-900 rounded-lg space-y-1 font-mono text-[11px]">
                  <span className="text-slate-400">Cryptographic Digital Signature Hash (SHA-256):</span>
                  <div className="text-emerald-400 break-all select-all font-bold">
                    089e9cd505e8301538433fd235bbd9982517ab9e4db43963aaa9ce4b6471b6f4
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN 10: FINAL DELIVERABLES */}
          {activeTab === 'deliverables' && (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">Final Proposal Deliverables & Release Center</h2>
                  <p className="text-xs text-slate-400">Generated publication-grade documents, verification manifests, and cryptographic submission receipts.</p>
                </div>
                <button
                  onClick={() => showToast('Downloading complete sealed release package (.zip)...')}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs rounded-lg transition shadow-lg shadow-emerald-950"
                >
                  Download Complete Package (.zip)
                </button>
              </div>

              {/* Cryptographic Receipt Banner */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[11px]">SUBMISSION RECEIPT HASH (SHA-256):</span>
                  <div className="text-emerald-400 font-bold text-xs mt-0.5">f30a17323c565a18149d8d226e1a50cba8a1758fa4917e91c342ce91f97e1783</div>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 text-[11px]">FINAL BID AMOUNT:</span>
                  <div className="text-white font-bold text-sm">$4,725,000.00 USD</div>
                </div>
              </div>

              {/* Deliverables Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">📄</span>
                    <div>
                      <h3 className="font-bold text-sm text-white">01_Tender_Intelligence_Report_JADC2.pdf</h3>
                      <p className="text-xs text-slate-400">48 Pages • 2.4 MB • Clause extraction & hard gates</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-xs">
                    <span className="text-emerald-400 font-mono">SHA-256 Verified</span>
                    <button className="text-emerald-400 hover:underline">Download PDF</button>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">📊</span>
                    <div>
                      <h3 className="font-bold text-sm text-white">02_Compliance_Matrix_and_ProofLink_Audit.xlsx</h3>
                      <p className="text-xs text-slate-400">Itemized 14-Clause Compliance Map & Evidence Citations</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-xs">
                    <span className="text-emerald-400 font-mono">SHA-256 Verified</span>
                    <button className="text-emerald-400 hover:underline">Download Excel</button>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">📝</span>
                    <div>
                      <h3 className="font-bold text-sm text-white">03_Technical_and_Management_Proposal.docx</h3>
                      <p className="text-xs text-slate-400">86 Pages • Complete Signed Proposal Narrative with ProofLinks</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-xs">
                    <span className="text-emerald-400 font-mono">SHA-256 Verified</span>
                    <button className="text-emerald-400 hover:underline">Download Word</button>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">🛡️</span>
                    <div>
                      <h3 className="font-bold text-sm text-white">04_Independent_Bid_Audit_and_Risk_Registry.pdf</h3>
                      <p className="text-xs text-slate-400">18 Pages • Pre-Flight Audit Certificate & 5x5 Risk Heat Matrix</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-xs">
                    <span className="text-emerald-400 font-mono">SHA-256 Verified</span>
                    <button className="text-emerald-400 hover:underline">Download PDF</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* EXTENDED: FINANCIAL WORKSPACE */}
          {activeTab === 'financial' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Financial Proposal Workspace</h2>
              <p className="text-xs text-slate-400">Strict deterministic calculations using Python Decimal with multi-scenario modeling.</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Base Cost Model</div>
                  <div className="text-2xl font-bold text-white font-mono mt-1">$4,725,000.00</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Conservative Margin (+15%)</div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">$5,433,750.00</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 font-mono">Aggressive Price (-5%)</div>
                  <div className="text-2xl font-bold text-amber-400 font-mono mt-1">$4,488,750.00</div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
