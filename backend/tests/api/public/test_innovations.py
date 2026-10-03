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
