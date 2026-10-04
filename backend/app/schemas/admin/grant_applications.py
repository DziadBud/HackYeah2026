from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.public.grant_applications import GrantApplicationStatus


class GrantApplicationDecision(BaseModel):
    status: Literal[GrantApplicationStatus.ACCEPTED, GrantApplicationStatus.REJECTED]
    # goes only into the mail to the applicant, it is not stored
    message: str | None = Field(default=None, max_length=2000)
