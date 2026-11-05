# TENDERFORGE — SWITCH ECOSYSTEM & IMPLEMENTATION AUDIT

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Competition:** Flip the Switch Hackathon 2026 (Best Business Workflow)  
**Phase:** Phase 2 Implementation Audit  
**Date:** November 2026  

---

## 1. Executive Summary

The Switch ecosystem (developed by SandboxAQ, `sandbox-quantum/switch`, `docs.switchagents.ai`) provides a foundational architecture for orchestrating multi-agent collaboration among specialized AI personas and human experts within conversational environments (Mattermost, Slack, Teams, Discord, and Web Workspaces).

This audit evaluates the Switch implementation mechanisms, protocol specifications, integration patterns, Model Context Protocol (MCP) tool exposure, and architectural constraints required to embed TenderForge into a collaborative Tender War Room.

---

## 2. Switch Ecosystem Components & Protocols

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Switch Communication Plane                      │
│                  (Mattermost / Slack / Web Channels)                   │
├────────────────────────────────────────────────────────────────────────┤
│  #tender-rfp-2026-001  [Bid Manager, Legal Counsel, Technical Lead]    │
│  @TenderAnalyst  @ComplianceOfficer  @EvidenceResearcher               │
│  @ProposalArchitect  @BidAuditor                                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         WebSocket / HTTP Stream
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Switch Agent Bridge                             │
│  - Handshake & Authentication (Bearer Token / API Key)                 │
│  - Agent Protocol Frame Parser (Events, Messages, Commands)            │
│  - Session & Room State Tracking                                       │
│  - Heartbeat & Auto-reconnect Resilience                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      TenderForge MCP & Tool Layer                      │
│  16 Deterministic Function Tools (Document, Evidence, Matrix, Proposal)│
│  Role-Based Execution Guardrails & Permission Matrix                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        TenderForge Core Services                       │
│  ProofLink Matching • Compliance Engine • Proposal Architect • Audit  │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Switch Agent Bridge Architecture
1. **Transport Layer:** Dual-mode transport:
   - **WebSocket Transport:** Low-latency bi-directional event stream for real-time room messaging, progress notifications, typing indicators, and streaming tokens.
   - **HTTP REST Fallback:** Standardized webhook endpoints and polling fallbacks when firewall or proxy restrictions prevent persistent WebSocket connections.
2. **Agent Protocol Frames:** Structured JSON envelopes conforming to the Agent Protocol specification:
   - `HANDSHAKE`: Agent registration, capability advertisement, and room joining.
   - `EVENT`: Room broadcast event (e.g. document uploaded, user mention, milestone achieved).
   - `COMMAND`: Slash-command or direct tool invocation issued by a participant.
   - `RESPONSE`: Result payload or execution status returned to the room.
   - `HEARTBEAT`: Ping/pong keepalive maintaining active connection status.

### 2.2 Model Context Protocol (MCP) Integration
Switch natively adopts Anthropic's Model Context Protocol (MCP) as its standardized tool abstraction. TenderForge acts as an MCP Server exposing typed tools with JSON Schema parameter definitions:
- Agents query tools dynamically via `tools/list`.
- Agents execute actions via `tools/call` with strict argument validation.
- Tool responses are returned as structured JSON containing content excerpts, ProofLink citations, and status flags.

### 2.3 Mattermost Chat Backend Integration
When deployed on premises or in private enterprise clouds, Switch commonly couples with a Mattermost team chat instance:
- **Tender War Room Channel:** Dedicated channel created per procurement (e.g., `~tender-rfp-2026-001`).
- **Bot Personas:** Each specialized agent is registered as a Mattermost bot account with custom avatar, display name, and role description.
- **Interactive Message Attachments:** Switch renders interactive message cards with action buttons (e.g., `[Approve Requirement]`, `[Review Evidence]`, `[Confirm Sign-off]`).

---

## 3. Specialized Multi-Agent Role Topology

TenderForge orchestrates five specialized agents inside the Switch Room:

| Agent Name | Room Handle | Persona / Role | Permitted Tools | Core Output |
| :--- | :--- | :--- | :--- | :--- |
| **Tender Analyst** | `@TenderAnalyst` | Document Intelligence Specialist | `get_tender_overview`, `analyze_tender`, `get_tender_requirements` | Extracted clauses, deadlines, scope, mandatory criteria with page citations. |
| **Compliance Officer** | `@ComplianceOfficer` | Regulatory & Legal Evaluator | `evaluate_compliance`, `get_compliance_matrix`, `request_human_review` | Compliance matrix (Pass/Fail/Risk), gap analyses, clarification requests. |
| **Evidence Researcher** | `@EvidenceResearcher` | Corporate Evidence Specialist | `upload_company_evidence`, `search_company_evidence`, `get_evidence_details` | Verified certificates, past project sheets, financial statements, ProofLink matches. |
| **Proposal Architect** | `@ProposalArchitect` | Technical Writer & Solution Lead | `create_proposal_draft`, `get_proposal_revision` | Grounded proposal sections with embedded ProofLink citations; zero fabrication. |
| **Bid Auditor** | `@BidAuditor` | Independent Quality & Risk Assessor | `audit_proposal`, `get_audit_report` | Discrepancy reports, unsupported claim flags, readiness score (0-100%). |

---

## 4. Architectural Boundaries & Decoupling Principle

To guarantee resilience, maintainability, and testability:
1. **Zero Hard Dependency on Switch Daemon:** TenderForge core services (parsing, matching, compliance, drafting, auditing) are fully operational and testable via REST API and Python service interfaces without a live Switch instance.
2. **Pluggable Agent Bridge Adapter:** The Switch Agent Bridge is implemented as an integration layer adapter (`backend/app/integrations/switch/agent_bridge.py`) that translates incoming Switch frames into TenderForge service calls and broadcasts outbound notifications.
3. **Mock Switch Bridge for Continuous Testing:** A deterministic in-memory `MockSwitchBridge` allows the entire multi-agent collaboration lifecycle to be tested headlessly in CI/CD without external network dependencies.
4. **Nothing Hardcoded:** All agent definitions (prompts, tool permissions, model temperatures, token limits) and room configurations reside in external YAML files in `config/agents/` and `config/application.yaml`.

---

## 5. Security and Governance Alignment

1. **Role-Based Tool Authorization:** Agents cannot invoke tools outside their authorized scope (e.g. `@ProposalArchitect` cannot invoke `audit_proposal` or `record_human_decision`).
2. **Immutable Human Authority:** Only human users with the `Bid Director` or `Authorized Signatory` role can invoke `record_human_decision` for final submission approval.
3. **Auditable Room History:** Every agent utterance, command execution, tool result, and human confirmation is logged with UTC timestamp, user/agent ID, and correlation ID.
4. **Data Privacy & Secret Redaction:** API keys, sensitive commercial formulas, and employee personal data are scrubbed before messages are transmitted across the chat bridge.

---

## 6. Implementation Readiness Verdict

The Switch ecosystem architecture is well understood, clearly bounded, and ready for Phase 2 integration.
