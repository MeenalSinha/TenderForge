"""
Parser Registry for TenderForge.
"""

from __future__ import annotations

from typing import Dict, Optional, Type
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.base import BaseParser
from backend.app.infrastructure.parsers.docx_parser import DocxParser
from backend.app.infrastructure.parsers.pdf_parser import PDFParser
from backend.app.infrastructure.parsers.spreadsheet_parser import SpreadsheetParser
from backend.app.infrastructure.parsers.txt_parser import TxtParser


class ParserRegistry:
    """Registry maintaining mapping between file extensions and parser instances."""

    def __init__(self) -> None:
        self._parsers: Dict[str, BaseParser] = {
            ".pdf": PDFParser(),
            ".docx": DocxParser(),
            ".txt": TxtParser(),
            ".csv": SpreadsheetParser(),
            ".xlsx": SpreadsheetParser(),
        }

    def register_parser(self, extension: str, parser: BaseParser) -> None:
        """Register or override a parser for a specific extension."""
        ext = extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        self._parsers[ext] = parser

    def get_parser(self, extension: str) -> BaseParser:
        """Retrieve parser configured for the given extension."""
        ext = extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        if ext not in self._parsers:
            raise ParserException(f"No registered parser available for extension '{ext}'")
        return self._parsers[ext]


# Singleton instance
parser_registry = ParserRegistry()

