BASE = "/admin/problem-reports"


def test_list_filters(client, auth) -> None:
    res = client.get(BASE, params={"is_critical": True}, headers=auth)
    assert res.status_code == 200
    assert res.json() and all(i["is_critical"] for i in res.json())

    res = client.get(BASE, params={"location": "skawina"}, headers=auth)
    assert [i["id"] for i in res.json()] == ["problem-report-3"]

    res = client.get(BASE, params={"challenge_area": "Seniorzy"}, headers=auth)
    assert all(i["challenge_area"] == "Seniorzy" for i in res.json())


def test_get_and_reply(client, auth) -> None:
    assert client.get(f"{BASE}/problem-report-1", headers=auth).json()["support_count"] == 14
    res = client.post(f"{BASE}/problem-report-1/reply", json={"message": "Pracujemy nad tym"}, headers=auth)
    assert res.json()["admin_reply"] == "Pracujemy nad tym"


def test_unknown_problem_report_404(client, auth) -> None:
    assert client.get(f"{BASE}/nope", headers=auth).status_code == 404


def test_invalid_area_422(client, auth) -> None:
    assert client.get(BASE, params={"challenge_area": "Kosmos"}, headers=auth).status_code == 422
    res = client.post(f"{BASE}/problem-report-1/reply", json={"message": ""}, headers=auth)
    assert res.status_code == 422
