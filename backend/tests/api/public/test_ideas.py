from datetime import date

from app.main import app
from app.schemas.admin.grant_calls import GrantCallCreate
from app.schemas.admin.ideas import IdeaStatus
from app.services.admin import deps as admin_deps

IDEA = {
    "summary": "Kawiarenka cyfrowa dla seniorów",
    "essence": "Wolontariusze uczą seniorów obsługi telefonu",
    "target_group": "seniorzy",
    "stage": "concept",
}


def test_create_idea_lands_in_admin(client) -> None:
    res = client.post("/ideas", json=IDEA)

    assert res.status_code == 201
    assert res.json()["status"] == "new"
    admin_ideas = app.dependency_overrides[admin_deps.get_idea_service]()
    assert admin_ideas.get(res.json()["id"]).essence == IDEA["essence"]


def test_create_idea_invalid_stage_422(client) -> None:
    assert client.post("/ideas", json={**IDEA, "stage": "dream"}).status_code == 422


def test_grant_application_full_form_shape_and_edit(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    open_call = client.get("/grant-calls").json()[0]

    res = client.post(f"/ideas/{idea_id}/grant-application", json={"grant_call_id": open_call["id"]})

    assert res.status_code == 201
    draft = res.json()
    assert draft["status"] == "draft"
    # §2 — empty person shape always present for FE editing
    assert draft["applicant_type"] == "person"
    assert set(draft["applicant"]) >= {
        "first_name",
        "last_name",
        "address",
        "postal_code",
        "city",
        "phone",
        "email",
    }
    # §3–9 present (LLM or template)
    for key in (
        "title",
        "description",
        "innovativeness",
        "problem_diagnosis",
        "beneficiaries",
        "expected_change",
        "future_vision",
        "action_plan",
    ):
        assert key in draft
    assert set(draft["action_plan"]) >= {
        "preparation_summary",
        "preparation",
        "testing_summary",
        "testing_phase_1",
        "testing_phase_2",
    }
    # §10–12
    assert draft["grant_amount_pln"] is None
    assert draft["team"] == ""
    assert draft["declarations"]["resides_in_poland"] is False
    assert "rodo_duties_fulfilled" in draft["declarations"]

    # user edits LLM fields + fills applicant / amount / declarations
    patched = client.patch(
        f"/grant-applications/{draft['id']}",
        json={
            "title": "Kawiarenka cyfrowa 2.0",
            "description": "Edytowany opis innowacji przez użytkownika.",
            "applicant": {
                "first_name": "Anna",
                "last_name": "Kowalska",
                "address": "ul. Floriańska 1/2",
                "postal_code": "31-019",
                "city": "Kraków",
                "phone": "+48123123123",
                "email": "anna@example.com",
            },
            "grant_amount_pln": "45000",
            "team": "Anna Kowalska — koordynacja",
            "declarations": {
                "resides_in_poland": True,
                "full_legal_capacity": True,
                "voluntary_participation": True,
                "accepts_procedures": True,
                "data_truthful": True,
            },
            "status": "submitted",
        },
    )
    assert patched.status_code == 200
    body = patched.json()
    assert body["title"] == "Kawiarenka cyfrowa 2.0"
    assert body["description"].startswith("Edytowany")
    assert body["applicant"]["first_name"] == "Anna"
    assert body["applicant"]["postal_code"] == "31-019"
    assert body["grant_amount_pln"] == "45000"
    assert body["declarations"]["resides_in_poland"] is True
    assert body["declarations"]["no_criminal_conviction"] is False  # still in payload
    assert body["status"] == "submitted"


def test_grant_application_switch_to_organization(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    open_call = client.get("/grant-calls").json()[0]
    draft_id = client.post(
        f"/ideas/{idea_id}/grant-application", json={"grant_call_id": open_call["id"]}
    ).json()["id"]

    res = client.patch(
        f"/grant-applications/{draft_id}",
        json={"applicant_type": "organization"},
    )
    assert res.status_code == 200
    applicant = res.json()["applicant"]
    assert "krs" in applicant and "representative" in applicant
    assert "role" in applicant["representative"]
    assert "entity_seat_in_poland" in res.json()["declarations"]


def test_grant_application_closed_call_422(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    grant_calls = app.dependency_overrides[admin_deps.get_grant_call_service]()
    closed = grant_calls.create(GrantCallCreate(name="Nabór 2025", deadline=date(2025, 12, 1), open=False))

    res = client.post(f"/ideas/{idea_id}/grant-application", json={"grant_call_id": closed.id})

    assert res.status_code == 422


def test_grant_application_rejected_idea_422(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    app.dependency_overrides[admin_deps.get_idea_service]().set_status(idea_id, IdeaStatus.REJECTED)
    open_call = client.get("/grant-calls").json()[0]

    res = client.post(f"/ideas/{idea_id}/grant-application", json={"grant_call_id": open_call["id"]})

    assert res.status_code == 422
