import os
from typing import Sequence
from uuid import UUID


class VectorStoreError(RuntimeError):
    pass


class PostgresVectorStore:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")

    def insert_document(
        self,
        *,
        text: str,
        source: str,
        page: int | None,
        chunks: Sequence[str],
        embeddings: Sequence[Sequence[float]],
    ) -> tuple[UUID, list[UUID]]:
        if len(chunks) != len(embeddings):
            raise VectorStoreError("each child chunk must have one embedding")
        if not self.database_url:
            raise VectorStoreError("DATABASE_URL is not configured")

        try:
            import psycopg
            from pgvector.psycopg import register_vector
        except ImportError as error:
            raise VectorStoreError(
                "psycopg and pgvector are required to write embeddings"
            ) from error

        try:
            with psycopg.connect(self.database_url) as connection:
                register_vector(connection)
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO rag_documents (text, source, page)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """,
                        (text, source, page),
                    )
                    row = cursor.fetchone()
                    if row is None:
                        raise VectorStoreError("database did not return a parent id")
                    parent_id = row[0]
                    child_ids: list[UUID] = []
                    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        cursor.execute(
                            """
                            INSERT INTO rag_chunks
                                (parent_id, chunk_index, text, source, page, embedding)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id
                            """,
                            (
                                parent_id,
                                index,
                                chunk,
                                source,
                                page,
                                list(embedding),
                            ),
                        )
                        child_row = cursor.fetchone()
                        if child_row is None:
                            raise VectorStoreError("database did not return a child id")
                        child_ids.append(child_row[0])
                    return parent_id, child_ids
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError(f"could not store embedding: {error}") from error


def get_vector_store() -> PostgresVectorStore:
    return PostgresVectorStore()