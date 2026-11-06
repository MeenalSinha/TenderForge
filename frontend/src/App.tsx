import React, { useState, useEffect } from 'react';
import { apiRequest } from './api/client';
import { Tender, Organization, User } from './types';

export default function App() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [activeTenderId, setActiveTenderId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [user, setUser] = useState<User>({
    id: localStorage.getItem('tf_user_id') || 'usr-system-admin',
    email: localStorage.getItem('tf_user_email') || 'admin@tenderforge.local',
    full_name: localStorage.getItem('tf_user_name') || 'Administrator',
    role: localStorage.getItem('tf_user_role') || 'Admin',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  });

  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [amendments, setAmendments] = useState<any[]>([]);
  const [marketTrends, setMarketTrends] = useState<any>(null);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [bidLearning, setBidLearning] = useState<any>(null);
  const [knowledgeAssets, setKnowledgeAssets] = useState<any[]>([]);

  useEffect(() => {
    loadTenders();
    loadPhase5Data();
  }, []);

  async function loadTenders() {
    const res = await apiRequest('/tenders');
    if (res.success && res.data) {
      const items = res.data.items || [];
      setTenders(items);
      if (items.length > 0 && !activeTenderId) {
        setActiveTenderId(items[0].id);
      }
    }
  }

  async function loadPhase5Data() {
    try {
      const [oppRes, recRes, srcRes, mktRes, compRes, learnRes, knRes] = await Promise.all([
        apiRequest('/opportunities'),
        apiRequest('/opportunities/recommendations'),
        apiRequest('/sources'),
        apiRequest('/market/trends'),
        apiRequest('/market/competitors'),
        apiRequest('/analytics/bid-learning'),
        apiRequest('/knowledge/assets'),
      ]);

      if (oppRes.success && oppRes.data) setOpportunities(oppRes.data.opportunities || []);
      if (recRes.success && recRes.data) setRecommendations(recRes.data.recommendations || []);
      if (srcRes.success && srcRes.data) setSources(srcRes.data.sources || []);
      if (mktRes.success && mktRes.data) setMarketTrends(mktRes.data);
      if (compRes.success && compRes.data) setCompetitors(compRes.data.competitors || []);
      if (learnRes.success && learnRes.data) setBidLearning(learnRes.data);
      if (knRes.success && knRes.data) setKnowledgeAssets(knRes.data.assets || []);
    } catch (e) {
      console.error('Phase 5 load error', e);
    }
  }

  const navItems = [
    { id: 'portfolio', label: 'Portfolio Dashboard', icon: '📊', category: 'Core' },
    { id: 'workspace', label: 'Tender Workspace', icon: '📋', category: 'Core' },
    { id: 'financial', label: 'Financial Workspace', icon: '💰', category: 'Core' },
    { id: 'war_room', label: 'Switch War Room', icon: '⚡', category: 'Core' },
    { id: 'opportunities', label: 'Tender Discovery', icon: '🔭', category: 'Procurement Intelligence' },
    { id: 'recommendations', label: 'AI Match & Explain', icon: '✨', category: 'Procurement Intelligence' },
    { id: 'sources', label: 'Source Connectors', icon: '🔌', category: 'Procurement Intelligence' },
    { id: 'monitoring', label: 'Monitor & Snapshots', icon: '📡', category: 'Procurement Intelligence' },
    { id: 'amendments', label: 'Amendment Intel', icon: '📑', category: 'Procurement Intelligence' },
    { id: 'market_trends', label: 'Market Analytics', icon: '📈', category: 'Procurement Intelligence' },
    { id: 'competitors', label: 'Competitor Tracking', icon: '🕵️', category: 'Procurement Intelligence' },
    { id: 'bid_learning', label: 'Bid Learning & Library', icon: '🧠', category: 'Procurement Intelligence' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between overflow-y-auto">
        <div>
          <div className="flex items-center gap-3 p-2 mb-4 border-b border-slate-800">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-bold">
              ⚔️
            </div>
            <div>
              <h1 className="font-bold text-sm">TenderForge</h1>
              <p className="text-[10px] text-slate-400">Enterprise Bid Workspace</p>
            </div>
          </div>

          <div className="text-[10px] font-bold uppercase text-slate-500 px-3 py-1">Operations</div>
          <nav className="space-y-1 text-xs mb-4">
            {navItems.filter((i) => i.category === 'Core').map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full text-left px-3 py-2 rounded-lg transition ${activeTab === item.id ? 'bg-emerald-600 text-white font-semibold' : 'text-slate-400 hover:bg-slate-900'}`}
              >
                {item.icon} {item.label}
              </button>
            ))}
          </nav>

          <div className="text-[10px] font-bold uppercase text-brand-400 px-3 py-1">Procurement Intelligence</div>
          <nav className="space-y-1 text-xs">
            {navItems.filter((i) => i.category === 'Procurement Intelligence').map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full text-left px-3 py-1.5 rounded-lg transition ${activeTab === item.id ? 'bg-slate-800 text-brand-400 font-semibold border-l-2 border-brand-400' : 'text-slate-400 hover:bg-slate-900/60'}`}
              >
                {item.icon} {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-xs mt-4">
          <div className="font-semibold text-white truncate">{user.full_name}</div>
          <div className="text-[10px] text-emerald-400">{user.role}</div>
        </div>
      </aside>

      {/* Main Body */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b border-slate-800 bg-slate-900/50 px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-400 font-medium">Active Workspace:</span>
            <select
              value={activeTenderId || ''}
              onChange={(e) => setActiveTenderId(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-white"
            >
              {tenders.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title} ({t.reference_number})
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs text-slate-400">Switch Mesh Ready</span>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {activeTab === 'portfolio' && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white">Executive Portfolio Dashboard</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-xs text-slate-400">Active Tenders</div>
                  <div className="text-2xl font-bold text-white mt-1">{tenders.length}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-xs text-slate-400">Discovered Opportunities</div>
                  <div className="text-2xl font-bold text-brand-400 mt-1">{opportunities.length}</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-xs text-slate-400">Knowledge Assets</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{knowledgeAssets.length}</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'opportunities' && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white">Discovered Procurement Opportunities ({opportunities.length})</h2>
              <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-3">Title</th>
                      <th className="p-3">Buyer</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Budget</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {opportunities.map((opp) => (
                      <tr key={opp.id} className="hover:bg-slate-800/50">
                        <td className="p-3 font-semibold text-white">{opp.title}</td>
                        <td className="p-3">{opp.buyer_name}</td>
                        <td className="p-3">{opp.procurement_category}</td>
                        <td className="p-3 font-mono text-emerald-400">${(opp.estimated_budget || 0).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white">AI Opportunity Match Recommendations ({recommendations.length})</h2>
              <div className="grid grid-cols-2 gap-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-2">
                    <div className="flex justify-between">
                      <span className="font-bold text-white">{rec.opportunity_title}</span>
                      <span className="font-mono font-bold text-brand-400">{rec.overall_match_score}%</span>
                    </div>
                    <div className="text-xs text-slate-400">{rec.recommendation_tier}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'market_trends' && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white">Procurement Market Trends</h2>
              <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                <div className="text-xs text-slate-400">Total Tracked Public Market Spend</div>
                <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
                  ${(marketTrends?.total_spend_observed || 0).toLocaleString()}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
