from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.admin.common import ChallengeArea, PatchModel


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Readiness(StrEnum):
    CONCEPT = "concept"
    PROTOTYPE = "prototype"
    PILOT = "pilot"
    RUNNING = "running"


class CostLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InnovationBase(BaseModel):
    title: str = Field(min_length=1)
    summary: str
    problem: str = ""
    innovator: str = ""
    challenge_areas: list[ChallengeArea]
    target_group: list[str]
    readiness: Readiness
    cost_level: CostLevel
    city: str = ""
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
    problem: str | None = None
    innovator: str | None = None
    target_group: list[str] | None = None
    readiness: Readiness | None = None
    cost_level: CostLevel | None = None
    city: str | None = None
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
