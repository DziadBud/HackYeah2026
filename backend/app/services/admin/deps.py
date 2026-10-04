# per-request db-backed services; tests override these with the mocks in mock.py
from datetime import timedelta
from functools import cache
from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.rag import RagClient
from app.config import settings
from app.db.session import SessionLocal, get_db
from app.services.admin.auth import AdminAuthService, hash_password
from app.services.admin.auth_models import AdminAccount
from app.services.admin.auth_store import InMemoryAdminAuthStore
from app.services.admin.db import (
    DbGrantApplicationAdminService,
    DbGrantCallAdminService,
    DbIdeaAdminService,
    DbInboxAdminService,
    DbInnovationAdminService,
    DbInnovationStore,
    DbProblemReportAdminService,
    DbReportAdminService,
    DbTestSignupAdminService,
    DbThreadAdminService,
)
from app.services.admin.innovation_upload import InnovationUploadService
from app.services.admin.interfaces import (
    GrantApplicationAdminService,
    GrantCallAdminService,
    IdeaAdminService,
    InboxAdminService,
    InnovationAdminService,
    ProblemReportAdminService,
    ReportAdminService,
    TestSignupAdminService,
    ThreadAdminService,
)
from app.services.notify import Notifier, get_notifier
from app.storage import LocalFileStorage

_admins = (
    # hashed once at startup, so login keeps the constant-time argon2 check
    [
        AdminAccount(
            id=settings.admin_username,
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
    ]
    if settings.admin_username and settings.admin_password
    else []
)
_auth = AdminAuthService(
    InMemoryAdminAuthStore(_admins),
    session_ttl=timedelta(hours=settings.admin_session_ttl_hours),
    idle_timeout=timedelta(minutes=settings.admin_session_idle_minutes),
    max_failures=settings.admin_login_max_failures,
    failure_window=timedelta(minutes=settings.admin_login_window_minutes),
)

def get_auth_service() -> AdminAuthService:
    return _auth


def get_innovation_service(db: Session = Depends(get_db)) -> InnovationAdminService:
    return DbInnovationAdminService(db)


def get_inbox_service(db: Session = Depends(get_db)) -> InboxAdminService:
    return DbInboxAdminService(db)


def get_idea_service(db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)) -> IdeaAdminService:
    return DbIdeaAdminService(db, notifier)


def get_problem_report_service(db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)) -> ProblemReportAdminService:
    return DbProblemReportAdminService(db, notifier)


def get_grant_call_service(db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)) -> GrantCallAdminService:
    return DbGrantCallAdminService(db, notifier)


def get_grant_application_service(db: Session = Depends(get_db)) -> GrantApplicationAdminService:
    return DbGrantApplicationAdminService(db)


def get_report_service(db: Session = Depends(get_db)) -> ReportAdminService:
    return DbReportAdminService(db)


def get_thread_service(db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)) -> ThreadAdminService:
    return DbThreadAdminService(db, notifier)


def get_test_signup_service(
    db: Session = Depends(get_db), notifier: Notifier = Depends(get_notifier)
) -> TestSignupAdminService:
    return DbTestSignupAdminService(db, notifier)


# own short sessions inside the store: the row must be committed before rag embeds it
@cache
def get_innovation_upload_service() -> InnovationUploadService:
    return InnovationUploadService(
        store=DbInnovationStore(SessionLocal),
        files=LocalFileStorage(Path(settings.upload_dir)),
        rag=RagClient(settings.rag_url, settings.rag_timeout_seconds, settings.rag_query_timeout_seconds),
        max_bytes=settings.max_upload_bytes,
    )
