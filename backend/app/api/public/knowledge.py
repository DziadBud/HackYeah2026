from fastapi import APIRouter, Depends

from app.schemas.admin.grant_calls import GrantCall
from app.services.public.deps import get_knowledge_service
from app.services.public.interfaces import KnowledgeService

router = APIRouter(tags=["knowledge"])


@router.get("/grant-calls", response_model=list[GrantCall])
def open_grant_calls(svc: KnowledgeService = Depends(get_knowledge_service)) -> list[GrantCall]:
    return svc.open_grant_calls()
