BASE = "/admin/innovations"
NEW = {
    "title": "Nowa innowacja",
    "summary": "Opis",
    "challenge_areas": ["Seniorzy"],
    "target_group": ["seniorzy"],
    "readiness": "concept",
    "cost_level": "low",
}


def test_list_filtered(client, auth) -> None:
    res = client.get(BASE, params={"status": "published", "limit": 1}, headers=auth)
    body = res.json()
    assert res.status_code == 200
    assert len(body["items"]) == 1
    assert body["total"] >= 2
    assert body["items"][0]["status"] == "published"


def test_list_bad_limit(client, auth) -> None:
    assert client.get(BASE, params={"limit": 0}, headers=auth).status_code == 422


def test_create_then_publish_and_unpublish(client, auth) -> None:
    res = client.post(BASE, json=NEW, headers=auth)
    assert res.status_code == 201
    created = res.json()
    assert created["status"] == "draft"

    res = client.post(f"{BASE}/{created['id']}/publish", headers=auth)
    assert res.json()["status"] == "published"
    res = client.post(f"{BASE}/{created['id']}/unpublish", headers=auth)
    assert res.json()["status"] == "draft"


def test_create_invalid_area(client, auth) -> None:
    res = client.post(BASE, json={**NEW, "challenge_areas": ["Kosmos"]}, headers=auth)
    assert res.status_code == 422


def test_get_and_patch(client, auth) -> None:
    assert client.get(f"{BASE}/wibraap", headers=auth).json()["id"] == "wibraap"
    res = client.patch(f"{BASE}/wibraap", json={"cost_level": "high"}, headers=auth)
    assert res.status_code == 200
    assert res.json()["cost_level"] == "high"
    assert res.json()["title"] == "Wibraap"


def test_feedback(client, auth) -> None:
    body = client.get(f"{BASE}/straznik/feedback", headers=auth).json()
    assert body["rating_count"] > 0
    assert body["recent_comments"]


def test_unknown_id_404(client, auth) -> None:
    for method, path in [
        ("GET", ""),
        ("PATCH", ""),
        ("POST", "/publish"),
        ("GET", "/feedback"),
        ("GET", "/stats"),
    ]:
        res = client.request(method, f"{BASE}/nope{path}", json={} if method == "PATCH" else None, headers=auth)
        assert res.status_code == 404, (method, path)


def test_patch_null_required_field_422(client, auth) -> None:
    res = client.patch(f"{BASE}/wibraap", json={"title": None}, headers=auth)
    assert res.status_code == 422


def test_patch_null_video_url_clears_it(client, auth) -> None:
    res = client.patch(f"{BASE}/wibraap", json={"video_url": None}, headers=auth)
    assert res.status_code == 200
    assert res.json()["video_url"] is None


def test_stats_totals_add_up(client, auth) -> None:
    res = client.get(f"{BASE}/wibraap/stats", headers=auth)
    assert res.status_code == 200
    body = res.json()
    total = body["matches_total"]
    assert total > 0
    assert sum(w["matches"] for w in body["matches_by_week"]) == total
    assert sum(a["matches"] for a in body["matches_by_area"]) == total
    assert body["matches_7d"] == body["matches_by_week"][-1]["matches"]
    assert sum(body["rating_distribution"]) == body["rating_count"]
    assert body["recent_problem_reports"]


def test_stats_suppresses_small_locations(client, auth) -> None:
    rows = {r["location"]: r for r in client.get(f"{BASE}/wibraap/stats", headers=auth).json()["matches_by_location"]}
    assert rows["Krakow"]["matches"] == 15
    assert rows["Wieliczka"]["matches"] is None
    assert rows["Wieliczka"]["note"]


def test_stats_for_new_innovation_are_empty(client, auth) -> None:
    created = client.post(BASE, json=NEW, headers=auth).json()
    body = client.get(f"{BASE}/{created['id']}/stats", headers=auth).json()
    assert body["matches_total"] == 0
    assert body["rating_avg"] is None
    assert len(body["matches_by_week"]) == 6


def test_feedback_matches_stats(client, auth) -> None:
    feedback = client.get(f"{BASE}/straznik/feedback", headers=auth).json()
    stats = client.get(f"{BASE}/straznik/stats", headers=auth).json()
    assert feedback["rating_avg"] == stats["rating_avg"]
    assert feedback["test_signups"] == sum(stats["test_signups"].values())


def test_stats_require_session(client) -> None:
    # test_auth's route discovery finds no routes on this fastapi version, so check the new ones here
    assert client.get(f"{BASE}/wibraap/stats").status_code == 401
    assert client.get("/admin/reports/innovations").status_code == 401
