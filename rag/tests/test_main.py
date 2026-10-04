from typing import cast

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class FakeEmbeddingService:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeOllamaClient:
    def generate(self, prompt: str) -> dict[str, str]:
        return {"result": "tekst przetworzony"}


class FakeVectorStore:
    def __init__(self) -> None:
        self.insert_kwargs: dict[str, object] = {}

    def get_content(self, innovation_id: str) -> str:
        return "support for seniors " * 20

    def create_test_innovation(self, innovation_id: str, text: str) -> None:
        self.test_innovation = (innovation_id, text)

    def get_innovation(self, innovation_id: str) -> dict[str, object]:
        return {
            "innovation_id": innovation_id,
            "title": "Test innovation",
            "content": "Wsparcie dla osób starszych",
            "tags": ["senior-support"],
            "status": "published",
            "chunk_count": 1,
        }

    def insert_document(self, **kwargs: object) -> tuple[str, list[str]]:
        self.insert_kwargs = kwargs
        chunks = cast(list[str], kwargs["chunks"])
        return (
            str(kwargs["innovation_id"]),
            [
                f"00000000-0000-0000-0000-00000000000{index + 2}"
                for index in range(len(chunks))
            ],
        )

    def search(self, **kwargs: object) -> list[dict[str, object]]:
        return []


class FakeSearchVectorStore(FakeVectorStore):
    def __init__(self) -> None:
        super().__init__()
        self.search_kwargs: dict[str, object] = {}

    def search(self, **kwargs: object) -> list[dict[str, object]]:
        self.search_kwargs = kwargs
        return [{"innovation_id": "wibraap"}]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_no_result_matches(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())

    response = client.post("/query", json={"query": "support for seniors"})

    assert response.status_code == 200
    assert response.json() == {
        "query": "support for seniors",
        "top_k": 3,
        "matches": [],
    }


def test_query_returns_only_innovation_ids(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    store = FakeSearchVectorStore()
    monkeypatch.setattr("app.main.get_vector_store", lambda: store)

    response = client.post(
        "/query",
        json={"query": "support", "search_tests": True},
    )

    assert response.status_code == 200
    assert store.search_kwargs["search_tests"] is True
    assert response.json()["matches"] == [{"innovation_id": "wibraap"}]


def test_query_test_returns_innovation_by_id(monkeypatch):
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())

    response = client.get("/query/test/test-wibraap")

    assert response.status_code == 200
    assert response.json()["innovation_id"] == "test-wibraap"
    assert response.json()["chunk_count"] == 1


def test_llm_test_accepts_prompt_and_text(monkeypatch):
    monkeypatch.setattr("app.main.ollama_client", FakeOllamaClient())

    response = client.post(
        "/llm/test",
        json={"prompt": "Wyciągnij najważniejszą informację.", "text": "Tekst testowy."},
    )

    assert response.status_code == 200
    assert response.json() == {"output": {"result": "tekst przetworzony"}}


def test_query_rejects_empty_query():
    response = client.post("/query", json={"query": ""})

    assert response.status_code == 422


def test_query_rejects_more_than_three_results():
    response = client.post(
        "/query", json={"query": "support for seniors", "top_k": 4}
    )

    assert response.status_code == 422


def test_embed_fetches_content_and_stores_chunks(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    store = FakeVectorStore()
    monkeypatch.setattr("app.main.get_vector_store", lambda: store)

    response = client.post("/embed", json={"innovation_id": "wibraap"})

    assert response.status_code == 201
    body = response.json()
    assert body["innovation_id"] == "wibraap"
    assert body["child_count"] >= 1
    assert body["dimensions"] == 3


def test_embed_test_accepts_plain_text_without_innovation_id(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    store = FakeVectorStore()
    monkeypatch.setattr("app.main.get_vector_store", lambda: store)

    response = client.post(
        "/embed/test",
        json={"text": "Wsparcie dla osób starszych"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["innovation_id"].startswith("test-")
    assert body["dimensions"] == 3
    assert store.test_innovation[1] == "Wsparcie dla osób starszych"


def test_embed_pdf_extracts_full_document(monkeypatch):
    monkeypatch.setattr("app.main.embedding_service", FakeEmbeddingService())
    monkeypatch.setattr("app.main.get_vector_store", lambda: FakeVectorStore())
    monkeypatch.setattr(
        "app.main.extract_pdf_text", lambda data: "whole PDF document text"
    )

    response = client.post(
        "/embed/pdf",
        files={"file": ("report.pdf", b"pdf bytes", "application/pdf")},
        data={"innovation_id": "wibraap"},
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


def test_embed_rejects_missing_innovation_id():
    response = client.post("/embed", json={})

    assert response.status_code == 422
