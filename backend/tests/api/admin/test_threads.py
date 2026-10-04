import pytest

BASE = "/admin/threads"


@pytest.mark.parametrize(
    "params, want",
    [
        pytest.param({}, ["thread-1", "thread-2"], id="#1 - OK - all"),
        # thread-2 is published but has a pending reply
        pytest.param({"status": "pending"}, ["thread-1", "thread-2"], id="#2 - OK - pending incl. replies"),
        pytest.param({"status": "hidden"}, [], id="#3 - OK - none hidden"),
        pytest.param({"innovation_id": "straznik"}, ["thread-2"], id="#4 - OK - by innovation"),
    ],
)
def test_list(client, auth, params, want) -> None:
    res = client.get(BASE, params=params, headers=auth)
    assert res.status_code == 200
    assert sorted(t["id"] for t in res.json()) == want


def test_publish_thread_and_hide_reply(client, auth) -> None:
    res = client.post(f"{BASE}/thread-1/status", json={"status": "published"}, headers=auth)
    assert (res.status_code, res.json()["status"]) == (200, "published")

    res = client.post(f"{BASE}/replies/reply-1/status", json={"status": "hidden"}, headers=auth)
    assert (res.status_code, res.json()["status"]) == (200, "hidden")

    assert client.get(BASE, params={"status": "pending"}, headers=auth).json() == []


def test_move_back_to_pending(client, auth) -> None:
    # pending is a valid decision: the panel's "Nowy" puts an item back in the moderation queue
    client.post(f"{BASE}/thread-1/status", json={"status": "published"}, headers=auth)
    res = client.post(f"{BASE}/thread-1/status", json={"status": "pending"}, headers=auth)
    assert (res.status_code, res.json()["status"]) == (200, "pending")


@pytest.mark.parametrize(
    "path, body, want",
    [
        pytest.param("/thread-1/status", {"status": "deleted"}, 422, id="#1 - FAIL - unknown status"),
        pytest.param("/nope/status", {"status": "published"}, 404, id="#2 - FAIL - unknown thread"),
        pytest.param("/replies/nope/status", {"status": "hidden"}, 404, id="#3 - FAIL - unknown reply"),
    ],
)
def test_set_status_errors(client, auth, path, body, want) -> None:
    assert client.post(f"{BASE}{path}", json=body, headers=auth).status_code == want


def test_requires_admin(client) -> None:
    assert client.get(BASE).status_code == 401
