# TENDERFORGE — SWITCH ROOM EVENT STREAM GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Event-Driven Architecture

The **Switch Room Event Stream** (`backend/app/integrations/switch/event_stream.py`) broadcasts real-time agent utterances, progress milestones, ProofLink citations, and governance events to the Tender War Room.

It bridges asynchronous backend service operations with synchronous conversational chat channels (Mattermost, Slack, Teams, or WebSockets).

---

## 2. Event Types & Payloads

### 2.1 Agent Utterance (`agent.message`)
Emitted whenever an agent completes an action, hands off to a colleague, or requests clarification:
```json
{
  "room_id": "chan_eb5fbbefe6f1",
  "event_type": "agent.message",
  "title": "Tender Analyst (@TenderAnalyst)",
  "summary": "Completed document intelligence on tender specification. Extracted 6 mandatory requirements. Handing off to @ComplianceOfficer.",
  "citations": [],
  "metadata": {
    "agent_handle": "@TenderAnalyst",
    "mentions": ["@ComplianceOfficer"],
    "action_items": [],
    "timestamp": "2026-11-05T08:02:29.487101+00:00"
  }
}
```

### 2.2 ProofLink Grounding Citation (`prooflink.citation`)
Transmitted when evidence is matched or cited:
```json
{
  "requirement_id": "req_889911",
  "category": "financial",
  "classification": "mandatory",
  "source_document_id": "doc_112233",
  "source_page": 1,
  "source_offset": 140,
  "source_excerpt": "Minimum annual turnover of USD 3,000,000 required.",
  "confidence_score": 0.95
}
```

### 2.3 Milestone Reached (`milestone.reached`)
Emitted when key lifecycle gates are crossed (e.g. `COMPLIANCE_EVALUATED`, `AUDIT_COMPLETED`, `BID_APPROVED`).

---

## 3. Streaming & Subscription API

External frontends and Switch bot adapters subscribe to the event stream using:
- **WebSocket Streaming:** `ws://host/api/v1/switch/stream` for real-time token and event delivery.
- **REST History Fallback:** `GET /api/v1/switch/rooms/{tender_id}/history` to retrieve prior utterances and reconstruct chat history upon channel reconnection.
