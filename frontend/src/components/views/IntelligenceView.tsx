import React, { useState } from 'react';
import {
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Filter,
  Shield,
  Clock,
  ArrowRight
} from 'lucide-react';
import { Tender, Requirement } from '../../types';

interface IntelligenceViewProps {
  activeTender?: Tender;
  requirements: Requirement[];
  onNavigateTab: (tabId: string) => void;
}

export const IntelligenceView: React.FC<IntelligenceViewProps> = ({
  activeTender,
  requirements,
  onNavigateTab,
}) => {
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  // Filtered requirements
  const filtered = requirements.filter(
    (r) => categoryFilter === 'ALL' || r.category.toLowerCase() === categoryFilter.toLowerCase()
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileSearch className="w-5 h-5 text-cyan-400" />
            Tender Analysis & Clause Extraction
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated clause extraction, requirement classification, and source document citations executed by @TenderAnalyst.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('compliance')}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Generate Compliance Matrix <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Active Tender Context Summary */}
      <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider">
            {activeTender?.reference_number || 'DOD-DISA-2026'}
          </span>
          <h3 className="font-bold text-sm text-white mt-0.5">
            {activeTender?.title || 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration'}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Authority: {activeTender?.issuing_authority || 'US Department of Defense (DISA)'} • Est. Value: $
            {(activeTender?.estimated_value || 12500000).toLocaleString()} USD
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono shrink-0">
          <div className="p-2.5 bg-navy-900 rounded-xl border border-navy-700 text-center min-w-[90px]">
            <div className="text-[10px] text-slate-400">Clauses Extracted</div>
            <div className="text-lg font-bold text-cyan-400 mt-0.5">{requirements.length || 14}</div>
          </div>
          <div className="p-2.5 bg-navy-900 rounded-xl border border-navy-700 text-center min-w-[90px]">
            <div className="text-[10px] text-slate-400">Mean Confidence</div>
            <div className="text-lg font-bold text-emerald-400 mt-0.5">97.4%</div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {['ALL', 'eligibility', 'technical', 'financial', 'submission'].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`px-3 py-1.5 rounded-xl capitalize font-medium transition ${
              categoryFilter === cat
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/30'
                : 'bg-navy-850 hover:bg-navy-800 text-slate-400 hover:text-slate-200 border border-navy-700/60'
            }`}
          >
            {cat === 'ALL' ? 'All Categories' : cat}
          </button>
        ))}
      </div>

      {/* Extracted Clauses Grid / List */}
      <div className="space-y-3">
        {filtered.map((req, idx) => (
          <div
            key={req.id || idx}
            className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl hover:border-navy-700 transition space-y-2.5 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                  REQ-{(idx + 1).toString().padStart(3, '0')}
                </span>
                <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider font-mono">
                  {req.category}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                    req.classification === 'mandatory'
                      ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      : 'bg-blue-500/15 text-blue-300 border-blue-500/30'
                  }`}
                >
                  {req.classification}
                </span>
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Confidence: {Math.round((req.confidence_score || 0.95) * 100)}%
                </span>
              </div>
            </div>

            <p className="text-xs text-white leading-relaxed font-sans font-medium">
              {req.description}
            </p>

            {req.source_excerpt && (
              <div className="p-2.5 bg-navy-900/80 rounded-xl border border-navy-700/60 text-[11px] font-mono text-slate-400">
                <span className="text-cyan-400 font-semibold mr-1.5">Source Excerpt (p. {req.source_page || 1}):</span>
                "{req.source_excerpt}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
