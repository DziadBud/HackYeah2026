# public mocks share the admin mock singletons, so public writes appear in the admin panel.
# tests override these the same way as the admin deps
from app.services.admin import deps as admin
from app.services.public.interfaces import (
    DocumentService,
    IdeaService,
    KnowledgeService,
    LibraryService,
    MatchService,
    ProblemReportService,
    ThreadService,
)
from app.services.public.mock import (
    MockDocumentService,
    MockDocumentStore,
    MockIdeaService,
    MockKnowledgeService,
    MockLibraryService,
    MockMatchService,
    MockProblemReportService,
    MockThreadService,
)

_documents = MockDocumentStore()
_match = MockMatchService(admin._innovations, admin._problem_reports)
_problem_reports = MockProblemReportService(admin._problem_reports)
_ideas = MockIdeaService(admin._ideas, admin._grant_calls, _documents)
_library = MockLibraryService(admin._innovations)
_threads = MockThreadService(admin._innovations)
_document_service = MockDocumentService(admin._innovations, _documents)
_knowledge = MockKnowledgeService(admin._innovations, admin._grant_calls)


def get_match_service() -> MatchService:
    return _match


def get_problem_report_service() -> ProblemReportService:
    return _problem_reports


def get_idea_service() -> IdeaService:
    return _ideas


def get_library_service() -> LibraryService:
    return _library


def get_thread_service() -> ThreadService:
    return _threads


def get_document_service() -> DocumentService:
    return _document_service


def get_knowledge_service() -> KnowledgeService:
    return _knowledge
