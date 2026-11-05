# TenderForge — Phase 1: Document Processing Guide

## 1. Supported Document Formats & Capabilities

TenderForge includes a modular parser architecture managed by `ParserRegistry`.

| Format | Extensions | Primary Engine | Capabilities |
| :--- | :--- | :--- | :--- |
| **PDF** | `.pdf` | **PyMuPDF** (`pymupdf`) | Page-by-page text extraction, coordinate tracking, header detection, scanned document OCR detection. Fallback to `pypdf`. |
| **Microsoft Word** | `.docx` | **python-docx** (`docx`) | Paragraph extraction, heading style identification, multi-row and multi-column table extraction. |
| **Plain Text** | `.txt` | **TxtParser** | Multi-encoding recovery (`utf-8`, `latin-1`, `cp1252`, `utf-16`), line ending normalization. |
| **Spreadsheets** | `.csv`, `.xlsx` | **openpyxl** + `csv` | Tabular row and cell coordinate parsing for financial schedules, Bills of Quantities (BOQ), and equipment compliance tables. |

---

## 2. Ingestion & Pre-Processing Pipeline

```
Upload Stream 
     │
     ▼
[1. File Size Verification] ──────> Rejects if bytes > MAX_UPLOAD_SIZE_BYTES (400)
     │
     ▼
[2. Magic Bytes Inspection] ──────> Rejects if signature does not match extension (400)
     │
     ▼
[3. Cryptographic Checksum] ──────> Rejects if SHA-256 already exists in workspace (409)
     │
     ▼
[4. UUID Storage Partition] ──────> Writes to storage/{uuid[:2]}/{uuid}.{ext}
     │
     ▼
[5. Parser Selection] ────────────> Fetches registered parser from ParserRegistry
     │
     ▼
[6. Structural Extraction] ───────> Yields ParsedDocument with ParsedBlocks
     │
     ▼
[7. Intelligent Segmentation] ────> Generates DocumentSegments with exact page & offsets
     │
     ▼
[8. Database Persistence] ────────> Stores ExtractedContent records
```

---

## 3. Scanned PDF & OCR Detection

When dealing with government tender documents, scanned physical printouts are common. 
Rather than silently failing or hallucinating text:
1. `PDFParser` calculates the character count across every page.
2. If total characters are below `settings.min_page_char_threshold * total_pages` (default 40 characters per page), the parser flags `ocr_required = True`.
3. The document is safely saved, the warning is recorded in `ProcessingJob.metadata_json`, and the API exposes `ocr_required` so users and future OCR workers can act accordingly.

---

## 4. Intelligent Segmentation & Provenance

To prepare documents for AI analysis without losing context:
- **Normalization**: Unicode is standardized via `NFKC`. Excessive blank lines are collapsed.
- **Sliding Window**: Text is partitioned into configurable chunks (`chunk_size_chars`, default 1,200 chars) with configurable overlap (`chunk_overlap_chars`, default 200 chars).
- **Boundary Awareness**: Breakpoints favor paragraph breaks (`\n\n`) and sentence endings (`. `) rather than splitting mid-word.
- **Coordinate Retention**: Every segment retains `chunk_index`, `page_number`, `start_char`, `end_char`, and `section_title`.

---

## 5. Adding a Custom Parser

To add support for a new format (e.g. `.rtf` or `.odt`):
1. Create a class inheriting from `BaseParser` in `backend/app/infrastructure/parsers/`:
```python
from backend.app.infrastructure.parsers.base import BaseParser, ParsedDocument

class MyCustomParser(BaseParser):
    name = "CustomParser"
    version = "1.0.0"

    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        # Implement parsing logic
        ...
```
2. Register it with the singleton registry in `app/infrastructure/parsers/registry.py`:
```python
parser_registry.register_parser(".custom", MyCustomParser())
```
3. Add the extension to `config/document_processing.yaml`.
No business services or API routes need to be modified.
