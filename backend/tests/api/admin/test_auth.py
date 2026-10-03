import re

import pytest
from fastapi.routing import APIRoute

from app.main import app

LOGIN = "/admin/auth/login"

PROTECTED = [
    (method, re.sub(r"\{[^}]+\}", "x", r.path))
    for r in app.routes
    if isinstance(r, APIRoute) and r.path.startswith("/admin") and r.path != LOGIN
    for method in r.methods
]


def test_protected_routes_discovered() -> None:
    assert len(PROTECTED) >= 20


@pytest.mark.parametrize("method,path", PROTECTED)
def test_requires_token(client, method, path) -> None:
    assert client.request(method, path).status_code == 401


def test_non_bearer_header_rejected(client) -> None:
    res = client.get("/admin/inbox", headers={"Authorization": "Basic abc"})
    assert res.status_code == 401


def test_login_ok(client) -> None:
    res = client.post(LOGIN, json={"username": "admin", "password": "pw"})
    assert res.status_code == 200
    assert res.json() == {"access_token": "mock-admin-token", "token_type": "bearer"}


def test_login_missing_password(client) -> None:
    assert client.post(LOGIN, json={"username": "admin"}).status_code == 422


def test_openapi_schema(client) -> None:
    assert client.get("/openapi.json").status_code == 200
