#!/usr/bin/env python3
"""
TenderForge Database Restore Utility.
Restores database and configuration from a verified backup archive.
"""

import hashlib
import os
import sys
import tarfile
from pathlib import Path


def restore_backup(archive_path: str, target_dir: str = ".") -> bool:
    path = Path(archive_path)
    if not path.is_file():
        print(f"[ERROR] Backup archive not found: {archive_path}")
        return False

    # Check sha256 checksum if present
    checksum_file = path.with_suffix(".tar.gz.sha256")
    if checksum_file.is_file():
        expected = checksum_file.read_text().split()[0].strip()
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual = hasher.hexdigest()
        if expected != actual:
            print(f"[ERROR] Checksum mismatch! Expected {expected}, got {actual}")
            return False
        print(f"[OK] SHA-256 integrity check verified: {actual}")

    print(f"[*] Extracting archive {path} into {target_dir}...")
    with tarfile.open(path, "r:gz") as tar:
        tar.extractall(path=target_dir)

    print("[OK] Restore completed successfully.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/restore_db.py <backup_archive.tar.gz> [target_dir]")
        sys.exit(1)
    archive = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "."
    restore_backup(archive, target)
