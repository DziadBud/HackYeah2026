from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class TestSignupStatus(StrEnum):
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TestSignup(BaseModel):
    id: str
    innovation_id: str
    innovation_title: str
    problem_report_id: str
    email: str
    status: TestSignupStatus
    created_at: datetime


class TestSignupStatusRequest(BaseModel):
    # back to applied is not a decision
    status: Literal[TestSignupStatus.ACCEPTED, TestSignupStatus.REJECTED, TestSignupStatus.COMPLETED]
