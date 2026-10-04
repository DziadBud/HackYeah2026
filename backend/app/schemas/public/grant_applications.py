from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.admin.common import PatchModel
from app.schemas.public.common import OptionalContact


class GrantApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class ApplicantType(StrEnum):
    PERSON = "person"
    ORGANIZATION = "organization"
    INFORMAL_GROUP = "informal_group"


class PlanStep(BaseModel):
    action: str = ""
    timeline: str = ""
    cost_pln: int | None = None
    note: str | None = None


class ActionPlan(BaseModel):
    preparation_summary: str = ""
    preparation: list[PlanStep] = Field(default_factory=list)
    testing_summary: str = ""
    testing_phase_1: list[PlanStep] = Field(default_factory=list)
    testing_phase_2: list[PlanStep] = Field(default_factory=list)


class GrantApplicationCreate(OptionalContact):
    """Start AI draft for an open grant call (fields 1+3–9 pre-filled)."""

    grant_call_id: str
    notes: str | None = Field(default=None, max_length=2000)


class GrantApplicationUpdate(PatchModel):
    """User completes the rest of Zał. 3 (and may edit AI text)."""

    title: str | None = None
    applicant_type: ApplicantType | None = None
    # person / organization / informal_group payload — validated loosely as dict
    applicant: dict[str, Any] | None = None
    description: str | None = None
    innovativeness: str | None = None
    problem_diagnosis: str | None = None
    beneficiaries: str | None = None
    expected_change: str | None = None
    future_vision: str | None = None
    action_plan: ActionPlan | None = None
    grant_amount_pln: Decimal | None = None
    team: str | None = None
    declarations: dict[str, Any] | None = None
    status: GrantApplicationStatus | None = None
    email: str | None = None


class GrantApplication(BaseModel):
    id: str
    idea_id: str | None
    grant_call_id: str | None
    status: GrantApplicationStatus
    title: str
    applicant_type: ApplicantType
    applicant: dict[str, Any]
    description: str
    innovativeness: str
    problem_diagnosis: str
    beneficiaries: str
    expected_change: str
    future_vision: str
    action_plan: ActionPlan
    grant_amount_pln: Decimal | None
    team: str
    declarations: dict[str, Any]
    email: str | None
    generated_by: str | None
    created_at: datetime
    updated_at: datetime
