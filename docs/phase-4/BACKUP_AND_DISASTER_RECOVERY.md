# TenderForge Phase 4: Backup & Disaster Recovery

## 1. Overview & Business Continuity

For an enterprise procurement platform managing confidential proposals valued in millions of dollars, data durability and zero data loss are non-negotiable requirements. Phase 4 provides automated, cryptographically verified backup and restore capabilities covering both relational database states and binary document storage.

---

## 2. Backup Architecture & Automation (`scripts/backup_db.py`)

The automated backup utility creates a unified, timestamped, compressed archive (`tar.gz`) containing:
1. **Relational Database**: Complete SQL dump (via `pg_dump` for PostgreSQL or file-level snapshot for SQLite).
2. **Document & Evidence Vault**: Ingested PDFs, tender specs, and client completion certificates from `storage/`.
3. **YAML Governance Configurations**: Active rules for financial policies, risk scoring, and application settings from `config/`.
4. **Integrity Digest**: Computes a SHA-256 cryptographic checksum saved alongside the archive.

```
+-----------------------------------------------------------------------------------------+
|                                    BACKUP PIPELINE                                      |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Postgres DB / SQLite]  --> (pg_dump / snapshot) --+                                   |
|  [Document Storage Root] --> (recursive tar)     ---+-> [tenderforge_backup_*.tar.gz]   |
|  [YAML Configuration]    --> (config tree)       --+         |                          |
|                                                              v                          |
|                                                   [Compute SHA-256 Digest]              |
|                                                              v                          |
|                                                   [tenderforge_backup_*.sha256]         |
+-----------------------------------------------------------------------------------------+
```

### Execution Example:
```bash
python scripts/backup_db.py --output backups/production_20261105.tar.gz

# Output:
# [*] Starting TenderForge backup to backups/production_20261105.tar.gz...
#   -> Archiving database: postgresql://tenderforge_user:***@db:5432/tenderforge_prod
#   -> Archiving storage assets from ./storage
#   -> Archiving YAML configuration
# [OK] Backup successfully created: backups/production_20261105.tar.gz (14.2 MB)
# [OK] SHA-256 Integrity: 4f8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
```

---

## 3. Disaster Recovery & Restoration Procedure (`scripts/restore_db.py`)

Restoration is protected by strict pre-flight safety checks:
1. **Checksum Verification**: The utility validates the SHA-256 digest of the backup archive against its companion `.sha256` signature before touching any production database.
2. **Atomic Rollback Safeguard**: If any step fails during decompression or database loading, existing tables and storage folders remain intact.
3. **Interactive Confirmation**: Prompts the operator unless explicitly passed `--force`.

### Restoration Command:
```bash
python scripts/restore_db.py --archive backups/production_20261105.tar.gz --verify-checksum

# Output:
# [*] Verifying archive checksum...
# [OK] Checksum matches: 4f8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
# [*] Restoring database schema and records...
# [*] Unpacking document storage assets to ./storage...
# [*] Re-aligning configuration files...
# [SUCCESS] TenderForge state restored successfully.
```

---

## 4. Recovery Time & Point Objectives (RTO / RPO)
- **Recovery Point Objective (RPO)**: $\le 1$ hour (hourly WAL archiving and daily automated backup cron).
- **Recovery Time Objective (RTO)**: $\le 15$ minutes (automated container restoration via Docker Compose).

