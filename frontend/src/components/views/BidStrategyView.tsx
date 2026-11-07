import React, { useState } from 'react';
import {
  Crosshair,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { Tender } from '../../types';

interface BidStrategyViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const BidStrategyView: React.FC<BidStrategyViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const [decision, setDecision] = useState<'APPROVED_BID' | 'APPROVED_NO_BID' | 'OVERRIDDEN'>('APPROVED_BID');
  const [rationale, setRationale] = useState(
    'Strong competitive advantage in DOD IL6 / FedRAMP High. Demonstrated USAF past performance. High gross margin trajectory (>22%). Formally approved to bid.'
  );

  const dimensions = [
    { name: 'Technical Capability Fit', score: 96, weight: '30%', status: 'HIGH' },
    { name: 'Commercial & Financial Feasibility', score: 90, weight: '25%', status: 'HIGH' },
    { name: 'Strategic Account Alignment', score: 95, weight: '20%', status: 'HIGH' },
    { name: 'Resource & Key Personnel Availability', score: 88, weight: '15%', status: 'MEDIUM' },
    { name: 'Risk & Delivery Governance', score: 92, weight: '10%', status: 'HIGH' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-cyan-400" />
            Bid Strategy & Bid / No-Bid Decision Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Data-driven pursuit qualification, capability gate checks, and executive governance authorization.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('compliance')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Review Compliance Center <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Decision Summary Card */}
      <div className="p-6 bg-navy-850 border border-navy-700/60 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 font-extrabold text-2xl font-mono">
            92
          </div>
          <div>
            <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider">
              Recommendation Engine Output
            </div>
            <h3 className="text-lg font-bold text-white mt-0.5 flex items-center gap-2">
              RECOMMENDATION: BID (Pursue aggressively)
              <span className="px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                100% Gates Passed
              </span>
            </h3>
            <p className="text-xs text-slate-300 mt-1">
              Estimated Value: ${(activeTender?.estimated_value || 12500000).toLocaleString()} USD • Target: {activeTender?.title}
            </p>
          </div>
        </div>

        <div className="text-right shrink-0">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Win Probability Index</span>
          <div className="text-2xl font-extrabold text-emerald-400 font-mono mt-0.5">84.5%</div>
        </div>
      </div>

      {/* 5-Dimension Radar / Bar Scoring */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl p-5 shadow-lg space-y-4">
        <h4 className="font-bold text-sm text-white">5-Dimension Scoring Breakdown</h4>
        <div className="space-y-3">
          {dimensions.map((dim) => (
            <div key={dim.name} className="space-y-1 text-xs">
              <div className="flex justify-between items-center text-slate-300">
                <span className="font-semibold">{dim.name}</span>
                <span className="font-mono text-cyan-400 font-bold">{dim.score}% ({dim.weight})</span>
              </div>
              <div className="w-full h-2 bg-navy-950 rounded-full overflow-hidden border border-navy-700">
                <div
                  style={{ width: `${dim.score}%` }}
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Human Decision Override Form */}
      <div className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3">
        <h4 className="font-bold text-sm text-white flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-cyan-400" /> Executive Pursuit Authorization
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            onClick={() => setDecision('APPROVED_BID')}
            className={`p-3 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              decision === 'APPROVED_BID'
                ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-950'
                : 'bg-navy-900 text-slate-300 border-navy-700 hover:bg-navy-800'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" /> Approve Bid (Formal Pursuit)
          </button>
          <button
            onClick={() => setDecision('APPROVED_NO_BID')}
            className={`p-3 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              decision === 'APPROVED_NO_BID'
                ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-950'
                : 'bg-navy-900 text-slate-300 border-navy-700 hover:bg-navy-800'
            }`}
          >
            <AlertTriangle className="w-4 h-4" /> Reject (No-Bid)
          </button>
          <button
            onClick={() => setDecision('OVERRIDDEN')}
            className={`p-3 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              decision === 'OVERRIDDEN'
                ? 'bg-amber-600 text-white border-amber-500 shadow-md shadow-amber-950'
                : 'bg-navy-900 text-slate-300 border-navy-700 hover:bg-navy-800'
            }`}
          >
            Conditional Pursuit
          </button>
        </div>

        <div className="space-y-1.5 pt-2">
          <label className="text-xs text-slate-400">Executive Rationale & Authorization Memo</label>
          <textarea
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            rows={2}
            className="w-full p-3 bg-navy-950 border border-navy-700 rounded-xl text-xs text-slate-200 font-sans focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>
    </div>
  );
};

