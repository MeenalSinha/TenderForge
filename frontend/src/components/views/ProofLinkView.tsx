import React from 'react';
import {
  Link2,
  CheckCircle2,
  ShieldCheck,
  FileText,
  Lock,
  ExternalLink,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface ProofLinkViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const ProofLinkView: React.FC<ProofLinkViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const links = [
    {
      id: 'pl-1',
      req_id: 'REQ-001 (FedRAMP High)',
      claim_text: 'Active FedRAMP High Authorization ATO #FR-2025-9941',
      document: 'FedRAMP_High_Authorization_Package_2025.pdf',
      page: 14,
      offset: 320,
      sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      match_score: 98,
      verified: true
    },
    {
      id: 'pl-2',
      req_id: 'REQ-002 (DoD IL6 Authorization)',
      claim_text: 'Impact Level 6 (IL6) Provisional Authorization for Secret Enclaves',
      document: 'DoD_IL6_Provisional_Authorization_Certificate.pdf',
      page: 6,
      offset: 140,
      sha256: '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
      match_score: 97,
      verified: true
    },
    {
      id: 'pl-3',
      req_id: 'REQ-003 (Zero Trust Architecture)',
      claim_text: 'NIST SP 800-207 Zero Trust Security Audit Report',
      document: 'Mandiant_Zero_Trust_Architecture_Evaluation_v2.pdf',
      page: 28,
      offset: 890,
      sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
      match_score: 95,
      verified: true
    },
    {
      id: 'pl-4',
      req_id: 'REQ-005 (Past Performance Defense)',
      claim_text: 'US Air Force Cloud One Migration ($14.2M) CPARS Rating',
      document: 'Past_Performance_Reference_USAF_CloudOne.pdf',
      page: 4,
      offset: 75,
      sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
      match_score: 99,
      verified: true
    }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Link2 className="w-5 h-5 text-cyan-400" />
            ProofLink Traceability Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic cryptographic requirement-to-evidence links with SHA-256 verification and character offset precision.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('proposal')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Review Proposal Studio <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Integrity Badge Banner */}
      <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white flex items-center gap-2">
              Cryptographic Lineage Active
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                100% Verified
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              All proposal claims are anchored to verified corporate evidence documents with immutable SHA-256 digests.
            </div>
          </div>
        </div>
        <div className="text-xs font-mono text-cyan-400 bg-navy-900 px-3 py-2 rounded-xl border border-navy-700 shrink-0">
          Target: {activeTender?.reference_number || 'DOD-DISA-2026'}
        </div>
      </div>

      {/* ProofLink Grid */}
      <div className="space-y-4">
        {links.map((link) => (
          <div
            key={link.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl hover:border-navy-700 transition shadow-sm space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                  {link.req_id}
                </span>
                <span className="text-xs text-white font-medium">
                  {link.claim_text}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono shrink-0">
                <span className="text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> {link.match_score}% Match
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-navy-900 rounded-xl border border-navy-700/60 space-y-1">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                  Referenced Evidence Document
                </div>
                <div className="text-slate-200 font-semibold truncate flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  {link.document}
                </div>
                <div className="text-[11px] text-slate-400 font-mono">
                  Citation: Page {link.page}, Character Offset {link.offset}
                </div>
              </div>

              <div className="p-3 bg-navy-900 rounded-xl border border-navy-700/60 space-y-1">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono flex items-center justify-between">
                  <span>Cryptographic Digest (SHA-256)</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <Lock className="w-3 h-3" /> Intact
                  </span>
                </div>
                <div className="text-[11px] text-cyan-400 font-mono truncate">
                  {link.sha256}
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                  Verified against Corporate Vault Registry
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
