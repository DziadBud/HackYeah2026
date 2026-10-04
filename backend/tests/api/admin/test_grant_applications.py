BASE = "/admin/grant-applications"


def test_list_newest_first(client, auth) -> None:
    res = client.get(BASE, headers=auth)
    assert res.status_code == 200
    assert [a["id"] for a in res.json()] == ["app-2", "app-1"]


def test_list_filters_by_status(client, auth) -> None:
    res = client.get(BASE, params={"status": "submitted"}, headers=auth)
    assert [a["id"] for a in res.json()] == ["app-1"]


def test_list_filters_by_call(client, auth) -> None:
    assert client.get(BASE, params={"grant_call_id": "other"}, headers=auth).json() == []


def test_list_invalid_status_422(client, auth) -> None:
    assert client.get(BASE, params={"status": "accepted"}, headers=auth).status_code == 422


def test_get_full_form(client, auth) -> None:
    res = client.get(f"{BASE}/app-1", headers=auth)
    assert res.status_code == 200
    body = res.json()
    # missing §2 fields and §12 checkboxes come back as their empty defaults
    assert body["applicant"]["postal_code"] == ""
    assert body["declarations"]["no_tax_arrears"] is False
    assert body["action_plan"]["preparation"][0]["cost_pln"] == 2000


def test_get_unknown_404(client, auth) -> None:
    assert client.get(f"{BASE}/nope", headers=auth).status_code == 404


def test_requires_login(client) -> None:
    assert client.get(BASE).status_code == 401
