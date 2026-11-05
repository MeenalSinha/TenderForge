# TENDERFORGE — SWITCH ECOSYSTEM SETUP GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Prerequisites & Environment

To connect TenderForge to a live Switch daemon or Mattermost chat instance:
- **Switch Daemon:** `sandbox-quantum/switch` v1.4+ (or Switch Cloud workspace).
- **Chat Backend:** Mattermost Team Edition v9.x+ (or Slack / Teams / Discord / Web).
- **Python Environment:** Python 3.11+ (Python 3.14.2 verified) with FastAPI, Uvicorn, SQLAlchemy.
- **Network Access:** WebSocket or HTTP connectivity between the Switch Agent Bridge and the TenderForge API server.

---

## 2. Configuration Parameters

Add the following environment variables to your `.env` file:

```bash
# Switch Ecosystem Integration
SWITCH_ENABLED=true
SWITCH_BRIDGE_URL=ws://localhost:8080/v1/bridge
SWITCH_API_KEY=tf_switch_sec_99887766554433221100
SWITCH_CHANNEL_BACKEND=mattermost  # mattermost, slack, teams, discord, web_mock
SWITCH_DEFAULT_TEAM=federal-procurement

# Mattermost Integration (when using Mattermost backend)
MATTERMOST_URL=http://localhost:8065
MATTERMOST_BOT_TOKEN=mm_bot_token_secret_here
MATTERMOST_TEAM_ID=team_fed_defense_01

# AI Model Configuration
AI_PROVIDER=openai  # or mock, gemini, anthropic
AI_MODEL_NAME=gpt-4o
AI_API_KEY=your_llm_api_key_here
```

---

## 3. Registering Specialized Agents in Switch

Switch registers agents via bot tokens or standard Agent Protocol handshakes. Each agent is registered with its handle and system prompt:

1. **Tender Analyst:** `@TenderAnalyst` (`config/agents/tender_analyst.yaml`)
2. **Compliance Officer:** `@ComplianceOfficer` (`config/agents/compliance_officer.yaml`)
3. **Evidence Researcher:** `@EvidenceResearcher` (`config/agents/evidence_researcher.yaml`)
4. **Proposal Architect:** `@ProposalArchitect` (`config/agents/proposal_architect.yaml`)
5. **Bid Auditor:** `@BidAuditor` (`config/agents/bid_auditor.yaml`)

---

## 4. Model Context Protocol (MCP) Server Setup

TenderForge provides standard Model Context Protocol endpoints:
- **Tool Listing:** `GET /api/v1/switch/tools`
- **Tool Execution:** `POST /api/v1/switch/tools/execute`

To register TenderForge in your Switch MCP configuration file (`mcp_servers.json`):
```json
{
  "mcpServers": {
    "tenderforge": {
      "command": "python",
      "args": ["-m", "backend.app.main"],
      "env": {
        "AI_PROVIDER": "mock",
        "DATABASE_URL": "sqlite:///./tenderforge.db"
      }
    }
  }
}
```

---

## 5. Standalone & Testing Modes

TenderForge includes a built-in headless `MockSwitchBridge` mode. When `SWITCH_ENABLED=false` or when running automated CI/CD tests, all room event streams, slash commands, and tool dispatches operate in-memory without requiring external daemons.
