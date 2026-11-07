import React from 'react';
import {
  History,
  CheckCircle2,
  Lock,
  UserCheck,
  Bot,
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface WorkflowHistoryViewProps {
  activeTender?: Tender;
}

export const WorkflowHistoryView: React.FC<WorkflowHistoryViewProps> = ({
  activeTender,
}) => {
  const events = [
    {
      id: 'ev-1',
      stage: 'Executive Approval Gate',
      title: 'Formal Executive Approval & Cryptographic Seal Issued',
      actor: 'Admin Approver (Human)',
      type: 'HUMAN',
      timestamp: 'Today, 11:30 AM',
      hash: 'SEAL-2026-DISA-8841-APPROVED-0x98f4e2a1b9',
      details: 'All 14 mandatory clauses verified. Proposal v2.1 approved for submission.',
    },
    {
      id: 'ev-2',
      stage: 'Independent Bid Audit',
      title: 'Red-Team Adversarial Audit Completed (94.2/100)',
      actor: '@BidAuditor (AI Agent)',
      type: 'AGENT',
      timestamp: 'Today, 10:45 AM',
      hash: 'AUDIT-SHA256-4b82d901f4c782103a88e91d520',
      details: 'Zero unverified factual claims detected. Low operational risk profile.',
    },
    {
      id: 'ev-3',
      stage: 'Proposal Studio',
      title: 'Proposal Draft v2.1 Generated & ProofLink Anchored',
      actor: '@ProposalArchitect (AI Agent)',
      type: 'AGENT',
      timestamp: 'Today, 10:15 AM',
      hash: 'PROP-v2.1-7a8e91b0c3d4f5e6a7b8c9d0e1f',
      details: '4 sections authored with inline ProofLink citations for FedRAMP & IL6.',
    },
    {
      id: 'ev-4',
      stage: 'ProofLink Traceability',
      title: 'Cryptographic Lineage Mapping Completed',
      actor: '@EvidenceResearcher (AI Agent)',
      type: 'AGENT',
      timestamp: 'Today, 09:40 AM',
      hash: 'PROOF-HASH-e3b0c44298fc1c149afbf4c8996',
      details: '21 evidence claims bound to certified corporate vault PDF documents.',
    },
    {
      id: 'ev-5',
      stage: 'Compliance Evaluation',
      title: 'Compliance Matrix Evaluated (94.2% Pass Rate)',
      actor: '@ComplianceOfficer (AI Agent)',
      type: 'AGENT',
      timestamp: 'Today, 09:10 AM',
      hash: 'COMP-MAT-99214b7e889a1c0d2e3f4a5b6c7',
      details: '12 Compliant, 2 Partial with remediation, 0 non-compliant gaps.',
    },
    {
      id: 'ev-6',
      stage: 'Tender Ingestion',
      title: 'Tender Solicitation Notice Ingested & Clauses Extracted',
      actor: '@TenderAnalyst (AI Agent)',
      type: 'AGENT',
      timestamp: 'Today, 08:30 AM',
      hash: 'INGEST-DOD-DISA-2026-0x12a884fc901b2e',
      details: '14 key evaluation clauses extracted from RFP solicitation PDF.',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            Workflow & Immutable Decision History
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tamper-evident audit trail recording every agent execution, human approval, and stage progression.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5" /> Immutable Hash Log
        </span>
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
        <span className="text-xs font-mono text-slate-400">
          6 Lifecycle Events Recorded
        </span>
      </div>

      {/* Timeline Stream */}
      <div className="relative pl-6 space-y-6 before:content-[''] before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-navy-700">
        {events.map((ev, idx) => (
          <div key={ev.id} className="relative flex items-start gap-4 text-xs">
            {/* Circle Node */}
            <div
              className={`absolute -left-6 top-1 w-5 h-5 rounded-full flex items-center justify-center ring-4 ring-navy-950 ${
                ev.type === 'HUMAN'
                  ? 'bg-emerald-500 text-white'
                  : 'bg-cyan-500 text-white'
              }`}
            >
              {ev.type === 'HUMAN' ? (
                <UserCheck className="w-3 h-3" />
              ) : (
                <Bot className="w-3 h-3" />
              )}
            </div>

            <div className="flex-1 p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-md space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-white">{ev.title}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20">
                    {ev.stage}
                  </span>
                </div>
                <span className="text-[11px] font-mono text-slate-400 shrink-0">
                  {ev.timestamp}
                </span>
              </div>

              <p className="text-slate-300 font-sans leading-relaxed">{ev.details}</p>

              <div className="pt-2 border-t border-navy-700/60 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] font-mono text-slate-500 gap-1">
                <span>Actor: {ev.actor}</span>
                <span className="truncate max-w-sm text-emerald-400/80">Hash: {ev.hash}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

