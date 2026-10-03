from fastapi.testclient import TestClient
from typing import cast

from app.main import app


client = TestClient(app)


class FakeEmbeddingService:
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeVectorStore:
    def insert_document(self, **kwargs: object) -> tuple[str, list[str]]:
        chunks = cast(list[str], kwargs["chunks"])
        return (
            "00000000-0000-0000-0000-000000000001",
            [
                f"00000000-0000-0000-0000-00000000000{index + 2}"
                for index in range(len(chunks))
            ],
        )


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


def test_embed_stores_vector(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())

    response = client.post(
        "/embed",
        json={
            "text": "support for seniors " * 20,
            "source": "sample",
            "page": 2,
            "chunk_size": 100,
            "chunk_overlap": 10,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["parent_id"] == "00000000-0000-0000-0000-000000000001"
    assert body["child_count"] > 1
    assert len(body["child_ids"]) == body["child_count"]
    assert body["dimensions"] == 3
    assert body["source"] == "sample"
    assert body["page"] == 2


def test_embed_rejects_empty_text():
    response = client.post("/embed", json={"text": ""})

    assert response.status_code == 422


def test_embed_rejects_invalid_chunk_overlap():
    response = client.post(
        "/embed",
        json={"text": "some text", "chunk_size": 100, "chunk_overlap": 100},
    )

    assert response.status_code == 422
