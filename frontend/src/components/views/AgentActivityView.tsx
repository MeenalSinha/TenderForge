import React from 'react';
import {
  Bot,
  CheckCircle2,
  Clock,
  Shield,
  Zap,
  Terminal,
  Activity,
  Layers,
  ArrowRight
} from 'lucide-react';

interface AgentActivityViewProps {
  switchStatus: any;
  onNavigateTab: (tabId: string) => void;
}

export const AgentActivityView: React.FC<AgentActivityViewProps> = ({
  switchStatus,
  onNavigateTab,
}) => {
  const agents = [
    {
      id: 'ag-1',
      name: 'Tender Analyst',
      handle: '@TenderAnalyst',
      role: 'Requirements & Clause Extraction',
      description: 'Extracts mandatory clauses, eligibility rules, and compliance criteria from unstructured tenders.',
      model: 'Switch Multi-Agent / Deep Document Engine',
      status: 'AVAILABLE',
      completedOps: 48,
      lastActive: '2m ago',
      tools: ['parse_tender_pdf', 'extract_clauses', 'classify_requirements', 'detect_deadlines'],
    },
    {
      id: 'ag-2',
      name: 'Compliance Officer',
      handle: '@ComplianceOfficer',
      role: 'Compliance Matrix & Gap Remediation',
      description: 'Constructs audit compliance matrices, flags compliance gaps, and verifies pass/fail gates.',
      model: 'Switch Multi-Agent / Logic Reasoning',
      status: 'AVAILABLE',
      completedOps: 36,
      lastActive: '3m ago',
      tools: ['evaluate_matrix', 'flag_gaps', 'score_eligibility', 'suggest_remediation'],
    },
    {
      id: 'ag-3',
      name: 'Evidence Researcher',
      handle: '@EvidenceResearcher',
      role: 'ProofLink & Evidence Retrieval',
      description: 'Discovers verified corporate evidence, checks cryptographic integrity, and binds citations.',
      model: 'Switch Multi-Agent / Vault Retriever',
      status: 'AVAILABLE',
      completedOps: 52,
      lastActive: '5m ago',
      tools: ['search_evidence_vault', 'verify_sha256', 'bind_prooflink', 'detect_contradictions'],
    },
    {
      id: 'ag-4',
      name: 'Proposal Architect',
      handle: '@ProposalArchitect',
      role: 'Evidence-Backed Proposal Drafting',
      description: 'Generates structured proposal volumes with strict citation grounding and deterministic BOQs.',
      model: 'Switch Multi-Agent / Proposal Generator',
      status: 'AVAILABLE',
      completedOps: 29,
      lastActive: '7m ago',
      tools: ['draft_proposal_section', 'embed_citations', 'calculate_boq', 'format_export_bundle'],
    },
    {
      id: 'ag-5',
      name: 'Bid Auditor',
      handle: '@BidAuditor',
      role: 'Adversarial Red-Team Audit',
      description: 'Independent auditor testing for unsupported claims, legal liabilities, and pricing errors.',
      model: 'Switch Multi-Agent / Red-Team Auditor',
      status: 'AVAILABLE',
      completedOps: 31,
      lastActive: '10m ago',
      tools: ['adversarial_audit', 'verify_claim_lineage', 'score_readiness', 'issue_audit_certificate'],
    },
  ];

  const isMeshConnected = switchStatus?.status === 'connected' || switchStatus?.mesh_connected;
  const isBroker = switchStatus?.internal_broker_active || switchStatus?.status === 'connected';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            AI Agent Subsystem & Mesh Registry
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Status, registered MCP tools, execution history, and capability boundaries for the 5 specialized AI agents.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('war_room')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Open Switch War Room <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Connectivity Banner */}
      <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white flex items-center gap-2">
              Subsystem Mode:{' '}
              {isMeshConnected
                ? 'Switch Mesh Synchronized'
                : isBroker
                ? 'Internal Agent Broker Active'
                : 'Offline'}
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                5 Agents Online
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              {switchStatus?.message || 'Switch Multi-Agent orchestration broker fully operational.'}
            </div>
          </div>
        </div>
        <div className="text-xs font-mono text-cyan-400 bg-navy-900 px-3 py-2 rounded-xl border border-navy-700 shrink-0">
          MCP Tools Registered: {switchStatus?.tools_registered || 31}
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((ag) => (
          <div
            key={ag.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg flex flex-col justify-between space-y-4 hover:border-navy-700 transition"
          >
            <div className="space-y-2.5">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-sm text-white">{ag.name}</h3>
                  <span className="text-xs font-mono text-cyan-400 font-semibold">{ag.handle}</span>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> {ag.status}
                </span>
              </div>

              <div className="text-[11px] font-semibold text-slate-300 font-mono">
                {ag.role}
              </div>

              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                {ag.description}
              </p>

              <div className="space-y-1.5 pt-1">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">
                  Permitted MCP Tools
                </div>
                <div className="flex flex-wrap gap-1">
                  {ag.tools.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 bg-navy-900 border border-navy-750 text-[10px] font-mono text-slate-300 rounded"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-navy-700/60 text-xs font-mono flex items-center justify-between text-slate-400">
              <span>Ops: {ag.completedOps} completed</span>
              <span className="text-slate-500">Active {ag.lastActive}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

