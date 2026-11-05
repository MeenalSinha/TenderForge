"""
Unit Tests: Security Utilities, Path Traversal Sanitization, & File Signatures.
"""

from backend.app.core.security import (
    compute_sha256,
    sanitize_filename,
    verify_file_signature,
)


def test_sanitize_filename_path_traversal():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe.docx") == "cmd.exe.docx"
    assert sanitize_filename("../../../../secret.txt") == "secret.txt"


def test_sanitize_filename_special_chars():
    dirty = "My Tender Document (v1.0) & Final #99.pdf"
    clean = sanitize_filename(dirty)
    assert ".." not in clean
    assert "/" not in clean
    assert "\\" not in clean
    assert clean.endswith(".pdf")


def test_compute_sha256():
    data = b"Hello TenderForge 2026"
    digest = compute_sha256(data)
    assert len(digest) == 64
    assert digest == compute_sha256(data)
    assert digest != compute_sha256(b"Different content")


def test_verify_file_signature():
    assert verify_file_signature(b"%PDF-1.7\n...", ".pdf") is True
    assert verify_file_signature(b"PK\x03\x04\x14\x00...", ".docx") is True
    assert verify_file_signature(b"PK\x03\x04\x14\x00...", ".xlsx") is True
    assert verify_file_signature(b"Plain text line", ".txt") is True
    # Spoofed file
    assert verify_file_signature(b"MZ\x90\x00\x03\x00...", ".pdf") is False
    assert verify_file_signature(b"GIF89a...", ".docx") is False

