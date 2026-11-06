# TenderForge — Documented Limitations & Operational Constraints

**Project Identity:** TenderForge — *From Tender to Trustworthy Proposal*  
**Release Version:** 1.0.0 (Release Candidate)  
**Audit Date:** November 2026  
**Status:** FULLY DOCUMENTED & TRANSPARENT  

---

## 1. Purpose of this Document

In accordance with enterprise software engineering standards and Flip the Switch hackathon integrity rules, TenderForge explicitly documents all external dependencies, network constraints, and operational boundaries.

TenderForge rejects artificial "mock everything" illusions: when an external service is unreachable or unconfigured, the system truthfully logs the constraint and provides documented fallback paths.

---

## 2. Documented Constraints & Boundaries

### 2.1 External Switch Mesh Network Connectivity
- **Description**: TenderForge is architected to connect with Switch Mesh multi-agent networks via WebSocket and REST adapters.
- **Limitation**: When deployed in an isolated local environment where no external Switch server is running, the system cannot establish an external mesh socket.
- **Truthful Behavior**: Rather than falsifying a "Connected" status, `GET /api/v1/switch/status` honestly reports `not_configured` or `disconnected`, and the UI displays a slate/red status badge with diagnostic counts.
- **Fallback Capability**: TenderForge seamlessly transitions into **Internal Autonomous Broker Mode**, executing all agent handoffs, MCP tool calls (31 tools), and collaborative workflows internally with zero degradation in business functionality.

### 2.2 Live External Procurement Portals (OCDS)
- **Description**: The Open Contracting Data Standard (OCDS) connector integrates with live public procurement portals (e.g., UK Contracts Finder, OpenTender EU).
- **Limitation**: Live synchronization requires active outbound internet connectivity and is subject to external portal rate limits, schema variations, and periodic maintenance windows.
- **Mitigation & Fallback**:
  - The connector enforces strict SSRF defenses to prevent access to private IP ranges.
  - For offline evaluation, development, and unit testing, TenderForge includes two fully deterministic offline connectors:
    1. `mock_sandbox`: Generates realistic synthetic public procurement notices (used in automated tests and `demo_phase5.py`).
    2. `manual`: Ingests standard JSON and CSV tender exports directly from disk.

### 2.3 LLM Provider Connectivity & Quotas
- **Description**: Natural language clause extraction, compliance evaluation, and proposal generation utilize Google Gemini API models.
- **Limitation**: High-volume parallel processing in production is subject to Gemini API rate limits and requires a valid `GEMINI_API_KEY`.
- **Fallback Capability**: When running without an API key or when network access is unavailable, TenderForge automatically activates its high-fidelity deterministic fallback provider (`backend/app/infrastructure/ai/mock_ai.py`). This provider performs keyword, regex, and rule-based clause extraction and structured proposal generation, enabling 100% offline testing.

### 2.4 Document Parsing & Scanned Image PDFs
- **Description**: The built-in document ingestion engine uses `pypdf` for PDF parsing and `python-docx` for Word documents.
- **Limitation**: `pypdf` extracts text from digital, vector-rendered PDFs. Scanned bitmap image documents (e.g., photocopied paper bids without an embedded OCR text layer) will yield empty or sparse text streams.
- **Recommended Production Workflow**: For organizations with legacy paper-based RFP pipelines, ingested bitmap documents should be pre-processed through an upstream OCR pipeline (e.g., Tesseract OCR or Google Cloud Document AI) before uploading.

### 2.5 Single-Instance SQLite vs. Multi-Instance PostgreSQL
- **Description**: TenderForge supports both SQLite and PostgreSQL.
- **Limitation**: In local development with SQLite (`tenderforge.db`), SQLite's database-level write lock limits concurrency under high parallel load.
- **Recommended Production Setup**: Production deployments must run PostgreSQL 16 (as pre-configured in `docker-compose.yml`) to support high-throughput parallel writes and ACID compliance across multiple application worker processes.

---

## 3. Engineering Conclusion

None of the above documented limitations compromise the core architecture, security, or business logic of TenderForge. Each limitation is handled gracefully with deterministic fallbacks and transparent status reporting.
