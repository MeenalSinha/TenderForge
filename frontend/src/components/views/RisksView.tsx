import React, { useState } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Clock,
  ArrowRight,
  Filter
} from 'lucide-react';
import { Tender } from '../../types';

interface RisksViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const RisksView: React.FC<RisksViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const [levelFilter, setLevelFilter] = useState('ALL');

  const risks = [
    {
      id: 'r-1',
      title: 'DoD IL6 Hardware Enclave Supply Chain Lead Times',
      category: 'Technical / Infrastructure',
      severity: 'Medium',
      probability: 'Low',
      mitigation: 'Pre-allocate reserved dedicated hardware nodes under existing DISA BPA agreement.',
      status: 'MITIGATED',
      owner: 'Lead Systems Architect',
    },
    {
      id: 'r-2',
      title: '15-Minute SLA Staffing Roster Coverage during Shift Handoff',
      category: 'Operational',
      severity: 'Low',
      probability: 'Medium',
      mitigation: 'Double-staff overlap hours with TS/SCI cleared rotational standby engineers.',
      status: 'MITIGATED',
      owner: 'VP of SOC Operations',
    },
    {
      id: 'r-3',
      title: 'Foreign Component Dependencies in Micro-Kubernetes Edge Stack',
      category: 'Compliance / Legal',
      severity: 'High',
      probability: 'Very Low',
      mitigation: 'Pure open-source CNCF vetted dependencies strictly built from audited US mirrors.',
      status: 'RESOLVED',
      owner: 'Chief Security Officer',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-cyan-400" />
            Bid Risk Register & Governance Matrix
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Continuous risk identification, exposure scoring, and verified mitigation strategies across the bid lifecycle.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('bid_audit')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Review Audit Findings <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Total Risks Tracked</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">3 Identified</div>
          <div className="text-[11px] text-emerald-400 mt-0.5">100% Mitigated / Controlled</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Residual Risk Exposure</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">Low (12.4%)</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Well within tolerance ceiling</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Governance Gate Status</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">PASSED</div>
          <div className="text-[11px] text-cyan-300/80 mt-0.5">Approved for commercial sign-off</div>
        </div>
      </div>

      {/* Risks Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Risk Description & Category</th>
                <th className="p-3.5">Severity / Probability</th>
                <th className="p-3.5">Mitigation Action</th>
                <th className="p-3.5">Owner</th>
                <th className="p-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {risks.map((r) => (
                <tr key={r.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 max-w-sm">
                    <div className="font-bold text-white text-xs">{r.title}</div>
                    <div className="text-[11px] text-cyan-400 font-mono mt-0.5">{r.category}</div>
                  </td>
                  <td className="p-3.5 whitespace-nowrap font-mono text-[11px]">
                    <span className="text-amber-400">{r.severity}</span> / <span className="text-slate-400">{r.probability}</span>
                  </td>
                  <td className="p-3.5 text-slate-200 text-xs leading-relaxed max-w-md">
                    {r.mitigation}
                  </td>
                  <td className="p-3.5 text-slate-300 text-xs whitespace-nowrap">
                    {r.owner}
                  </td>
                  <td className="p-3.5 whitespace-nowrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

