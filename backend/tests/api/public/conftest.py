import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.admin import deps as admin_deps
from app.services.admin import mock as admin_mock
from app.services.public import deps
from app.services.public import mock


def _provide(svc):
    # a closure, not a default arg: fastapi deep-copies parameter defaults
    return lambda: svc


@pytest.fixture(autouse=True)
def fresh_services():
    # public mocks write into the admin mocks; both get fresh state per test
    innovations = admin_mock.MockInnovationAdminService()
    ideas = admin_mock.MockIdeaAdminService()
    problem_reports = admin_mock.MockProblemReportAdminService()
    grant_calls = admin_mock.MockGrantCallAdminService()
    test_signups = admin_mock.MockTestSignupAdminService()
    documents = mock.MockDocumentStore()
    ratings = mock.MockRatingService()
    services = {
        deps.get_match_service: mock.MockMatchService(innovations, problem_reports),
        deps.get_problem_report_service: mock.MockProblemReportService(problem_reports),
        deps.get_idea_service: mock.MockIdeaService(ideas, grant_calls, documents),
        deps.get_library_service: mock.MockLibraryService(innovations, test_signups),
        deps.get_thread_service: mock.MockThreadService(innovations),
        deps.get_document_service: mock.MockDocumentService(innovations, documents),
        deps.get_knowledge_service: mock.MockKnowledgeService(innovations, grant_calls),
        deps.get_rating_service: ratings,
        admin_deps.get_idea_service: ideas,
        admin_deps.get_problem_report_service: problem_reports,
        admin_deps.get_grant_call_service: grant_calls,
        admin_deps.get_test_signup_service: test_signups,
    }
    app.dependency_overrides = {dep: _provide(svc) for dep, svc in services.items()}
    yield ratings
    app.dependency_overrides = {}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
