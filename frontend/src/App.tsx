import React, { useState, useEffect } from 'react';
import { apiRequest } from './api/client';
import { Tender, Organization, User } from './types';

export default function App() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [activeTenderId, setActiveTenderId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [user, setUser] = useState<User>({
    id: 'usr-system-admin',
    email: 'admin@tenderforge.local',
    full_name: 'Administrator',
    role: 'Admin',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  });

  useEffect(() => {
    loadTenders();
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

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 p-2 mb-6 border-b border-slate-800">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-bold">
              ⚔️
            </div>
            <div>
              <h1 className="font-bold text-sm">TenderForge</h1>
              <p className="text-[10px] text-slate-400">Enterprise Bid Workspace</p>
            </div>
          </div>

          <nav className="space-y-1 text-xs">
            <button
              onClick={() => setActiveTab('portfolio')}
              className={`w-full text-left px-3 py-2 rounded-lg transition ${activeTab === 'portfolio' ? 'bg-emerald-600 text-white font-semibold' : 'text-slate-400 hover:bg-slate-900'}`}
            >
              📊 Portfolio Dashboard
            </button>
            <button
              onClick={() => setActiveTab('workspace')}
              className={`w-full text-left px-3 py-2 rounded-lg transition ${activeTab === 'workspace' ? 'bg-emerald-600 text-white font-semibold' : 'text-slate-400 hover:bg-slate-900'}`}
            >
              📋 Tender Workspace
            </button>
            <button
              onClick={() => setActiveTab('financial')}
              className={`w-full text-left px-3 py-2 rounded-lg transition ${activeTab === 'financial' ? 'bg-emerald-600 text-white font-semibold' : 'text-slate-400 hover:bg-slate-900'}`}
            >
              💰 Financial Workspace
            </button>
            <button
              onClick={() => setActiveTab('war_room')}
              className={`w-full text-left px-3 py-2 rounded-lg transition ${activeTab === 'war_room' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:bg-slate-900'}`}
            >
              ⚡ Switch War Room
            </button>
          </nav>
        </div>

        <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-xs">
          <div className="font-semibold text-white truncate">{user.full_name}</div>
          <div className="text-[10px] text-emerald-400">{user.role}</div>
        </div>
      </aside>

      {/* Main Body */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b border-slate-800 bg-slate-900/50 px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-mono text-slate-400">Opportunity:</span>
            <select
              value={activeTenderId || ''}
              onChange={(e) => setActiveTenderId(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-white text-xs rounded px-2.5 py-1"
            >
              {tenders.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title}
                </option>
              ))}
            </select>
          </div>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
            Switch Connected
          </span>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          <h2 className="text-xl font-bold text-white mb-2">TenderForge Enterprise Intelligence</h2>
          <p className="text-xs text-slate-400">
            Unified full-stack bid intelligence and proposal preparation active.
          </p>
        </div>
      </main>
    </div>
  );
}
