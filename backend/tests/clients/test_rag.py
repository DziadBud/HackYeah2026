import httpx
import pytest

from app.clients import rag
from app.clients.rag import RagAnswer, RagClient
from app.services.admin.errors import UpstreamUnavailableError

URL = "http://rag:8000/query"


def _respond(status: int, body: object):
    def post(url, **kwargs):
        return httpx.Response(status, json=body, request=httpx.Request("POST", url))

    return post


def _timeout(url, **kwargs):
    raise httpx.ReadTimeout("timed out")


@pytest.mark.parametrize(
    "post, want",
    [
        pytest.param(
            _respond(200, {"answer": "Seniorzy", "matches": [{"innovation_id": "a"}, {"innovation_id": "b"}]}),
            RagAnswer(answer="Seniorzy", innovation_ids=["a", "b"]),
            id="#1 - OK",
        ),
        pytest.param(
            _respond(200, {"matches": [{"innovation_id": "a"}]}),
            RagAnswer(answer="", innovation_ids=["a"]),
            id="#2 - OK - no answer",
        ),
        pytest.param(_respond(503, {"detail": "down"}), None, id="#3 - FAIL - rag error status"),
        pytest.param(_timeout, None, id="#4 - FAIL - timeout"),
        pytest.param(_respond(200, {"answer": "x"}), None, id="#5 - FAIL - unexpected body"),
    ],
)
def test_query(monkeypatch, post, want) -> None:
    monkeypatch.setattr(rag.httpx, "post", post)
    client = RagClient("http://rag:8000/", timeout_seconds=300, query_timeout_seconds=60)

    if want is None:
        with pytest.raises(UpstreamUnavailableError):
            client.query("problem", 3)
    else:
        assert client.query("problem", 3) == want
