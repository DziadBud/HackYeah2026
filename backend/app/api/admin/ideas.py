from fastapi import APIRouter, Depends

from app.schemas.admin.common import ReplyRequest
from app.schemas.admin.ideas import Idea, IdeaStatus, IdeaStatusRequest
from app.services.admin.deps import get_idea_service
from app.services.admin.interfaces import IdeaAdminService

router = APIRouter(prefix="/ideas", tags=["admin:ideas"])


@router.get("", response_model=list[Idea])
def list_ideas(
    status: IdeaStatus | None = None,
    svc: IdeaAdminService = Depends(get_idea_service),
) -> list[Idea]:
    return svc.list(status)


@router.get("/{idea_id}", response_model=Idea)
def get_idea(idea_id: str, svc: IdeaAdminService = Depends(get_idea_service)) -> Idea:
    return svc.get(idea_id)


@router.post("/{idea_id}/reply", response_model=Idea)
def reply_to_idea(
    idea_id: str,
    body: ReplyRequest,
    svc: IdeaAdminService = Depends(get_idea_service),
) -> Idea:
    return svc.reply(idea_id, body.message)


@router.post("/{idea_id}/status", response_model=Idea)
def set_idea_status(
    idea_id: str,
    body: IdeaStatusRequest,
    svc: IdeaAdminService = Depends(get_idea_service),
) -> Idea:
    return svc.set_status(idea_id, body.status)
