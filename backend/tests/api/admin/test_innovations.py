import pytest

from app.main import app
from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.innovations import CostLevel, Readiness
from app.services.admin import deps
from app.services.admin.errors import EmbedPublishError, InvalidUploadError, UploadTooLargeError
from app.services.admin.innovation_upload import CreatedInnovation, InnovationUploadService, NewInnovation
from app.storage import LocalFileStorage

BASE = "/admin/innovations"
PDF = b"%PDF-1.7 fake"
UPLOADED = NewInnovation(
    title="Nowa innowacja",
    summary="Opis",
    problem="Problem",
    innovator="Fundacja Testowa",
    challenge_areas=[ChallengeArea.SENIORS],
    readiness=Readiness.CONCEPT,
    cost_level=CostLevel.LOW,
)
FORM = {
    "title": "Opaska",
    "summary": "Opis",
    "problem": "Seniorzy nie slysza alarmow",
    "innovator": "Fundacja Testowa",
    "challenge_areas": ["Seniorzy"],
    "readiness": "pilot",
    "cost_level": "low",
    "tags": ["opaska", "pilotaz"],
}


def test_list_filtered(client, auth) -> None:
    res = client.get(BASE, params={"status": "published", "limit": 1}, headers=auth)
    body = res.json()
    assert res.status_code == 200
    assert len(body["items"]) == 1
    assert body["total"] >= 2
    assert body["items"][0]["status"] == "published"


def test_list_bad_limit(client, auth) -> None:
    assert client.get(BASE, params={"limit": 0}, headers=auth).status_code == 422


def test_publish_and_unpublish(client, auth) -> None:
    res = client.post(f"{BASE}/wibraap/unpublish", headers=auth)
    assert res.json()["status"] == "draft"
    res = client.post(f"{BASE}/wibraap/publish", headers=auth)
    assert res.json()["status"] == "published"


class FakeUploadService:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls: list[tuple[NewInnovation, bytes]] = []
        self.error = error

    def create(self, data: NewInnovation, pdf: bytes) -> CreatedInnovation:
        if self.error:
            raise self.error
        self.calls.append((data, pdf))
        return CreatedInnovation(id="opaska-abc123", title=data.title, status="draft", file_path="/x.pdf")


@pytest.mark.parametrize(
    "error, want",
    [
        pytest.param(None, 202, id="#1 - OK"),
        pytest.param(InvalidUploadError("file is not a pdf"), 415, id="#2 - FAIL - not a pdf"),
        pytest.param(UploadTooLargeError("too big"), 413, id="#3 - FAIL - too large"),
        pytest.param(EmbedPublishError("broker down"), 503, id="#4 - FAIL - publish failed"),
    ],
)
def test_upload(client, auth, error, want) -> None:
    svc = FakeUploadService(error)
    app.dependency_overrides[deps.get_innovation_upload_service] = lambda: svc

    res = client.post(BASE, data=FORM, files={"file": ("opaska.pdf", PDF, "application/pdf")}, headers=auth)

    assert res.status_code == want
    if want == 202:
        assert res.json() == {"id": "opaska-abc123", "title": "Opaska", "status": "draft"}
        data, pdf = svc.calls[0]
        assert (data.innovator, data.challenge_areas, data.tags, data.city, pdf) == (
            "Fundacja Testowa", ["Seniorzy"], ["opaska", "pilotaz"], "", PDF
        )


@pytest.mark.parametrize(
    "override",
    [
        pytest.param({"problem": ""}, id="#1 - FAIL - empty problem"),
        pytest.param({"challenge_areas": ["Kosmos"]}, id="#2 - FAIL - unknown area"),
        pytest.param({"readiness": "someday"}, id="#3 - FAIL - unknown readiness"),
    ],
)
def test_upload_invalid_field_422(client, auth, override) -> None:
    app.dependency_overrides[deps.get_innovation_upload_service] = lambda: FakeUploadService()
    res = client.post(
        BASE, data={**FORM, **override}, files={"file": ("a.pdf", PDF, "application/pdf")}, headers=auth
    )
    assert res.status_code == 422


def test_upload_missing_fields_422(client, auth) -> None:
    app.dependency_overrides[deps.get_innovation_upload_service] = lambda: FakeUploadService()
    res = client.post(BASE, data={"title": "Opaska"}, files={"file": ("a.pdf", PDF, "application/pdf")}, headers=auth)
    assert res.status_code == 422


def test_upload_requires_admin(client) -> None:
    app.dependency_overrides[deps.get_innovation_upload_service] = lambda: FakeUploadService()
    res = client.post(BASE, data=FORM, files={"file": ("a.pdf", PDF, "application/pdf")})
    assert res.status_code == 401


def test_get_and_patch(client, auth) -> None:
    assert client.get(f"{BASE}/wibraap", headers=auth).json()["id"] == "wibraap"
    res = client.patch(f"{BASE}/wibraap", json={"cost_level": "high"}, headers=auth)
    assert res.status_code == 200
    assert res.json()["cost_level"] == "high"
    assert res.json()["title"] == "Wibraap"


def test_feedback(client, auth) -> None:
    body = client.get(f"{BASE}/straznik/feedback", headers=auth).json()
    assert body["rating_count"] > 0
    assert body["recent_comments"]


def test_unknown_id_404(client, auth) -> None:
    for method, path in [
        ("GET", ""),
        ("PATCH", ""),
        ("POST", "/publish"),
        ("GET", "/feedback"),
        ("GET", "/stats"),
    ]:
        res = client.request(method, f"{BASE}/nope{path}", json={} if method == "PATCH" else None, headers=auth)
        assert res.status_code == 404, (method, path)


def test_patch_null_required_field_422(client, auth) -> None:
    res = client.patch(f"{BASE}/wibraap", json={"title": None}, headers=auth)
    assert res.status_code == 422


def test_patch_null_video_url_clears_it(client, auth) -> None:
    res = client.patch(f"{BASE}/wibraap", json={"video_url": None}, headers=auth)
    assert res.status_code == 200
    assert res.json()["video_url"] is None


def test_stats_totals_add_up(client, auth) -> None:
    res = client.get(f"{BASE}/wibraap/stats", headers=auth)
    assert res.status_code == 200
    body = res.json()
    total = body["matches_total"]
    assert total > 0
    assert sum(w["matches"] for w in body["matches_by_week"]) == total
    assert sum(a["matches"] for a in body["matches_by_area"]) == total
    assert body["matches_7d"] == body["matches_by_week"][-1]["matches"]
    assert sum(body["rating_distribution"]) == body["rating_count"]
    assert body["recent_problem_reports"]


def test_stats_suppresses_small_locations(client, auth) -> None:
    rows = {r["location"]: r for r in client.get(f"{BASE}/wibraap/stats", headers=auth).json()["matches_by_location"]}
    assert rows["Krakow"]["matches"] == 15
    assert rows["Wieliczka"]["matches"] is None
    assert rows["Wieliczka"]["note"]


def test_stats_for_new_innovation_are_empty(client, auth) -> None:
    # creation goes through the pdf upload, so the draft is put into the mock store directly
    innovations = app.dependency_overrides[deps.get_innovation_service]()
    innovations.insert_draft("nowa-abc123", UPLOADED, [])
    body = client.get(f"{BASE}/nowa-abc123/stats", headers=auth).json()
    assert body["matches_total"] == 0
    assert body["rating_avg"] is None
    assert len(body["matches_by_week"]) == 6


def test_feedback_matches_stats(client, auth) -> None:
    feedback = client.get(f"{BASE}/straznik/feedback", headers=auth).json()
    stats = client.get(f"{BASE}/straznik/stats", headers=auth).json()
    assert feedback["rating_avg"] == stats["rating_avg"]
    assert feedback["test_signups"] == sum(stats["test_signups"].values())


def test_stats_require_session(client) -> None:
    # test_auth's route discovery finds no routes on this fastapi version, so check the new ones here
    assert client.get(f"{BASE}/wibraap/stats").status_code == 401
    assert client.get("/admin/reports/innovations").status_code == 401


def test_upload_lands_in_mock_list(client, auth, tmp_path) -> None:
    published: list[str] = []

    class FakePublisher:
        def publish_embed_requested(self, innovation_id: str, file_path: str) -> None:
            published.append(innovation_id)

    innovations = app.dependency_overrides[deps.get_innovation_service]()
    svc = InnovationUploadService(innovations, LocalFileStorage(tmp_path), FakePublisher(), max_bytes=1024)
    app.dependency_overrides[deps.get_innovation_upload_service] = lambda: svc

    res = client.post(BASE, data=FORM, files={"file": ("opaska.pdf", PDF, "application/pdf")}, headers=auth)

    created = client.get(f"{BASE}/{res.json()['id']}", headers=auth).json()
    assert created["status"] == "draft"
    assert created["challenge_areas"] == ["Seniorzy"]
    assert (created["problem"], created["innovator"], created["readiness"]) == (
        "Seniorzy nie slysza alarmow", "Fundacja Testowa", "pilot"
    )
    assert published == [created["id"]]
