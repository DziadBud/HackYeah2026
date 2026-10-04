from fastapi import APIRouter, Depends

from app.schemas.admin.grant_applications import GrantApplicationDecision
from app.schemas.public.grant_applications import GrantApplication, GrantApplicationStatus
from app.services.admin.deps import get_grant_application_service
from app.services.admin.interfaces import GrantApplicationAdminService

router = APIRouter(prefix="/grant-applications", tags=["admin:grant-applications"])


@router.get("", response_model=list[GrantApplication])
def list_grant_applications(
    status: GrantApplicationStatus | None = None,
    grant_call_id: str | None = None,
    svc: GrantApplicationAdminService = Depends(get_grant_application_service),
) -> list[GrantApplication]:
    return svc.list(status, grant_call_id)


@router.get("/{application_id}", response_model=GrantApplication)
def get_grant_application(
    application_id: str,
    svc: GrantApplicationAdminService = Depends(get_grant_application_service),
) -> GrantApplication:
    return svc.get(application_id)


@router.post("/{application_id}/status", response_model=GrantApplication)
def decide_grant_application(
    application_id: str,
    body: GrantApplicationDecision,
    svc: GrantApplicationAdminService = Depends(get_grant_application_service),
) -> GrantApplication:
    return svc.decide(application_id, body.status, body.message)
