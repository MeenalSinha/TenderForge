# TenderForge Phase 4: Switch War Room Collaboration UI

## 1. Overview & Switch Integration Architecture

The **Switch War Room** is the collaborative command center where human procurement specialists, bid directors, and five specialized AI agents interact in real time. TenderForge connects to the Switch multi-agent collaboration platform to coordinate complex multi-step workflows.

```
+-----------------------------------------------------------------------------------------+
|                                    SWITCH WAR ROOM                                      |
+-----------------------------------------------------------------------------------------+
|  [Agent Cards Grid]                                                                     |
|  +--------------------+ +--------------------+ +--------------------+ +---------------+ |
|  |  Tender Analyst    | |  Evidence Finder   | |  Proposal Writer   | |  Compliance   | |
|  |  Status: ACTIVE    | |  Status: READY     | |  Status: STREAMING | |  Status: IDLE | |
|  |  Tools: doc_parser | |  Tools: sem_search | |  Tools: prooflink  | |  Tools: audit | |
|  +--------------------+ +--------------------+ +--------------------+ +---------------+ |
+-----------------------------------------------------------------------------------------+
|  [Left: Real-Time Event Stream]              |  [Right: War Room Collaborative Chat]    |
|  14:32:01 [Tender Analyst] Parsed 48 clauses |  Bid Manager: "Check ISO 27001 expiry"   |
|  14:32:05 [Evidence] Matched cert #CERT-881  |  Evidence Agent: "Valid until Nov 2027   |
|  14:32:12 [Proposal] Drafted Section 3.2.1   |  [ProofLink: REF-ISO-2027]."             |
|  14:32:20 [Compliance] 0 contradictions      |  Bid Manager: "Approved for inclusion."  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. The 5 Specialized Collaborative Agents

Each agent has bounded responsibilities, dedicated system instructions, and authorized tool permissions:

1. **`tender_analyst` (Tender Intelligence Specialist)**:
   - Evaluates tender specifications, extracts technical clauses, and identifies mandatory vs. optional eligibility requirements.
   - Authorized Tools: `parse_document_tool`, `extract_clauses_tool`, `classify_requirements_tool`.
2. **`evidence_finder` (Corporate Evidence Discovery Specialist)**:
   - Searches historical past performance records, audited financials, and compliance certifications.
   - Authorized Tools: `search_evidence_tool`, `verify_prooflink_tool`, `audit_cert_freshness_tool`.
3. **`proposal_writer` (Proposal Section Authoring Specialist)**:
   - Drafts compliant, persuasive proposal narrative strictly grounded in verified prooflink evidence.
   - Authorized Tools: `draft_section_tool`, `embed_citation_tool`, `align_criteria_tool`.
4. **`compliance_officer` (Independent Validation & Anti-Hallucination Officer)**:
   - Performs adversarial cross-checking against tender rules, verifies prooflink citations, and flags factual contradictions.
   - Authorized Tools: `verify_compliance_tool`, `detect_contradictions_tool`, `flag_unsupported_claims_tool`.
5. **`bid_strategist` (Commercial & Viability Strategist)**:
   - Evaluates commercial competitiveness, monitors profit margins, executes bid/no-bid gating, and assesses risks.
   - Authorized Tools: `compute_viability_radar_tool`, `check_hard_gates_tool`, `model_boq_scenarios_tool`.

---

## 3. Real-Time Event Streaming & Coordination
- **Event Bus Protocol**: Server-Sent Events (SSE) stream tool execution events to connected clients via `/api/v1/switch/rooms/{room_id}/events`.
- **Tool Execution Tracing**: Every tool invocation logs its inputs, execution latency, and return status to the collaborative event stream.
- **Human Interruption & Override**: Humans can halt automated agent execution at any moment, inject guidance, or reject proposed proposal edits.

---

## 4. UI Implementation Features
- **Live Pulse Indicators**: Dynamic green pulsing rings signify active reasoning or tool execution for each agent.
- **Action Timeline**: Visual chronological feed categorizing agent actions by urgency (`info`, `warning`, `critical`).
- **One-Click Human Approvals**: Integrated action buttons in the chat feed allow bid managers to approve or revise agent-drafted sections with a single click.
