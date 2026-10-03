from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.public.common import OptionalContact


class ModerationStatus(StrEnum):
    PENDING = "pending"
    PUBLISHED = "published"
    HIDDEN = "hidden"


class ReplyKind(StrEnum):
    PRACTITIONER = "practitioner"
    EXPERT = "expert"
    MENTOR = "mentor"
    ADMIN = "admin"


class ThreadCreate(OptionalContact):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    author_label: str = Field(min_length=1, max_length=100)


class ReplyCreate(OptionalContact):
    body: str = Field(min_length=1, max_length=5000)
    author_label: str = Field(min_length=1, max_length=100)
    # no kind here: public replies are always practitioner, expert/mentor/admin are set by ROPS


class Reply(BaseModel):
    id: str
    body: str
    author_label: str
    kind: ReplyKind
    created_at: datetime


class Thread(BaseModel):
    id: str
    innovation_id: str
    title: str
    body: str
    author_label: str
    created_at: datetime
    replies: list[Reply]


class Submitted(BaseModel):
    # new threads and replies wait for moderation
    id: str
    status: ModerationStatus
