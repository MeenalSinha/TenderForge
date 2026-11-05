# TenderForge Switch Integration Expansion

## 1. Overview & Switch Multi-Agent Collaboration

Switch is the collaborative multi-agent communication substrate powering the Flip the Switch Hackathon.

In Phase 3, Switch integration is expanded to:
1. **Model Context Protocol (MCP) Expansion**: Expanded tool catalogue from 17 to 26 tools.
2. **Proactive Deadline Alerts**: Real-time message broadcasting into tender rooms.
3. **Multi-Agent Room Routing**: Contextual command routing for financial modeling, risk analysis, and optimization.

---

## 2. Phase 3 MCP Tool Catalogue

| Tool Name | Caller Permission | Description |
|---|---|---|
| `evaluate_bid_decision` | Agent / Human | Runs multi-dimensional bid viability scoring. |
| `audit_evidence_freshness` | Agent / Human | Scans repository for expiring and obsolete evidence. |
| `detect_evidence_contradictions` | Agent / Human | Discovers conflicting numerical claims across documents. |
| `manage_financial_proposal` | Agent / Human | Creates BOQ and performs exact Decimal calculations. |
| `generate_pricing_scenarios` | Agent / Human | Compares Base Case, Conservative, and Aggressive models. |
| `harvest_bid_risks` | Agent / Human | Centralizes risks across compliance, evidence, and commercials. |
| `optimize_proposal_coverage` | Agent / Human | Produces Before/After enhancement suggestions. |
| `validate_proposal_quality` | Agent / Human | Inspects placeholders, word counts, and formatting hygiene. |
| `get_portfolio_summary` | Agent / Human | Returns executive pipeline metrics and win rates. |

---

## 3. Human Governance Guardrails

As established in Phase 2, `record_human_decision` is hardcoded as **human-only**:
```python
if caller_type == "agent" and tool_name in ("record_human_decision",):
    raise SecurityError(f"Agent '{caller_id}' is strictly forbidden from executing human governance tool '{tool_name}'.")
```
Agents attempting to approve their own proposals are immediately rejected with a `SecurityError`.
