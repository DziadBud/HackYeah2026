import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse

from app.config import settings

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.public.innovations import (
    FeedbackCreate,
    FeedbackCreated,
    LibraryInnovation,
    TestSignupCreate,
    TestSignupCreated,
    LikeState,
)
from app.schemas.public.threads import Submitted, Thread, ThreadCreate
from app.services.admin.errors import NotFoundError
from app.services.public.deps import get_library_service, get_thread_service
from app.services.public.interfaces import LibraryService, ThreadService

router = APIRouter(prefix="/innovations", tags=["innovations"])


def _pdf_path(innovation_id: str) -> Path | None:
    # an admin upload (same name the admin upload saves under) wins over the seeded file
    for path in (
        Path(settings.upload_dir) / f"{innovation_id}.pdf",
        Path(settings.seed_media_dir) / innovation_id / "document.pdf",
    ):
        if path.is_file():
            return path
    return None


@router.get("", response_model=Page[LibraryInnovation])
def list_innovations(
    challenge_area: ChallengeArea | None = None,
    q: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: LibraryService = Depends(get_library_service),
) -> Page[LibraryInnovation]:
    return svc.list(challenge_area, q, limit, offset)


@router.get("/{innovation_id}", response_model=LibraryInnovation)
def get_innovation(
    innovation_id: str, svc: LibraryService = Depends(get_library_service)
) -> LibraryInnovation:
    card = svc.get(innovation_id)
    return card.model_copy(update={"has_pdf": _pdf_path(card.id) is not None})


@router.get("/{innovation_id}/pdf", response_class=FileResponse)
def get_innovation_pdf(
    innovation_id: str, svc: LibraryService = Depends(get_library_service)
) -> FileResponse:
    # the lookup 404s drafts, so only published innovations' pdfs are public
    card = svc.get(innovation_id)
    path = _pdf_path(card.id)
    if path is None:
        raise NotFoundError(innovation_id)
    # the whole document is a download ("Więcej informacji (PDF)"), not a viewer page
    return FileResponse(path, media_type="application/pdf", filename=f"{card.id}.pdf")


@router.get("/{innovation_id}/photos/{name}", response_class=FileResponse)
def get_innovation_photo(
    innovation_id: str, name: str, svc: LibraryService = Depends(get_library_service)
) -> FileResponse:
    # only names listed on the innovation, so the path can't leave its folder; drafts 404
    card = svc.get(innovation_id)
    path = Path(settings.seed_media_dir) / card.id / name
    if name not in card.photos or not path.is_file():
        raise NotFoundError(name)
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


@router.post(
    "/{innovation_id}/feedback", response_model=FeedbackCreated, status_code=status.HTTP_201_CREATED
)
def add_feedback(
    innovation_id: str, body: FeedbackCreate, svc: LibraryService = Depends(get_library_service)
) -> FeedbackCreated:
    return svc.add_feedback(innovation_id, body)


# R4: volunteer for this one innovation; /match?test_signup=true signs up for every match
@router.post(
    "/{innovation_id}/test-signups",
    response_model=TestSignupCreated,
    status_code=status.HTTP_201_CREATED,
)
def sign_up_for_test(
    innovation_id: str, body: TestSignupCreate, svc: LibraryService = Depends(get_library_service)
) -> TestSignupCreated:
    return svc.sign_up_for_test(innovation_id, body)


# anonymous likes: client_id is a random uuid the browser keeps, one like per browser
@router.get("/{innovation_id}/likes", response_model=LikeState)
def get_likes(
    innovation_id: str,
    client_id: uuid.UUID | None = None,
    svc: LibraryService = Depends(get_library_service),
) -> LikeState:
    return svc.likes(innovation_id, str(client_id) if client_id else None)


@router.put("/{innovation_id}/likes/{client_id}", response_model=LikeState)
def like(
    innovation_id: str, client_id: uuid.UUID, svc: LibraryService = Depends(get_library_service)
) -> LikeState:
    return svc.set_like(innovation_id, str(client_id), True)


@router.delete("/{innovation_id}/likes/{client_id}", response_model=LikeState)
def unlike(
    innovation_id: str, client_id: uuid.UUID, svc: LibraryService = Depends(get_library_service)
) -> LikeState:
    return svc.set_like(innovation_id, str(client_id), False)


@router.get("/{innovation_id}/threads", response_model=list[Thread])
def list_threads(innovation_id: str, svc: ThreadService = Depends(get_thread_service)) -> list[Thread]:
    return svc.list(innovation_id)


@router.post(
    "/{innovation_id}/threads", response_model=Submitted, status_code=status.HTTP_202_ACCEPTED
)
def create_thread(
    innovation_id: str, body: ThreadCreate, svc: ThreadService = Depends(get_thread_service)
) -> Submitted:
    return svc.create(innovation_id, body)
