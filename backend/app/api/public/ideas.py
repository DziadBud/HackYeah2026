from fastapi import APIRouter, Depends, status

from app.schemas.public.documents import GeneratedDocument
from app.schemas.public.ideas import GrantApplicationRequest, IdeaCreate, IdeaCreated
from app.services.public.deps import get_idea_service
from app.services.public.interfaces import IdeaService

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("", response_model=IdeaCreated, status_code=status.HTTP_201_CREATED)
def create_idea(body: IdeaCreate, svc: IdeaService = Depends(get_idea_service)) -> IdeaCreated:
    return svc.create(body)


@router.post(
    "/{idea_id}/grant-application",
    response_model=GeneratedDocument,
    status_code=status.HTTP_201_CREATED,
)
def generate_grant_application(
    idea_id: str, body: GrantApplicationRequest, svc: IdeaService = Depends(get_idea_service)
) -> GeneratedDocument:
    return svc.grant_application(idea_id, body)
