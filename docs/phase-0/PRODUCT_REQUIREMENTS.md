# TenderForge — Phase 0: Product Requirements Document (PRD)

## 1. Product Identity & Purpose

- **Project**: TenderForge
- **Tagline**: *From Tender to Trustworthy Proposal*
- **Competition**: Flip the Switch Hackathon 2026 (Track: Best Business Workflow)
- **Vision**: Transform high-stakes, manual, fragmented tender/RFP responses into a reliable, collaborative, evidence-backed workflow where humans and specialized AI agents operate with verified provenance and zero hallucinations.

---

## 2. Functional Requirements

### 2.1 Requirements Allocation Matrix (Phase 1 vs. Future Phases)

| ID | Requirement Area | Description | Scope |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Tender Ingestion & Validation** | Accept multi-format uploads (PDF, DOCX, TXT, CSV/XLSX), validate MIME types, magic bytes, enforce configurable size ceilings, compute SHA-256 checksums, and detect duplicates. | **Phase 1** |
| **FR-02** | **Document Storage & Metadata** | Store files in decoupled storage (local filesystem adapter with UUID-partitioned storage keys), record timestamps, parser versions, and lifecycle status. | **Phase 1** |
| **FR-03** | **Text & Table Extraction** | Extract readable text, tabular structures, and structural boundaries page-by-page (PDF), paragraph-by-paragraph (DOCX), or row-by-row (spreadsheets). | **Phase 1** |
| **FR-04** | **Structural Segmentation** | Clean and normalize text, segmenting into coherent chunks with configurable token/character windows and overlap while preserving source page, offset, and heading metadata. | **Phase 1** |
| **FR-05** | **Tender Registration & Linkage** | Register tender entities, associate uploaded documents, and track parsing and analysis job lifecycles. | **Phase 1** |
| **FR-06** | **Structured Tender Intelligence** | Extract general tender data, eligibility criteria, technical requirements, financial terms, and submission requirements using an externalized AI provider. | **Phase 1** |
| **FR-07** | **Source Provenance Recording** | Attach exact source references (document ID, page number, section offset, verbatim excerpt) to every extracted requirement. | **Phase 1** |
| **FR-08** | **Graceful AI Degradation** | Fully support ingestion, parsing, segmentation, and metadata retrieval when an AI runtime provider is absent, returning an explicit `ai_configuration_required` state. | **Phase 1** |
| **FR-09** | **RESTful API & Health Probes** | Expose OpenAPI-compliant endpoints for document upload, retrieval, processing status, tender management, and intelligence extraction. | **Phase 1** |
| **FR-10** | **Future Switch Integration Contracts**| Define interfaces, data schemas, and API contracts ready for Switch Room agent consumers without importing Switch runtime code. | **Phase 1** |
| **FR-11** | **Evidence Ingestion & Cataloging** | Ingest company certifications, past performance records, financial audit reports, and CVs. | *Phase 2 / Future* |
| **FR-12** | **ProofLink Traceability Engine** | Compute automated evidence-to-requirement matches with five traceable statuses: `Verified`, `Human Confirmed`, `Pending`, `Unsupported`, `Contradicted`. | *Phase 2 / Future* |
| **FR-13** | **Compliance Matrix Generation** | Dynamic compliance grid detailing gaps, mandatory passes/fails, and risk factors across all requirements. | *Phase 2 / Future* |
| **FR-14** | **Multi-Agent Room Orchestration** | Autonomous Switch room collaboration across 5 roles (Tender Analyst, Compliance Officer, Evidence Researcher, Proposal Architect, Bid Auditor). | *Phase 2 / Future* |
| **FR-15** | **Evidence-Backed Proposal Drafting** | Generate RFP proposal chapters strictly grounded in verified company proof with inline ProofLink citations. | *Phase 2 / Future* |
| **FR-16** | **Human Clarification & Sign-off** | Human-in-the-loop workflow for resolving ambiguities, reviewing unverified claims, and approving final submission packages. | *Phase 2 / Future* |

---

## 3. Detailed Specifications for Phase 1 Requirements

### FR-01: Tender Ingestion & Validation
1. System shall accept file streams via `multipart/form-data`.
2. Supported initial extensions: `.pdf`, `.docx`, `.txt`, `.csv`, `.xlsx`.
3. System shall inspect both file extension and initial binary header signatures (magic bytes).
4. System shall calculate cryptographic SHA-256 hash before saving.
5. If SHA-256 exists for the active workspace, system shall register the duplicate reference or flag appropriately per configuration.
6. Maximum file size must be read from configuration (`MAX_UPLOAD_SIZE_BYTES`, default 50 MB) and enforced before writing to disk.

### FR-03 & FR-04: Document Intelligence & Segmentation
1. **PDF**: Extracted page by page, capturing page index, text length, character count, and structural headers.
2. **DOCX**: Extracted per paragraph and table, preserving row/cell indices and styles.
3. **TXT**: Extracted with multi-encoding fallback (UTF-8, UTF-16, Latin-1, CP1252) and line tracking.
4. **OCR Detection**: If a PDF contains 0 extractable characters across pages or below a configurable threshold per page, tag with `ocr_required=True` without failing the pipeline.
5. **Segmentation**: Chunks generated by character/token limits with overlap; each chunk preserves `document_id`, `page_number`, `start_char`, `end_char`, and parent section title.

### FR-06 & FR-07: Structured Tender Intelligence & Provenance
1. Intelligence extraction operates against a strictly typed Pydantic schema:
   - **General Information**: Title, reference number, authority, procurement category, estimated budget, submission deadline, bid validity period.
   - **Eligibility Criteria**: Financial turnover, minimum years of experience, past project threshold, certifications (ISO, CMMI), statutory registrations.
   - **Technical Specifications**: Scope summary, key deliverables, service level agreements, milestones.
   - **Financial Requirements**: Earnest Money Deposit (EMD), performance security, payment terms, pricing schedule format.
   - **Submission Requirements**: Required forms, envelopes (technical/commercial), format requirements, submission mode.
2. Every item extracted must capture `source_excerpt`, `page_number`, and `confidence_score` (0.0 to 1.0).
3. If a field cannot be located in the text, it must be represented as `None` or marked with `status="not_found"` — NEVER hallucinated.

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Security & Privacy
- **NFR-SEC-01 (Untrusted Input)**: All document text must be treated as untrusted user payload. Never evaluate or execute document strings.
- **NFR-SEC-02 (Prompt Injection Defense)**: AI prompts must isolate document text within explicit data delimiters (`<document_content>...</document_content>`) with system instructions stating document text must not override instructions.
- **NFR-SEC-03 (Path Traversal Prevention)**: Stored files must use system-generated UUID filenames. Original client filenames must be sanitized and stored only as metadata.
- **NFR-SEC-04 (Credential Hygiene)**: Zero hardcoded secrets. All API keys and connection URLs must be loaded via environment variables and masked in logs.

### 4.2 Performance & Scalability
- **NFR-PERF-01 (Throughput)**: Ingestion and text extraction of a 50-page PDF shall complete within 3 seconds on standard commodity hardware.
- **NFR-PERF-02 (Storage Decoupling)**: Storage and database layers must use abstract interfaces allowing trivial swapping from Local Storage to S3/GCS and from SQLite to PostgreSQL.

### 4.3 Reliability & Explainability
- **NFR-REL-01 (Atomic Operations)**: Database records and file storage writes must be managed with proper rollback on failure.
- **NFR-EXP-01 (Zero Fabrication)**: No AI claim or requirement may be presented without an auditable source reference or explicit indicator that it was inferred.

### 4.4 Configurability & Maintainability
- **NFR-CFG-01 (Nothing Hardcoded)**: All operational parameters (thresholds, model names, prompt paths, file extensions, categories) must reside in external configuration.
- **NFR-MNT-01 (Strict Typing)**: Full Python type hint coverage across domain models, services, and API schemas.

