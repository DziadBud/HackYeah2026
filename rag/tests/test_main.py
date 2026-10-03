from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_empty_retrieval_result():
    response = client.post("/query", json={"query": "support for seniors"})

    assert response.status_code == 200
    assert response.json() == {
        "query": "support for seniors",
        "top_k": 5,
        "matches": [],
    }


def test_query_rejects_empty_query():
    response = client.post("/query", json={"query": ""})

    assert response.status_code == 422
