# TenderForge Production Reliability & Security Architecture

## 1. Overview & Security Objectives

TenderForge handles sensitive corporate evidence (audited accounts, proprietary IP, pricing models, employee qualifications) and mission-critical government proposals.

Security and reliability are non-negotiable architectural foundations.

---

## 2. Security Defense-in-Depth

1. **File Validation & Magic Byte Verification**: Uploaded files undergo extension validation, MIME type checking, and magic byte signature verification to defeat MIME spoofing.
2. **Path Traversal Protection**: Filenames are strictly sanitized to prevent directory traversal attacks (`../../etc/passwd`).
3. **Prompt Injection Hardening**: All LLM prompt templates isolate external document content within explicit XML boundary tags (`<source_document>`) with strict instructions to ignore embedded system override instructions.
4. **Token Leak Protection**: All configuration files, database connection strings, and logs mask API keys, passwords, and sensitive headers.
5. **Deterministic Arithmetic**: Eliminates floating-point vulnerabilities in financial schedules.

---

## 3. Reliability & Transactional Integrity

- **Database Atomicity**: All multi-step operations (e.g., proposal drafting with line items or optimization updates) execute within SQLAlchemy database transactions. Errors trigger automatic rollback.
- **SQLite Concurrency & Date Safety**: Timezone-aware datetimes are normalized to UTC before persisting to SQLite to prevent offset-naive comparison runtime exceptions.
- **Stateless Agent Operations**: Switch integration tools operate statelessly against the database, ensuring resilient horizontal scaling.
