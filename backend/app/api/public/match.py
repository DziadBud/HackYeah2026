from fastapi import APIRouter, Depends

from app.schemas.public.match import MatchRequest, MatchResponse
from app.services.public.deps import get_match_service
from app.services.public.interfaces import MatchService

router = APIRouter(tags=["match"])


@router.post("/match", response_model=MatchResponse)
def match(
    body: MatchRequest,
    test_signup: bool = False,
    svc: MatchService = Depends(get_match_service),
) -> MatchResponse:
    return svc.match(body, test_signup)
