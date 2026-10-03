from datetime import datetime

from pydantic import BaseModel

from app.schemas.admin.common import ChallengeArea


class ProblemReport(BaseModel):
    id: str
    text: str
    # null when the llm classification failed
    challenge_area: ChallengeArea | None
    location: str
    support_count: int
    is_critical: bool
    criticality_score: float
    admin_reply: str | None = None
    created_at: datetime
