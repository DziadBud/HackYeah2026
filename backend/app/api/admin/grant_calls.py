from fastapi import APIRouter, Depends, status

from app.schemas.admin.grant_calls import GrantCall, GrantCallCreate, GrantCallUpdate
from app.services.admin.deps import get_grant_call_service
from app.services.admin.interfaces import GrantCallAdminService

router = APIRouter(prefix="/grant-calls", tags=["admin:grant-calls"])


@router.get("", response_model=list[GrantCall])
def list_grant_calls(
    svc: GrantCallAdminService = Depends(get_grant_call_service),
) -> list[GrantCall]:
    return svc.list()


@router.post("", response_model=GrantCall, status_code=status.HTTP_201_CREATED)
def create_grant_call(
    body: GrantCallCreate,
    svc: GrantCallAdminService = Depends(get_grant_call_service),
) -> GrantCall:
    return svc.create(body)


@router.patch("/{call_id}", response_model=GrantCall)
def update_grant_call(
    call_id: str,
    body: GrantCallUpdate,
    svc: GrantCallAdminService = Depends(get_grant_call_service),
) -> GrantCall:
    return svc.update(call_id, body)
