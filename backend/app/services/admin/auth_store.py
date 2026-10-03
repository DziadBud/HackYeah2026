import threading
from dataclasses import replace
from datetime import datetime

from app.services.admin.auth_models import AdminAccount, AdminSession


class InMemoryAdminAuthStore:
    # single-instance only: sessions and attempts are lost on restart and not shared
    # between replicas; swap for the postgres store once the db layer lands
    def __init__(self, admins: list[AdminAccount]) -> None:
        self._admins = {a.id: a for a in admins}
        self._by_email = {a.email: a for a in admins}
        self._sessions: dict[bytes, AdminSession] = {}
        self._attempts: list[tuple[str, datetime, bool]] = []
        self._lock = threading.Lock()

    def get_admin_by_email(self, email: str) -> AdminAccount | None:
        return self._by_email.get(email)

    def get_admin(self, admin_id: str) -> AdminAccount | None:
        return self._admins.get(admin_id)

    def create_session(self, session: AdminSession) -> None:
        with self._lock:
            self._sessions[session.token_hash] = session

    def get_session(self, token_hash: bytes) -> AdminSession | None:
        return self._sessions.get(token_hash)

    def touch_session(self, token_hash: bytes, at: datetime) -> None:
        with self._lock:
            if session := self._sessions.get(token_hash):
                self._sessions[token_hash] = replace(session, last_seen_at=at)

    def delete_session(self, token_hash: bytes) -> None:
        with self._lock:
            self._sessions.pop(token_hash, None)

    def record_login_attempt(self, key: str, at: datetime, ok: bool) -> None:
        with self._lock:
            self._attempts.append((key, at, ok))

    def count_failed_attempts(self, key: str, since: datetime) -> int:
        with self._lock:
            return sum(1 for k, at, ok in self._attempts if k == key and at >= since and not ok)
