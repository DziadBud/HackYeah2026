import hashlib
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.services.admin.auth_models import AdminPrincipal, AdminSession
from app.services.admin.errors import (
    InvalidCredentialsError,
    NotAuthenticatedError,
    TooManyAttemptsError,
)
from app.services.admin.interfaces import AdminAuthStore

_hasher = PasswordHasher()
# verified when the email is unknown, so response time doesn't reveal which emails exist
_DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(16))
# avoid a store write on every request
_TOUCH_EVERY = timedelta(minutes=1)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def hash_token(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AdminAuthService:
    def __init__(
        self,
        store: AdminAuthStore,
        session_ttl: timedelta,
        idle_timeout: timedelta,
        max_failures: int,
        failure_window: timedelta,
        now: Callable[[], datetime] = _utcnow,
    ) -> None:
        self._store = store
        self._session_ttl = session_ttl
        self._idle_timeout = idle_timeout
        self._max_failures = max_failures
        self._failure_window = failure_window
        self._now = now

    def login(self, email: str, password: str) -> str:
        """returns the raw session token for the cookie"""
        now = self._now()
        email = email.strip().lower()
        key = f"email:{email}"
        if self._store.count_failed_attempts(key, now - self._failure_window) >= self._max_failures:
            raise TooManyAttemptsError

        admin = self._store.get_admin_by_email(email)
        if not self._verify(admin.password_hash if admin else _DUMMY_HASH, password) or not (
            admin and admin.is_active
        ):
            self._store.record_login_attempt(key, now, ok=False)
            raise InvalidCredentialsError

        self._store.record_login_attempt(key, now, ok=True)
        token = secrets.token_urlsafe(32)
        self._store.create_session(
            AdminSession(
                token_hash=hash_token(token),
                admin_id=admin.id,
                created_at=now,
                last_seen_at=now,
                expires_at=now + self._session_ttl,
            )
        )
        return token

    def authenticate(self, token: str) -> AdminPrincipal:
        now = self._now()
        token_hash = hash_token(token)
        session = self._store.get_session(token_hash)
        if session is None:
            raise NotAuthenticatedError
        if now >= session.expires_at or now - session.last_seen_at > self._idle_timeout:
            self._store.delete_session(token_hash)
            raise NotAuthenticatedError

        admin = self._store.get_admin(session.admin_id)
        if admin is None or not admin.is_active:
            self._store.delete_session(token_hash)
            raise NotAuthenticatedError

        if now - session.last_seen_at >= _TOUCH_EVERY:
            self._store.touch_session(token_hash, now)
        return AdminPrincipal(id=admin.id, email=admin.email)

    def logout(self, token: str) -> None:
        self._store.delete_session(hash_token(token))

    @staticmethod
    def _verify(password_hash: str, password: str) -> bool:
        try:
            return _hasher.verify(password_hash, password)
        # malformed configured hash fails closed
        except (VerificationError, InvalidHashError):
            return False
