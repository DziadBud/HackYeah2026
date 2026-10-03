from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.public.threads import ModerationStatus, ReplyKind


class AdminReply(BaseModel):
    id: str
    body: str
    author_label: str
    email: str | None
    kind: ReplyKind
    status: ModerationStatus
    created_at: datetime


class AdminThread(BaseModel):
    id: str
    innovation_id: str
    title: str
    body: str
    author_label: str
    email: str | None
    status: ModerationStatus
    created_at: datetime
    # every reply, whatever its status, oldest first
    replies: list[AdminReply]


class ModerationDecision(BaseModel):
    # back to pending is not a moderation decision
    status: Literal[ModerationStatus.PUBLISHED, ModerationStatus.HIDDEN]
