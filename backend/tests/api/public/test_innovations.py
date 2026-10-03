from app.config import settings



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


def test_pdf_served_inline(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    (tmp_path / "wibraap.pdf").write_bytes(b"%PDF-1.4 demo")

    assert client.get("/innovations/wibraap").json()["has_pdf"] is True
    res = client.get("/innovations/wibraap/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.headers["content-disposition"].startswith("inline")
    assert res.content == b"%PDF-1.4 demo"


def test_pdf_missing_404(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))

    assert client.get("/innovations/wibraap").json()["has_pdf"] is False
    assert client.get("/innovations/wibraap/pdf").status_code == 404


def test_draft_pdf_404(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    (tmp_path / "paszport-choroby-rzadkiej.pdf").write_bytes(b"%PDF-1.4")

    assert client.get("/innovations/paszport-choroby-rzadkiej/pdf").status_code == 404
