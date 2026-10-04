from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class TestSignupStatus(StrEnum):
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    # set by the tester's rating from the mail, not by the admin
    RATED = "rated"


class TestSignup(BaseModel):
    id: str
    innovation_id: str
    innovation_title: str
    # null for direct signups from an innovation page
    problem_report_id: str | None
    email: str
    status: TestSignupStatus
    created_at: datetime


class TestSignupStatusRequest(BaseModel):
    # back to applied is not a decision
    status: Literal[TestSignupStatus.ACCEPTED, TestSignupStatus.REJECTED, TestSignupStatus.COMPLETED]
