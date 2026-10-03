from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.innovations import (
    CostLevel,
    Innovation,
    InnovationFeedback,
    InnovationStats,
    PublicationStatus,
    InnovationUpdate,
    InnovationUploaded,
    Readiness,
)
from app.config import settings
from app.services.admin.deps import get_innovation_service, get_innovation_upload_service
from app.services.admin.innovation_upload import InnovationUploadService, NewInnovation
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


# 202: the row exists as a draft, rag embeds the pdf asynchronously and only then is it searchable
@router.post("", response_model=InnovationUploaded, status_code=status.HTTP_202_ACCEPTED)
def create_innovation(
    file: UploadFile = File(...),
    title: str = Form(min_length=1, max_length=300),
    summary: str = Form(min_length=1, max_length=5000),
    problem: str = Form(min_length=1, max_length=5000),
    innovator: str = Form(min_length=1, max_length=200),
    challenge_areas: list[ChallengeArea] = Form(min_length=1),
    readiness: Readiness = Form(),
    cost_level: CostLevel = Form(),
    target_group: list[str] = Form(default=[]),
    tags: list[str] = Form(default=[]),
    city: str = Form(default="", max_length=200),
    page_url: str | None = Form(default=None, max_length=2000),
    image_url: str | None = Form(default=None, max_length=2000),
    video_url: str | None = Form(default=None, max_length=2000),
    svc: InnovationUploadService = Depends(get_innovation_upload_service),
) -> InnovationUploaded:
    # read one byte past the limit so oversized files fail without loading them whole
    pdf = file.file.read(settings.max_upload_bytes + 1)
    created = svc.create(
        NewInnovation(
            title=title,
            summary=summary,
            problem=problem,
            innovator=innovator,
            challenge_areas=challenge_areas,
            readiness=readiness,
            cost_level=cost_level,
            target_group=target_group,
            tags=tags,
            city=city,
            page_url=page_url,
            image_url=image_url,
            video_url=video_url,
        ),
        pdf,
    )
    return InnovationUploaded(id=created.id, title=created.title, status=created.status)


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


@router.get("/{innovation_id}/stats", response_model=InnovationStats)
def innovation_stats(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> InnovationStats:
    return svc.stats(innovation_id)
