# TenderForge Backend

This package contains the core FastAPI application, document intelligence parsers, database persistence models, application services, and Switch integration contracts.

## Running Locally

```powershell
# From the project root
python -m uvicorn backend.app.main:app --reload --port 8000
```

## Running Migrations

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

