# TenderForge Phase 4: Production Database & Storage

## 1. Overview & Data Layer Architecture

The TenderForge data tier is engineered for enterprise high availability, concurrency, transaction isolation, and horizontal scalability. Phase 4 establishes enterprise connection pooling for PostgreSQL while maintaining transparent local fallback to SQLite for edge and developer workstations.

```
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION TIER                                     |
+-----------------------------------------------------------------------------------------+
                             |                             |
      (Relational Data)      v                             v      (Blobs & Artifacts)
+------------------------------------+    +-----------------------------------------------+
|     SQLALCHEMY CONNECTION POOL     |    |           OBJECT STORAGE ADAPTER              |
|  - pool_size: 10                   |    |  - Provider: local / S3 / MinIO / GCS         |
|  - max_overflow: 20                |    |  - Content-Addressed SHA-256 Storage          |
|  - pool_recycle: 1800s (30 min)    |    |  - Stream I/O for Large Documents (> 50 MB)   |
|  - pool_pre_ping: True (Liveness)  |    |  - Automatic Fallback Graceful Degradation    |
+------------------------------------+    +-----------------------------------------------+
                 |                                                |
                 v                                                v
+------------------------------------+    +-----------------------------------------------+
|        POSTGRESQL 16 CLUSTER       |    |         MINIO / S3 ENTERPRISE BUCKET          |
|  - WAL Archiving & Point-In-Time   |    |  - SSE-S3 Encryption at Rest                  |
|  - ACID Transactional Guarantees   |    |  - Immutable Versioning & Retention Policies  |
+------------------------------------+    +-----------------------------------------------+
```

---

## 2. PostgreSQL Connection Pooling (`session.py`)

In `backend/app/infrastructure/database/session.py`, connection pooling parameters are dynamically configured based on the connection scheme:

```python
if "postgresql" in database_url:
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,         # Default: 10 connections
        max_overflow=settings.DB_MAX_OVERFLOW,   # Default: 20 overflow burst
        pool_recycle=1800,                       # Recycle connections older than 30 mins
        pool_pre_ping=True,                      # Validate connection liveness before query
        echo=settings.DB_ECHO,
    )
```

### Benefits of Pre-Ping and Recycling
- **Zero Stale Connection Exceptions**: Automatically detects dropped TCP sockets caused by stateful firewalls or cloud load balancers.
- **Leak Prevention**: Unclosed sessions are reclaimed gracefully back into the connection pool.

---

## 3. Pluggable Storage Abstraction (`object_storage.py`)

The object storage subsystem implements `BaseStorageProvider`:

```python
class BaseStorageProvider(ABC):
    @abstractmethod
    def save(self, relative_path: str, data: bytes, content_type: Optional[str] = None) -> str: ...
    @abstractmethod
    def read(self, relative_path: str) -> bytes: ...
    @abstractmethod
    def exists(self, relative_path: str) -> bool: ...
    @abstractmethod
    def delete(self, relative_path: str) -> bool: ...
    @abstractmethod
    def get_url(self, relative_path: str) -> str: ...
```

### Storage Providers Supported:
1. **`LocalStorageProvider`**: Uses directory structure partitioned by organization and tender ID (`storage/tenders/{tender_id}/...`). Ideal for local evaluation, air-gapped deployments, and automated testing.
2. **`S3CompatibleStorageProvider`**: Connects via `boto3` to Amazon S3, MinIO, or Google Cloud Storage (via S3 interoperability). Includes automatic local disk fallback if network storage is unreachable.

---

## 4. Alembic Schema Version Tracking

The database lifecycle is governed strictly by version-controlled Alembic migrations:
- `001_initial_schema.py`: Base tender, document, requirement, and evidence tables.
- `002_phase2_switch_agents.py`: Agent execution records, Switch room mappings, audit events.
- `003_phase3_advanced_intelligence.py`: Viability radar, financial BOQ items, 5x5 risks, milestones.
- `004_phase4_auth_models.py`: Enterprise users, organization memberships, sessions, password resets.
