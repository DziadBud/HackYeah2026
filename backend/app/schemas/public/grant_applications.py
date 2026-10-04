"""ROPS Zał. 3 formularz aplikacyjny — pełny kształt w API (LLM + edycja użytkownika)."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.admin.common import PatchModel
from app.schemas.public.common import OptionalContact


class GrantApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    # set by the admin only (POST /admin/grant-applications/{id}/status); final
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ApplicantType(StrEnum):
    PERSON = "person"
    ORGANIZATION = "organization"
    INFORMAL_GROUP = "informal_group"


# --- §9 Plan działania ---


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


# --- §2 Dane pomysłodawcy ---


class PersonApplicant(BaseModel):
    """§2 OSOBA FIZYCZNA a–g"""

    first_name: str = ""
    last_name: str = ""
    address: str = ""
    postal_code: str = ""
    city: str = ""
    phone: str = ""
    email: str = ""


class OrgContact(BaseModel):
    """Osoba upoważniona / kontakt roboczy"""

    role: str = ""
    full_name: str = ""
    phone: str = ""
    email: str = ""


class OrganizationApplicant(BaseModel):
    """§2 PODMIOT a–k"""

    name: str = ""
    krs: str = ""
    regon: str = ""
    nip: str = ""
    address: str = ""
    postal_code: str = ""
    city: str = ""
    phone: str = ""
    email: str = ""
    representative: OrgContact = Field(default_factory=OrgContact)
    working_contact: OrgContact = Field(default_factory=OrgContact)


class InformalPartnerPerson(BaseModel):
    kind: Literal["person"] = "person"
    person: PersonApplicant = Field(default_factory=PersonApplicant)


class InformalPartnerOrganization(BaseModel):
    kind: Literal["organization"] = "organization"
    organization: OrganizationApplicant = Field(default_factory=OrganizationApplicant)


InformalPartner = Annotated[
    InformalPartnerPerson | InformalPartnerOrganization,
    Field(discriminator="kind"),
]


class InformalGroupApplicant(BaseModel):
    """§2 GRUPA NIEFORMALNA — do 5 partnerów + reprezentant"""

    partners: list[InformalPartner] = Field(default_factory=list, max_length=5)
    representative_full_name: str = ""
    representative_phone: str = ""
    representative_email: str = ""


# --- §12 Oświadczenia ---


class PersonDeclarations(BaseModel):
    """§12 A — oświadczenia osoby fizycznej (każdy checkbox osobno)."""

    resides_in_poland: bool = False
    full_legal_capacity: bool = False
    no_criminal_conviction: bool = False
    not_excluded_public_funds: bool = False
    not_under_sanctions: bool = False
    no_tax_arrears: bool = False
    voluntary_participation: bool = False
    accepts_procedures: bool = False
    data_truthful: bool = False
    not_employed_rops_innoagh: bool = False
    no_parallel_application: bool = False
    not_duplicating_existing: bool = False
    no_fees_from_testers: bool = False
    max_two_applications: bool = False
    not_implementation_character: bool = False
    aware_form_shared: bool = False
    equality_and_dnsh: bool = False
    rodo_info_received: bool = False
    rodo_duties_fulfilled: bool = False


class OrganizationDeclarations(BaseModel):
    """§12 B — oświadczenia reprezentanta podmiotu."""

    entity_seat_in_poland: bool = False
    management_no_conviction: bool = False
    entity_not_excluded_public_funds: bool = False
    entity_not_under_sanctions: bool = False
    entity_no_tax_arrears: bool = False
    partners_not_employed_rops: bool = False
    no_conflict_of_interest: bool = False
    not_malopolska_unit: bool = False
    not_agh_capital_linked: bool = False
    voluntary_participation: bool = False
    accepts_procedures: bool = False
    data_truthful: bool = False
    no_parallel_application: bool = False
    not_duplicating_existing: bool = False
    no_fees_from_testers: bool = False
    max_two_applications: bool = False
    not_implementation_character: bool = False
    aware_form_shared: bool = False
    equality_and_dnsh: bool = False
    rodo_info_received: bool = False
    rodo_duties_fulfilled: bool = False


def empty_applicant(applicant_type: ApplicantType) -> dict:
    if applicant_type == ApplicantType.ORGANIZATION:
        return OrganizationApplicant().model_dump()
    if applicant_type == ApplicantType.INFORMAL_GROUP:
        return InformalGroupApplicant().model_dump()
    return PersonApplicant().model_dump()


def empty_declarations(applicant_type: ApplicantType) -> dict:
    if applicant_type == ApplicantType.ORGANIZATION:
        return OrganizationDeclarations().model_dump()
    # informal group uses person-style declarations for the representative
    return PersonDeclarations().model_dump()


def normalize_applicant(applicant_type: ApplicantType, raw: dict | None) -> dict:
    """Merge partial payload into full §2 shape (missing keys → empty defaults)."""
    data = raw or {}
    if applicant_type == ApplicantType.ORGANIZATION:
        return OrganizationApplicant.model_validate(data).model_dump()
    if applicant_type == ApplicantType.INFORMAL_GROUP:
        return InformalGroupApplicant.model_validate(data).model_dump()
    return PersonApplicant.model_validate(data).model_dump()


def normalize_declarations(applicant_type: ApplicantType, raw: dict | None) -> dict:
    """Merge partial checkboxes into full §12 shape (missing → False)."""
    data = raw or {}
    if applicant_type == ApplicantType.ORGANIZATION:
        return OrganizationDeclarations.model_validate(data).model_dump()
    return PersonDeclarations.model_validate(data).model_dump()


# --- API ---


class GrantApplicationCreate(OptionalContact):
    """Start draft (sections 1+3–9). Rest comes empty for the user to fill/edit."""

    grant_call_id: str
    applicant_type: ApplicantType = ApplicantType.PERSON
    notes: str | None = Field(default=None, max_length=2000)
    # false = skip Gemini, fill from template only
    use_ai: bool = True


class GrantApplicationUpdate(PatchModel):
    """Pełna edycja formularza — FE może nadpisać też treść z LLM."""

    # amount starts as null on create; FE may clear it again
    nullable_fields: ClassVar[frozenset[str]] = frozenset({"grant_amount_pln", "email"})

    status: GrantApplicationStatus | None = None
    title: str | None = None
    applicant_type: ApplicantType | None = None
    # shape depends on applicant_type — see Person/Organization/InformalGroupApplicant
    applicant: dict | None = None
    description: str | None = None
    innovativeness: str | None = None
    problem_diagnosis: str | None = None
    beneficiaries: str | None = None
    expected_change: str | None = None
    future_vision: str | None = None
    action_plan: ActionPlan | None = None
    grant_amount_pln: Decimal | None = None
    team: str | None = None
    # shape depends on applicant_type — see Person/OrganizationDeclarations
    declarations: dict | None = None
    email: str | None = None

    @field_validator("status")
    @classmethod
    def _applicant_cannot_decide(cls, v: GrantApplicationStatus | None) -> GrantApplicationStatus | None:
        if v in (GrantApplicationStatus.ACCEPTED, GrantApplicationStatus.REJECTED):
            raise ValueError("only the admin can accept or reject an application")
        return v


class GrantApplication(BaseModel):
    """Pełny wniosek Zał. 3 — zawsze sekcje 1–12 (puste lub wypełnione, edytowalne)."""

    id: str
    idea_id: str | None
    grant_call_id: str | None
    status: GrantApplicationStatus
    # 1
    title: str
    # 2 — always full typed shape for the current applicant_type
    applicant_type: ApplicantType
    applicant: dict
    # 3–8
    description: str
    innovativeness: str
    problem_diagnosis: str
    beneficiaries: str
    expected_change: str
    future_vision: str
    # 9
    action_plan: ActionPlan
    # 10
    grant_amount_pln: Decimal | None
    # 11
    team: str
    # 12 — always full checkbox map for the current applicant_type
    declarations: dict
    email: str | None
    generated_by: str | None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _coerce_full_shapes(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        at = ApplicantType(data.get("applicant_type") or ApplicantType.PERSON)
        data["applicant_type"] = at
        raw_applicant = data.get("applicant")
        if hasattr(raw_applicant, "model_dump"):
            raw_applicant = raw_applicant.model_dump()
        raw_declarations = data.get("declarations")
        if hasattr(raw_declarations, "model_dump"):
            raw_declarations = raw_declarations.model_dump()
        data["applicant"] = normalize_applicant(at, raw_applicant)
        data["declarations"] = normalize_declarations(at, raw_declarations)
        return data
