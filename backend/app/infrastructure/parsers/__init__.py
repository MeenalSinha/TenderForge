"""Parsers package."""
from backend.app.infrastructure.parsers.base import BaseParser, ParsedBlock, ParsedDocument
from backend.app.infrastructure.parsers.pdf_parser import PDFParser
from backend.app.infrastructure.parsers.docx_parser import DocxParser
from backend.app.infrastructure.parsers.txt_parser import TxtParser
from backend.app.infrastructure.parsers.spreadsheet_parser import SpreadsheetParser
from backend.app.infrastructure.parsers.registry import ParserRegistry, parser_registry

__all__ = [
    "BaseParser",
    "ParsedBlock",
    "ParsedDocument",
    "PDFParser",
    "DocxParser",
    "TxtParser",
    "SpreadsheetParser",
    "ParserRegistry",
    "parser_registry",
]

