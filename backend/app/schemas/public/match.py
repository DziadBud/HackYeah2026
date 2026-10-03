from pydantic import BaseModel, Field

from app.schemas.public.common import OptionalContact


class MatchRequest(OptionalContact):
    text: str = Field(min_length=3, max_length=2000)
    city: str = Field(default="", max_length=200)


class MatchedInnovation(BaseModel):
    id: str
    title: str
    summary: str
    # llm explanation of the fit; null when the llm is down
    why: str | None
    tags: list[str]
    city: str


class SimilarProblemReport(BaseModel):
    id: str
    text: str
    city: str
    support_count: int
    admin_reply: str | None = None


class MatchResponse(BaseModel):
    problem_report_id: str
    innovations: list[MatchedInnovation]
    similar_reports: list[SimilarProblemReport]
    # one per matched innovation when ?test_signup=true
    test_signup_ids: list[str] = []
