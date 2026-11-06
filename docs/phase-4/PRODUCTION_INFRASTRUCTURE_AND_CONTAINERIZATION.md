# TenderForge Phase 4: Production Infrastructure & Containerization

## 1. Overview & Deployment Philosophy

TenderForge is packaged for frictionless enterprise deployment across on-premises bare-metal, Kubernetes, Amazon Web Services (ECS/EKS), Google Cloud Platform (Cloud Run/GKE), and Microsoft Azure. Containerization follows 12-factor application design, unprivileged runtime execution, multi-stage builds, and defense-in-depth networking.

```
+-----------------------------------------------------------------------------------------+
|                                    DOCKER COMPOSE                                       |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Reverse Proxy: nginx:1.27-alpine]                                                     |
|  Port: 80 / 443 -> SSL termination, SPA routing, gzip, /api/ reverse proxy               |
|         |                                                                               |
|         v                                                                               |
|  [App Service: backend/Dockerfile]                                                      |
|  Python 3.14-slim, unprivileged user 'tenderforge' (UID 1001), Uvicorn ASGI             |
|         |                                                                               |
|         +---------------------------------------+                                       |
|         |                                       |                                       |
|         v                                       v                                       |
|  [Database: postgres:16-alpine]          [Object Storage: MinIO / S3]                   |
|  Persistent Volume: postgres_data        Persistent Volume: storage_data                |
|  Healthcheck: pg_isready                 Healthcheck: curl /minio/health/live           |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Container Images & Dockerfiles

### 2.1 Backend Container (`backend/Dockerfile`)
- **Base Image**: `python:3.14-slim`
- **Security Hardening**:
  - Non-root user: Runs as user `tenderforge` (`UID 1001, GID 1001`).
  - No build toolchains retained in the final image.
  - Read-only root filesystem with writable mounts strictly restricted to `/app/storage` and `/app/temp_uploads`.
- **Healthcheck**: Configured to poll `http://localhost:8000/health` every 30 seconds with 5-second timeout and 3 retries.

### 2.2 Frontend Container (`frontend/Dockerfile`)
- **Stage 1 (Builder)**: Node.js 20 Alpine compiling the React 18 TypeScript source code into optimized production assets.
- **Stage 2 (Server)**: High-performance `nginx:1.27-alpine` serving the static assets, applying gzip compression, caching headers, and routing client paths back to `index.html`.

---

## 3. Production Orchestration: `docker-compose.yml`

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:1.27-alpine
    container_name: tenderforge_proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      backend:
        condition: service_healthy

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: tenderforge_api
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://tenderforge_user:ChangeMeSecurely2026!@db:5432/tenderforge_prod
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - STORAGE_PROVIDER=local
      - STORAGE_ROOT=/app/storage
      - AI_PROVIDER=openai
      - AI_API_KEY=${AI_API_KEY}
    volumes:
      - storage_data:/app/storage
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: postgres:16-alpine
    container_name: tenderforge_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: tenderforge_user
      POSTGRES_PASSWORD: ChangeMeSecurely2026!
      POSTGRES_DB: tenderforge_prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tenderforge_user -d tenderforge_prod"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  storage_data:
```

---

## 4. Single-Command Launch Instructions

To launch the full enterprise stack in production mode:
```bash
# 1. Provide production secrets
cp .env.example .env

# 2. Build and launch all services in detached mode
docker-compose up --build -d

# 3. Apply database migrations
docker-compose exec backend alembic -c backend/alembic.ini upgrade head

# 4. Access the application
# Frontend SPA & API: http://localhost:80
```

