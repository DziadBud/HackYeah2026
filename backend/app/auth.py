from fastapi import Depends, HTTPException, Request, Response, status

from app.config import settings
from app.services.admin.auth import AdminAuthService
from app.services.admin.auth_models import AdminPrincipal
from app.services.admin.deps import get_auth_service
from app.services.admin.errors import NotAuthenticatedError

SESSION_COOKIE = "admin_session"
# principal used when the login is switched off for the demo
DEMO_ADMIN = AdminPrincipal(id="demo-admin", username="demo")
_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.admin_session_ttl_hours * 3600,
        httponly=True,
        # local dev runs over plain http
        secure=not settings.debug,
        samesite="strict",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        SESSION_COOKIE, httponly=True, secure=not settings.debug, samesite="strict", path="/"
    )


def require_same_origin(request: Request) -> None:
    # csrf defence on top of samesite=strict; non-browser clients send no origin and
    # cannot carry the admin's browser cookie, so a missing header is allowed
    origin = request.headers.get("origin")
    if request.method in _UNSAFE_METHODS and origin and origin not in settings.cors_origins:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "origin not allowed")


def require_admin(
    request: Request, svc: AdminAuthService = Depends(get_auth_service)
) -> AdminPrincipal:
    if settings.debug and settings.admin_auth_disabled:
        return DEMO_ADMIN
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not logged in")
    try:
        return svc.authenticate(token)
    except NotAuthenticatedError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "session expired") from None
