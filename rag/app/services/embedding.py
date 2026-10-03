import os

import httpx


class EmbeddingService:
    def __init__(self) -> None:
        self.service_url = os.getenv("EMBEDDING_SERVICE_URL")

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not self.service_url:
            raise RuntimeError("EMBEDDING_SERVICE_URL is required")

        try:
            response = httpx.post(
                self.service_url,
                json={"inputs": texts},
                timeout=60.0,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise RuntimeError("external embedding service request failed") from error

        vectors = payload
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise RuntimeError("external embedding service returned invalid embeddings")

        return vectors