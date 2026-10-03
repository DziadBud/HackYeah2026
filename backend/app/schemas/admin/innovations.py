from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.admin.common import ChallengeArea, PatchModel


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class InnovationBase(BaseModel):
    title: str = Field(min_length=1)
    summary: str
    challenge_areas: list[ChallengeArea]
    target_group: list[str]
    readiness: str
    cost_level: str
    video_url: str | None = None


class InnovationUploaded(BaseModel):
    id: str
    title: str
    # stays draft until rag has embedded the pdf
    status: PublicationStatus


class InnovationUpdate(PatchModel):
    nullable_fields = frozenset({"video_url"})

    title: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    challenge_areas: list[ChallengeArea] | None = None
    target_group: list[str] | None = None
    readiness: str | None = None
    cost_level: str | None = None
    video_url: str | None = None


class Innovation(InnovationBase):
    id: str
    status: PublicationStatus


class FeedbackComment(BaseModel):
    comment: str
    rating: int = Field(ge=1, le=5)
    created_at: datetime


class InnovationFeedback(BaseModel):
    rating_avg: float | None
    rating_count: int
    test_signups: int
    recent_comments: list[FeedbackComment]
