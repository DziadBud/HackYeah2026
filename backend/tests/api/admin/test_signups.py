import pytest

BASE = "/admin/test-signups"


@pytest.mark.parametrize(
    "params, want",
    [
        pytest.param({}, ["signup-1", "signup-2"], id="#1 - OK - all"),
        pytest.param({"status": "applied"}, ["signup-1"], id="#2 - OK - by status"),
        pytest.param({"innovation_id": "wibraap"}, ["signup-2"], id="#3 - OK - by innovation"),
    ],
)
def test_list(client, auth, params, want) -> None:
    res = client.get(BASE, params=params, headers=auth)
    assert res.status_code == 200
    assert sorted(s["id"] for s in res.json()) == want


@pytest.mark.parametrize(
    "signup_id, body, want",
    [
        pytest.param("signup-1", {"status": "accepted"}, 200, id="#1 - OK - accept"),
        pytest.param("signup-2", {"status": "completed"}, 200, id="#2 - OK - complete"),
        pytest.param("signup-1", {"status": "applied"}, 422, id="#3 - FAIL - applied is not a decision"),
        pytest.param("nope", {"status": "rejected"}, 404, id="#4 - FAIL - unknown signup"),
    ],
)
def test_set_status(client, auth, signup_id, body, want) -> None:
    res = client.post(f"{BASE}/{signup_id}/status", json=body, headers=auth)
    assert res.status_code == want
    if want == 200:
        assert res.json()["status"] == body["status"]


def test_requires_admin(client) -> None:
    assert client.get(BASE).status_code == 401
