# per-request db-backed services; tests override these with the mocks in mock.py
from fastapi import Depends
from sqlalchemy.orm import Session

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
    DbThreadService,
)
from app.services.notify import Notifier, get_notifier
from app.services.public.interfaces import (
    DocumentService,
    IdeaService,
    KnowledgeService,
    LibraryService,
    MatchService,
    ProblemReportService,
    ThreadService,
)


_rag = RagClient(settings.rag_url, settings.rag_timeout_seconds, settings.rag_query_timeout_seconds)


def get_match_service(
    db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)
) -> MatchService:
    return DbMatchService(db, _rag, notifier)


def get_problem_report_service(db: Session = Depends(get_db)) -> ProblemReportService:
    return DbProblemReportService(db)


def get_idea_service(
    db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)
) -> IdeaService:
    return DbIdeaService(db, notifier)


def get_library_service(db: Session = Depends(get_db)) -> LibraryService:
    return DbLibraryService(db)


def get_thread_service(
    db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)
) -> ThreadService:
    return DbThreadService(db, notifier)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DbDocumentService(db)


def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return DbKnowledgeService(db)
