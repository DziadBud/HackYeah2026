from datetime import datetime

from pydantic import BaseModel

from app.schemas.admin.common import ChallengeArea


class PublicProblemReport(BaseModel):
    id: str
    text: str
    challenge_area: ChallengeArea | None
    city: str
    support_count: int
    # one reply covers everyone who pressed "mnie też"
    admin_reply: str | None = None
    created_at: datetime


class SupportResponse(BaseModel):
    support_count: int
