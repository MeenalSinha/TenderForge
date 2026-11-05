"""
Base Document Parser Interfaces & Data Structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ParsedBlock:
    """A granular structural unit of extracted content."""

    page_number: int  # 1-indexed
    block_type: str  # "heading", "paragraph", "table", "row"
    text: str
    section_title: Optional[str] = None
    table_data: Optional[List[List[str]]] = None
    char_offset: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """Normalized document representation returned by all parsers."""

    filename: str
    parser_name: str
    parser_version: str
    total_pages: int
    blocks: List[ParsedBlock]
    full_text: str
    ocr_required: bool = False
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


class BaseParser(ABC):
    """Abstract contract implemented by all format-specific parsers."""

    name: str = "BaseParser"
    version: str = "1.0.0"

    @abstractmethod
    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        """Parse raw document bytes into a structured ParsedDocument."""
        pass

