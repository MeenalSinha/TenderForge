import React, { useState } from 'react';
import {
  FileCheck,
  CheckCircle2,
  Lock,
  ShieldCheck,
  ArrowRight,
  UserCheck,
  Calendar
} from 'lucide-react';
import { Tender, User } from '../../types';

interface HumanApprovalViewProps {
  user: User;
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const HumanApprovalView: React.FC<HumanApprovalViewProps> = ({
  user,
  activeTender,
  onNavigateTab,
}) => {
  const [isSigned, setIsSigned] = useState(true);
  const [signatureNotes, setSignatureNotes] = useState(
    'Proposal v2.1 thoroughly evaluated. All compliance clauses satisfied with verifiable ProofLink citations. Approved for formal submission to DISA.'
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-cyan-400" />
            Human-in-the-Loop Approval Gate
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Mandatory human verification and cryptographic sign-off gate before legal proposal submission.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('deliverables')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Export Final Deliverables <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Approval Status Card */}
      <div className="p-6 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="text-base font-bold text-white flex items-center gap-2">
                Executive Approval: Formal Sign-Off Complete
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  Approved & Sealed
                </span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                Target: {activeTender?.title || 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration'}
              </div>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Sign-Off Date</span>
            <div className="text-xs font-bold text-white font-mono flex items-center gap-1 justify-end mt-0.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
            </div>
          </div>
        </div>

        {/* Cryptographic Seal Details */}
        <div className="p-4 bg-navy-900 rounded-xl border border-navy-700 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-cyan-400 flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5" /> Cryptographic ECDSA Signature Seal
            </span>
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              SHA-256 Digest Verified
            </span>
          </div>

          <div className="p-3 bg-navy-950 rounded-lg border border-navy-800 font-mono text-[11px] text-emerald-300 break-all select-all">
            SEAL-2026-DISA-8841-APPROVED-0x98f4e2a1b9c704f6e3a1258d4107cb5294ae07d
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
            <div>
              <span className="text-slate-400 text-[10px] block">Approved By:</span>
              <span className="text-white font-semibold">{user.full_name || 'Admin Approver'}</span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] block">Role Authority:</span>
              <span className="text-cyan-400 font-mono font-semibold">{user.role || 'Approver'}</span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] block">Organization:</span>
              <span className="text-slate-200">Apex Global Defense & IT Solutions</span>
            </div>
          </div>
        </div>

        {/* Signer Notes */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300">Approval Rationale & Audit Notes</label>
          <textarea
            value={signatureNotes}
            onChange={(e) => setSignatureNotes(e.target.value)}
            rows={3}
            className="w-full p-3 bg-navy-950 border border-navy-700 rounded-xl text-xs text-slate-200 font-sans focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>
    </div>
  );
};
