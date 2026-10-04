# per-request db-backed services; tests override these with the mocks in mock.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.gemini import GeminiClient
from app.clients.rag import RagClient
from app.config import settings
from app.db.session import get_db
from app.services.public.db import (
    DbDocumentService,
    DbIdeaService,
    DbKnowledgeService,
    DbLibraryService,
    DbMatchService,
    DbProblemReportService,
    DbRatingService,
    DbThreadService,
)
from app.services.public.interfaces import (
    DocumentService,
    IdeaService,
    KnowledgeService,
    LibraryService,
    MatchService,
    ProblemReportService,
    RatingService,
    ThreadService,
)


_rag = RagClient(settings.rag_url, settings.rag_timeout_seconds, settings.rag_query_timeout_seconds)
_gemini = GeminiClient()


def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    return DbMatchService(db, _rag)


def get_problem_report_service(db: Session = Depends(get_db)) -> ProblemReportService:
    return DbProblemReportService(db)


def get_idea_service(db: Session = Depends(get_db)) -> IdeaService:
    return DbIdeaService(db, _gemini)


def get_library_service(db: Session = Depends(get_db)) -> LibraryService:
    return DbLibraryService(db)


def get_thread_service(db: Session = Depends(get_db)) -> ThreadService:
    return DbThreadService(db)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DbDocumentService(db)


def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return DbKnowledgeService(db)


def get_rating_service(db: Session = Depends(get_db)) -> RatingService:
    return DbRatingService(db)
