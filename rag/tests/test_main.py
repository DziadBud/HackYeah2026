from fastapi.testclient import TestClient
import pytest
from typing import cast

from app.main import app


client = TestClient(app)


class FakeEmbeddingService:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeTaggingService:
    def generate(self, text: str) -> list[str]:
        return ["senior-support", "accessibility"]


class FakeVectorStore:
    def __init__(self) -> None:
        self.insert_kwargs: dict[str, object] = {}

    def insert_document(self, **kwargs: object) -> tuple[str, list[str]]:
        self.insert_kwargs = kwargs
        chunks = cast(list[str], kwargs["chunks"])
        return (
            "wibraap",
            [
                f"00000000-0000-0000-0000-00000000000{index + 2}"
                for index in range(len(chunks))
            ],
        )

    def search(self, **kwargs: object) -> list[dict[str, object]]:
        return []


class FakeSearchVectorStore(FakeVectorStore):
    def __init__(self) -> None:
        self.search_kwargs: dict[str, object] = {}

    def search(self, **kwargs: object) -> list[dict[str, object]]:
        self.search_kwargs = kwargs
        return [
            {
                "parent_id": "parent-1",
                "child_id": "child-1",
                "title": "Senior support",
                "city": "Krakow",
                "summary": "Services for older residents.",
                "parent_url": "https://example.com/senior-support",
                "tags": ["seniors", "support"],
                "source": "sample",
                "page": 2,
                "text": "Detailed support for seniors.",
                "score": 0.91,
            }
        ]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_empty_retrieval_result(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())
    response = client.post("/query", json={"query": "support for seniors"})

    assert response.status_code == 200
    assert response.json() == {
        "query": "support for seniors",
        "top_k": 3,
        "matches": [],
    }


def test_query_rejects_empty_query():
    response = client.post("/query", json={"query": ""})

    assert response.status_code == 422


def test_query_rejects_more_than_three_results():
    response = client.post(
        "/query", json={"query": "support for seniors", "top_k": 4}
    )

    assert response.status_code == 422


def test_embed_stores_vector(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.tagging_service", FakeTaggingService())
    store = FakeVectorStore()
    monkeypatch.setattr("app.main.get_vector_store", lambda: store)

    response = client.post(
        "/embed",
        json={
            "text": "support for seniors " * 20,
            "innovation_id": "wibraap",
            "title": "Senior support",
            "city": "Krakow",
            "summary": "Services for older residents.",
            "parent_url": "https://example.com/senior-support",
            "tags": ["seniors", "support"],
            "source": "sample",
            "page": 2,
            "chunk_size": 100,
            "chunk_overlap": 10,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["innovation_id"] == "wibraap"
    assert body["tags"] == ["senior-support", "accessibility"]
    assert store.insert_kwargs["tags"] == ["senior-support", "accessibility"]
    assert body["child_count"] > 1
    assert len(body["child_ids"]) == body["child_count"]
    assert body["dimensions"] == 3


def test_query_searches_children_with_title_and_tag_filters(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    store = FakeSearchVectorStore()
    monkeypatch.setattr(
        "app.main.get_vector_store", lambda: store
    )

    response = client.post(
        "/query",
        json={
            "query": "support",
            "search_tests": True,
            "city": "Krakow",
            "title": "Senior",
            "tags": ["seniors"],
        },
    )

    assert response.status_code == 200
    assert store.search_kwargs["search_tests"] is True
    assert response.json()["matches"] == [
        {
            "parent_id": "parent-1",
            "child_id": "child-1",
            "title": "Senior support",
            "city": "Krakow",
            "summary": "Services for older residents.",
            "parent_url": "https://example.com/senior-support",
            "tags": ["seniors", "support"],
            "source": "sample",
            "page": 2,
            "text": "Detailed support for seniors.",
            "score": 0.91,
        }
    ]


def test_query_returns_parent_metadata_for_visible_result(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr(
        "app.main.get_vector_store", lambda: FakeSearchVectorStore()
    )

    response = client.post("/query", json={"query": "support"})
    match = response.json()["matches"][0]

    assert match["title"] == "Senior support"
    assert match["summary"] == "Services for older residents."
    assert match["parent_url"] == "https://example.com/senior-support"


def test_embed_pdf_extracts_full_document(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())
    monkeypatch.setattr(
        "app.main.extract_pdf_text", lambda data: "whole PDF document text"
    )

    response = client.post(
        "/embed/pdf",
        files={"file": ("report.pdf", b"pdf bytes", "application/pdf")},
        data={
            "innovation_id": "wibraap",
            "title": "Report",
            "summary": "Full report summary",
            "parent_url": "https://example.com/report",
        },
    )

    assert response.status_code == 201
    assert response.json()["innovation_id"] == "wibraap"


def test_embed_pdf_rejects_non_pdf():
    response = client.post(
        "/embed/pdf",
        files={"file": ("report.txt", b"text", "text/plain")},
        data={"innovation_id": "wibraap"},
    )

    assert response.status_code == 415


def test_embed_rejects_empty_text():
    response = client.post("/embed", json={"text": ""})

    assert response.status_code == 422


def test_embed_rejects_invalid_chunk_overlap():
    response = client.post(
        "/embed",
        json={"text": "some text", "chunk_size": 100, "chunk_overlap": 100},
    )

    assert response.status_code == 422
