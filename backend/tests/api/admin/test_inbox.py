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


def test_inbox_naive_since_422(client, auth) -> None:
    res = client.get("/admin/inbox", params={"since": "2026-10-01T00:00:00"}, headers=auth)
    assert res.status_code == 422


def test_inbox_reflects_status_and_reply(client, auth) -> None:
    client.post("/admin/ideas/idea-1/status", json={"status": "rejected"}, headers=auth)
    client.post("/admin/problem-reports/problem-report-1/reply", json={"message": "ok"}, headers=auth)
    body = client.get("/admin/inbox", headers=auth).json()
    assert "idea-1" not in {i["id"] for i in body["new_ideas"]}
    assert "problem-report-1" not in {r["id"] for r in body["new_problem_reports"]}


def test_inbox_pending_threads(client, auth) -> None:
    body = client.get("/admin/inbox", headers=auth).json()
    assert "thread-1" in {t["id"] for t in body["pending_threads"]}
    assert body["new_test_signups"] == []
    client.post("/admin/threads/thread-1/status", json={"status": "published"}, headers=auth)
    body = client.get("/admin/inbox", headers=auth).json()
    assert "thread-1" not in {t["id"] for t in body["pending_threads"]}
