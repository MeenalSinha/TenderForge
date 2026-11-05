# TenderForge — Phase 0: Switch Ecosystem Integration Audit

## 1. Executive Summary

This document presents a technical audit of the **Switch AI** platform (`sandbox-quantum/switch`, documentation at `docs.switchagents.ai`), created by **SandboxAQ** as part of their Flint AI suite. 

The audit evaluates the integration mechanics between Switch and TenderForge to ensure that the Phase 1 backend architecture establishes seamless integration boundaries for the multi-agent collaboration planned in future phases.

---

## 2. Switch Architecture & Core Primitives

### 2.1 What is Switch?
Switch is an open-source, framework-agnostic collaboration platform that connects autonomous AI agents and human teams inside shared communication channels (Slack, Microsoft Teams, Discord, Mattermost, Telegram) and web workspaces. Rather than isolating AI agents in private conversational silos or single-turn prompts, Switch provides shared context, synchronized message history, task tracking, and governance.

### 2.2 Core Architectural Components

```
┌────────────────────────────────────────────────────────┐
│                   Chat / UI Channels                   │
│      (Slack, Teams, Discord, Web Workspace, etc.)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                      Switch Core                       │
│  ┌─────────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │  Room Context   │ │ Event Buffer  │ │ Trust / ROI│  │
│  │   & Documents   │ │ & Router      │ │ Governance │  │
│  └─────────────────┘ └───────────────┘ └────────────┘  │
└───────────────────────────┬────────────────────────────┘
                            │
               Agent Protocol (HTTP + WebSocket)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                      Agent Bridge                      │
└───────┬───────────────────┬───────────────────┬────────┘
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Tender Analyst│    │  Compliance  │    │   Evidence   │  ... [Other Agents]
│    Agent     │    │   Officer    │    │  Researcher  │
└───────┬──────┘    └───────┬──────┘    └───────┬──────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                TenderForge REST / MCP API
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             TenderForge Backend (Phase 1)              │
│       Document Intelligence & Verification Core        │
└────────────────────────────────────────────────────────┘
```

1. **Switch Rooms**:
   - Virtual collaboration environments where multiple human users and AI agents co-exist.
   - Preserves message history, room-level operational guidelines (system instructions), uploaded documents, and shared decisions.
   - An agent can join multiple rooms while isolating context between rooms.

2. **Agent Bridge**:
   - The central gateway providing a persistent WebSocket connection and HTTP API endpoints.
   - Manages agent registration, session handshakes, heartbeat keep-alives, and event distribution.
   - Delivers incoming user queries, room events, and mentions to connected agents via structured event frames.

3. **Switch Agent Protocol**:
   - Event-driven streaming protocol over WebSockets with standard JSON framing.
   - Standard event types include `message.created`, `room.document_uploaded`, `agent.invoked`, `task.status_changed`, and `decision.recorded`.
   - Agents emit actions such as `message.send`, `tool.execute`, `status.update`, and `document.publish`.

4. **Model Context Protocol (MCP) & Provider Agnosticism**:
   - Switch natively supports the Model Context Protocol (MCP) for exposing tools, resources, and documentation to agents.
   - Compatible with multiple agent runtimes (Claude Code, Google ADK, OpenAI Assistants, LangChain, AutoGen, and custom Python daemons).

---

## 3. TenderForge Multi-Agent Collaboration Model

TenderForge designs five specialized agent roles that will operate inside a dedicated **Tender War Room**:

| Agent Role | Primary Focus | Switch Integration Mechanism | TenderForge Backend Invocation |
| :--- | :--- | :--- | :--- |
| **1. Tender Analyst** | Deconstructs tender documents, extracts requirements, identifies critical dates & submission forms. | Switch Room Agent listening to document upload events. | Calls `/api/v1/tenders/{id}/analyze` and `/api/v1/documents/{id}/content`. |
| **2. Compliance Officer** | Cross-checks mandatory criteria (turnover, licenses, certifications) against extracted requirements. | Responds to Tender Analyst findings and human review requests in the room. | Queries requirement schemas and updates compliance matrix state. |
| **3. Evidence Researcher** | Searches internal repository for audited financials, past completion certificates, ISO accreditations. | Subscribes to missing evidence alerts and coordinates with human uploaders. | Uses document intelligence search and ProofLink verification APIs. |
| **4. Proposal Architect** | Drafts evidence-backed technical responses, methodology chapters, and compliance sheets. | Operates in collaborative drafting threads, generating structured sections. | Fetches segmented chunks and verifies claim citations before posting. |
| **5. Bid Auditor** | Independently reviews proposal drafts for consistency, risk indicators, and unverified assertions. | Acts as final gatekeeper in room before human executive sign-off. | Audits ProofLink claims for status `Unsupported` or `Contradicted`. |

---

## 4. Phase 1 vs. Phase 2 Scope Boundary

### Strict Separation of Concerns:
- **Phase 1 (This Phase)**: Focuses entirely on the core backend, document ingestion, multi-format text parsing, normalization, intelligent segmentation, structured tender intelligence models, and RESTful API endpoints.
- **Switch Decoupling**: Phase 1 **must NOT** require a running Switch Core daemon, live WebSocket connection, or external chat application to operate or pass tests.
- **Contract Readiness**: Phase 1 **must** provide clean, versioned interface contracts (`app/integrations/switch/contracts/`) that define how Switch agent bridge adapters will invoke TenderForge services.

---

## 5. Verified Assumptions vs. Unverified Limitations

### 5.1 Verified Switch Capabilities
1. Switch provides HTTP and WebSocket agent protocol connections.
2. Switch allows custom agents written in any language to connect to the Agent Bridge.
3. Switch supports MCP servers for discovering tools and invoking backend operations.
4. Rooms preserve multi-user conversation history and maintain agent operational state.

### 5.2 Unverified Assumptions & Future Questions
1. *WebSocket Session Reconnect Semantics*: Exact retry/backoff parameters on long-lived connections across corporate proxies will need testing against live Switch instances in Phase 2.
2. *Binary Payload Handling*: Large PDF documents should be passed via URL / storage reference rather than raw WebSocket frames to prevent buffer saturation.
3. *Switch Trust CLI Policies*: Enterprise scanning of agent tools will require strict OpenAPI schemas and rate-limiting rules.

---

## 6. Implementation Strategy for Phase 1

1. Implement standard REST API endpoints with comprehensive Pydantic schemas.
2. Expose OpenAPI schemas (`/openapi.json`) for seamless future tool generation by MCP and Switch.
3. Provide mockable agent contract interfaces in `app/integrations/switch/` defining:
   - `TenderIngestionRequest` / `TenderAnalysisRequest`
   - `AgentCommandPayload`
   - `RoomNotificationEvent`
4. Document the exact bridge pattern in `docs/phase-1/FUTURE_SWITCH_INTEGRATION.md`.

