from fastapi import APIRouter, Depends
from pydantic import AwareDatetime

from app.schemas.admin.inbox import Inbox
from app.services.admin.deps import get_inbox_service
from app.services.admin.interfaces import InboxAdminService

router = APIRouter(prefix="/inbox", tags=["admin:inbox"])


@router.get("", response_model=Inbox)
def get_inbox(
    since: AwareDatetime | None = None,
    svc: InboxAdminService = Depends(get_inbox_service),
) -> Inbox:
    return svc.get(since)
