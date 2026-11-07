import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Download,
  Calendar,
  Layers,
  CheckCircle2,
  Clock
} from 'lucide-react';

export const AnalyticsView: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            Executive Workspace Analytics & Bid Velocity
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Pipeline velocity, stage conversion efficiency, win/loss ratios, and response time telemetry.
          </p>
        </div>
        <button
          onClick={() => alert('Exporting complete executive PDF report.')}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
        >
          <Download className="w-3.5 h-3.5" /> Export Intelligence Report
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Average Proposal Velocity</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">7.4 Days</div>
          <div className="text-[11px] text-emerald-300 mt-0.5">65% faster than 21-day industry benchmark</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Total Bids Submitted</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">28 Pursuits</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Past 12 Months</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Overall Win Rate</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">71.4%</div>
          <div className="text-[11px] text-cyan-300 mt-0.5">20 Won • 8 Lost</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Total Award Revenue</div>
          <div className="text-2xl font-bold text-purple-300 font-mono mt-1">$34.8M</div>
          <div className="text-[11px] text-purple-400 mt-0.5">Awarded Defense Contracts</div>
        </div>
      </div>

      {/* Pipeline Stage Conversion Funnel */}
      <div className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-4">
        <h3 className="font-bold text-sm text-white">Pipeline Conversion Funnel</h3>
        <div className="space-y-3">
          {[
            { stage: '1. Opportunity Discovery', count: 68, pct: 100 },
            { stage: '2. Qualification & Clause Extraction', count: 32, pct: 47 },
            { stage: '3. Bid Strategy Gate (Approved to Bid)', count: 24, pct: 35 },
            { stage: '4. Proposal Studio & ProofLink Binding', count: 22, pct: 32 },
            { stage: '5. Executive Audit & Cryptographic Sign-Off', count: 21, pct: 31 },
            { stage: '6. Formal Submission & Award', count: 20, pct: 29 },
          ].map((item) => (
            <div key={item.stage} className="space-y-1 text-xs">
              <div className="flex justify-between items-center text-slate-300">
                <span className="font-medium">{item.stage}</span>
                <span className="font-mono text-cyan-400 font-bold">{item.count} Pursuits ({item.pct}%)</span>
              </div>
              <div className="w-full h-2 bg-navy-950 rounded-full overflow-hidden border border-navy-700">
                <div
                  style={{ width: `${item.pct}%` }}
                  className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full transition-all duration-500"
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

