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


def test_grant_application(client) -> None:
    idea_id = client.post("/ideas", json=IDEA).json()["id"]
    open_call = client.get("/grant-calls").json()[0]

    res = client.post(f"/ideas/{idea_id}/grant-application", json={"grant_call_id": open_call["id"]})

    assert res.status_code == 201
    doc = res.json()
    assert doc["kind"] == "grant_application"
    assert doc["idea_id"] == idea_id


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
