from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.admin.common import ChallengeArea, PatchModel


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class InnovationBase(BaseModel):
    title: str = Field(min_length=1)
    summary: str
    # read from rag's area:<slug> tags
    challenge_areas: list[ChallengeArea]
    city: str = ""
    page_url: str | None = None


class InnovationUploaded(BaseModel):
    id: str
    title: str
    # stays draft until rag has embedded the pdf
    status: PublicationStatus


class InnovationUpdate(PatchModel):
    nullable_fields = frozenset({"page_url"})

    title: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    challenge_areas: list[ChallengeArea] | None = None
    city: str | None = None
    page_url: str | None = None


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


class SignupCounts(BaseModel):
    applied: int
    accepted: int
    rejected: int


class WeeklyMatches(BaseModel):
    week_start: date
    matches: int


class AreaMatches(BaseModel):
    challenge_area: ChallengeArea
    matches: int


class LocationMatches(BaseModel):
    location: str
    # None when suppressed (fewer than 5 problem reports), same rule as the locations report
    matches: int | None
    note: str | None = None


class MatchedProblemReport(BaseModel):
    id: str
    text: str
    challenge_area: ChallengeArea
    location: str
    support_count: int
    created_at: datetime


class InnovationStatsRow(BaseModel):
    # flat so it streams as csv (GET /admin/reports/innovations)
    innovation_id: str
    title: str
    status: PublicationStatus
    # problem reports whose top 3 contained this innovation
    matches_total: int
    matches_7d: int
    matches_prev_7d: int
    # matched problem reports plus their "mnie tez" presses
    people_reached: int
    distinct_locations: int
    test_signups_applied: int
    test_signups_accepted: int
    test_signups_rejected: int
    rating_avg: float | None
    rating_count: int
    last_matched_at: datetime | None


class InnovationStats(BaseModel):
    innovation_id: str
    matches_total: int
    matches_7d: int
    matches_prev_7d: int
    people_reached: int
    distinct_locations: int
    last_matched_at: datetime | None
    # last 6 weeks, oldest first, zero weeks included
    matches_by_week: list[WeeklyMatches]
    matches_by_area: list[AreaMatches]
    matches_by_location: list[LocationMatches]
    test_signups: SignupCounts
    rating_avg: float | None
    rating_count: int
    # index 0 = 1 star ... index 4 = 5 stars
    rating_distribution: list[int] = Field(min_length=5, max_length=5)
    recent_comments: list[FeedbackComment]
    recent_problem_reports: list[MatchedProblemReport]
