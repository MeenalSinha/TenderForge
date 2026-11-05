"""
Pytest Test Fixtures and Test Harness Setup.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.core.config import settings
from backend.app.infrastructure.database.models import Base
from backend.app.infrastructure.database.session import get_db
from backend.app.main import create_app


@pytest.fixture(scope="session")
def test_temp_dir() -> Generator[str, None, None]:
    """Create isolated temporary storage directory."""
    temp_dir = tempfile.mkdtemp(prefix="tenderforge_test_")
    orig_storage = settings.STORAGE_ROOT
    orig_temp = settings.TEMP_STORAGE_ROOT
    settings.STORAGE_ROOT = os.path.join(temp_dir, "storage")
    settings.TEMP_STORAGE_ROOT = os.path.join(temp_dir, "temp")
    os.makedirs(settings.STORAGE_ROOT, exist_ok=True)
    os.makedirs(settings.TEMP_STORAGE_ROOT, exist_ok=True)

    yield temp_dir

    shutil.rmtree(temp_dir, ignore_errors=True)
    settings.STORAGE_ROOT = orig_storage
    settings.TEMP_STORAGE_ROOT = orig_temp


@pytest.fixture(scope="function")
def db_session(test_temp_dir: str) -> Generator[Session, None, None]:
    """Create an isolated in-memory SQLite database for each test function."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        test_engine.dispose()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Test client with overridden database dependency."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
