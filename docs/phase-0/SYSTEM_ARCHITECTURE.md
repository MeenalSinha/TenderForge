# TenderForge — Phase 0: System Architecture Specification

## 1. Architectural Overview

TenderForge is engineered with a modular, decoupled, layered architecture adhering strictly to the **Nothing Hardcoded** and **Zero Fabrication** principles. 

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Clients Layer                             │
│       Web Dashboard / CLI / Switch Multi-Agent War Room (Phase 2)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                               API Layer                                │
│  ┌───────────────────────┐ ┌────────────────────┐ ┌─────────────────┐  │
│  │    Document Routes    │ │   Tender Routes    │ │  Health Probes  │  │
│  │   (/api/v1/documents) │ │ (/api/v1/tenders)  │ │ (/health, ready)│  │
│  └───────────────────────┘ └────────────────────┘ └─────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │           Middleware: Correlation ID, Error Handling, CORS       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                             Services Layer                             │
│  ┌───────────────────────┐ ┌────────────────────┐ ┌─────────────────┐  │
│  │    DocumentService    │ │   TenderService    │ │TenderIntellignce│  │
│  │ (Ingestion, Storage)  │ │(Registry, Linkage) │ │(AI Extraction)  │  │
│  └───────────┬───────────┘ └─────────┬──────────┘ └────────┬────────┘  │
│              │                       │                     │           │
│              ▼                       │                     ▼           │
│  ┌───────────────────────┐           │            ┌─────────────────┐  │
│  │DocumentProcessingServ.│           │            │ Prompt Manager  │  │
│  │(Parsing, Normalization│           │            │& Schema Validate│  │
│  └───────────┬───────────┘           │            └────────┬────────┘  │
└──────────────┼───────────────────────┼─────────────────────┼───────────┘
               │                       │                     │
               ▼                       ▼                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          Infrastructure Layer                          │
│  ┌───────────────────────┐ ┌────────────────────┐ ┌─────────────────┐  │
│  │   Document Parsers    │ │ Persistence & Repos│ │  AI Providers  │  │
│  │ (PyMuPDF, Docx, TXT)  │ │(SQLAlchemy, Models)│ │(OpenAI, Ollama, │  │
│  └───────────┬───────────┘ └─────────┬──────────┘ │  Mock / None)   │  │
│              │                       │            └─────────────────┘  │
│              ▼                       ▼                                 │
│  ┌───────────────────────┐ ┌────────────────────┐                      │
│  │ Storage Adapter       │ │ Relational DB      │                      │
│  │ (UUID File System)    │ │ (SQLite / Postgres)│                      │
│  └───────────────────────┘ └────────────────────┘                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Responsibilities

### 2.1 API Layer (`app/api/`)
- **Endpoints**: Health, documents upload/download/inspect, tender registration, parsing orchestration, and structured intelligence queries.
- **Request Validation**: Pydantic v2 schemas validating request structures, MIME types, and query parameters before invoking application services.
- **Response Normalization**: Standardized JSON envelopes with status codes, error details, and metadata.
- **Correlation ID Middleware**: Assigns an `X-Correlation-ID` header to every request, passing it into structured logs.

### 2.2 Core Layer (`app/core/`)
- **Configuration**: `Settings` class powered by `pydantic-settings` reading `.env` and YAML configurations (`config/application.yaml`, `config/document_processing.yaml`).
- **Logging**: Structured, formatted logging with masking for tokens, passwords, and sensitive information.
- **Exceptions**: Domain-specific exception hierarchy (`DocumentNotFoundError`, `DuplicateDocumentError`, `ParserError`, `AIProviderError`, `ConfigurationError`) with centralized HTTP status mapping.

### 2.3 Services Layer (`app/services/`)
- **DocumentService**: Orchestrates file stream validation, checksum calculation, storage persistence, and database registration.
- **DocumentProcessingService**: Coordinates parser selection, text normalization, structural heading extraction, and intelligent segmentation.
- **TenderService**: Manages tender entity lifecycles, links tender records to uploaded documents, and retrieves consolidated requirements.
- **TenderIntelligenceService**: Ingests segmented document content, formats external prompt templates, calls the configured AI provider, validates structured Pydantic output, and stores requirements with exact source provenance.

### 2.4 Infrastructure Layer (`app/infrastructure/`)
- **Document Parsers (`app/infrastructure/parsers/`)**: Extensible parser registry implementing `BaseParser`:
  - `PDFParser`: Page-by-page extraction, header detection, and OCR requirement detection.
  - `DocxParser`: Paragraph and table extraction with structure retention.
  - `TxtParser`: Multi-encoding decoding and line preservation.
  - `SpreadsheetParser`: Sheet, row, and column extraction for structured pricing/schedules.
- **Storage Adapter (`app/infrastructure/storage/`)**: Decoupled file persistence generating non-colliding UUID file names, isolated directory hashing, and cleanup handlers.
- **AI Integration (`app/infrastructure/ai/`)**: Unified `BaseAIProvider` interface with adapters for:
  - Configured REST APIs (OpenAI / Anthropic / Gemini format).
  - Configurable Local/Ollama models.
  - `FallbackProvider` / `MockProvider` used when keys are not configured or in unit test suites.

---

## 3. Data Flow: From Tender Document to Intelligence

```
[User Upload] 
      │ 
      ▼
1. Validation (File size, Extension, Magic Bytes)
      │
      ▼
2. Checksum (SHA-256) & Duplicate Check
      │
      ▼
3. Secure Storage (Save file as storage/{uuid_prefix}/{uuid}.ext)
      │
      ▼
4. Database Registration (Create Document & ProcessingJob records)
      │
      ▼
5. Document Parsing (Select Parser -> Extract text, pages, tables)
      │
      ▼
6. Normalization & Segmentation (Clean text -> Generate Chunks with Provenance)
      │
      ▼
7. Tender Association (Link Document to Tender Record)
      │
      ▼
8. AI Extraction (If Provider Configured -> External Prompt -> LLM -> Pydantic Validation)
   OR
   Graceful Degradation (If No Provider -> Record status="ai_configuration_required")
      │
      ▼
9. Structured Persistence (Store Tender Requirements with Source Page & Excerpt)
```

---

## 4. Key Architectural Decisions

1. **Zero Hardcoding**: All parser options (chunk sizes, overlap, max upload size, enabled formats), AI options (model name, temperature, max tokens, timeout, retry count), and database connection strings are read dynamically through configuration files and environment variables.
2. **Untrusted Document Boundary**: Tender documents are treated strictly as read-only data blocks. Extracted text is sanitized and wrapped in protective delimiter tags before being passed to LLM prompts, preventing indirect prompt injection from altering system behavior.
3. **Evidence Traceability (ProofLink Foundation)**: Every requirement entity persisted in the database contains `source_document_id`, `source_page_number`, `source_offset`, and verbatim `source_excerpt`. This allows future Phase 2 agents and human auditors to instantly verify claims against the original tender text.
4. **Clean Decoupling from Switch**: The backend is completely standalone. Future Switch room agents will interact with TenderForge exclusively through documented REST APIs, MCP tool definitions, or the adapter contracts defined in `app/integrations/switch/`.

