from datetime import UTC, datetime

import pytest

from app.schemas.public.grant_applications import ActionPlan, GrantApplication
from app.services.admin.db import applicant_email

NOW = datetime(2026, 10, 4, tzinfo=UTC)


def make(applicant_type: str, applicant: dict, email: str | None = None) -> GrantApplication:
    return GrantApplication(
        id="a", idea_id=None, grant_call_id=None, status="submitted", title="T",
        applicant_type=applicant_type, applicant=applicant, description="", innovativeness="",
        problem_diagnosis="", beneficiaries="", expected_change="", future_vision="",
        action_plan=ActionPlan(), grant_amount_pln=None, team="", declarations={},
        email=email, generated_by=None, created_at=NOW, updated_at=NOW,
    )


@pytest.mark.parametrize(
    "app, want",
    [
        pytest.param(make("person", {"email": "p@x.pl"}, email="form@x.pl"), "form@x.pl", id="#1 - OK - form email wins"),
        pytest.param(make("person", {"email": " p@x.pl "}), "p@x.pl", id="#2 - OK - person"),
        pytest.param(make("organization", {"working_contact": {"email": "w@x.pl"}}), "w@x.pl", id="#3 - OK - org contact"),
        pytest.param(make("informal_group", {"representative_email": "r@x.pl"}), "r@x.pl", id="#4 - OK - informal group"),
        pytest.param(make("person", {}), None, id="#5 - OK - nobody to mail"),
    ],
)
def test_applicant_email(app, want) -> None:
    assert applicant_email(app) == want
