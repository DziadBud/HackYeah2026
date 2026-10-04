import pytest


def test_list_test_signups(client, auth) -> None:
    res = client.get("/admin/test-signups", headers=auth)
    assert res.status_code == 200
    assert {s["id"] for s in res.json()} == {"signup-1", "signup-2"}


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"status": "applied"}, {"signup-1"}),
        ({"innovation_id": "wibraap", "status": "accepted"}, {"signup-2"}),
        ({"innovation_id": "missing"}, set()),
    ],
    ids=["#1 - OK - status", "#2 - OK - innovation and status", "#3 - OK - no match"],
)
def test_list_test_signups_filters(client, auth, params, expected) -> None:
    res = client.get("/admin/test-signups", params=params, headers=auth)
    assert {s["id"] for s in res.json()} == expected


def test_set_test_signup_status(client, auth) -> None:
    res = client.post("/admin/test-signups/signup-1/status", json={"status": "accepted"}, headers=auth)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
    inbox = client.get("/admin/inbox", headers=auth).json()
    assert inbox["new_test_signups"] == []


@pytest.mark.parametrize(
    ("signup_id", "body", "status"),
    [
        ("signup-1", {"status": "applied"}, 422),
        ("signup-1", {"status": "maybe"}, 422),
        ("missing", {"status": "accepted"}, 404),
    ],
    ids=["#1 - FAIL - back to applied", "#2 - FAIL - unknown status", "#3 - FAIL - not found"],
)
def test_set_test_signup_status_fails(client, auth, signup_id, body, status) -> None:
    res = client.post(f"/admin/test-signups/{signup_id}/status", json=body, headers=auth)
    assert res.status_code == status


def test_test_signups_require_admin(client) -> None:
    assert client.get("/admin/test-signups").status_code == 401
