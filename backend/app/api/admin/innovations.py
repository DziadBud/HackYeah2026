from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile, status

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.innovations import (
    Innovation,
    InnovationFeedback,
    InnovationRating,
    InnovationStats,
    PublicationStatus,
    InnovationUpdate,
    InnovationUploaded,
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


# 202: the row exists as a draft; a background task sends the pdf to rag and publishes it on success
@router.post("", response_model=InnovationUploaded, status_code=status.HTTP_202_ACCEPTED)
def create_innovation(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(min_length=1, max_length=300),
    summary: str = Form(min_length=1, max_length=5000),
    challenge_areas: list[ChallengeArea] = Form(min_length=1),
    tags: list[str] = Form(default=[]),
    city: str = Form(default="", max_length=200),
    page_url: str | None = Form(default=None, max_length=2000),
    svc: InnovationUploadService = Depends(get_innovation_upload_service),
) -> InnovationUploaded:
    # read one byte past the limit so oversized files fail without loading them whole
    pdf = file.file.read(settings.max_upload_bytes + 1)
    created = svc.create(
        NewInnovation(
            title=title,
            summary=summary,
            challenge_areas=challenge_areas,
            tags=tags,
            city=city,
            page_url=page_url,
        ),
        pdf,
    )
    background.add_task(svc.embed, created.id, created.file_path)
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


# 202: rag re-embeds the new pdf in the background and replaces the chunks; on failure the
# old chunks stay. a successful embed publishes the innovation, like the first upload
@router.post(
    "/{innovation_id}/pdf", response_model=InnovationUploaded, status_code=status.HTTP_202_ACCEPTED
)
def replace_innovation_pdf(
    innovation_id: str,
    background: BackgroundTasks,
    file: UploadFile = File(...),
    svc: InnovationAdminService = Depends(get_innovation_service),
    upload: InnovationUploadService = Depends(get_innovation_upload_service),
) -> InnovationUploaded:
    innovation = svc.get(innovation_id)
    pdf = file.file.read(settings.max_upload_bytes + 1)
    path = upload.replace_pdf(innovation.id, pdf)
    background.add_task(upload.embed, innovation.id, path)
    return InnovationUploaded(id=innovation.id, title=innovation.title, status=innovation.status)


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


@router.get("/{innovation_id}/ratings", response_model=list[InnovationRating])
def innovation_ratings(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> list[InnovationRating]:
    return svc.ratings(innovation_id)


@router.get("/{innovation_id}/stats", response_model=InnovationStats)
def innovation_stats(
    innovation_id: str, svc: InnovationAdminService = Depends(get_innovation_service)
) -> InnovationStats:
    return svc.stats(innovation_id)
