"""API Dependencies."""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.session import get_db
from backend.app.services.document_service import DocumentService
from backend.app.services.tender_service import TenderService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService


def get_doc_service() -> DocumentService:
    return DocumentService()


def get_tndr_service() -> TenderService:
    return TenderService()


def get_intelligence_service() -> TenderIntelligenceService:
    return TenderIntelligenceService()

