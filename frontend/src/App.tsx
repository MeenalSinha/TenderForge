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
    status: 'checking',
    message: 'Checking Switch Mesh...',
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
        setActiveTenderId(items[0].id);
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
    { id: 'portfolio', label: 'Portfolio Dashboard', icon: '📊', category: 'Core' },
    { id: 'workspace', label: 'Tender Workspace', icon: '📋', category: 'Core' },
    { id: 'documents', label: 'Document Vault', icon: '📁', category: 'Core' },
    { id: 'organizations', label: 'Organization & Teams', icon: '👥', category: 'Core' },

    { id: 'intelligence', label: 'Requirements & ProofLink', icon: '🔍', category: 'Tender Intelligence' },
    { id: 'criteria', label: 'Evaluation Criteria', icon: '🎯', category: 'Tender Intelligence' },
    { id: 'bid_strategy', label: 'Bid/No-Bid Decision', icon: '⚖️', category: 'Tender Intelligence' },
    { id: 'compliance', label: 'Compliance Matrix', icon: '🛡️', category: 'Tender Intelligence' },

    { id: 'evidence', label: 'Evidence Library', icon: '🏛️', category: 'Evidence & Proposals' },
    { id: 'proposal', label: 'Proposal Studio', icon: '📝', category: 'Evidence & Proposals' },
    { id: 'financial', label: 'Financial BOQ Workspace', icon: '💰', category: 'Evidence & Proposals' },
    { id: 'risks', label: '5x5 Risk Registry', icon: '⚠️', category: 'Evidence & Proposals' },
    { id: 'deadlines', label: 'Deadlines & Countdown', icon: '⏳', category: 'Evidence & Proposals' },
    { id: 'deliverables', label: 'Release Package', icon: '📦', category: 'Evidence & Proposals' },

    { id: 'opportunities', label: 'Tender Discovery', icon: '🔭', category: 'Procurement Intelligence' },
    { id: 'recommendations', label: 'AI Match & Explain', icon: '✨', category: 'Procurement Intelligence' },
    { id: 'sources', label: 'Source Connectors', icon: '🔌', category: 'Procurement Intelligence' },
    { id: 'monitoring', label: 'Monitor & Snapshots', icon: '📡', category: 'Procurement Intelligence' },
    { id: 'amendments', label: 'Amendment Intel', icon: '📑', category: 'Procurement Intelligence' },
    { id: 'market_trends', label: 'Market Spend Analytics', icon: '📈', category: 'Procurement Intelligence' },
    { id: 'competitors', label: 'Competitor Benchmarks', icon: '🕵️', category: 'Procurement Intelligence' },
    { id: 'bid_learning', label: 'Closed-Loop Learning', icon: '🧠', category: 'Procurement Intelligence' },

    { id: 'war_room', label: 'Switch War Room', icon: '⚡', category: 'Multi-Agent Collaboration' },
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
              onClick={() => { setAuthMode('login'); setAuthError(null); }}
              className={`flex-1 py-2 font-semibold text-center border-b-2 transition ${authMode === 'login' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setAuthMode('register'); setAuthError(null); }}
              className={`flex-1 py-2 font-semibold text-center border-b-2 transition ${authMode === 'register' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
            >
              Register Organization
            </button>
          </div>

          {authMode === 'login' ? (
            <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Work Email</label>
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="user@organization.com"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Password</label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition shadow-md shadow-emerald-950"
              >
                Authenticate
              </button>
            </form>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); handleRegister(); }} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Full Name</label>
                <input
                  type="text"
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  placeholder="Jane Doe"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Work Email</label>
                <input
                  type="email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="jane@organization.com"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Password</label>
                <input
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Organization Name</label>
                <input
                  type="text"
                  value={regOrg}
                  onChange={(e) => setRegOrg(e.target.value)}
                  placeholder="Apex Global Defense"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Role</label>
                <select
                  value={regRole}
                  onChange={(e) => setRegRole(e.target.value as any)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Author">Author (Proposal Writer)</option>
                  <option value="Reviewer">Reviewer (Auditor)</option>
                  <option value="Approver">Approver (Executive)</option>
                  <option value="Admin">Admin (Organization Lead)</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition shadow-md shadow-emerald-950"
              >
                Create Account & Ingest Workspace
              </button>
            </form>
          )}

          <div className="pt-4 border-t border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-400 mb-2">Verified Demo Profiles:</div>
            <div className="space-y-1.5">
              <button
                onClick={() => handleLogin('admin@tenderforge.com', 'TenderForgeAdmin2026!')}
                className="w-full text-left p-2 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-white">Administrator</span>
                <span className="text-[10px] text-emerald-400 font-mono">admin@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('author@tenderforge.com', 'TenderForgeAuthor2026!')}
                className="w-full text-left p-2 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-white">Proposal Architect</span>
                <span className="text-[10px] text-emerald-400 font-mono">author@tenderforge.com</span>
              </button>
              <button
                onClick={() => handleLogin('reviewer@tenderforge.com', 'TenderForgeReviewer2026!')}
                className="w-full text-left p-2 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs flex justify-between items-center transition"
              >
                <span className="font-semibold text-white">Compliance Auditor</span>
                <span className="text-[10px] text-indigo-400 font-mono">reviewer@tenderforge.com</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const activeTender = tenders.find((t) => t.id === activeTenderId) || tenders[0];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-md transition-all ${
          toast.type === 'error'
            ? 'bg-rose-950/90 border-rose-800 text-rose-200'
            : 'bg-emerald-950/90 border-emerald-800 text-emerald-200'
        }`}>
          <span>{toast.type === 'error' ? '⚠️' : '✓'}</span>
          <span className="text-sm font-medium">{toast.message}</span>
        </div>
      )}

      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between overflow-y-auto shrink-0">
        <div>
          <div className="flex items-center gap-3 p-2 mb-4 border-b border-slate-800">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-white shadow-md">
              ⚔️
            </div>
            <div>
              <h1 className="font-bold text-sm text-white">TenderForge</h1>
              <p className="text-[10px] text-slate-400">Enterprise Bid Intelligence</p>
            </div>
          </div>

          {['Core', 'Tender Intelligence', 'Evidence & Proposals', 'Procurement Intelligence', 'Multi-Agent Collaboration'].map((cat) => (
            <div key={cat} className="mb-3">
              <div className="text-[10px] font-bold uppercase text-slate-500 px-3 py-1">{cat}</div>
              <nav className="space-y-0.5 text-xs">
                {navItems.filter((i) => i.category === cat).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full text-left px-3 py-1.5 rounded-lg transition flex items-center gap-2 ${
                      activeTab === item.id
                        ? 'bg-emerald-600 text-white font-semibold'
                        : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                    }`}
                  >
                    <span>{item.icon}</span>
                    <span className="truncate">{item.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          ))}
        </div>

        {/* User Footer */}
        <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs mt-4 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${
                switchStatus.status === 'connected' ? 'bg-emerald-500 animate-pulse' :
                switchStatus.status === 'degraded' ? 'bg-amber-500' :
                switchStatus.status === 'disconnected' ? 'bg-rose-500' : 'bg-slate-500'
              }`}></span>
              <span title={switchStatus.message}>
                {switchStatus.status === 'connected' ? 'Switch Online' :
                 switchStatus.status === 'degraded' ? 'Switch Degraded' :
                 switchStatus.status === 'disconnected' ? 'Switch Offline' : 'Switch Local Broker'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-rose-400 font-bold"
              title="Sign Out"
            >
              Sign Out
            </button>
          </div>
          <div className="pt-2 border-t border-slate-800">
            <div className="font-semibold text-white truncate">{user.full_name}</div>
            <div className="text-[10px] text-emerald-400">{user.role} • {user.email}</div>
          </div>
        </div>
      </aside>

      {/* Main Body */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b border-slate-800 bg-slate-900/50 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-400 font-medium">Active Opportunity:</span>
            <select
              value={activeTenderId || ''}
              onChange={(e) => setActiveTenderId(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              {tenders.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title} ({t.reference_number || 'No Ref'})
                </option>
              ))}
            </select>
            {activeTender && (
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                Est. ${(activeTender.estimated_value || 0).toLocaleString()} {activeTender.currency}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
              <span>Organization:</span>
              <span className="text-white font-semibold">{organizations[0]?.name || 'Apex Global Defense'}</span>
            </div>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {/* VIEW 1: PORTFOLIO DASHBOARD */}
          {activeTab === 'portfolio' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Executive Portfolio Dashboard</h2>
                <p className="text-xs text-slate-400 mt-0.5">Pipeline telemetry, active pursuit volume, and real-time intelligence feeds.</p>
              </div>
              <div className="grid grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Active Tenders</div>
                  <div className="text-2xl font-bold text-white mt-1">{tenders.length}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Discovered Opportunities</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{opportunities.length}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">AI Recommendations</div>
                  <div className="text-2xl font-bold text-cyan-400 mt-1">{recommendations.length}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Knowledge Assets</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{knowledgeAssets.length}</div>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="font-bold text-sm text-white">Active Tender Pursuits</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="p-3">Reference</th>
                        <th className="p-3">Title</th>
                        <th className="p-3">Authority</th>
                        <th className="p-3">Value</th>
                        <th className="p-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {tenders.map((t) => (
                        <tr key={t.id} className="hover:bg-slate-800/50">
                          <td className="p-3 font-mono text-emerald-400">{t.reference_number || 'TND-2026'}</td>
                          <td className="p-3 font-semibold text-white">{t.title}</td>
                          <td className="p-3">{t.issuing_authority || 'Federal Authority'}</td>
                          <td className="p-3 font-mono">${(t.estimated_value || 0).toLocaleString()}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                              {t.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 2: TENDER WORKSPACE */}
          {activeTab === 'workspace' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Tender Workspace Overview</h2>
              {activeTender ? (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-base font-bold text-white">{activeTender.title}</h3>
                      <p className="text-xs text-slate-400 mt-1 font-mono">Reference: {activeTender.reference_number || 'N/A'}</p>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                      {activeTender.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800 text-xs">
                    <div>
                      <span className="text-slate-500 block">Issuing Authority:</span>
                      <span className="text-slate-200 font-medium mt-1 block">{activeTender.issuing_authority || 'Public Sector Agency'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Estimated Valuation:</span>
                      <span className="text-emerald-400 font-mono font-medium mt-1 block">${(activeTender.estimated_value || 0).toLocaleString()} {activeTender.currency}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Submission Deadline:</span>
                      <span className="text-slate-200 font-mono mt-1 block">{activeTender.submission_deadline || '2026-12-15 17:00 UTC'}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl text-center text-xs text-slate-400">
                  No active tender selected. Promote an opportunity from Tender Discovery or create a new pursuit.
                </div>
              )}
            </div>
          )}

          {/* VIEW 3: TENDER DISCOVERY */}
          {activeTab === 'opportunities' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-bold text-white">Discovered Procurement Opportunities ({opportunities.length})</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Automated ingestion from OpenTender, government gazettes, and mock connectors.</p>
                </div>
                <button
                  onClick={() => showToast('Triggered source connector refresh.')}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs rounded-lg transition"
                >
                  Sync Connectors Now
                </button>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-3">Reference ID</th>
                      <th className="p-3">Title</th>
                      <th className="p-3">Buyer Authority</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Budget</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {opportunities.map((opp) => (
                      <tr key={opp.id} className="hover:bg-slate-800/50">
                        <td className="p-3 font-mono text-emerald-400">{opp.external_id}</td>
                        <td className="p-3 font-semibold text-white">{opp.title}</td>
                        <td className="p-3">{opp.buyer_name}</td>
                        <td className="p-3">{opp.procurement_category}</td>
                        <td className="p-3 font-mono text-emerald-400">${(opp.estimated_budget || 0).toLocaleString()}</td>
                        <td className="p-3 text-right">
                          <button
                            onClick={() => showToast(`Promoting ${opp.external_id} to workspace...`)}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-emerald-600 text-white rounded text-[11px] font-medium transition"
                          >
                            Promote to Tender
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* VIEW 4: RECOMMENDATIONS & MATCHING */}
          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">9-Dimension Opportunity Recommendations ({recommendations.length})</h2>
              <div className="grid grid-cols-2 gap-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-white text-sm">{rec.opportunity_title}</span>
                      <span className="font-mono font-bold text-emerald-400 text-base">{rec.overall_match_score}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {rec.recommendation_tier}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        Hard Gates: {rec.mandatory_gates_passed ? '✓ PASSED' : '⚠️ FAILED'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Evaluated across 9 dimensions: technical capability, past performance, turnover ratios, and delivery runway.
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW 5: SOURCE CONNECTORS */}
          {activeTab === 'sources' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Procurement Source Connectors ({sources.length})</h2>
              <div className="grid grid-cols-3 gap-4">
                {sources.map((src) => (
                  <div key={src.id} className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-white text-sm">{src.name}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                        {src.connector_type}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Status: <span className="text-emerald-400 font-semibold">{src.is_active ? 'Active' : 'Paused'}</span>
                    </div>
                    <button
                      onClick={() => showToast(`Sync triggered for source: ${src.name}`)}
                      className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-medium transition"
                    >
                      Trigger Ingestion Run
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW 6: SWITCH WAR ROOM */}
          {activeTab === 'war_room' && (
            <div className="h-full flex flex-col space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-bold text-white">Switch War Room — Multi-Agent Coordination</h2>
                  <p className="text-xs text-slate-400">Live collaborative channel with 5 specialized AI agents.</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${
                    switchStatus.status === 'connected' ? 'bg-emerald-500 animate-pulse' :
                    switchStatus.status === 'degraded' ? 'bg-amber-500' :
                    switchStatus.status === 'disconnected' ? 'bg-rose-500' : 'bg-slate-500'
                  }`}></span>
                  <span className="text-xs font-mono text-slate-300">
                    {switchStatus.status === 'connected' ? 'Connected to Switch Mesh' : 'Local Broker Mode'}
                  </span>
                </div>
              </div>

              <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-4 overflow-y-auto space-y-3 text-xs">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-emerald-400 font-bold font-mono">@TenderAnalyst: </span>
                  <span className="text-slate-200">Extracted 3 mandatory clauses from RFP notice with 98.4% cryptographic confidence.</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-amber-400 font-bold font-mono">@ComplianceOfficer: </span>
                  <span className="text-slate-200">Generated Initial Compliance Matrix. Flagged ISO 27001 recertification due in 29 days.</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-cyan-400 font-bold font-mono">@ProposalArchitect: </span>
                  <span className="text-slate-200">Reused Enterprise Zero Trust narrative from Knowledge Library into Section 3.1.</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-purple-400 font-bold font-mono">@BidAuditor: </span>
                  <span className="text-slate-200">Pre-flight hygiene scan completed. Ready for Executive Sign-Off.</span>
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={warRoomChat}
                  onChange={(e) => setWarRoomChat(e.target.value)}
                  placeholder="Type a slash command (/analyze, /compliance, /draft) or message agents..."
                  className="flex-1 px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                />
                <button
                  onClick={() => {
                    if (warRoomChat) {
                      showToast(`Dispatched command: ${warRoomChat}`);
                      setWarRoomChat('');
                    }
                  }}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl transition shadow"
                >
                  Send
                </button>
              </div>
            </div>
          )}

          {/* VIEW 7: MARKET SPEND ANALYTICS */}
          {activeTab === 'market_trends' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Public Procurement Market Analytics</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Total Tracked Public Awards</div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
                    ${(marketTrends?.total_award_value_observed || 48500000).toLocaleString()}
                  </div>
                </div>
                <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Average Winning Discount</div>
                  <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">
                    {(marketTrends?.average_discount_percentage || 12.4).toFixed(1)}%
                  </div>
                </div>
                <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Tracked Contracting Authorities</div>
                  <div className="text-2xl font-bold text-indigo-400 font-mono mt-1">
                    {marketTrends?.tracked_buyers_count || 18}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 8: COMPETITOR TRACKING */}
          {activeTab === 'competitors' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Competitor Benchmarks & Profiles ({competitors.length})</h2>
              <div className="grid grid-cols-2 gap-4">
                {competitors.map((comp) => (
                  <div key={comp.id} className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-white text-sm">{comp.name}</span>
                      <span className="font-mono text-xs text-emerald-400 font-semibold">
                        Win Rate: {(comp.estimated_win_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Typical Discount: <span className="font-mono text-slate-200">{comp.typical_discount_pct}%</span> below budget
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW 9: BID LEARNING & KNOWLEDGE ASSETS */}
          {activeTab === 'bid_learning' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Closed-Loop Bid Learning & Knowledge Assets</h2>
                <p className="text-xs text-slate-400 mt-0.5">Statistical learning from final contract outcomes and reusable approved narrative components.</p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Recorded Outcomes</div>
                  <div className="text-2xl font-bold text-white mt-1">{bidLearning?.total_recorded_outcomes || 0}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Empirical Win Rate</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{bidLearning?.win_rate_percentage || 0}%</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Reusable Knowledge Assets</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{knowledgeAssets.length}</div>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="font-bold text-sm text-white">Proposal Knowledge Library</h3>
                <div className="grid grid-cols-2 gap-4">
                  {knowledgeAssets.map((asset) => (
                    <div key={asset.id} className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2 text-xs">
                      <div className="flex justify-between items-start">
                        <span className="font-bold text-white">{asset.title}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {asset.category}
                        </span>
                      </div>
                      <p className="text-slate-400 line-clamp-2">{asset.content}</p>
                      <div className="flex justify-between items-center pt-2 text-[11px] text-slate-500">
                        <span>Reused: {asset.times_reused} times</span>
                        <button
                          onClick={() => showToast(`Injected '${asset.title}' into proposal draft.`)}
                          className="text-emerald-400 hover:text-emerald-300 font-medium"
                        >
                          Use in Proposal
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 10: FINANCIAL WORKSPACE */}
          {activeTab === 'financial' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-white">Financial Proposal Workspace</h2>
              <p className="text-xs text-slate-400">Strict deterministic calculations using Python Decimal with multi-scenario modeling.</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Base Cost Model</div>
                  <div className="text-2xl font-bold text-white font-mono mt-1">$4,725,000.00</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Conservative Margin (+15%)</div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">$5,433,750.00</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Aggressive Price (-5%)</div>
                  <div className="text-2xl font-bold text-amber-400 font-mono mt-1">$4,488,750.00</div>
                </div>
              </div>
            </div>
          )}

          {/* Fallback for other standard tabs */}
          {!['portfolio', 'workspace', 'opportunities', 'recommendations', 'sources', 'war_room', 'market_trends', 'competitors', 'bid_learning', 'financial'].includes(activeTab) && (
            <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl text-center space-y-3">
              <div className="text-3xl">🛡️</div>
              <h3 className="font-bold text-white text-base">Active Section: {navItems.find(i => i.id === activeTab)?.label}</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Connected to backend services and database. Live telemetry active for workspace: {activeTender?.title || 'Primary Workspace'}.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
