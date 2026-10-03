def test_inbox(client, auth) -> None:
    res = client.get("/admin/inbox", headers=auth)
    body = res.json()
    assert res.status_code == 200
    assert body["new_ideas"] and body["new_problem_reports"] and body["critical_problem_reports"]


def test_inbox_since_filters(client, auth) -> None:
    res = client.get("/admin/inbox", params={"since": "2030-01-01T00:00:00Z"}, headers=auth)
    assert res.json()["new_ideas"] == []


def test_inbox_bad_since(client, auth) -> None:
    assert client.get("/admin/inbox", params={"since": "yesterday"}, headers=auth).status_code == 422
