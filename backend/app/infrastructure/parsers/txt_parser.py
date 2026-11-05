"""
Plain Text Document Parser with multi-encoding recovery.
"""

from __future__ import annotations

from typing import List
from backend.app.core.config import settings
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.base import BaseParser, ParsedBlock, ParsedDocument


class TxtParser(BaseParser):
    """Parses plain text documents with multi-encoding fallback."""

    name: str = "TxtParser"
    version: str = "1.0.0"

    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        if not content_bytes:
            raise ParserException("Text file is empty (0 bytes).")

        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
        decoded_text: str = ""
        used_encoding: str = ""

        for enc in encodings:
            try:
                decoded_text = content_bytes.decode(enc)
                used_encoding = enc
                break
            except UnicodeDecodeError:
                continue

        if not decoded_text and content_bytes:
            raise ParserException("Failed to decode text file using supported encodings.")

        # Normalize line breaks
        normalized_text = decoded_text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized_text.split("\n")

        blocks: List[ParsedBlock] = []
        current_offset = 0

        # Group non-empty paragraphs
        current_para: List[str] = []
        current_section = "General"

        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith("#") or (len(stripped) < 60 and stripped.isupper()):
                    current_section = stripped.lstrip("#").strip()
                current_para.append(stripped)
            else:
                if current_para:
                    p_text = " ".join(current_para)
                    blocks.append(
                        ParsedBlock(
                            page_number=1,
                            block_type="paragraph",
                            text=p_text,
                            section_title=current_section,
                            char_offset=current_offset,
                        )
                    )
                    current_offset += len(p_text) + 2
                    current_para = []

        if current_para:
            p_text = " ".join(current_para)
            blocks.append(
                ParsedBlock(
                    page_number=1,
                    block_type="paragraph",
                    text=p_text,
                    section_title=current_section,
                    char_offset=current_offset,
                )
            )

        full_text = normalized_text.strip()

        return ParsedDocument(
            filename=filename,
            parser_name=self.name,
            parser_version=self.version,
            total_pages=1,
            blocks=blocks,
            full_text=full_text,
            ocr_required=len(full_text) == 0,
            statistics={
                "encoding": used_encoding,
                "total_lines": len(lines),
                "total_characters": len(full_text),
            },
        )

