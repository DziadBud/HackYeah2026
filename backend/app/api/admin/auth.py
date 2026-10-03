from fastapi import APIRouter, Depends

from app.schemas.admin.auth import LoginRequest, TokenResponse
from app.services.admin.deps import get_auth_service
from app.services.admin.interfaces import AuthAdminService

router = APIRouter(prefix="/auth", tags=["admin:auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest, svc: AuthAdminService = Depends(get_auth_service)
) -> TokenResponse:
    return TokenResponse(access_token=svc.login(body.username, body.password))
