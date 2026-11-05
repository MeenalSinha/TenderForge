"""
DOCX Document Parser using python-docx.
"""

from __future__ import annotations

import io
from typing import List
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.base import BaseParser, ParsedBlock, ParsedDocument


class DocxParser(BaseParser):
    """Parses Microsoft Word .docx documents preserving paragraphs and tables."""

    name: str = "DocxParser"
    version: str = "1.2.0"

    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        if not content_bytes:
            raise ParserException("DOCX file is empty (0 bytes).")

        try:
            import docx

            doc = docx.Document(io.BytesIO(content_bytes))
        except Exception as e:
            raise ParserException(f"Invalid or corrupted DOCX archive: {str(e)}")

        blocks: List[ParsedBlock] = []
        full_text_parts: List[str] = []
        current_offset = 0
        current_section = "Introduction"

        # 1. Paragraphs
        for p_idx, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue

            style_name = p.style.name.lower() if p.style else ""
            is_heading = "heading" in style_name or "title" in style_name
            if is_heading:
                current_section = text

            block = ParsedBlock(
                page_number=1,  # DOCX has no fixed native pagination without render engine
                block_type="heading" if is_heading else "paragraph",
                text=text,
                section_title=current_section,
                char_offset=current_offset,
                metadata={"style": style_name, "paragraph_index": p_idx},
            )
            blocks.append(block)
            full_text_parts.append(text)
            current_offset += len(text) + 2

        # 2. Tables
        for t_idx, table in enumerate(doc.tables):
            table_grid: List[List[str]] = []
            table_text_lines: List[str] = []

            for row in table.rows:
                row_vals = [cell.text.strip() for cell in row.cells]
                table_grid.append(row_vals)
                table_text_lines.append(" | ".join(row_vals))

            if table_text_lines:
                table_str = "\n".join(table_text_lines)
                block = ParsedBlock(
                    page_number=1,
                    block_type="table",
                    text=f"[Table {t_idx + 1}]\n{table_str}",
                    section_title=current_section,
                    table_data=table_grid,
                    char_offset=current_offset,
                    metadata={"table_index": t_idx, "rows": len(table.rows), "cols": len(table.columns)},
                )
                blocks.append(block)
                full_text_parts.append(block.text)
                current_offset += len(block.text) + 2

        full_text = "\n\n".join(full_text_parts)

        return ParsedDocument(
            filename=filename,
            parser_name=self.name,
            parser_version=self.version,
            total_pages=1,  # Semantic flow representation
            blocks=blocks,
            full_text=full_text,
            ocr_required=len(full_text.strip()) == 0,
            warnings=["Pagination is flow-based for DOCX documents."] if blocks else ["DOCX contains no text content."],
            statistics={
                "total_paragraphs": len(doc.paragraphs),
                "total_tables": len(doc.tables),
                "total_characters": len(full_text),
            },
        )

