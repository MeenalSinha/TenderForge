import React from 'react';
import {
  GraduationCap,
  Trophy,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Bot
} from 'lucide-react';

interface BidLearningViewProps {
  bidLearning?: any;
}

export const BidLearningView: React.FC<BidLearningViewProps> = ({
  bidLearning,
}) => {
  const winFactors = [
    'Direct FedRAMP High / DoD IL6 provisional authorization package in corporate vault.',
    'Verified CPARS ratings > 4.8 on previous multi-region defense cloud initiatives.',
    'Deterministic Decimal pricing model with 0 round-off ambiguity in CLIN submissions.',
  ];

  const lossPatterns = [
    'Sub-15m operational staffing SLA required explicit named personnel in initial proposal response.',
    'Competitors with local state presence scored higher on municipal emergency response bids.',
  ];

  const agentRecommendations = [
    {
      agent: '@ProposalArchitect',
      recommendation: 'Auto-inject 24/7 dedicated clearance roster matrix into Volume 2 whenever SLA is <= 15 minutes.',
    },
    {
      agent: '@ComplianceOfficer',
      recommendation: 'Flag any state/local municipal pursuit lacking a regional branch office as Medium Risk.',
    },
    {
      agent: '@EvidenceResearcher',
      recommendation: 'Prioritize CPARS evaluation certificates with "Exceptional" ratings for past performance weightings.',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-cyan-400" />
            Closed-Loop Bid Learning & Agent Prompt Refinement
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical post-bid outcome telemetry, debrief analysis, and automated continuous optimization of AI agent prompts.
          </p>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Decided Pursuits</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">
            {bidLearning?.total_decided_bids || 28}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Formal Evaluation Complete</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Contracts Won</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
            {bidLearning?.total_wins || 20}
          </div>
          <div className="text-[11px] text-emerald-400 mt-0.5">\$34.8M Captured Revenue</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Contracts Lost</div>
          <div className="text-2xl font-bold text-rose-400 font-mono mt-1">
            {bidLearning?.total_losses || 8}
          </div>
          <div className="text-[11px] text-rose-300 mt-0.5">Post-Award Debrief Analyzed</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Calculated Win Rate</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">
            {bidLearning?.win_rate_percentage || 71.4}%
          </div>
          <div className="text-[11px] text-cyan-300 mt-0.5">+8.2% vs Industry Average</div>
        </div>
      </div>

      {/* Win Drivers & Loss Reasons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Win Drivers */}
        <div className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3">
          <h3 className="font-bold text-sm text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> Statistically Validated Win Drivers
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {winFactors.map((f, i) => (
              <li key={i} className="flex items-start gap-2 p-2 bg-navy-900 rounded-xl border border-navy-700/60">
                <span className="text-emerald-400 font-bold shrink-0 mt-0.5">✓</span>
                <span className="leading-relaxed">{f}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Loss Patterns */}
        <div className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3">
          <h3 className="font-bold text-sm text-rose-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" /> Debrief Loss Patterns & Root Causes
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {lossPatterns.map((p, i) => (
              <li key={i} className="flex items-start gap-2 p-2 bg-navy-900 rounded-xl border border-navy-700/60">
                <span className="text-rose-400 font-bold shrink-0 mt-0.5">!</span>
                <span className="leading-relaxed">{p}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* AI Agent Automated Optimization Recommendations */}
      <div className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg space-y-3">
        <h3 className="font-bold text-sm text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" /> Automated AI Agent Prompt Fine-Tuning Directives
        </h3>
        <div className="space-y-2">
          {agentRecommendations.map((r) => (
            <div
              key={r.agent}
              className="p-3 bg-navy-900 rounded-xl border border-navy-700 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20">
                  {r.agent}
                </span>
                <span className="text-slate-200">{r.recommendation}</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded shrink-0">
                Prompt Injected
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
