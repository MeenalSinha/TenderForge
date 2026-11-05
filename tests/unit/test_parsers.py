"""
Unit Tests: Modular Document Parsers (PDF, DOCX, TXT, Spreadsheets).
"""

import io
import pytest
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.docx_parser import DocxParser
from backend.app.infrastructure.parsers.pdf_parser import PDFParser
from backend.app.infrastructure.parsers.spreadsheet_parser import SpreadsheetParser
from backend.app.infrastructure.parsers.txt_parser import TxtParser
from tests.helpers import create_synthetic_docx_bytes, create_synthetic_pdf_bytes


def test_pdf_parser_success():
    pdf_bytes = create_synthetic_pdf_bytes()
    parser = PDFParser()
    result = parser.parse(pdf_bytes, "tender.pdf")

    assert result.total_pages == 2
    assert len(result.blocks) >= 2
    assert "RFP-2026-001" in result.full_text
    assert result.ocr_required is False
    assert result.statistics["total_pages"] == 2


def test_pdf_parser_empty_error():
    parser = PDFParser()
    with pytest.raises(ParserException):
        parser.parse(b"", "empty.pdf")


def test_docx_parser_success():
    docx_bytes = create_synthetic_docx_bytes()
    parser = DocxParser()
    result = parser.parse(docx_bytes, "specs.docx")

    assert len(result.blocks) >= 2
    assert "Scope of Work" in result.full_text
    assert "Core Switch" in result.full_text
    assert result.ocr_required is False


def test_docx_parser_corrupted():
    parser = DocxParser()
    with pytest.raises(ParserException):
        parser.parse(b"PK\x03\x04not_a_real_docx", "corrupt.docx")


def test_txt_parser_success():
    txt_content = (
        "SECTION 1: ELIGIBILITY CRITERIA\n\n"
        "1.1 The bidder must have minimum 5 years of experience in system integration.\n"
        "1.2 Valid ISO 9001 certification is mandatory.\n"
    ).encode("utf-8")

    parser = TxtParser()
    result = parser.parse(txt_content, "eligibility.txt")

    assert len(result.blocks) >= 1
    assert "ISO 9001" in result.full_text
    assert result.statistics["encoding"] == "utf-8"


def test_csv_spreadsheet_parser():
    csv_bytes = b"Item,Description,Unit,Price\n1,Fiber Transceiver,Each,450.00\n2,Patch Cable,Each,25.00\n"
    parser = SpreadsheetParser()
    result = parser.parse(csv_bytes, "boq.csv")

    assert result.total_pages == 1
    assert "Fiber Transceiver" in result.full_text
    assert len(result.blocks) == 1
    assert result.blocks[0].table_data is not None
