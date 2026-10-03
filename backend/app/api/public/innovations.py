from fastapi import APIRouter, Depends, Query, status

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.public.innovations import FeedbackCreate, FeedbackCreated, LibraryInnovation
from app.schemas.public.threads import Submitted, Thread, ThreadCreate
from app.services.public.deps import get_library_service, get_thread_service
from app.services.public.interfaces import LibraryService, ThreadService

router = APIRouter(prefix="/innovations", tags=["innovations"])


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
    return svc.get(innovation_id)


@router.post(
    "/{innovation_id}/feedback", response_model=FeedbackCreated, status_code=status.HTTP_201_CREATED
)
def add_feedback(
    innovation_id: str, body: FeedbackCreate, svc: LibraryService = Depends(get_library_service)
) -> FeedbackCreated:
    return svc.add_feedback(innovation_id, body)


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
