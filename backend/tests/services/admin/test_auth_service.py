from datetime import datetime, timedelta, timezone

import pytest

from app.services.admin.auth import AdminAuthService, hash_password, hash_token
from app.services.admin.auth_models import AdminAccount
from app.services.admin.auth_store import InMemoryAdminAuthStore
from app.services.admin.errors import (
    InvalidCredentialsError,
    NotAuthenticatedError,
    TooManyAttemptsError,
)

PASSWORD = "correct horse battery"
T0 = datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture(scope="module")
def pw_hash() -> str:
    return hash_password(PASSWORD)


@pytest.fixture
def clock() -> Clock:
    return Clock()


def make(pw_hash: str, clock: Clock, active: bool = True):
    store = InMemoryAdminAuthStore(
        [AdminAccount(id="a1", email="admin@rops.test", password_hash=pw_hash, is_active=active)]
    )
    svc = AdminAuthService(
        store,
        session_ttl=timedelta(hours=8),
        idle_timeout=timedelta(minutes=30),
        max_failures=5,
        failure_window=timedelta(minutes=15),
        now=clock,
    )
    return svc, store


@pytest.mark.parametrize(
    "email,password,active,err",
    [
        ("admin@rops.test", PASSWORD, True, None),
        (" Admin@ROPS.test ", PASSWORD, True, None),
        ("admin@rops.test", "wrong", True, InvalidCredentialsError),
        ("ghost@rops.test", PASSWORD, True, InvalidCredentialsError),
        ("admin@rops.test", PASSWORD, False, InvalidCredentialsError),
    ],
    ids=[
        "#1 - OK",
        "#2 - OK - email normalised",
        "#3 - FAIL - wrong password",
        "#4 - FAIL - unknown email",
        "#5 - FAIL - inactive admin",
    ],
)
def test_login(pw_hash, clock, email, password, active, err) -> None:
    svc, _ = make(pw_hash, clock, active)
    if err:
        with pytest.raises(err):
            svc.login(email, password)
    else:
        assert svc.authenticate(svc.login(email, password)).id == "a1"


def test_raw_token_never_stored(pw_hash, clock) -> None:
    svc, store = make(pw_hash, clock)
    token = svc.login("admin@rops.test", PASSWORD)
    assert store.get_session(token.encode()) is None
    assert store.get_session(hash_token(token)) is not None


def test_rate_limit(pw_hash, clock) -> None:
    svc, _ = make(pw_hash, clock)
    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            svc.login("admin@rops.test", "wrong")
    with pytest.raises(TooManyAttemptsError):
        svc.login("admin@rops.test", PASSWORD)


def test_rate_limit_window_expires(pw_hash, clock) -> None:
    svc, _ = make(pw_hash, clock)
    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            svc.login("admin@rops.test", "wrong")
    clock.now += timedelta(minutes=16)
    assert svc.login("admin@rops.test", PASSWORD)


@pytest.mark.parametrize(
    "steps,ok",
    [
        ([timedelta(minutes=29)], True),
        ([timedelta(minutes=31)], False),
        ([timedelta(minutes=25)] * 19 + [timedelta(minutes=30)], False),
    ],
    ids=["#1 - OK - within idle", "#2 - FAIL - idle timeout", "#3 - FAIL - absolute ttl"],
)
def test_session_expiry(pw_hash, clock, steps, ok) -> None:
    svc, _ = make(pw_hash, clock)
    token = svc.login("admin@rops.test", PASSWORD)
    for step in steps[:-1]:
        clock.now += step
        svc.authenticate(token)
    clock.now += steps[-1]
    if ok:
        svc.authenticate(token)
    else:
        with pytest.raises(NotAuthenticatedError):
            svc.authenticate(token)


def test_logout_revokes(pw_hash, clock) -> None:
    svc, _ = make(pw_hash, clock)
    token = svc.login("admin@rops.test", PASSWORD)
    svc.logout(token)
    with pytest.raises(NotAuthenticatedError):
        svc.authenticate(token)


def test_malformed_configured_hash_fails_closed(clock) -> None:
    svc, _ = make("not-a-hash", clock)
    with pytest.raises(InvalidCredentialsError):
        svc.login("admin@rops.test", PASSWORD)
