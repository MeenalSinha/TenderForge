import React, { useState } from 'react';
import {
  Zap,
  Send,
  Bot,
  User,
  CheckCircle2,
  Clock,
  Sparkles,
  Terminal,
  ShieldAlert
} from 'lucide-react';
import { Tender, User as UserType } from '../../types';

interface SwitchWarRoomViewProps {
  user: UserType;
  activeTender?: Tender;
  switchStatus: any;
  onSendCommand?: (cmd: string) => Promise<any>;
}

export const SwitchWarRoomView: React.FC<SwitchWarRoomViewProps> = ({
  user,
  activeTender,
  switchStatus,
  onSendCommand,
}) => {
  const [messages, setMessages] = useState<any[]>([
    {
      id: 'm-1',
      sender: 'Human Lead',
      senderRole: 'Bid Director',
      handle: user.email,
      timestamp: '10:00 AM',
      content: 'Team, let us kick off analysis for DOD JADC2 Cloud Integration (DOD-DISA-2026). @TenderAnalyst, please extract all mandatory security clauses.',
      isAgent: false,
    },
    {
      id: 'm-2',
      sender: 'Tender Analyst',
      senderRole: 'AI Clause Extraction',
      handle: '@TenderAnalyst',
      timestamp: '10:01 AM',
      content: 'Acknowledged. Extracted 14 critical requirements from DOD-DISA-2026. Primary gates: FedRAMP High, DoD IL6 Secret enclave, NIST 800-207 Zero Trust, and US citizen 15m response SLA. Passing to @ComplianceOfficer.',
      isAgent: true,
      agentColor: 'emerald',
    },
    {
      id: 'm-3',
      sender: 'Compliance Officer',
      senderRole: 'AI Compliance Evaluation',
      handle: '@ComplianceOfficer',
      timestamp: '10:02 AM',
      content: 'Compliance matrix evaluated. 12 Compliant, 2 Partial (15-min SLA staffing schedule). Overall readiness is 94.2%. Zero disqualifying fatal flaws detected. Requesting evidence links from @EvidenceResearcher.',
      isAgent: true,
      agentColor: 'cyan',
    },
    {
      id: 'm-4',
      sender: 'Evidence Researcher',
      senderRole: 'AI Evidence Intelligence',
      handle: '@EvidenceResearcher',
      timestamp: '10:03 AM',
      content: 'ProofLink mappings established! Anchored FedRAMP High ATO #FR-2025-9941, DoD IL6 provisional package, and USAF Cloud One CPARS ($14.2M). All cryptographic hashes matched against the corporate vault.',
      isAgent: true,
      agentColor: 'indigo',
    },
    {
      id: 'm-5',
      sender: 'Proposal Architect',
      senderRole: 'AI Proposal Studio',
      handle: '@ProposalArchitect',
      timestamp: '10:04 AM',
      content: 'Proposal Draft v2.1 compiled across 4 core sections. Inline ProofLink citations embedded for all factual claims. Ready for adversarial red-team audit by @BidAuditor.',
      isAgent: true,
      agentColor: 'purple',
    },
    {
      id: 'm-6',
      sender: 'Bid Auditor',
      senderRole: 'AI Adversarial Audit',
      handle: '@BidAuditor',
      timestamp: '10:05 AM',
      content: 'Adversarial audit completed. Readiness score: 94.2/100. 0 unverified claims. Risk profile: LOW. Ready for executive human sign-off.',
      isAgent: true,
      agentColor: 'amber',
    },
  ]);

  const [inputVal, setInputVal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const userMsg = {
      id: `m-${Date.now()}`,
      sender: user.full_name,
      senderRole: user.role,
      handle: user.email,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: inputVal,
      isAgent: false,
    };

    setMessages((prev) => [...prev, userMsg]);
    const cmd = inputVal;
    setInputVal('');
    setIsSubmitting(true);

    try {
      if (onSendCommand) {
        const resp = await onSendCommand(cmd);
        if (resp && resp.message) {
          const agentMsg = {
            id: `m-resp-${Date.now()}`,
            sender: resp.agent_name || 'Switch Mesh Coordinator',
            senderRole: 'Switch Multi-Agent',
            handle: resp.agent_handle || '@SwitchBroker',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            content: resp.message,
            isAgent: true,
            agentColor: 'cyan',
          };
          setMessages((prev) => [...prev, agentMsg]);
        }
      } else {
        // Fallback local agent response simulation
        setTimeout(() => {
          const agentMsg = {
            id: `m-resp-${Date.now()}`,
            sender: 'Switch Agent Mesh',
            senderRole: 'Coordinated Response',
            handle: '@SwitchCoordinator',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            content: `Instruction received: "${cmd}". Specialized AI agents are processing the tender context.`,
            isAgent: true,
            agentColor: 'cyan',
          };
          setMessages((prev) => [...prev, agentMsg]);
          setIsSubmitting(false);
        }, 600);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const agents = [
    { handle: '@TenderAnalyst', role: 'Clause Extraction', color: 'bg-emerald-400' },
    { handle: '@ComplianceOfficer', role: 'Matrix Evaluation', color: 'bg-cyan-400' },
    { handle: '@EvidenceResearcher', role: 'ProofLink Vault', color: 'bg-indigo-400' },
    { handle: '@ProposalArchitect', role: 'Proposal Studio', color: 'bg-purple-400' },
    { handle: '@BidAuditor', role: 'Adversarial Audit', color: 'bg-amber-400' },
  ];

  return (
    <div className="space-y-4 flex flex-col h-[calc(100vh-130px)] animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-navy-700/60 shrink-0">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            Switch War Room — Multi-Agent Collaboration
          </h2>
          <p className="text-xs text-slate-400">
            Real-time collaboration channel connecting human bid managers with 5 specialized AI agents over the Switch broker.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Switch Mesh: {switchStatus.status === 'connected' ? 'Connected' : 'Local Broker Active'}
          </span>
        </div>
      </div>

      {/* Agents Status Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 shrink-0">
        {agents.map((ag) => (
          <div
            key={ag.handle}
            className="p-2.5 bg-navy-850 border border-navy-700/60 rounded-xl flex items-center gap-2 shadow-sm"
          >
            <span className={`w-2 h-2 rounded-full ${ag.color} shrink-0`} />
            <div className="overflow-hidden">
              <div className="text-[11px] font-bold text-white truncate">{ag.handle}</div>
              <div className="text-[9px] text-slate-400 font-mono truncate">{ag.role}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Message Chat Canvas */}
      <div className="flex-1 overflow-y-auto bg-navy-850 border border-navy-700/60 rounded-2xl p-4 space-y-4 shadow-inner">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-start gap-3 text-xs ${
              m.isAgent ? 'bg-navy-900/60 p-3 rounded-xl border border-navy-700/50' : 'p-3'
            }`}
          >
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-white font-bold text-xs ${
                m.isAgent
                  ? 'bg-gradient-to-tr from-cyan-600 to-blue-600 border border-cyan-400/30'
                  : 'bg-navy-750 border border-navy-700'
              }`}
            >
              {m.isAgent ? <Bot className="w-4 h-4 text-cyan-300" /> : <User className="w-4 h-4 text-slate-300" />}
            </div>

            <div className="flex-1 overflow-hidden space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-xs">{m.sender}</span>
                  <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded">
                    {m.handle}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">{m.timestamp}</span>
              </div>
              <p className="text-slate-200 text-xs leading-relaxed font-sans">{m.content}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Chat Command Input Bar */}
      <form onSubmit={handleSend} className="flex items-center gap-2 shrink-0">
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Send a prompt or command (e.g. /analyze, /compliance, /audit)..."
          className="flex-1 px-4 py-2.5 bg-navy-850 border border-navy-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 shadow-md font-sans"
        />
        <button
          type="submit"
          disabled={isSubmitting || !inputVal.trim()}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition shrink-0"
        >
          <Send className="w-3.5 h-3.5" /> Send
        </button>
      </form>
    </div>
  );
};
