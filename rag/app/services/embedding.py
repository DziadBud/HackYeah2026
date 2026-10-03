import os
from typing import Any


class EmbeddingService:
    def __init__(self) -> None:
        self.model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._model: Any | None = None

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        model = self._model
        if model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise RuntimeError(
                    "sentence-transformers is required to create embeddings"
                ) from error
            model = SentenceTransformer(self.model_name)
            self._model = model

        vectors = model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]