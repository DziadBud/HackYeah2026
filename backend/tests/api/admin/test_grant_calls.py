BASE = "/admin/grant-calls"


def test_list(client, auth) -> None:
    res = client.get(BASE, headers=auth)
    assert res.status_code == 200
    assert res.json()[0]["id"] == "call-1"


def test_create_and_patch(client, auth) -> None:
    body = {"name": "Nabor wiosenny", "deadline": "2027-03-01", "sections": [{"title": "Opis"}]}
    res = client.post(BASE, json=body, headers=auth)
    assert res.status_code == 201
    created = res.json()
    assert created["open"] is False

    res = client.patch(f"{BASE}/{created['id']}", json={"open": True}, headers=auth)
    assert res.status_code == 200
    assert res.json()["open"] is True
    assert res.json()["name"] == "Nabor wiosenny"


def test_patch_unknown_404(client, auth) -> None:
    assert client.patch(f"{BASE}/nope", json={"open": True}, headers=auth).status_code == 404


def test_create_invalid_deadline_422(client, auth) -> None:
    res = client.post(BASE, json={"name": "x", "deadline": "soon"}, headers=auth)
    assert res.status_code == 422
