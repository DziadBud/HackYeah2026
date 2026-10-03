from fastapi import APIRouter, Depends

from app.schemas.admin.threads import AdminReply, AdminThread, ModerationDecision
from app.schemas.public.threads import ModerationStatus
from app.services.admin.deps import get_thread_service
from app.services.admin.interfaces import ThreadAdminService

router = APIRouter(prefix="/threads", tags=["admin:threads"])


# status matches the thread or any of its replies, so ?status=pending lists everything awaiting moderation
@router.get("", response_model=list[AdminThread])
def list_threads(
    status: ModerationStatus | None = None,
    innovation_id: str | None = None,
    svc: ThreadAdminService = Depends(get_thread_service),
) -> list[AdminThread]:
    return svc.list(status, innovation_id)


@router.post("/{thread_id}/status", response_model=AdminThread)
def set_thread_status(
    thread_id: str,
    body: ModerationDecision,
    svc: ThreadAdminService = Depends(get_thread_service),
) -> AdminThread:
    return svc.set_status(thread_id, body.status)


@router.post("/replies/{reply_id}/status", response_model=AdminReply)
def set_reply_status(
    reply_id: str,
    body: ModerationDecision,
    svc: ThreadAdminService = Depends(get_thread_service),
) -> AdminReply:
    return svc.set_reply_status(reply_id, body.status)
