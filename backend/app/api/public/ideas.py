from fastapi import APIRouter, Depends, status

from app.schemas.public.grant_applications import (
    GrantApplication,
    GrantApplicationCreate,
    GrantApplicationUpdate,
)
from app.schemas.public.ideas import IdeaCreate, IdeaCreated
from app.services.public.deps import get_idea_service
from app.services.public.interfaces import IdeaService

router = APIRouter(tags=["ideas"])


@router.post("/ideas", response_model=IdeaCreated, status_code=status.HTTP_201_CREATED)
def create_idea(body: IdeaCreate, svc: IdeaService = Depends(get_idea_service)) -> IdeaCreated:
    return svc.create(body)


@router.post(
    "/ideas/{idea_id}/grant-application",
    response_model=GrantApplication,
    status_code=status.HTTP_201_CREATED,
)
def create_grant_application(
    idea_id: str, body: GrantApplicationCreate, svc: IdeaService = Depends(get_idea_service)
) -> GrantApplication:
    return svc.grant_application(idea_id, body)


@router.get("/grant-applications/{application_id}", response_model=GrantApplication)
def get_grant_application(
    application_id: str, svc: IdeaService = Depends(get_idea_service)
) -> GrantApplication:
    return svc.get_grant_application(application_id)


@router.patch("/grant-applications/{application_id}", response_model=GrantApplication)
def update_grant_application(
    application_id: str,
    body: GrantApplicationUpdate,
    svc: IdeaService = Depends(get_idea_service),
) -> GrantApplication:
    return svc.update_grant_application(application_id, body)
