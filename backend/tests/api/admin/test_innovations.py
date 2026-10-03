BASE = "/admin/innovations"
NEW = {
    "title": "Nowa innowacja",
    "summary": "Opis",
    "challenge_areas": ["Seniorzy"],
    "target_group": ["seniorzy"],
    "readiness": "concept",
    "cost_level": "low",
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


def test_create_then_publish_and_unpublish(client, auth) -> None:
    res = client.post(BASE, json=NEW, headers=auth)
    assert res.status_code == 201
    created = res.json()
    assert created["status"] == "draft"

    res = client.post(f"{BASE}/{created['id']}/publish", headers=auth)
    assert res.json()["status"] == "published"
    res = client.post(f"{BASE}/{created['id']}/unpublish", headers=auth)
    assert res.json()["status"] == "draft"


def test_create_invalid_area(client, auth) -> None:
    res = client.post(BASE, json={**NEW, "challenge_areas": ["Kosmos"]}, headers=auth)
    assert res.status_code == 422


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
