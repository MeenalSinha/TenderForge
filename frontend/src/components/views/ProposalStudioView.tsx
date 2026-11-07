import React, { useState } from 'react';
import {
  FileText,
  Save,
  RefreshCw,
  Eye,
  Edit3,
  Link2,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface ProposalStudioViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const ProposalStudioView: React.FC<ProposalStudioViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const [activeSection, setActiveSection] = useState('executive_summary');
  const [isEditing, setIsEditing] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  const sections: Record<string, { title: string; content: string }> = {
    executive_summary: {
      title: '1. Executive Summary & Solution Alignment',
      content: `### Executive Summary

Apex Global Defense and IT Solutions is pleased to submit this comprehensive, evidence-backed proposal for the **Joint Multi-Domain Command and Control (JADC2) Cloud Integration** initiative (*DOD-DISA-2026*).

Our architecture is engineered specifically to meet the high-assurance requirements of DISA, providing an enterprise-grade cloud mesh that delivers sub-50ms tactical edge synchronization, strict DoD Impact Level 6 (IL6) Secret isolation, and certified Zero Trust transit gateways [ProofLink: FedRAMP_High_ATO_p14].

With over a decade of defense cloud modernization experience—demonstrated on the Air Force Cloud One ($14.2M) and Navy SeaPort-NxG initiatives [ProofLink: USAF_CloudOne_p4]—our team guarantees zero-downtime transition, continuous STIG compliance, and 24/7/365 US citizen TS/SCI operational clearance support.`,
    },
    technical_architecture: {
      title: '2. Technical Architecture & Hybrid Mesh',
      content: `### Technical Architecture

The proposed TenderForge hybrid tactical cloud architecture consists of three federated tiers:
1. **Core Command Hub:** Hosted across dual FedRAMP High regions with active-active high availability and automated disaster recovery failover under 30 seconds.
2. **Tactical Edge Enclaves:** Hardware-isolated edge nodes running micro-Kubernetes clusters capable of operating autonomously during disconnected, intermittent, or limited bandwidth (DDIL) conditions.
3. **Zero Trust Data Plane:** All inter-domain communications enforce cryptographic mutual TLS (mTLS 1.3), attribute-based access control (ABAC), and continuous policy evaluation following NIST SP 800-207 guidelines [ProofLink: Mandiant_ZeroTrust_p28].`,
    },
    compliance_security: {
      title: '3. Compliance, Cybersecurity & Risk Governance',
      content: `### Compliance & Security Governance

Our security implementation exceeds the mandatory baselines set forth in the solicitation:
- **FedRAMP High:** Provisional Authorization ATO #FR-2025-9941 maintained on DOD Cloud Marketplace.
- **DoD IL6 Clearance:** Hardware-separated cryptographic enclaves certified for Secret security domains [ProofLink: DoD_IL6_PA_p6].
- **CMMC Level 3:** Verified third-party assessment certification covering all 110 NIST SP 800-171 controls.
- **Incident Response:** Dedicated Tier-3 Security Operations Center (SOC) staffed exclusively by cleared US citizens with guaranteed 15-minute response SLA.`,
    },
    cost_model: {
      title: '4. Financial BOQ & Resource Allocation Model',
      content: `### Financial Model & Pricing Structure

Our transparent pricing model leverages Python Decimal deterministic arithmetic to prevent round-off distortions across multi-year option periods:
- **Base Year 1 Cost:** $4,725,000.00 USD (Software licensing, engineering rollout, and DISA onboarding).
- **Option Years 2-4:** $2,591,666.67 USD annually (Operations, 24/7 cleared SOC, continuous maintenance).
- **Total Evaluated Price:** $12,500,000.00 USD (Guaranteed firm-fixed-price ceiling).`,
    },
  };

  const current = sections[activeSection] || sections.executive_summary;

  const handleSave = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Proposal Studio & Drafting Workspace
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Collaborative proposal drafting by @ProposalArchitect with inline ProofLink citations and automated fact verification.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {savedNotice && (
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-1 animate-fade-in">
              <CheckCircle2 className="w-3.5 h-3.5" /> Changes Persisted
            </span>
          )}
          <button
            onClick={handleSave}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            <Save className="w-3.5 h-3.5" /> Save Revision
          </button>
          <button
            onClick={() => onNavigateTab('bid_audit')}
            className="px-3.5 py-1.5 bg-navy-800 hover:bg-navy-750 border border-navy-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-1.5 transition"
          >
            Run Bid Audit <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Proposal Editor & Preview Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Section List */}
        <div className="lg:col-span-4 bg-navy-850 border border-navy-700/60 rounded-2xl p-4 shadow-lg space-y-2">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-2 pb-2 border-b border-navy-700/60">
            Proposal Document Sections
          </div>
          {Object.entries(sections).map(([key, sec]) => (
            <button
              key={key}
              onClick={() => setActiveSection(key)}
              className={`w-full text-left p-3 rounded-xl text-xs transition duration-150 flex items-center justify-between ${
                activeSection === key
                  ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-900/40'
                  : 'text-slate-400 hover:text-white hover:bg-navy-800/80 border border-transparent'
              }`}
            >
              <span className="truncate">{sec.title}</span>
              <span className="text-[10px] font-mono opacity-80 shrink-0">v2.1</span>
            </button>
          ))}

          <div className="pt-4 border-t border-navy-700/60 mt-4 space-y-2">
            <div className="text-[11px] font-mono text-cyan-400">Inline ProofLink Citations</div>
            <div className="p-2.5 bg-navy-900 rounded-xl border border-navy-700 text-[11px] text-slate-300 space-y-1">
              <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <Link2 className="w-3 h-3" /> 4 Verified Citations
              </div>
              <p className="text-[10px] text-slate-400">
                Every assertion in this section maps to an immutable evidence file in the enterprise vault.
              </p>
            </div>
          </div>
        </div>

        {/* Right Section Canvas */}
        <div className="lg:col-span-8 bg-navy-850 border border-navy-700/60 rounded-2xl p-6 shadow-lg flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-navy-700/60">
            <div className="font-bold text-sm text-white">{current.title}</div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="px-2.5 py-1 rounded-lg bg-navy-900 border border-navy-700 text-xs text-slate-300 hover:text-white flex items-center gap-1"
              >
                {isEditing ? <Eye className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
                {isEditing ? 'Preview' : 'Edit'}
              </button>
            </div>
          </div>

          {isEditing ? (
            <textarea
              defaultValue={current.content}
              className="w-full h-80 p-4 bg-navy-950 border border-navy-700 rounded-xl text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
            />
          ) : (
            <div className="p-4 bg-navy-950/70 border border-navy-700/50 rounded-xl text-xs leading-relaxed font-sans text-slate-200 whitespace-pre-line overflow-y-auto max-h-96">
              {current.content}
            </div>
          )}

          <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-xs text-slate-400">
            <span>Author: @ProposalArchitect • Evidence Verified</span>
            <span className="font-mono text-[11px] text-cyan-400">Cryptographic Seal Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

