"""
Spreadsheet Parser for CSV and Excel (.xlsx) Tender Schedules.
"""

from __future__ import annotations

import csv
import io
from typing import List
from backend.app.core.exceptions import ParserException
from backend.app.infrastructure.parsers.base import BaseParser, ParsedBlock, ParsedDocument


class SpreadsheetParser(BaseParser):
    """Parses tabular financial spreadsheets (BOQ / Schedules)."""

    name: str = "SpreadsheetParser"
    version: str = "1.0.0"

    def parse(self, content_bytes: bytes, filename: str) -> ParsedDocument:
        if not content_bytes:
            raise ParserException("Spreadsheet file is empty (0 bytes).")

        ext = filename.lower()
        blocks: List[ParsedBlock] = []
        full_text_parts: List[str] = []
        total_sheets = 1

        if ext.endswith(".csv"):
            try:
                text_content = content_bytes.decode("utf-8-sig", errors="replace")
                reader = csv.reader(io.StringIO(text_content))
                rows: List[List[str]] = list(reader)

                table_lines = [" | ".join([cell.strip() for cell in r]) for r in rows if any(cell.strip() for cell in r)]
                text_repr = "\n".join(table_lines)

                block = ParsedBlock(
                    page_number=1,
                    block_type="table",
                    text=text_repr,
                    section_title="CSV Sheet",
                    table_data=rows,
                    char_offset=0,
                )
                blocks.append(block)
                full_text_parts.append(text_repr)
            except Exception as e:
                raise ParserException(f"Failed to parse CSV spreadsheet: {str(e)}")

        elif ext.endswith(".xlsx"):
            try:
                import openpyxl

                wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True, read_only=True)
                total_sheets = len(wb.sheetnames)
                current_offset = 0

                for sheet_idx, sheet_name in enumerate(wb.sheetnames):
                    sheet = wb[sheet_name]
                    grid: List[List[str]] = []
                    lines: List[str] = []

                    for row in sheet.iter_rows(values_only=True):
                        row_vals = [str(val).strip() if val is not None else "" for val in row]
                        if any(row_vals):
                            grid.append(row_vals)
                            lines.append(" | ".join(row_vals))

                    if lines:
                        sheet_text = f"[Sheet: {sheet_name}]\n" + "\n".join(lines)
                        block = ParsedBlock(
                            page_number=sheet_idx + 1,
                            block_type="table",
                            text=sheet_text,
                            section_title=f"Sheet: {sheet_name}",
                            table_data=grid,
                            char_offset=current_offset,
                        )
                        blocks.append(block)
                        full_text_parts.append(sheet_text)
                        current_offset += len(sheet_text) + 2

                wb.close()
            except Exception as e:
                raise ParserException(f"Failed to parse Excel workbook: {str(e)}")
        else:
            raise ParserException(f"Unsupported spreadsheet format for {filename}")

        full_text = "\n\n".join(full_text_parts)

        return ParsedDocument(
            filename=filename,
            parser_name=self.name,
            parser_version=self.version,
            total_pages=total_sheets,
            blocks=blocks,
            full_text=full_text,
            ocr_required=len(full_text.strip()) == 0,
            statistics={
                "sheets": total_sheets,
                "total_characters": len(full_text),
            },
        )

