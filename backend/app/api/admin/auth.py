from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth import (
    SESSION_COOKIE,
    clear_session_cookie,
    require_admin,
    set_session_cookie,
)
from app.schemas.admin.auth import AdminMe, LoginRequest
from app.services.admin.auth import AdminAuthService
from app.services.admin.auth_models import AdminPrincipal
from app.services.admin.deps import get_auth_service
from app.services.admin.errors import InvalidCredentialsError, TooManyAttemptsError

router = APIRouter(prefix="/auth", tags=["admin:auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(
    body: LoginRequest,
    response: Response,
    svc: AdminAuthService = Depends(get_auth_service),
) -> None:
    try:
        token = svc.login(body.username, body.password)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials") from None
    except TooManyAttemptsError:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "too many failed logins, try again later"
        ) from None
    set_session_cookie(response, token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    svc: AdminAuthService = Depends(get_auth_service),
) -> None:
    if token := request.cookies.get(SESSION_COOKIE):
        svc.logout(token)
    clear_session_cookie(response)


@router.get("/me", response_model=AdminMe)
def me(admin: AdminPrincipal = Depends(require_admin)) -> AdminMe:
    return AdminMe(id=admin.id, username=admin.username)
