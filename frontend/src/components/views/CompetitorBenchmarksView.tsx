import React from 'react';
import {
  Award,
  Users,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Building
} from 'lucide-react';

interface CompetitorBenchmarksViewProps {
  competitors?: any[];
}

export const CompetitorBenchmarksView: React.FC<CompetitorBenchmarksViewProps> = ({
  competitors = [],
}) => {
  const defaultCompetitors = [
    {
      id: 'comp-1',
      competitor_name: 'General Dynamics Information Technology (GDIT)',
      domain: 'gdit.com',
      observed_tenders: 18,
      estimated_win_rate: 68.5,
      strengths: ['Massive cleared workforce', 'Long-standing DISA relationships', 'Incumbent advantage'],
      weaknesses: ['Higher overhead cost multiplier', 'Legacy software architecture transition speed'],
      pricing_notes: 'Tends to bid at standard GSA Schedule rates with minimal discounting on software licenses.',
    },
    {
      id: 'comp-2',
      competitor_name: 'Leidos Defense Solutions',
      domain: 'leidos.com',
      observed_tenders: 14,
      estimated_win_rate: 62.0,
      strengths: ['DoD IL6 Secret accredited facilities', 'Strong cyber security past performance'],
      weaknesses: ['Subcontractor dependency for tactical edge micro-Kubernetes'],
      pricing_notes: 'Aggressive pricing on fixed-price base periods, escalates on option year staffing.',
    },
    {
      id: 'comp-3',
      competitor_name: 'Booz Allen Hamilton',
      domain: 'boozallen.com',
      observed_tenders: 11,
      estimated_win_rate: 58.0,
      strengths: ['High C-suite strategy influence', 'Consulting & Zero Trust architectural design'],
      weaknesses: ['Lower hardware engineering execution track record vs pure defense integrators'],
      pricing_notes: 'Premium advisory rates; vulnerable to cost-technical tradeoff competitions.',
    },
  ];

  const items = competitors.length > 0 ? competitors : defaultCompetitors;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-cyan-400" />
            Competitor Intelligence & Award Benchmarks
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Historical competitor win rate telemetry, strategic strengths/weaknesses, and empirical price-to-win models.
          </p>
        </div>
      </div>

      {/* Competitor Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {items.map((c: any) => (
          <div
            key={c.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg flex flex-col justify-between space-y-4 hover:border-navy-700 transition"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-sm text-white leading-snug">{c.competitor_name}</h3>
                  <span className="text-[11px] font-mono text-cyan-400">{c.domain}</span>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-sm font-extrabold text-amber-400 font-mono">
                    {c.estimated_win_rate || c.win_rate || 60}%
                  </div>
                  <div className="text-[9px] text-slate-400">Est. Win Rate</div>
                </div>
              </div>

              <div className="text-xs font-mono text-slate-300">
                Observed In: <span className="font-bold text-white">{c.observed_tenders || 12} Pursuits</span>
              </div>

              {/* Strengths */}
              <div className="space-y-1 text-xs">
                <span className="text-[10px] text-emerald-400 uppercase tracking-wider font-mono font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Key Strengths
                </span>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                  {(c.strengths || []).map((s: string) => (
                    <li key={s} className="truncate">{s}</li>
                  ))}
                </ul>
              </div>

              {/* Weaknesses */}
              <div className="space-y-1 text-xs">
                <span className="text-[10px] text-rose-400 uppercase tracking-wider font-mono font-bold flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Exploitable Vulnerabilities
                </span>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                  {(c.weaknesses || []).map((w: string) => (
                    <li key={w} className="truncate">{w}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="pt-3 border-t border-navy-700/60 text-xs">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono block mb-1">
                Pricing Strategy
              </span>
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                {c.pricing_notes || 'Standard defense contractor cost-plus or T&M rate cards.'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
