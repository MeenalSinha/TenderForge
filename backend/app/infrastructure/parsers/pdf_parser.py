"""
PDF Document Parser supporting PyMuPDF and PyPDF fallback.
"""

from __future__ import annotations

import io
from typing import List
from backend.app.core.config import settings
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.base import BaseParser, ParsedBlock, ParsedDocument


class PDFParser(BaseParser):
    """High-performance PDF parser preserving page numbers and structural headers."""

    name: str = "PyMuPDFParser"
    version: str = "2.1.0"

    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        if not content_bytes:
            raise ParserException("PDF file is empty (0 bytes).")

        blocks: List[ParsedBlock] = []
        full_text_parts: List[str] = []
        warnings: List[str] = []
        total_pages = 0
        total_chars = 0

        try:
            # Primary extraction using pymupdf
            import pymupdf

            doc = pymupdf.open(stream=content_bytes, filetype="pdf")
            total_pages = len(doc)

            current_offset = 0
            for page_idx in range(total_pages):
                page_num = page_idx + 1
                page = doc[page_idx]
                page_text = page.get_text("text") or ""
                clean_text = page_text.strip()
                char_count = len(clean_text)
                total_chars += char_count

                if char_count == 0:
                    warnings.append(f"Page {page_num} contains no extractable text.")
                else:
                    # Detect potential heading if first line is short and uppercase or title-like
                    lines = [ln.strip() for ln in clean_text.splitlines() if ln.strip()]
                    section_title = lines[0][:100] if lines else None

                    block = ParsedBlock(
                        page_number=page_num,
                        block_type="page_content",
                        text=clean_text,
                        section_title=section_title,
                        char_offset=current_offset,
                        metadata={"page_char_count": char_count},
                    )
                    blocks.append(block)
                    full_text_parts.append(clean_text)
                    current_offset += len(clean_text) + 2  # newline separation

            doc.close()

        except Exception as primary_err:
            warnings.append(f"Primary PyMuPDF parser encountered error: {str(primary_err)}. Attempting PyPDF fallback.")
            try:
                import pypdf

                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                total_pages = len(reader.pages)
                current_offset = 0

                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    page = reader.pages[page_idx]
                    page_text = page.extract_text() or ""
                    clean_text = page_text.strip()
                    char_count = len(clean_text)
                    total_chars += char_count

                    if clean_text:
                        blocks.append(
                            ParsedBlock(
                                page_number=page_num,
                                block_type="page_content",
                                text=clean_text,
                                char_offset=current_offset,
                            )
                        )
                        full_text_parts.append(clean_text)
                        current_offset += len(clean_text) + 2
            except Exception as fallback_err:
                raise ParserException(f"Failed to parse PDF document with both engines: {str(fallback_err)}")

        # Determine if OCR is required
        threshold = settings.min_page_char_threshold * max(1, total_pages)
        ocr_required = total_chars < threshold

        if ocr_required:
            warnings.append(
                f"Document text density ({total_chars} chars across {total_pages} pages) "
                f"is below threshold ({threshold}). Scanned document or OCR may be required."
            )

        full_text = "\n\n".join(full_text_parts)

        return ParsedDocument(
            filename=filename,
            parser_name=self.name,
            parser_version=self.version,
            total_pages=total_pages,
            blocks=blocks,
            full_text=full_text,
            ocr_required=ocr_required,
            warnings=warnings,
            statistics={
                "total_pages": total_pages,
                "total_characters": total_chars,
                "blocks_extracted": len(blocks),
            },
        )

