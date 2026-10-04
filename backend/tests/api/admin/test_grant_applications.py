import pytest

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
    assert client.get(BASE, params={"status": "deleted"}, headers=auth).status_code == 422


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


@pytest.mark.parametrize(
    "app_id, status",
    [
        pytest.param("app-1", "accepted", id="#1 - OK - accept"),
        pytest.param("app-1", "rejected", id="#2 - OK - reject"),
    ],
)
def test_decide(client, auth, app_id, status) -> None:
    res = client.post(f"{BASE}/{app_id}/status", json={"status": status, "message": "Gratulacje"}, headers=auth)
    assert (res.status_code, res.json()["status"]) == (200, status)


@pytest.mark.parametrize(
    "app_id, body, want",
    [
        pytest.param("app-2", {"status": "accepted"}, 422, id="#1 - FAIL - draft cannot be decided"),
        pytest.param("app-1", {"status": "submitted"}, 422, id="#2 - FAIL - not a decision"),
        pytest.param("app-1", {"status": "accepted", "message": "x" * 2001}, 422, id="#3 - FAIL - message too long"),
        pytest.param("nope", {"status": "accepted"}, 404, id="#4 - FAIL - unknown application"),
    ],
)
def test_decide_errors(client, auth, app_id, body, want) -> None:
    assert client.post(f"{BASE}/{app_id}/status", json=body, headers=auth).status_code == want


def test_decision_is_final(client, auth) -> None:
    client.post(f"{BASE}/app-1/status", json={"status": "accepted"}, headers=auth)
    res = client.post(f"{BASE}/app-1/status", json={"status": "rejected"}, headers=auth)
    assert res.status_code == 422


def test_requires_login(client) -> None:
    assert client.get(BASE).status_code == 401
