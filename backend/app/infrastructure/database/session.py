"""
Database Session and Engine Management (SQLAlchemy 2.0).
Provides connection pooling, pool pre-ping, and automatic session cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

# Engine configuration with pooling
engine_kwargs: Dict[str, Any] = {
    "echo": settings.DB_ECHO,
    "pool_pre_ping": True,
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Enterprise PostgreSQL connection pool settings
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_recycle"] = 1800  # Recycle connections every 30 minutes

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding scoped database session with automatic commit/rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
