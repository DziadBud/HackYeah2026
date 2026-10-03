import pytest

from app.main import app
from app.services.admin import deps
from app.services.admin.errors import EmbedPublishError, InvalidUploadError, UploadTooLargeError
from app.services.admin.innovation_upload import CreatedInnovation, NewInnovation

BASE = "/admin/innovations"
PDF = b"%PDF-1.7 fake"
FORM = {"title": "Opaska", "summary": "Opis", "author": "Jan Testowy", "tags": ["Seniorzy", "pilotaz"]}


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
        assert (data.author, data.tags, data.city, pdf) == ("Jan Testowy", ["Seniorzy", "pilotaz"], "", PDF)


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
