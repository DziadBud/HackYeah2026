# R4: rating straight from the tester mail. html, not json: the link opens in a browser.
# the mail link only opens the prefilled form; saving needs the button, so link scanners
# that open every url in a mail can't record a rating
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.schemas.public.ratings import RatingState, RatingTarget
from app.services.public.deps import get_rating_service
from app.services.public.interfaces import RatingService

router = APIRouter(prefix="/ratings", include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[2] / "templates")


def _page(request: Request, target: RatingTarget, stars: int | None = None, saved: bool = False) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "rating.html",
        {"t": target, "stars": stars, "saved": saved, "web_url": settings.web_url.rstrip("/")},
        status_code=status.HTTP_404_NOT_FOUND if target.state == RatingState.UNAVAILABLE else status.HTTP_200_OK,
    )


@router.get("/{signup_id}", response_class=HTMLResponse)
def rating_form(
    request: Request,
    signup_id: str,
    rating: int | None = None,
    svc: RatingService = Depends(get_rating_service),
) -> HTMLResponse:
    stars = rating if rating is not None and 1 <= rating <= 5 else None
    return _page(request, svc.target(signup_id), stars)


@router.post("/{signup_id}", response_class=HTMLResponse)
def submit_rating(
    request: Request,
    signup_id: str,
    stars: int = Form(ge=1, le=5),
    comment: str = Form(default="", max_length=2000),
    svc: RatingService = Depends(get_rating_service),
) -> HTMLResponse:
    before = svc.target(signup_id).state
    target = svc.rate(signup_id, stars, comment)
    return _page(request, target, saved=before == RatingState.OPEN and target.state == RatingState.RATED)
