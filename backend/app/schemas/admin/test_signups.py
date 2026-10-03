from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class SignupStatus(StrEnum):
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class AdminTestSignup(BaseModel):
    id: str
    innovation_id: str
    innovation_title: str
    problem_report_id: str
    # the problem the volunteer described in /match
    problem_text: str
    email: str
    status: SignupStatus
    created_at: datetime


class SignupDecision(BaseModel):
    # applied is where every signup starts, not a decision
    status: Literal[SignupStatus.ACCEPTED, SignupStatus.REJECTED, SignupStatus.COMPLETED]
