import pytest

BASE = "/admin/reports"
NAMES = ["trends", "critical", "locations", "gaps"]


@pytest.mark.parametrize("name", NAMES)
def test_json(client, auth, name) -> None:
    res = client.get(f"{BASE}/{name}", headers=auth)
    assert res.status_code == 200
    assert len(res.json()) >= 1


@pytest.mark.parametrize("name", NAMES)
def test_csv(client, auth, name) -> None:
    res = client.get(f"{BASE}/{name}", params={"format": "csv"}, headers=auth)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert len(res.text.strip().splitlines()) >= 2


def test_locations_suppressed(client, auth) -> None:
    rows = {r["location"]: r for r in client.get(f"{BASE}/locations", headers=auth).json()}
    assert rows["Skawina"]["problem_reports"] is None
    assert rows["Skawina"]["note"]
    assert rows["Krakow"]["problem_reports"] == 12


def test_bad_format_422(client, auth) -> None:
    assert client.get(f"{BASE}/trends", params={"format": "xml"}, headers=auth).status_code == 422
