from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class IdeaStatus(StrEnum):
    NEW = "new"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class IdeaStage(StrEnum):
    CONCEPT = "concept"
    PROTOTYPE = "prototype"
    PILOT = "pilot"
    RUNNING = "running"


class SocialCanvas(BaseModel):
    problem: str
    solution: str
    beneficiaries: str
    resources: str | None = None


class Idea(BaseModel):
    id: str
    summary: str
    target_group: str
    stage: IdeaStage
    social_canvas: SocialCanvas
    status: IdeaStatus
    admin_reply: str | None = None
    created_at: datetime


class IdeaStatusRequest(BaseModel):
    status: IdeaStatus
