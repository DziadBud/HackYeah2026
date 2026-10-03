def test_support_increments(client) -> None:
    report_id = client.post("/match", json={"text": "Samotność seniorów na wsi"}).json()["problem_report_id"]

    assert client.post(f"/problem-reports/{report_id}/support").json() == {"support_count": 1}
    assert client.post(f"/problem-reports/{report_id}/support").json() == {"support_count": 2}


def test_unknown_report_404(client) -> None:
    assert client.get("/problem-reports/nope").status_code == 404
    assert client.post("/problem-reports/nope/support").status_code == 404
