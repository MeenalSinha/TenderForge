# TenderForge — Phase 1: Future Switch Ecosystem Integration Guide

## 1. Overview & Architectural Boundary

The **Switch AI** platform (`sandbox-quantum/switch`, `docs.switchagents.ai`), built by **SandboxAQ**, enables multi-agent collaboration between humans and specialized AI agents inside shared communication channels (Slack, Microsoft Teams, Discord, Mattermost, Telegram) and web workspaces.

### 1.1 Scope Decoupling Principle
- **Phase 1 (Completed)**: Implements the self-contained backend, document parsers, segmentation engine, database models, and RESTful API endpoints. The application is completely functional and testable without a live Switch daemon or chat platform.
- **Phase 2 (Future)**: Connects Switch Rooms and the Switch Agent Bridge to TenderForge services, activating the five specialized agents in a shared **Tender War Room**.

---

## 2. Multi-Agent Collaboration Model in Switch

In future phases, TenderForge will establish a dedicated Switch room for each active procurement response:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Switch Tender War Room                          │
│               (Slack / Teams / Discord / Web Workspace)                │
│                                                                        │
│   [Human Bid Manager]  [Human Legal/Finance]  [Specialized AI Agents]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                       Switch Agent Bridge (WS/HTTP)
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Specialized Switch Room Agents                       │
│                                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Tender Analyst  │  │Compliance Officer│  │ Evidence Researcher  │  │
│  │ (Deconstructs doc│  │(Evaluates pass/  │  │ (Finds certificates, │  │
│  │  & requirements) │  │ fail criteria)   │  │  audits, past work)  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘  │
│           │                     │                       │              │
│           │            ┌────────┴─────────┐  ┌──────────┴───────────┐  │
│           │            │Proposal Architect│  │     Bid Auditor      │  │
│           │            │(Drafts evidence- │  │(Reviews consistency, │  │
│           │            │ backed responses)│  │ risks & citations)   │  │
│           │            └────────┬─────────┘  └──────────┬───────────┘  │
└───────────┼─────────────────────┼───────────────────────┼──────────────┘
            │                     │                       │
            └─────────────────────┼───────────────────────┘
                                  │ REST / MCP Calls
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      TenderForge Backend Core                          │
│       Document Intelligence, ProofLink Engine, Persistence             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Specialized Agent Role Mappings

| Role | Switch Room Trigger | TenderForge Service Invocation |
| :--- | :--- | :--- |
| **1. Tender Analyst** | `room.document_uploaded` event | Calls `POST /api/v1/documents` and `POST /api/v1/tenders/{id}/analyze`. Publishes extracted requirements summary with citations to the room. |
| **2. Compliance Officer** | Tender Analyst completion or user mention `@Compliance` | Evaluates mandatory clauses against company parameters. Flags missing criteria (e.g., turnover gap, missing ISO) as room warnings. |
| **3. Evidence Researcher** | Missing evidence warnings or user request | Queries the internal document intelligence repository for supporting certificates, past completion records, and CVs. |
| **4. Proposal Architect** | User command `/draft-section [title]` | Uses segmented context and mapped evidence to generate proposal chapters with embedded ProofLink citations. |
| **5. Bid Auditor** | Proposal section ready for review | Audits drafts for unverified claims, status `Unsupported` or `Contradicted`, and flags potential disqualification risks. |

---

## 4. Implemented Integration Contracts in Phase 1

The following typed contracts have been established in `backend/app/integrations/switch/`:

### 4.1 `SwitchRoomContext` & `SwitchRoomParticipant`
Represents the active room metadata, participant identities, and operational guidelines:
```python
class SwitchRoomContext(BaseModel):
    room_id: str
    room_name: str
    channel_type: str  # slack, teams, discord, web
    participants: List[SwitchRoomParticipant]
    system_instructions: Optional[str]
```

### 4.2 `SwitchAgentCommand`
Command frame emitted by Switch agents when invoking TenderForge capabilities:
```python
class SwitchAgentCommand(BaseModel):
    command_id: str
    command_name: str  # analyze_document, audit_claims, match_evidence
    agent_role: str
    parameters: Dict[str, Any]
    timestamp: datetime
```

### 4.3 `SwitchRequirementCitation` & `SwitchRoomNotification`
ProofLink-compatible event notification broadcasted back to the room:
```python
class SwitchRequirementCitation(BaseModel):
    requirement_id: str
    category: str
    classification: str
    source_document_id: str
    source_page: int
    source_offset: int
    source_excerpt: str
    confidence_score: float

class SwitchRoomNotification(BaseModel):
    room_id: str
    event_type: str
    title: str
    summary: str
    citations: List[SwitchRequirementCitation]
    metadata: Dict[str, Any]
    timestamp: datetime
```

### 4.4 `BaseSwitchAgentBridge`
Abstract adapter interface in `backend/app/integrations/switch/interfaces/agent_bridge.py` ready to be subclassed by the Phase 2 WebSocket/HTTP connector.

---

## 5. Model Context Protocol (MCP) Tool Exposure

Because TenderForge generates strict OpenAPI 3.1 definitions (`/openapi.json`), exposing tools to Switch via MCP in Phase 2 is straightforward:
- `tenderforge_upload_document(file, category)`
- `tenderforge_get_content(document_id)`
- `tenderforge_create_tender(title, reference_number, document_ids)`
- `tenderforge_analyze_tender(tender_id)`
- `tenderforge_get_requirements(tender_id)`

These tools can be plugged directly into the Switch Provider Registry or invoked via standard Agent Protocol frames.

