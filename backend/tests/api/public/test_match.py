import pytest

from app.main import app
from app.services.admin.errors import UpstreamUnavailableError
from app.services.public import deps

QUERY = {"text": "Osoby niesłyszące nie słyszą alarmów pożarowych", "city": "Krakow"}


def test_match_returns_innovations_and_stores_report(client) -> None:
    res = client.post("/match", json=QUERY)

    assert res.status_code == 200
    body = res.json()
    assert body["innovations"][0]["id"] == "straznik"
    assert body["answer"]
    assert body["test_signup_ids"] == []
    report = client.get(f"/problem-reports/{body['problem_report_id']}").json()
    assert report["text"] == QUERY["text"]


@pytest.mark.parametrize(
    "extra, want",
    [
        pytest.param({"email": "jan@example.com", "consent": True}, 200, id="#1 - OK"),
        pytest.param({}, 422, id="#2 - FAIL - no email"),
        pytest.param({"email": "jan@example.com"}, 422, id="#3 - FAIL - no consent"),
    ],
)
def test_match_with_test_signup(client, extra, want) -> None:
    res = client.post("/match", params={"test_signup": True}, json={**QUERY, **extra})

    assert res.status_code == want
    if want == 200:
        body = res.json()
        assert len(body["test_signup_ids"]) == len(body["innovations"]) > 0


def test_match_rejects_short_text(client) -> None:
    assert client.post("/match", json={"text": "a"}).status_code == 422


def test_match_rag_down_503(client) -> None:
    class RagDown:
        def match(self, data, test_signup):
            raise UpstreamUnavailableError("rag query failed: timeout")

    app.dependency_overrides[deps.get_match_service] = lambda: RagDown()
    assert client.post("/match", json=QUERY).status_code == 503
