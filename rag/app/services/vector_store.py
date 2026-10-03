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
        innovation_id: str,
        source: str,
        page: int | None,
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
                                list(embedding),
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
                                i.id AS innovation_id,
                                c.id AS child_id,
                                i.title,
                                i.city,
                                i.summary,
                                i.image_url,
                                i.page_url AS parent_url,
                                i.tags,
                                c.source,
                                c.page,
                                c.text,
                                1 - (c.embedding <=> %s) AS vector_score,
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
                            WHERE (%s IS NULL OR i.city = %s)
                              AND (%s IS NULL OR i.title ILIKE ('%%' || %s || '%%'))
                              AND (
                                  cardinality(%s::text[]) = 0
                                  OR i.tags && %s::text[]
                              )
                              AND i.status = 'published'
                        )
                        SELECT innovation_id, child_id, title, city, summary,
                               image_url, parent_url, tags, source, page, text, score
                        FROM (
                            SELECT DISTINCT ON (innovation_id)
                                innovation_id, child_id, title, city, summary,
                                image_url, parent_url, tags, source, page, text,
                                vector_score + (title_score * 0.2) + (tag_score * 0.2)
                                    AS score
                            FROM ranked
                            ORDER BY innovation_id, score DESC
                        ) AS best_matches
                        ORDER BY score DESC
                        LIMIT %s
                        """,
                        (
                            list(embedding),
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
                            top_k,
                        ),
                    )
                    rows = cursor.fetchall()
                    return [
                        {
                            "parent_id": row[0],
                            "child_id": row[1],
                            "innovation_id": row[0],
                            "title": row[2],
                            "city": row[3],
                            "summary": row[4],
                            "image_url": row[5],
                            "parent_url": row[6],
                            "tags": row[7],
                            "source": row[8],
                            "page": row[9],
                            "text": row[10],
                            "score": float(row[11]),
                        }
                        for row in rows
                    ]
        except Exception as error:
            raise VectorStoreError(f"could not search embeddings: {error}") from error


def get_vector_store() -> PostgresVectorStore:
    return PostgresVectorStore()
