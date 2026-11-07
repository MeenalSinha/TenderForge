import React, { useState } from 'react';
import {
  CheckSquare,
  Award,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import { Tender, Requirement } from '../../types';

interface RequirementsViewProps {
  activeTender?: Tender;
  requirements: Requirement[];
  onNavigateTab: (tabId: string) => void;
}

export const RequirementsView: React.FC<RequirementsViewProps> = ({
  activeTender,
  requirements,
  onNavigateTab,
}) => {
  const evaluationCriteria = [
    {
      id: 'crit-1',
      name: 'Technical Architecture & Tactical Mesh Capability',
      weightage: 35,
      minScore: 80,
      achievedScore: 95,
      status: 'EXCEEDS',
      description: 'Low-latency multi-domain routing, DDIL edge autonomy, and dual-region failover.',
    },
    {
      id: 'crit-2',
      name: 'Cybersecurity, FedRAMP High & IL6 Clearance',
      weightage: 30,
      minScore: 90,
      achievedScore: 98,
      status: 'EXCEEDS',
      description: 'Zero Trust architecture, hardware enclave isolation, and continuous STIG compliance.',
    },
    {
      id: 'crit-3',
      name: 'Past Performance on Major Defense Cloud Modernizations',
      weightage: 20,
      minScore: 75,
      achievedScore: 94,
      status: 'EXCEEDS',
      description: 'Demonstrated execution on multi-region contracts exceeding $10M in value (USAF Cloud One).',
    },
    {
      id: 'crit-4',
      name: 'Pricing Realism & BOQ Cost Effectiveness',
      weightage: 15,
      minScore: 70,
      achievedScore: 90,
      status: 'COMPLIANT',
      description: 'Transparent firm-fixed-price structure with guaranteed SLA staffing models.',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-cyan-400" />
            Requirements & Evaluation Criteria Weighting
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Formal solicitation evaluation scoring model, section weightings, and compliance threshold validation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('bid_decision')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Review Bid/No-Bid Strategy <ArrowRight className="w-3.5 h-3.5" />
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
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
          Total Evaluation Weight: 100%
        </span>
      </div>

      {/* Criteria Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {evaluationCriteria.map((c) => (
          <div
            key={c.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3"
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="font-bold text-sm text-white leading-snug">{c.name}</h4>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 shrink-0">
                {c.weightage}% Weight
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans">{c.description}</p>

            <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">Passing Threshold: {c.minScore}%</span>
              <span className="text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Achieved: {c.achievedScore}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
