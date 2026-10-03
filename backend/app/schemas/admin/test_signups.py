from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TestSignupStatus(StrEnum):
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TestSignup(BaseModel):
    # not a pytest test class
    __test__ = False

    id: str
    innovation_id: str
    problem_report_id: str
    email: str
    status: TestSignupStatus
    created_at: datetime
