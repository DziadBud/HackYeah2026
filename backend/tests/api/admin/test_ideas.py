BASE = "/admin/ideas"


def test_list_and_get(client, auth) -> None:
    res = client.get(BASE, params={"status": "in_review"}, headers=auth)
    assert res.status_code == 200
    assert {i["status"] for i in res.json()} == {"in_review"}
    idea = client.get(f"{BASE}/idea-1", headers=auth).json()
    assert idea["id"] == "idea-1"
    assert idea["stage"] == "concept"
    assert idea["summary"] and idea["social_canvas"]["problem"]


def test_reply_and_status(client, auth) -> None:
    res = client.post(f"{BASE}/idea-1/reply", json={"message": "Dziekujemy"}, headers=auth)
    assert res.json()["admin_reply"] == "Dziekujemy"
    res = client.post(f"{BASE}/idea-1/status", json={"status": "accepted"}, headers=auth)
    assert res.json()["status"] == "accepted"


def test_unknown_idea_404(client, auth) -> None:
    assert client.get(f"{BASE}/nope", headers=auth).status_code == 404
    res = client.post(f"{BASE}/nope/reply", json={"message": "x"}, headers=auth)
    assert res.status_code == 404


def test_invalid_status_422(client, auth) -> None:
    res = client.post(f"{BASE}/idea-1/status", json={"status": "bogus"}, headers=auth)
    assert res.status_code == 422
