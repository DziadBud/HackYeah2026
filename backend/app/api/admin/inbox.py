from datetime import datetime

from fastapi import APIRouter, Depends

from app.schemas.admin.inbox import Inbox
from app.services.admin.deps import get_inbox_service
from app.services.admin.interfaces import InboxAdminService

router = APIRouter(prefix="/inbox", tags=["admin:inbox"])


@router.get("", response_model=Inbox)
def get_inbox(
    since: datetime | None = None,
    svc: InboxAdminService = Depends(get_inbox_service),
) -> Inbox:
    return svc.get(since)
