# override these (app.dependency_overrides or edit) to switch to db-backed services
from app.services.admin.interfaces import (
    AuthAdminService,
    GrantCallAdminService,
    IdeaAdminService,
    InboxAdminService,
    InnovationAdminService,
    ProblemReportAdminService,
    ReportAdminService,
)
from app.services.admin.mock import (
    MockAuthAdminService,
    MockGrantCallAdminService,
    MockIdeaAdminService,
    MockInboxAdminService,
    MockInnovationAdminService,
    MockProblemReportAdminService,
    MockReportAdminService,
)

# module-level singletons so mock state survives between requests
_auth = MockAuthAdminService()
_innovations = MockInnovationAdminService()
_inbox = MockInboxAdminService()
_ideas = MockIdeaAdminService()
_problem_reports = MockProblemReportAdminService()
_grant_calls = MockGrantCallAdminService()
_reports = MockReportAdminService()


def get_auth_service() -> AuthAdminService:
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
