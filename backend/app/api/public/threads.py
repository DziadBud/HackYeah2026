from fastapi import APIRouter, Depends, status

from app.schemas.public.threads import ReplyCreate, Submitted
from app.services.public.deps import get_thread_service
from app.services.public.interfaces import ThreadService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("/{thread_id}/replies", response_model=Submitted, status_code=status.HTTP_202_ACCEPTED)
def reply_to_thread(
    thread_id: str, body: ReplyCreate, svc: ThreadService = Depends(get_thread_service)
) -> Submitted:
    return svc.reply(thread_id, body)
