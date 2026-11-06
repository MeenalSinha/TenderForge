# Phase 5: Deployment, Configuration & Operations Guide

## 1. Overview

TenderForge is engineered for production containerized deployment using Docker Compose, PostgreSQL, Redis, and Nginx. This guide outlines configuration settings, deployment procedures, and operational maintenance.

---

## 2. Configuration Files

All Phase 5 services are dynamically configured via centralized YAML files in `config/`:

| File | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `config/procurement_sources.yaml` | Connectors & Endpoints | Connector timeouts, max batch sizes, default rate-limit delays, user-agent headers. |
| `config/opportunity_matching.yaml` | 9-Dimension Weights | Dimension weights ($w_1 \dots w_9$), recommendation tier thresholds, hard gate flags. |
| `config/monitoring_policies.yaml` | Corrigenda Polling | Interval tiers (Standard 24h, Critical 6h, Urgent 1h), materiality criteria thresholds. |
| `config/market_intelligence.yaml` | Market & Learning | Learning significance threshold ($N=5$), discount calculation method, provenance rules. |

---

## 3. Environment Variables

Production deployments require key environment variables configured in `.env`:

```ini
# Application Core
ENVIRONMENT=production
DEBUG=false
APP_SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database
DATABASE_URL=postgresql://tenderforge_user:StrongPassword2026!@postgres:5432/tenderforge_prod

# Switch Room Integration
SWITCH_API_URL=https://switch.example.internal/api/v1
SWITCH_API_KEY=switch_prod_key_2026_xyz
SWITCH_WEBHOOK_SECRET=switch_webhook_secret_hmac_sha256

# Storage & Document Vault
DOCUMENT_STORAGE_DIR=/var/tenderforge/vault
MAX_UPLOAD_SIZE_BYTES=52428800
```

---

## 4. Production Docker Deployment

To launch the full containerized stack:

```powershell
# 1. Build and launch services in background
docker compose up -d --build

# 2. Execute database migrations
docker compose exec backend alembic -c backend/alembic.ini upgrade head

# 3. Check health status
curl -f http://localhost:8000/api/v1/health
```

---

## 5. Background Daemon & Task Execution

Tender continuous monitoring executes via the background polling daemon:
```powershell
python -m backend.app.services.tender_monitoring_service --poll-all
```
In containerized production, this runs as a Celery/Beat periodic worker service or systemd timer.
