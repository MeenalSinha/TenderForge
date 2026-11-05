"""
Text Normalization & Intelligent Traceable Segmentation.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional
from backend.app.core.config import settings
from backend.app.infrastructure.parsers.base import ParsedBlock, ParsedDocument


@dataclass
class DocumentSegment:
    """A segmented chunk of text with exact source traceability."""

    chunk_index: int
    page_number: int
    start_char: int
    end_char: int
    section_title: Optional[str]
    content: str


class TextNormalizer:
    """Cleans and standardizes extracted text while preserving technical structure."""

    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        # Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", text)
        # Normalize newlines
        norm = norm.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse 3 or more consecutive blank lines into 2
        norm = re.sub(r"\n{3,}", "\n\n", norm)
        # Strip trailing whitespace on each line
        lines = [re.sub(r"[ \t]+$", "", line) for line in norm.splitlines()]
        return "\n".join(lines).strip()


class IntelligentSegmenter:
    """Segments parsed documents into coherent chunks with source page and offset references."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        min_chunk_size: Optional[int] = None,
    ) -> None:
        self.chunk_size = chunk_size or settings.chunk_size_chars
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap_chars
        self.min_chunk_size = min_chunk_size or settings.min_chunk_size_chars

    def segment_parsed_document(self, parsed_doc: ParsedDocument) -> List[DocumentSegment]:
        segments: List[DocumentSegment] = []
        chunk_counter = 0

        # Segment block by block to preserve page references
        for block in parsed_doc.blocks:
            clean_text = TextNormalizer.normalize(block.text)
            if not clean_text or len(clean_text) < self.min_chunk_size:
                if clean_text:
                    segments.append(
                        DocumentSegment(
                            chunk_index=chunk_counter,
                            page_number=block.page_number,
                            start_char=block.char_offset or 0,
                            end_char=(block.char_offset or 0) + len(clean_text),
                            section_title=block.section_title,
                            content=clean_text,
                        )
                    )
                    chunk_counter += 1
                continue

            # Sliding window segmentation across block
            start = 0
            text_len = len(clean_text)
            block_base_offset = block.char_offset or 0

            while start < text_len:
                end = min(start + self.chunk_size, text_len)

                # Attempt to break on paragraph or sentence boundary if not at end
                if end < text_len:
                    break_point = clean_text.rfind("\n\n", start, end)
                    if break_point != -1 and break_point > start + (self.chunk_size // 2):
                        end = break_point + 2
                    else:
                        period_point = clean_text.rfind(". ", start, end)
                        if period_point != -1 and period_point > start + (self.chunk_size // 2):
                            end = period_point + 1

                chunk_content = clean_text[start:end].strip()
                if chunk_content:
                    segments.append(
                        DocumentSegment(
                            chunk_index=chunk_counter,
                            page_number=block.page_number,
                            start_char=block_base_offset + start,
                            end_char=block_base_offset + end,
                            section_title=block.section_title,
                            content=chunk_content,
                        )
                    )
                    chunk_counter += 1

                if end >= text_len:
                    break
                start = max(start + 1, end - self.chunk_overlap)

        return segments

