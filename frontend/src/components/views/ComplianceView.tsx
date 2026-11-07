import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Filter,
  FileCheck,
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import { Tender, ComplianceItem } from '../../types';

interface ComplianceViewProps {
  activeTender?: Tender;
  complianceItems: ComplianceItem[];
  onNavigateTab: (tabId: string) => void;
}

export const ComplianceView: React.FC<ComplianceViewProps> = ({
  activeTender,
  complianceItems,
  onNavigateTab,
}) => {
  const [statusFilter, setStatusFilter] = useState('ALL');

  const displayItems = complianceItems.length > 0 ? complianceItems : [
    {
      id: 'c-1',
      requirement_id: 'REQ-001',
      requirement_text: 'FedRAMP High Authorization must be active and verifiable on DOD Cloud Marketplace.',
      compliance_status: 'Compliant' as const,
      risk_level: 'Low' as const,
      evidence_claim: 'Active FedRAMP High Authorization ATO #FR-2025-9941 verifiable in vault.',
      clarification_notes: 'Verified against FedRAMP Marketplace registry on 2026-10-15.'
    },
    {
      id: 'c-2',
      requirement_id: 'REQ-002',
      requirement_text: 'Impact Level 6 (IL6) Secret enclave security compliance for classified workloads.',
      compliance_status: 'Compliant' as const,
      risk_level: 'Low' as const,
      evidence_claim: 'DoD IL6 Provisional Authorization package valid through 2027.',
      clarification_notes: 'Dedicated isolated hardware tenancy matches DISA STIG guidelines.'
    },
    {
      id: 'c-3',
      requirement_id: 'REQ-003',
      requirement_text: 'Zero Trust Architecture adherence across all ingress/egress transit gateways.',
      compliance_status: 'Compliant' as const,
      risk_level: 'Low' as const,
      evidence_claim: 'NIST SP 800-207 Zero Trust audit report by Mandiant Security.',
      clarification_notes: 'Continuous mTLS and micro-segmentation policies enforced.'
    },
    {
      id: 'c-4',
      requirement_id: 'REQ-004',
      requirement_text: '24/7/365 US citizen on-soil dedicated clearance support with 15-minute response SLA.',
      compliance_status: 'Clarification Needed' as const,
      risk_level: 'Medium' as const,
      evidence_claim: 'Current SOC staffed with TS/SCI US personnel, Tier-1 SLA is currently 20 mins.',
      clarification_notes: 'Remediation plan to assign dedicated standby engineer to satisfy 15m SLA.'
    },
    {
      id: 'c-5',
      requirement_id: 'REQ-005',
      requirement_text: 'Demonstrated past performance on at least 2 multi-region defense cloud contracts > $10M.',
      compliance_status: 'Compliant' as const,
      risk_level: 'Low' as const,
      evidence_claim: 'Past Performance Reference: US Air Force Cloud One ($14.2M) and Navy SeaPort-NxG ($11.8M).',
      clarification_notes: 'CPARS ratings: Exceptional across all evaluation criteria.'
    }
  ];

  const filtered = displayItems.filter(
    (item) => statusFilter === 'ALL' || item.compliance_status === statusFilter
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
            Compliance Center & Matrix Evaluation
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Requirement-by-requirement gap analysis, risk tiering, and evidence validation certified by @ComplianceOfficer.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('prooflink')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Trace ProofLink Evidence <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Compliance Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Overall Readiness</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">94.2%</div>
          <div className="text-[11px] text-emerald-400 mt-0.5">Compliant Base</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Compliant Requirements</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">12</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Fully Satisfied & Evidenced</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Partial / Clarification</div>
          <div className="text-2xl font-bold text-amber-400 font-mono mt-1">2</div>
          <div className="text-[11px] text-amber-300/80 mt-0.5">Remediation Action Defined</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Non-Compliant / Gaps</div>
          <div className="text-2xl font-bold text-rose-400 font-mono mt-1">0</div>
          <div className="text-[11px] text-emerald-400 mt-0.5">Zero Disqualifying Gaps</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto text-xs">
        {['ALL', 'Compliant', 'Clarification Needed', 'Non-Compliant'].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`px-3 py-1.5 rounded-xl font-medium transition ${
              statusFilter === st
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/30'
                : 'bg-navy-850 hover:bg-navy-800 text-slate-400 hover:text-slate-200 border border-navy-700/60'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Compliance Matrix Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Clause / Requirement</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Evidence Claim</th>
                <th className="p-3.5">Risk Level</th>
                <th className="p-3.5">Auditor Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {filtered.map((item, idx) => (
                <tr key={item.id || idx} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 max-w-sm">
                    <div className="font-bold text-white text-xs">
                      {item.requirement_id || `REQ-00${idx + 1}`}
                    </div>
                    <div className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                      {item.requirement_text}
                    </div>
                  </td>
                  <td className="p-3.5 whitespace-nowrap">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold border inline-flex items-center gap-1.5 ${
                        item.compliance_status === 'Compliant'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : item.compliance_status === 'Clarification Needed'
                          ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      }`}
                    >
                      {item.compliance_status === 'Compliant' ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <AlertTriangle className="w-3 h-3" />
                      )}
                      {item.compliance_status}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-300 text-[11px] leading-relaxed max-w-xs font-mono">
                    {item.evidence_claim || 'Evidence verified in vault.'}
                  </td>
                  <td className="p-3.5 whitespace-nowrap">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                        item.risk_level === 'Low'
                          ? 'text-emerald-400 bg-emerald-500/10'
                          : item.risk_level === 'Medium'
                          ? 'text-amber-400 bg-amber-500/10'
                          : 'text-rose-400 bg-rose-500/10'
                      }`}
                    >
                      {item.risk_level}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-400 text-[11px] max-w-xs leading-relaxed">
                    {item.clarification_notes || 'No clarification required.'}
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
