import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}
