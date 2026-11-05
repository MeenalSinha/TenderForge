# TenderForge — Phase 1: Database Schema & Migration Specification

## 1. Overview & Engine Support

The TenderForge persistence layer is built on **SQLAlchemy 2.0** and managed through **Alembic** migrations (`backend/alembic/versions/001_initial_schema.py`). 

- **Primary Supported Dialects**:
  - SQLite (Development, Testing, and Single-node deployment)
  - PostgreSQL (Production enterprise deployments)
- **Primary Keys**: UUID v4 (stored as `VARCHAR(36)`).
- **Timestamps**: All timestamps stored in UTC (`DATETIME`).

---

## 2. Table Specifications

### 2.1 `organizations`
Represents the top-level multi-tenant enterprise boundary.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `name` | VARCHAR(255) | NOT NULL | Organization name |
| `slug` | VARCHAR(255) | UNIQUE, NOT NULL | URL-friendly slug |
| `created_at` | DATETIME | NOT NULL | UTC creation timestamp |

### 2.2 `workspaces`
Sub-partitions within an organization (e.g. Defense Bids, Civilian IT).
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `organization_id` | VARCHAR(36) | FOREIGN KEY (`organizations.id`) ON DELETE CASCADE | Parent organization |
| `name` | VARCHAR(255) | NOT NULL | Workspace name |
| `description` | TEXT | NULLABLE | Workspace description |
| `created_at` | DATETIME | NOT NULL | UTC creation timestamp |

### 2.3 `documents`
Uploaded tender specification files, RFPs, and company evidence certificates.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `workspace_id` | VARCHAR(36) | FOREIGN KEY (`workspaces.id`) ON DELETE CASCADE | Owning workspace |
| `original_filename` | VARCHAR(255) | NOT NULL | Client filename sanitized |
| `storage_path` | VARCHAR(512) | NOT NULL | Physical disk / object key path |
| `mime_type` | VARCHAR(128) | NOT NULL | Verified MIME type |
| `file_extension` | VARCHAR(16) | NOT NULL | E.g. `.pdf`, `.docx` |
| `file_size_bytes` | INTEGER | NOT NULL | Size in bytes |
| `checksum_sha256` | VARCHAR(64) | NOT NULL, INDEX | Cryptographic digest for deduplication |
| `document_category` | VARCHAR(64) | NOT NULL | E.g. `tender_notice`, `evidence_cert` |
| `processing_status` | VARCHAR(32) | NOT NULL | `pending`, `parsed`, `failed` |
| `parser_name` | VARCHAR(64) | NULLABLE | E.g. `PyMuPDFParser`, `DocxParser` |
| `parser_version` | VARCHAR(32) | NULLABLE | Version of the parser adapter |
| `ocr_required` | BOOLEAN | NOT NULL, DEFAULT FALSE | Flag set if text density is low |
| `error_message` | TEXT | NULLABLE | Extraction diagnostics |
| `created_at` | DATETIME | NOT NULL | UTC creation timestamp |
| `updated_at` | DATETIME | NOT NULL | UTC update timestamp |

### 2.4 `document_versions`
Historical version records for re-uploaded or amended documents.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `document_id` | VARCHAR(36) | FOREIGN KEY (`documents.id`) ON DELETE CASCADE | Parent document |
| `version_number` | INTEGER | NOT NULL | Sequential version counter |
| `storage_path` | VARCHAR(512) | NOT NULL | Path to version binary |
| `checksum_sha256` | VARCHAR(64) | NOT NULL | Version SHA-256 |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |

### 2.5 `processing_jobs`
Lifecycle stages tracking ingestion, parsing, normalization, and segmentation.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `document_id` | VARCHAR(36) | FOREIGN KEY (`documents.id`) ON DELETE CASCADE | Target document |
| `stage` | VARCHAR(64) | NOT NULL | E.g. `parsing_and_segmentation` |
| `status` | VARCHAR(32) | NOT NULL | `queued`, `in_progress`, `completed`, `failed` |
| `retry_count` | INTEGER | NOT NULL, DEFAULT 0 | Retries attempted |
| `error_message` | TEXT | NULLABLE | Diagnostic details |
| `metadata_json` | JSON | NULLABLE | Metrics (pages, chunks, warnings) |
| `started_at` | DATETIME | NOT NULL | Start timestamp |
| `completed_at` | DATETIME | NULLABLE | Completion timestamp |

### 2.6 `extracted_contents`
Normalized, segmented text chunks preserving exact source coordinates.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `document_id` | VARCHAR(36) | FOREIGN KEY (`documents.id`) ON DELETE CASCADE | Source document |
| `chunk_index` | INTEGER | NOT NULL | Sequential chunk order |
| `page_number` | INTEGER | NULLABLE | Source document page number (1-indexed) |
| `start_char` | INTEGER | NULLABLE | Starting character offset |
| `end_char` | INTEGER | NULLABLE | Ending character offset |
| `section_title` | VARCHAR(255) | NULLABLE | Inferred section heading |
| `content` | TEXT | NOT NULL | Normalized segment text |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |

### 2.7 `tenders`
Procurement opportunities managed by the platform.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `workspace_id` | VARCHAR(36) | FOREIGN KEY (`workspaces.id`) ON DELETE CASCADE | Owning workspace |
| `reference_number` | VARCHAR(128) | NULLABLE, INDEX | Official RFP notice number |
| `title` | VARCHAR(512) | NOT NULL | Tender title |
| `issuing_authority` | VARCHAR(255) | NULLABLE | Procuring agency |
| `procurement_category`| VARCHAR(128) | NULLABLE | Category classification |
| `estimated_value` | FLOAT | NULLABLE | Budget/Value |
| `currency` | VARCHAR(8) | NOT NULL, DEFAULT 'USD' | ISO currency code |
| `submission_deadline`| DATETIME | NULLABLE | Submission deadline |
| `status` | VARCHAR(32) | NOT NULL, DEFAULT 'draft' | `draft`, `analyzing`, `analyzed` |
| `metadata_json` | JSON | NULLABLE | Extensible metadata |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Update timestamp |

### 2.8 `tender_documents`
Association table linking tender opportunities to uploaded documents.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `tender_id` | VARCHAR(36) | FOREIGN KEY (`tenders.id`) ON DELETE CASCADE | Linked tender |
| `document_id` | VARCHAR(36) | FOREIGN KEY (`documents.id`) ON DELETE CASCADE | Linked document |
| `relationship_type` | VARCHAR(64) | NOT NULL | E.g. `primary_specification`, `corrigendum` |
| `created_at` | DATETIME | NOT NULL | Link timestamp |

### 2.9 `tender_requirements`
Structured requirements with auditable ProofLink citations.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `tender_id` | VARCHAR(36) | FOREIGN KEY (`tenders.id`) ON DELETE CASCADE | Parent tender |
| `source_document_id`| VARCHAR(36) | FOREIGN KEY (`documents.id`) ON DELETE SET NULL | Origin document |
| `category` | VARCHAR(64) | NOT NULL | `eligibility`, `technical`, `financial`, `submission` |
| `classification` | VARCHAR(32) | NOT NULL, DEFAULT 'mandatory' | `mandatory`, `optional`, `desirable` |
| `description` | TEXT | NOT NULL | Actionable requirement statement |
| `source_page` | INTEGER | NULLABLE | Document page number |
| `source_offset` | INTEGER | NULLABLE | Character offset |
| `source_excerpt` | TEXT | NOT NULL | Verbatim text quote |
| `confidence_score` | FLOAT | NOT NULL, DEFAULT 1.0 | Model extraction confidence |
| `human_review_status`| VARCHAR(32) | NOT NULL, DEFAULT 'unreviewed' | `unreviewed`, `confirmed`, `rejected` |
| `extra_metadata` | JSON | NULLABLE | Additional key-values |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Update timestamp |

### 2.10 `extraction_results`
Audit log of raw and structured outputs from AI models.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 |
| `tender_id` | VARCHAR(36) | FOREIGN KEY (`tenders.id`) ON DELETE CASCADE | Analyzed tender |
| `provider_id` | VARCHAR(64) | NOT NULL | Provider (`openai`, `mock`, `none`) |
| `model_id` | VARCHAR(128) | NOT NULL | Model identifier |
| `prompt_version` | VARCHAR(32) | NOT NULL | Prompt version used |
| `raw_response` | JSON | NULLABLE | Raw LLM provider payload |
| `structured_data` | JSON | NULLABLE | Validated JSON payload |
| `validation_status` | VARCHAR(32) | NOT NULL | `valid`, `invalid`, `ai_configuration_required` |
| `error_message` | TEXT | NULLABLE | Extraction diagnostics |
| `execution_timestamp`| DATETIME | NOT NULL | Execution timestamp |

---

## 3. Migration Instructions

To run migrations:
```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

To rollback:
```powershell
python -m alembic -c backend/alembic.ini downgrade -1
```

