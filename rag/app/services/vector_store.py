import os
from typing import Sequence
from uuid import UUID


class VectorStoreError(RuntimeError):
    pass


def _vector_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


class PostgresVectorStore:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")

    def get_content(self, innovation_id: str) -> str:
        if not self.database_url:
            raise VectorStoreError("DATABASE_URL is not configured")

        try:
            import psycopg
        except ImportError as error:
            raise VectorStoreError("psycopg is required to read innovations") from error

        try:
            with psycopg.connect(self.database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT content FROM innovations WHERE id = %s",
                        (innovation_id,),
                    )
                    row = cursor.fetchone()
                    if row is None:
                        raise VectorStoreError(
                            f"innovation does not exist: {innovation_id}"
                        )
                    if not row[0]:
                        raise VectorStoreError(
                            f"innovation has no content: {innovation_id}"
                        )
                    return str(row[0])
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError(f"could not read innovation content: {error}") from error

    def get_innovation(self, innovation_id: str) -> dict[str, object]:
        if not self.database_url:
            raise VectorStoreError("DATABASE_URL is not configured")

        try:
            import psycopg
        except ImportError as error:
            raise VectorStoreError("psycopg is required to read innovations") from error

        try:
            with psycopg.connect(self.database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT i.id, i.title, i.content, i.tags, i.status,
                               COUNT(c.id)::int AS chunk_count
                        FROM innovations AS i
                        LEFT JOIN innovation_chunks AS c ON c.innovation_id = i.id
                        WHERE i.id = %s
                        GROUP BY i.id
                        """,
                        (innovation_id,),
                    )
                    row = cursor.fetchone()
                    if row is None:
                        raise VectorStoreError(
                            f"innovation does not exist: {innovation_id}"
                        )
                    return {
                        "innovation_id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "tags": row[3],
                        "status": row[4],
                        "chunk_count": row[5],
                    }
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError(f"could not read innovation: {error}") from error

    def create_test_innovation(self, innovation_id: str, text: str) -> None:
        if not self.database_url:
            raise VectorStoreError("DATABASE_URL is not configured")

        try:
            import psycopg
        except ImportError as error:
            raise VectorStoreError("psycopg is required to create test innovations") from error

        try:
            with psycopg.connect(self.database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO innovations (id, title, content, summary, status)
                        VALUES (%s, %s, %s, %s, 'published')
                        """,
                        (innovation_id, "Test innovation", text, text[:500]),
                    )
        except Exception as error:
            raise VectorStoreError(
                f"could not create test innovation: {error}"
            ) from error

    def insert_document(
        self,
        *,
        text: str,
        innovation_id: str,
        source: str,
        page: int | None,
        tags: Sequence[str],
        chunks: Sequence[str],
        embeddings: Sequence[Sequence[float]],
    ) -> tuple[str, list[UUID]]:
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
                        "SELECT id FROM innovations WHERE id = %s FOR UPDATE",
                        (innovation_id,),
                    )
                    if cursor.fetchone() is None:
                        raise VectorStoreError(
                            f"innovation does not exist: {innovation_id}"
                        )
                    cursor.execute(
                        "UPDATE innovations SET tags = %s, updated_at = now() WHERE id = %s",
                        (list(tags), innovation_id),
                    )
                    cursor.execute(
                        "DELETE FROM innovation_chunks WHERE innovation_id = %s",
                        (innovation_id,),
                    )
                    child_ids: list[UUID] = []
                    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        cursor.execute(
                            """
                            INSERT INTO innovation_chunks
                                (innovation_id, chunk_index, text, source, page, embedding)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id
                            """,
                            (
                                innovation_id,
                                index,
                                chunk,
                                source,
                                page,
                                _vector_literal(embedding),
                            ),
                        )
                        row = cursor.fetchone()
                        if row is None:
                            raise VectorStoreError("database did not return a child id")
                        child_ids.append(row[0])
                    return innovation_id, child_ids
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError(f"could not store embeddings: {error}") from error

    def search(
        self,
        *,
        query: str,
        embedding: Sequence[float],
        top_k: int,
        search_tests: bool,
        city: str | None,
        title: str | None,
        tags: Sequence[str],
    ) -> list[dict[str, object]]:
        if not self.database_url:
            raise VectorStoreError("DATABASE_URL is not configured")
        top_k = min(top_k, 3)

        try:
            import psycopg
            from pgvector.psycopg import register_vector
        except ImportError as error:
            raise VectorStoreError(
                "psycopg and pgvector are required to search embeddings"
            ) from error

        try:
            with psycopg.connect(self.database_url) as connection:
                register_vector(connection)
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        WITH ranked AS (
                            SELECT
                                i.id AS parent_id,
                                c.id AS child_id,
                                i.title,
                                i.city,
                                i.summary,
                                i.page_url AS parent_url,
                                i.tags,
                                c.source,
                                c.page,
                                c.text,
                                1 - (c.embedding <=> %s::vector) AS vector_score,
                                CASE
                                    WHEN %s <> '' AND i.title ILIKE ('%%' || %s || '%%')
                                    THEN 1.0 ELSE 0.0
                                END AS title_score,
                                CASE
                                    WHEN %s <> '' AND EXISTS (
                                        SELECT 1 FROM unnest(i.tags) AS tag
                                        WHERE tag ILIKE ('%%' || %s || '%%')
                                    )
                                    THEN 1.0 ELSE 0.0
                                END AS tag_score
                            FROM innovation_chunks AS c
                            JOIN innovations AS i ON i.id = c.innovation_id
                                                        WHERE (%s::text IS NULL OR i.city = %s)
                                                            AND (%s::text IS NULL OR i.title ILIKE ('%%' || %s || '%%'))
                              AND (
                                  cardinality(%s::text[]) = 0
                                  OR i.tags && %s::text[]
                              )
                              AND (
                                  NOT %s
                                  OR EXISTS (
                                      SELECT 1 FROM feedback AS f
                                      WHERE f.innovation_id = i.id
                                        AND f.kind = 'test_signup'
                                  )
                              )
                              AND i.status = 'published'
                        )
                        SELECT parent_id, score
                        FROM (
                            SELECT DISTINCT ON (parent_id)
                                parent_id,
                                vector_score + (title_score * 0.2) + (tag_score * 0.2)
                                    AS score
                            FROM ranked
                            ORDER BY parent_id, score DESC
                        ) AS best_matches
                        ORDER BY score DESC
                        LIMIT %s
                        """,
                        (
                            _vector_literal(embedding),
                            query,
                            query,
                            query,
                            query,
                            city,
                            city,
                            title,
                            title,
                            list(tags),
                            list(tags),
                            search_tests,
                            top_k,
                        ),
                    )
                    rows = cursor.fetchall()
                    return [
                        {
                            "innovation_id": row[0],
                        }
                        for row in rows
                    ]
        except Exception as error:
            raise VectorStoreError(f"could not search embeddings: {error}") from error


def get_vector_store() -> PostgresVectorStore:
    return PostgresVectorStore()
