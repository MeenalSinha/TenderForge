import React from 'react';
import {
  FileDiff,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldAlert,
  FileText
} from 'lucide-react';
import { Tender } from '../../types';

interface AmendmentsViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const AmendmentsView: React.FC<AmendmentsViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const amendments = [
    {
      id: 'amend-1',
      amendment_number: 1,
      title: 'Corrigendum 01: Submission Deadline Extended & Security Clarification',
      issued_date: '2026-11-02',
      materiality: 'MODERATE',
      approval_invalidated: false,
      diff_summary: 'Submission deadline moved from Dec 01 to Dec 15, 2026. Added explicit DoD IL6 testing matrix references.',
      impact_sections: ['Submission Schedule', 'Compliance Matrix (REQ-002)'],
    },
    {
      id: 'amend-2',
      amendment_number: 2,
      title: 'Corrigendum 02: Pricing CLIN Template & Labor Rate Caps Published',
      issued_date: '2026-11-04',
      materiality: 'CRITICAL',
      approval_invalidated: true,
      diff_summary: 'Updated government pricing workbook CLIN-0004 with maximum hourly rate ceiling for TS/SCI personnel.',
      impact_sections: ['Financial BOQ (CLIN-0004)', 'Executive Sign-Off Gate'],
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileDiff className="w-5 h-5 text-cyan-400" />
            Amendment Intelligence & Corrigendum Impact Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated semantic diff analysis, downstream requirement invalidation detection, and human re-approval triggers.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('compliance')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Review Compliance Updates <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Target Tender Banner */}
      <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider">
            {activeTender?.reference_number || 'DOD-DISA-2026'}
          </span>
          <h3 className="font-bold text-sm text-white mt-0.5">
            {activeTender?.title || 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration'}
          </h3>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
          2 Formal Corrigenda Analyzed
        </span>
      </div>

      {/* Amendments List */}
      <div className="space-y-4">
        {amendments.map((a) => (
          <div
            key={a.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                    Amendment #{a.amendment_number}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">Issued {a.issued_date}</span>
                </div>
                <h3 className="font-bold text-sm text-white mt-1.5">{a.title}</h3>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono border ${
                    a.materiality === 'CRITICAL'
                      ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                  }`}
                >
                  {a.materiality} MATERIALITY
                </span>
                {a.approval_invalidated && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950/80 text-rose-200 border border-rose-800">
                    Requires Sign-Off Re-Sealing
                  </span>
                )}
              </div>
            </div>

            <div className="p-3 bg-navy-900 rounded-xl border border-navy-700/60 text-xs text-slate-200 font-mono leading-relaxed">
              <span className="text-cyan-400 font-bold mr-1">Diff Summary:</span>
              {a.diff_summary}
            </div>

            <div className="pt-2 flex items-center gap-2 text-xs">
              <span className="text-slate-400 text-[11px] font-mono">Impacted Modules:</span>
              {a.impact_sections.map((sec) => (
                <span
                  key={sec}
                  className="px-2 py-0.5 bg-navy-950 border border-navy-700 text-[10px] font-mono text-cyan-300 rounded"
                >
                  {sec}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
