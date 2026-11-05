#!/usr/bin/env python3
"""
TenderForge Database Backup Utility.
Exports and archives database state and storage assets with SHA-256 integrity verification.
"""

import hashlib
import os
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.core.config import settings


def create_backup(backup_dir: str = "./backups") -> str:
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"tenderforge_backup_{timestamp}.tar.gz"
    archive_path = Path(backup_dir) / archive_name

    print(f"[*] Starting TenderForge backup to {archive_path}...")

    with tarfile.open(archive_path, "w:gz") as tar:
        # 1. Backup SQLite database if local
        if "sqlite" in settings.DATABASE_URL:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "").lstrip("/")
            if os.path.exists(db_path):
                print(f"  -> Archiving SQLite database: {db_path}")
                tar.add(db_path, arcname=f"db/{os.path.basename(db_path)}")
            elif os.path.exists("tenderforge.db"):
                print("  -> Archiving root tenderforge.db")
                tar.add("tenderforge.db", arcname="db/tenderforge.db")

        # 2. Backup storage documents
        if os.path.exists(settings.STORAGE_ROOT):
            print(f"  -> Archiving storage assets from {settings.STORAGE_ROOT}")
            tar.add(settings.STORAGE_ROOT, arcname="storage")

        # 3. Backup config directory
        if os.path.exists("./config"):
            print("  -> Archiving YAML configuration")
            tar.add("./config", arcname="config")

    # Compute checksum
    hasher = hashlib.sha256()
    with open(archive_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    checksum_file = archive_path.with_suffix(".tar.gz.sha256")
    checksum_file.write_text(f"{checksum}  {archive_name}\n")

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Backup successfully created: {archive_path} ({size_mb:.2f} MB)")
    print(f"[OK] SHA-256 Integrity: {checksum}")
    return str(archive_path)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "./backups"
    create_backup(out_dir)
