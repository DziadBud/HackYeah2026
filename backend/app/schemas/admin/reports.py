from datetime import date

from pydantic import BaseModel

from app.schemas.admin.common import ChallengeArea


class TrendRow(BaseModel):
    week_start: date
    challenge_area: ChallengeArea
    location: str
    problem_reports: int
    support_count: int


class CriticalRow(BaseModel):
    problem_report_id: str
    text: str
    challenge_area: ChallengeArea
    distinct_locations: int
    growth_ratio_7d: float
    score: float


class LocationRow(BaseModel):
    location: str
    challenge_area: ChallengeArea
    # None when suppressed (fewer than 5 problem reports)
    problem_reports: int | None
    note: str | None = None


class GapRow(BaseModel):
    problem_report_id: str
    text: str
    challenge_area: ChallengeArea
    # cosine similarity of the closest innovation, 0..1
    best_match_similarity: float
