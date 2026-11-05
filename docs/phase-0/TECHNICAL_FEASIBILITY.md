# TenderForge — Phase 0: Technical Feasibility Assessment

## 1. Executive Summary

This assessment evaluates the architectural feasibility, operational dependencies, performance characteristics, and potential risks of the technology stack selected for **TenderForge Phase 0 & Phase 1**.

---

## 2. Technology Stack Evaluation

| Subsystem | Selected Technology | Justification & Compatibility | Alternatives Evaluated | Risk & Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** (`0.141.1`) + **Uvicorn** (`0.52.1`) | High-performance asynchronous ASGI framework; native Pydantic v2 integration; automated OpenAPI 3.1 documentation generation; robust dependency injection. Fully validated on Python 3.14. | Flask, Django REST Framework, Litestar | *Low Risk*: FastAPI is widely adopted and industry standard for AI-driven backends. |
| **Data Validation & Schemas** | **Pydantic v2** (`2.12.5`) + **Pydantic-Settings** (`2.15.0`) | Up to 10x faster validation using Rust core (`pydantic-core`); strict type coercion; deep JSON schema generation for AI structured outputs; robust configuration hierarchy management. | Marshmallow, Cerberus, Attrs | *Very Low Risk*: Native to FastAPI ecosystem. |
| **Persistence & ORM** | **SQLAlchemy 2.0** (`2.1.0b3`) + **Alembic** (`1.13.2`) | Enterprise-grade ORM with modern 2.0 type-safe syntax; zero-lockout database abstraction supporting SQLite for zero-setup local dev/test and PostgreSQL for production concurrency; automated schema migrations. | Peewee, Tortoise ORM, Raw SQL | *Low Risk*: Ensure connection pooling and transactions are scoped per request via FastAPI dependencies. |
| **Document Processing (PDF)** | **PyMuPDF** (`2.1.0`) with **PyPDF** (`6.21.4`) fallback | Extremely fast C-backed rendering engine; accurate page-by-page text extraction, font information, and block coordinate detection; robust handling of complex multi-column government tenders. | pdfplumber, Tesseract (direct) | *Notice*: In Python 3.14, `pymupdf` warns against using deprecated `fitz` import; use `import pymupdf` directly. |
| **Document Processing (DOCX)** | **python-docx** (`1.2.0`) | Reliable parsing of Office Open XML (.docx); structured access to paragraphs, heading styles, and multi-row/multi-column tables. | docx2txt, Pandoc | *Low Risk*: Malformed zip archives handled safely with strict size/file validation. |
| **Document Processing (Spreadsheets)** | **openpyxl** + Python standard `csv` | Sheet-by-sheet and cell coordinate extraction for financial pricing schedules, Bills of Quantities (BOQ), and equipment compliance tables. | pandas, calamine | *Low Risk*: Avoid loading massive formulas by extracting cell values only (`data_only=True`). |
| **AI Integration Engine** | **Provider-Neutral Adapter Architecture** | Decouples business logic from proprietary LLM SDKs. Supports OpenAI, Google Gemini, Anthropic, Ollama, and a configurable local/mock provider. | Direct SDK coupling (e.g. raw openai calls) | *Critical*: Runtime AI provider is distinct from developer coding assistant. If no API key is provided, pipeline must never hallucinate results; it returns `ai_configuration_required`. |
| **Configuration Engine** | **Pydantic-Settings + YAML** | Strict priority: CLI args > Environment Variables > `.env` file > YAML defaults > Built-in application fallbacks. Complete elimination of hardcoded operational values. | Decouple, dynaconf | *Very Low Risk*: Fully typed with clear validation failure messages on boot. |
| **Storage Layer** | **Abstract FileSystemAdapter** | Local file system storage with safe SHA-256 / UUID partitioning for Phase 1; clean protocol interface allows dropping in S3/GCS adapters in future phases without altering domain logic. | Direct `open()` calls in routes | *Low Risk*: Directory traversal mitigated through path normalization and UUID filenames. |
| **Testing Harness** | **pytest** (`8.2.2`) + **pytest-asyncio** + **httpx** | Async test runner; fixtures for clean SQLite databases and mock document streams; isolated temporary storage directories. | unittest | *Very Low Risk*: Industry standard. |

---

## 3. Runtime AI Independence & Governance Principle

A critical distinction must be enforced throughout TenderForge:

> **Development Assistant vs. Application Runtime AI:**
> The assistant writing the code (Claude, Codex, Antigravity) is NOT the runtime AI provider of TenderForge. TenderForge must execute its own independent runtime calls against configured LLM APIs (such as OpenAI, Gemini, or local models). When an end-user runs the backend without an API key configured in `.env`, the system must gracefully acknowledge the absence of runtime credentials, complete all document ingestion, extraction, and segmentation steps, and explicitly mark the intelligence extraction status as `ai_configuration_required`.

**Zero Fabrication Rule:**
Under no circumstances may the application fabricate requirement records, company experience, or financial estimates to simulate successful AI operation.

---

## 4. Feasibility Conclusion & Next Actions

All required technologies have been installed, verified, and tested for import compatibility on Python 3.14.2 on Windows. No architectural roadblocks exist. The project proceeds immediately to detailed system architecture design (Task 0.5).

