from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AdminAccount:
    id: str
    email: str
    password_hash: str
    is_active: bool = True


@dataclass(frozen=True)
class AdminSession:
    # sha256 of the cookie value; the raw token is never stored
    token_hash: bytes
    admin_id: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AdminPrincipal:
    id: str
    email: str
