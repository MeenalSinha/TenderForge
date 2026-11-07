import React from 'react';
import {
  Scale,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  FileCheck,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface BidAuditViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const BidAuditView: React.FC<BidAuditViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const auditChecks = [
    {
      id: 'chk-1',
      title: 'Mandatory RFP Compliance Baseline',
      status: 'PASSED',
      score: 100,
      detail: 'All 14 mandatory solicitations clauses satisfied with direct proof.',
    },
    {
      id: 'chk-2',
      title: 'Evidence Claim Lineage & Hash Integrity',
      status: 'PASSED',
      score: 100,
      detail: 'All 21 claims in proposal draft match verified SHA-256 evidence digests.',
    },
    {
      id: 'chk-3',
      title: 'Pricing & Financial Arithmetic Determinism',
      status: 'PASSED',
      score: 96,
      detail: 'Python Decimal deterministic cost calculation confirmed across 4 option periods.',
    },
    {
      id: 'chk-4',
      title: 'Operational SLA & Staffing Clearance Verifiability',
      status: 'OBSERVATION',
      score: 85,
      detail: '15-minute response SLA requires formal roster shift schedule in Volume 2.',
    },
    {
      id: 'chk-5',
      title: 'Legal & Export Control Compliance (ITAR/EAR)',
      status: 'PASSED',
      score: 100,
      detail: 'No foreign national participation in core tactical mesh code modules.',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Scale className="w-5 h-5 text-cyan-400" />
            Independent Bid Audit & Risk Verification
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Red-team adversarial audit executed by @BidAuditor to identify unsupported claims, pricing risks, and compliance gaps.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('human_approval')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Proceed to Human Sign-Off <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Audit Readiness Score Banner */}
      <div className="p-6 bg-navy-850 border border-navy-700/60 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-5">
          <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
            <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#19284d"
                strokeWidth="3.2"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#22d3ee"
                strokeWidth="3.2"
                strokeDasharray="94.2, 100"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-extrabold text-white font-mono">94.2</span>
              <span className="text-[9px] text-slate-400">Score / 100</span>
            </div>
          </div>
          <div>
            <div className="text-base font-bold text-white flex items-center gap-2">
              Proposal Audit Certification: APPROVED
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Grade A+
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-lg leading-relaxed">
              The proposal has zero unverified factual claims, passes all mandatory evaluation gates, and satisfies the legal standards for DISA submission.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs font-mono shrink-0">
          <div className="p-3 bg-navy-900 rounded-xl border border-navy-700 text-center min-w-[120px]">
            <div className="text-[10px] text-slate-400">Unverified Claims</div>
            <div className="text-lg font-bold text-emerald-400 mt-0.5">0</div>
          </div>
          <div className="p-3 bg-navy-900 rounded-xl border border-navy-700 text-center min-w-[120px]">
            <div className="text-[10px] text-slate-400">Flagged Observations</div>
            <div className="text-lg font-bold text-amber-400 mt-0.5">1</div>
          </div>
        </div>
      </div>

      {/* Audit Checklist Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Audit Evaluation Dimension</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Confidence Score</th>
                <th className="p-3.5">Audit Findings & Evidence Trace</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {auditChecks.map((chk) => (
                <tr key={chk.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 font-bold text-white max-w-xs">
                    {chk.title}
                  </td>
                  <td className="p-3.5 whitespace-nowrap">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold border inline-flex items-center gap-1.5 ${
                        chk.status === 'PASSED'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {chk.status === 'PASSED' ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <AlertTriangle className="w-3 h-3" />
                      )}
                      {chk.status}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-cyan-400 font-bold">
                    {chk.score}%
                  </td>
                  <td className="p-3.5 text-slate-300 leading-relaxed text-xs">
                    {chk.detail}
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

