# override these (app.dependency_overrides or edit) to switch to db-backed services
from datetime import timedelta
from functools import cache
from pathlib import Path

from app.config import settings
from app.messaging import RabbitEmbedPublisher
from app.services.admin.auth import AdminAuthService
from app.services.admin.auth_models import AdminAccount
from app.services.admin.auth_store import InMemoryAdminAuthStore
from app.storage import LocalFileStorage
from app.services.admin.interfaces import (
    GrantCallAdminService,
    IdeaAdminService,
    InboxAdminService,
    InnovationAdminService,
    ProblemReportAdminService,
    ReportAdminService,
)
from app.services.admin.innovation_upload import InnovationUploadService
from app.services.admin.mock import (
    MockGrantCallAdminService,
    MockIdeaAdminService,
    MockInboxAdminService,
    MockInnovationAdminService,
    MockProblemReportAdminService,
    MockReportAdminService,
)

_auth = AdminAuthService(
    InMemoryAdminAuthStore(
        [
            AdminAccount(id=email.lower(), email=email.lower(), password_hash=pw_hash)
            for email, pw_hash in settings.admin_accounts.items()
        ]
    ),
    session_ttl=timedelta(hours=settings.admin_session_ttl_hours),
    idle_timeout=timedelta(minutes=settings.admin_session_idle_minutes),
    max_failures=settings.admin_login_max_failures,
    failure_window=timedelta(minutes=settings.admin_login_window_minutes),
)

# module-level singletons so mock state survives between requests
_innovations = MockInnovationAdminService()
_ideas = MockIdeaAdminService()
_problem_reports = MockProblemReportAdminService()
_inbox = MockInboxAdminService(_ideas, _problem_reports)
_grant_calls = MockGrantCallAdminService()
_reports = MockReportAdminService()


def get_auth_service() -> AdminAuthService:
    return _auth


def get_innovation_service() -> InnovationAdminService:
    return _innovations


def get_inbox_service() -> InboxAdminService:
    return _inbox


def get_idea_service() -> IdeaAdminService:
    return _ideas


def get_problem_report_service() -> ProblemReportAdminService:
    return _problem_reports


def get_grant_call_service() -> GrantCallAdminService:
    return _grant_calls


def get_report_service() -> ReportAdminService:
    return _reports


# the pdf and the rabbit message are real; the innovation row goes to the mock until the data model is settled
@cache
def get_innovation_upload_service() -> InnovationUploadService:
    return InnovationUploadService(
        store=_innovations,
        files=LocalFileStorage(Path(settings.upload_dir)),
        publisher=RabbitEmbedPublisher(settings.rabbitmq_url, settings.embed_queue),
        max_bytes=settings.max_upload_bytes,
    )
