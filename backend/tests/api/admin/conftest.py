from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.admin import deps, mock
from app.services.admin.auth import AdminAuthService, hash_password
from app.services.admin.auth_models import AdminAccount
from app.services.admin.auth_store import InMemoryAdminAuthStore

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "correct horse battery"


@pytest.fixture(scope="session")
def admin_password_hash() -> str:
    # argon2 is slow on purpose; hash once per run
    return hash_password(ADMIN_PASSWORD)


def make_auth_service(password_hash: str, **overrides) -> AdminAuthService:
    store = InMemoryAdminAuthStore(
        [AdminAccount(id="admin-1", username=ADMIN_USERNAME, password_hash=password_hash)]
    )
    params = {
        "session_ttl": timedelta(hours=8),
        "idle_timeout": timedelta(minutes=30),
        "max_failures": 5,
        "failure_window": timedelta(minutes=15),
    } | overrides
    return AdminAuthService(store, **params)


@pytest.fixture(autouse=True)
def fresh_services(admin_password_hash):
    # mock services are stateful singletons; give each test its own copy
    auth = make_auth_service(admin_password_hash)
    innovations = mock.MockInnovationAdminService()
    ideas = mock.MockIdeaAdminService()
    problem_reports = mock.MockProblemReportAdminService()
    inbox = mock.MockInboxAdminService(ideas, problem_reports)
    grant_calls = mock.MockGrantCallAdminService()
    reports = mock.MockReportAdminService()
    threads = mock.MockThreadAdminService()
    signups = mock.MockTestSignupAdminService()
    app.dependency_overrides = {
        deps.get_auth_service: lambda: auth,
        deps.get_innovation_service: lambda: innovations,
        deps.get_idea_service: lambda: ideas,
        deps.get_problem_report_service: lambda: problem_reports,
        deps.get_inbox_service: lambda: inbox,
        deps.get_grant_call_service: lambda: grant_calls,
        deps.get_report_service: lambda: reports,
        deps.get_thread_service: lambda: threads,
        deps.get_test_signup_service: lambda: signups,
    }
    yield
    app.dependency_overrides = {}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth(client) -> dict[str, str]:
    # logs `client` in; the session cookie lives in its cookie jar, so no headers are needed
    res = client.post("/admin/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert res.status_code == 204
    return {}
