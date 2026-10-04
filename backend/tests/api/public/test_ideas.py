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


def test_grant_application_draft_and_update(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    open_call = client.get("/grant-calls").json()[0]

    res = client.post(f"/ideas/{idea_id}/grant-application", json={"grant_call_id": open_call["id"]})

    assert res.status_code == 201
    draft = res.json()
    assert draft["status"] == "draft"
    assert draft["idea_id"] == idea_id
    assert draft["title"]
    assert draft["applicant"] == {}
    assert draft["grant_amount_pln"] is None

    patched = client.patch(
        f"/grant-applications/{draft['id']}",
        json={
            "applicant_type": "person",
            "applicant": {
                "first_name": "Anna",
                "last_name": "Kowalska",
                "city": "Kraków",
                "email": "anna@example.com",
            },
            "grant_amount_pln": "45000",
            "team": "Anna Kowalska — koordynacja; wolontariusze OPS",
            "declarations": {"kind": "person", "accepted_all": True},
            "status": "submitted",
        },
    )
    assert patched.status_code == 200
    body = patched.json()
    assert body["applicant"]["first_name"] == "Anna"
    assert body["grant_amount_pln"] == "45000"
    assert body["status"] == "submitted"
    assert client.get(f"/grant-applications/{draft['id']}").json()["team"].startswith("Anna")


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
