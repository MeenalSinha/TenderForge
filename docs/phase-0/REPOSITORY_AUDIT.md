# TenderForge — Phase 0: Repository Audit

## 1. Executive Summary

This repository audit establishes the initial baseline for **TenderForge** (*From Tender to Trustworthy Proposal*), developed for the **Flip the Switch Hackathon 2026** (Track: Best Business Workflow). 

The audit was performed on November 5, 2026, across the workspace directory `C:\Users\Meenal Sinha\Downloads\TenderForge`.

---

## 2. Inventory & Inspection

### 2.1 Directory Structure & Git Baseline
- **Initial State**: The project root directory was completely pristine with no pre-existing files, source code, or configuration manifests.
- **Git Repository**: Initialized clean git tracking (`git init`) to maintain atomic revision history and traceability.
- **Python Environment**:
  - Python runtime: `Python 3.14.2 (CPython, x86_64 / Windows AMD64)`.
  - Package manager: `uv` (v0.10.9) and `pip` (v26.1.2) available.
  - Core installed capabilities in environment: FastAPI 0.141.1, Uvicorn 0.52.1, Pydantic 2.12.5, Pydantic-Settings 2.15.0, SQLAlchemy 2.1.0b3, Alembic 1.13.2, PyPDF 6.21.4, PyMuPDF 2.1, python-docx 1.2.0, openpyxl, PyYAML 6.0.3, pytest 8.2.2, pytest-asyncio 0.23.7, HTTPX 0.28.1.

### 2.2 Component State Matrix

| Component Area | Current State | Reusability | Action Required |
| :--- | :--- | :--- | :--- |
| **Project Root & Config** | Empty | None | Establish `.gitignore`, `.env.example`, `README.md`, centralized YAML configs. |
| **Backend Core** | Not present | None | Create modular FastAPI architecture adhering to strict non-hardcoding rules. |
| **Document Parsers** | Not present | None | Implement modular parser adapters (PDF via PyMuPDF/PyPDF, DOCX via python-docx, TXT, CSV/XLSX). |
| **Tender Intelligence** | Not present | None | Implement provider-neutral AI extraction, external versioned prompt templates, Pydantic schemas. |
| **Database & ORM** | Not present | None | Build SQLAlchemy 2.0 declarative models, Alembic migrations, repository interfaces. |
| **Switch Integration** | Not present | None | Establish clear integration boundary contracts and interfaces for Switch room agents. |
| **Test Suite** | Not present | None | Build unit, integration, API, and security tests with pytest. |
| **Documentation** | Not present | None | Produce all Phase 0 and Phase 1 technical specs and user manuals. |

---

## 3. Identified Technical Challenges & Environmental Considerations

1. **Python 3.14 Compatibility**:
   - Python 3.14 includes stricter deprecation rules and asyncio/typing updates. Libraries such as `pymupdf` issue deprecation warnings when imported as `fitz` (`FutureWarning: The 'fitz' API is deprecated and will be removed in future. Use 'import pymupdf' instead.`).
   - *Mitigation*: Strictly use `import pymupdf` and ensure compatibility in all parser adapters and model type annotations.
2. **Strict Non-Hardcoding Mandate**:
   - Hardcoding company names, tender reference numbers, financial figures, file thresholds, API keys, or prompt strings inside business logic is strictly prohibited.
   - *Mitigation*: Build a centralized configuration architecture using `pydantic-settings` layered with YAML configuration files (`config/application.yaml`, `config/document_processing.yaml`) and external versioned prompt templates (`config/prompts/`).
3. **Graceful Degradation Without Active AI Credentials**:
   - If runtime LLM credentials (OpenAI, Gemini, Anthropic, Ollama, etc.) are omitted, document processing, text extraction, segmentation, and metadata extraction must still work completely without fabricating data or silently failing.
   - *Mitigation*: Implement an explicit `AIProvider` protocol with a `MissingConfigProvider` / `MockProvider` pattern that returns explicit `status="ai_configuration_required"` and transparent diagnostic messaging.
4. **Untrusted Input Security**:
   - Uploaded PDF, DOCX, and TXT documents must be treated as untrusted data (potential zip-bombs, malicious XML entities, path traversal in filenames, or prompt injection attempts).
   - *Mitigation*: Validate file signatures (magic bytes), enforce configurable size limits, sanitize filenames with UUID storage keys, and isolate extracted content as data blocks when passing to AI prompts.

---

## 4. Architectural Baseline & Next Steps

Because there is no legacy technical debt or fragile legacy code to preserve, TenderForge Phase 0 and Phase 1 will be built with a clean, decoupled, layered architecture:
- Layer 1: Core & Configuration (`app/core/`)
- Layer 2: Domain Entities & Enums (`app/domain/`)
- Layer 3: Infrastructure (Database, Storage, Parsers, AI adapters) (`app/infrastructure/`)
- Layer 4: Services Layer (`app/services/`)
- Layer 5: API Layer (`app/api/`)
- Layer 6: Future Switch Integration Contracts (`app/integrations/switch/`)

All recommendations from this audit are formalized in the subsequent Phase 0 specifications.

