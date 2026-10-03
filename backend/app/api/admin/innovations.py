from fastapi import APIRouter, Depends, Query, status

from app.schemas.admin.common import Page
from app.schemas.admin.innovations import (
    Innovation,
    InnovationCreate,
    InnovationFeedback,
    PublicationStatus,
    InnovationUpdate,
)
from app.services.admin.deps import get_innovation_service
from app.services.admin.interfaces import InnovationAdminService

router = APIRouter(prefix="/innovations", tags=["admin:innovations"])


@router.get("", response_model=Page[Innovation])
def list_innovations(
    status: PublicationStatus | None = None,
    q: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: InnovationAdminService = Depends(get_innovation_service),
) -> Page[Innovation]:
    return svc.list(status, q, limit, offset)


@router.post("", response_model=Innovation, status_code=status.HTTP_201_CREATED)
def create_innovation(
    body: InnovationCreate,
    svc: InnovationAdminService = Depends(get_innovation_service),
) -> Innovation:
    return svc.create(body)


@router.get("/{innovation_id}", response_model=Innovation)
def get_innovation(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> Innovation:
    return svc.get(innovation_id)


@router.patch("/{innovation_id}", response_model=Innovation)
def update_innovation(
    innovation_id: str,
    body: InnovationUpdate,
    svc: InnovationAdminService = Depends(get_innovation_service),
) -> Innovation:
    return svc.update(innovation_id, body)


@router.post("/{innovation_id}/publish", response_model=Innovation)
def publish_innovation(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> Innovation:
    return svc.set_status(innovation_id, PublicationStatus.PUBLISHED)


@router.post("/{innovation_id}/unpublish", response_model=Innovation)
def unpublish_innovation(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> Innovation:
    return svc.set_status(innovation_id, PublicationStatus.DRAFT)


@router.get("/{innovation_id}/feedback", response_model=InnovationFeedback)
def innovation_feedback(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> InnovationFeedback:
    return svc.feedback(innovation_id)
