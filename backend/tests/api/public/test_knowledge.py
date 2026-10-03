def test_open_grant_calls_only(client) -> None:
    calls = client.get("/grant-calls").json()
    assert calls
    assert all(c["open"] for c in calls)
