# TenderForge Phase 4: Observability & Diagnostics

## 1. Overview & Telemetry Architecture

Enterprise operations demand complete visibility into system latency, error frequencies, database connection states, storage throughput, and multi-agent execution status. TenderForge incorporates structured JSON logging, distributed correlation IDs, and standard Kubernetes liveness, readiness, and diagnostic probes.

```
+-----------------------------------------------------------------------------------------+
|                                    OBSERVABILITY TIER                                   |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Incoming HTTP Request]                                                                |
|           |                                                                             |
|           v                                                                             |
|  [CorrelationIdMiddleware] --> Extracts/Generates X-Correlation-ID                      |
|           |                    Injects into ContextVar & Response Headers               |
|           v                                                                             |
|  [Structured JSON Logger]  --> Outputs JSON lines with timestamp, level, correlation_id  |
|           |                                                                             |
|           +-----------------------+-----------------------+                             |
|           |                       |                       |                             |
|           v                       v                       v                             |
|    [/health Probe]          [/ready Probe]         [/diagnostics Probe]                 |
|  (Liveness / 200 OK)    (DB + Storage Checks)   (Full Subsystem Health Telemetry)       |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Distributed Tracing & Correlation IDs

Every inbound request is assigned a unique UUID `X-Correlation-ID` header:
- If the incoming request contains `X-Correlation-ID`, it is preserved for cross-service distributed tracing.
- If missing, a fresh UUIDv4 is generated.
- The ID is stored in Python's `contextvars.ContextVar` and automatically included in all log entries, API responses, and database audit events.

### Log Format Example:
```json
{
  "timestamp": "2026-11-05T19:45:12.381Z",
  "level": "INFO",
  "logger": "tenderforge.auth",
  "correlation_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "user_id": "usr-jane-doe-admin",
  "action": "USER_LOGIN_SUCCESS",
  "details": "User jane.doe@acme.com authenticated successfully from 192.168.1.50"
}
```

---

## 3. Health & Readiness Probes (`health.py`)

### 3.1 Liveness Probe: `GET /health`
- **Purpose**: Verifies that the ASGI worker process is alive and accepting event loop cycles.
- **Response**:
```json
{
  "status": "healthy",
  "app_name": "TenderForge",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2026-11-05T19:45:12.400Z"
}
```

### 3.2 Readiness Probe: `GET /ready`
- **Purpose**: Verifies that downstream dependencies (PostgreSQL database, object storage) are operational before routing client traffic.
- **Checks Executed**:
  1. `database`: Runs `SELECT 1` against the active connection pool.
  2. `storage`: Performs a write-read-delete probe to verify storage writeability.
  3. `ai_provider`: Validates model credentials and base URL connectivity.
  4. `auth_subsystem`: Confirms JWT signing secrets are initialized.
- **Status Codes**: Returns `200 OK` if all critical dependencies pass; returns `503 Service Unavailable` if database or storage fails.

### 3.3 Diagnostic Telemetry: `GET /diagnostics`
- **Purpose**: Provides non-sensitive operational telemetry for DevOps dashboards, Datadog/Grafana monitors, and administrative troubleshooting without leaking secrets.
- **Fields**: Database pool utilization, storage provider type, configured AI model, JWT token expiration parameters, and server timestamp.

