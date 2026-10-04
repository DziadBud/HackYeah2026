import pytest

from app.config import settings
from app.main import app
from app.services.admin import deps as admin_deps
from app.services.public import deps



def test_library_lists_published_only(client) -> None:
    body = client.get("/innovations").json()

    ids = [i["id"] for i in body["items"]]
    assert "wibraap" in ids
    assert "paszport-choroby-rzadkiej" not in ids


def test_library_filter_by_area(client) -> None:
    body = client.get("/innovations", params={"challenge_area": "Seniorzy"}).json()
    assert [i["id"] for i in body["items"]] == ["straznik"]


def test_draft_innovation_404(client) -> None:
    assert client.get("/innovations/paszport-choroby-rzadkiej").status_code == 404


def test_feedback_updates_rating(client) -> None:
    assert client.post("/innovations/wibraap/feedback", json={"stars": 4}).status_code == 201
    client.post("/innovations/wibraap/feedback", json={"stars": 2, "comment": "za droga"})

    card = client.get("/innovations/wibraap").json()
    assert (card["rating_avg"], card["rating_count"]) == (3.0, 2)


def test_feedback_invalid_stars_422(client) -> None:
    assert client.post("/innovations/wibraap/feedback", json={"stars": 6}).status_code == 422


def test_pdf_served_as_download(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    (tmp_path / "wibraap.pdf").write_bytes(b"%PDF-1.4 demo")

    assert client.get("/innovations/wibraap").json()["has_pdf"] is True
    res = client.get("/innovations/wibraap/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.headers["content-disposition"].startswith("attachment")
    assert res.content == b"%PDF-1.4 demo"


def test_pdf_falls_back_to_seed_media(client, tmp_path, monkeypatch) -> None:
    uploads, seed = tmp_path / "uploads", tmp_path / "seed"
    monkeypatch.setattr(settings, "upload_dir", str(uploads))
    monkeypatch.setattr(settings, "seed_media_dir", str(seed))
    (seed / "wibraap").mkdir(parents=True)
    (seed / "wibraap" / "document.pdf").write_bytes(b"%PDF-1.4 seed")

    assert client.get("/innovations/wibraap/pdf").content == b"%PDF-1.4 seed"
    # an admin upload replaces the seeded file
    uploads.mkdir()
    (uploads / "wibraap.pdf").write_bytes(b"%PDF-1.4 admin")
    assert client.get("/innovations/wibraap/pdf").content == b"%PDF-1.4 admin"


def test_pdf_missing_404(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    monkeypatch.setattr(settings, "seed_media_dir", str(tmp_path / "seed"))

    assert client.get("/innovations/wibraap").json()["has_pdf"] is False
    assert client.get("/innovations/wibraap/pdf").status_code == 404


def test_draft_pdf_404(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    (tmp_path / "paszport-choroby-rzadkiej.pdf").write_bytes(b"%PDF-1.4")

    assert client.get("/innovations/paszport-choroby-rzadkiej/pdf").status_code == 404


def test_test_signup_creates_one_signup(client) -> None:
    signups = app.dependency_overrides[admin_deps.get_test_signup_service]()
    before = len(signups.list(None, None))

    res = client.post("/innovations/wibraap/test-signups", json={"email": "gmina@example.com", "consent": True})

    assert res.status_code == 201
    assert res.json()["status"] == "applied"
    after = signups.list(None, None)
    assert len(after) == before + 1
    created = next(s for s in after if s.id == res.json()["id"])
    assert (created.innovation_id, created.email, created.problem_report_id) == ("wibraap", "gmina@example.com", None)


@pytest.mark.parametrize(
    ("innovation_id", "body", "status"),
    [
        ("wibraap", {"consent": True}, 422),
        ("wibraap", {"email": "gmina@example.com"}, 422),
        ("wibraap", {"email": "not-an-email", "consent": True}, 422),
        ("paszport-choroby-rzadkiej", {"email": "gmina@example.com", "consent": True}, 404),
        ("missing", {"email": "gmina@example.com", "consent": True}, 404),
    ],
    ids=[
        "#1 - FAIL - no email",
        "#2 - FAIL - no consent",
        "#3 - FAIL - bad email",
        "#4 - FAIL - draft innovation",
        "#5 - FAIL - unknown innovation",
    ],
)
def test_test_signup_fails(client, innovation_id, body, status) -> None:
    assert client.post(f"/innovations/{innovation_id}/test-signups", json=body).status_code == status


CLIENT = "6f1c2b9e-3d4a-4f5b-8c7d-1e2f3a4b5c6d"
OTHER = "0a1b2c3d-4e5f-4a6b-8c9d-0e1f2a3b4c5d"


def test_like_and_unlike(client) -> None:
    assert client.get("/innovations/wibraap/likes").json() == {"like_count": 0, "liked": False}

    assert client.put(f"/innovations/wibraap/likes/{CLIENT}").json() == {"like_count": 1, "liked": True}
    # liking twice keeps one like
    assert client.put(f"/innovations/wibraap/likes/{CLIENT}").json()["like_count"] == 1
    client.put(f"/innovations/wibraap/likes/{OTHER}")

    state = client.get("/innovations/wibraap/likes", params={"client_id": CLIENT}).json()
    assert state == {"like_count": 2, "liked": True}

    res = client.delete(f"/innovations/wibraap/likes/{CLIENT}")
    assert res.status_code == 200
    assert res.json() == {"like_count": 1, "liked": False}


def test_like_draft_404(client) -> None:
    assert client.put(f"/innovations/paszport-choroby-rzadkiej/likes/{CLIENT}").status_code == 404


def test_like_bad_client_id_422(client) -> None:
    assert client.put("/innovations/wibraap/likes/not-a-uuid").status_code == 422


def _seed_photo(tmp_path, monkeypatch, innovation_id: str) -> None:
    monkeypatch.setattr(settings, "seed_media_dir", str(tmp_path))
    (tmp_path / innovation_id).mkdir()
    (tmp_path / innovation_id / "photo-1.jpg").write_bytes(b"\xff\xd8jpeg")
    library = app.dependency_overrides[deps.get_library_service]()
    library.profiles[innovation_id] = {"photos": ["photo-1.jpg"], "problem": "Brak dostępu do muzyki."}


def test_profile_and_photo(client, tmp_path, monkeypatch) -> None:
    _seed_photo(tmp_path, monkeypatch, "wibraap")

    card = client.get("/innovations/wibraap").json()
    assert (card["photos"], card["problem"]) == (["photo-1.jpg"], "Brak dostępu do muzyki.")
    res = client.get("/innovations/wibraap/photos/photo-1.jpg")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"
    assert res.content == b"\xff\xd8jpeg"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param("/innovations/wibraap/photos/photo-2.jpg", id="#1 - FAIL - not listed"),
        pytest.param("/innovations/wibraap/photos/..%2F..%2Fsecret", id="#2 - FAIL - path traversal"),
        pytest.param("/innovations/paszport-choroby-rzadkiej/photos/photo-1.jpg", id="#3 - FAIL - draft"),
    ],
)
def test_photo_404(client, tmp_path, monkeypatch, path) -> None:
    _seed_photo(tmp_path, monkeypatch, "wibraap")
    assert client.get(path).status_code == 404
