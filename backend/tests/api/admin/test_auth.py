import re

import pytest
from fastapi.routing import APIRoute

from app.config import settings
from app.main import app
from tests.api.admin.conftest import ADMIN_USERNAME, ADMIN_PASSWORD

LOGIN = "/admin/auth/login"
PUBLIC = {LOGIN, "/admin/auth/logout"}

PROTECTED = [
    (method, re.sub(r"\{[^}]+\}", "x", r.path))
    for r in app.routes
    if isinstance(r, APIRoute) and r.path.startswith("/admin") and r.path not in PUBLIC
    for method in r.methods
]


def test_protected_routes_discovered() -> None:
    assert len(PROTECTED) >= 20


@pytest.mark.parametrize("method,path", PROTECTED)
def test_requires_session(client, method, path) -> None:
    assert client.request(method, path).status_code == 401


def test_unknown_session_cookie_rejected(client) -> None:
    client.cookies.set("admin_session", "forged")
    assert client.get("/admin/inbox").status_code == 401


def test_bearer_header_no_longer_accepted(client) -> None:
    res = client.get("/admin/inbox", headers={"Authorization": "Bearer anything"})
    assert res.status_code == 401


def test_login_sets_hardened_cookie(client) -> None:
    res = client.post(LOGIN, json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert res.status_code == 204
    cookie = res.headers["set-cookie"].lower()
    assert "admin_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie


@pytest.mark.parametrize(
    "body,status",
    [
        ({"username": ADMIN_USERNAME, "password": "wrong"}, 401),
        ({"username": "nobody", "password": ADMIN_PASSWORD}, 401),
        ({"username": ADMIN_USERNAME}, 422),
    ],
    ids=["#1 - FAIL - wrong password", "#2 - FAIL - unknown username", "#3 - FAIL - no password"],
)
def test_login_failures(client, body, status) -> None:
    assert client.post(LOGIN, json=body).status_code == status


def test_login_rate_limited(client) -> None:
    for _ in range(5):
        client.post(LOGIN, json={"username": ADMIN_USERNAME, "password": "wrong"})
    res = client.post(LOGIN, json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert res.status_code == 429


def test_me_and_logout(client, auth) -> None:
    assert client.get("/admin/auth/me").json() == {"id": "admin-1", "username": ADMIN_USERNAME}
    token = client.cookies["admin_session"]
    assert client.post("/admin/auth/logout").status_code == 204
    # the old token must be dead server-side, not just removed from the browser
    client.cookies.set("admin_session", token)
    assert client.get("/admin/auth/me").status_code == 401


def test_foreign_origin_blocked(client, auth) -> None:
    res = client.post(
        "/admin/ideas/idea-1/reply",
        json={"message": "x"},
        headers={"Origin": "https://evil.example"},
    )
    assert res.status_code == 403


def test_allowed_origin_passes(client, auth) -> None:
    res = client.post(
        "/admin/ideas/idea-1/reply",
        json={"message": "x"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert res.status_code == 200


def test_openapi_schema(client) -> None:
    assert client.get("/openapi.json").status_code == 200


def test_demo_mode_skips_login(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "debug", True)
    monkeypatch.setattr(settings, "admin_auth_disabled", True)
    assert client.get("/admin/inbox").status_code == 200
    assert client.get("/admin/auth/me").json()["username"] == "demo"


def test_demo_flag_ignored_without_debug(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "debug", False)
    monkeypatch.setattr(settings, "admin_auth_disabled", True)
    assert client.get("/admin/inbox").status_code == 401
