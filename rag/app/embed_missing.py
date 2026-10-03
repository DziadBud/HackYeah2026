"""Embed published innovations that have no chunks yet (seeded rows).

Run by the compose `seed-embed` one-shot after rag is healthy. Calls rag's own
POST /embed, retrying while the embeddings container is still loading its model.
"""

import os
import sys
import time

import httpx
import psycopg

RAG_URL = os.getenv("RAG_URL", "http://rag:8000")
ATTEMPTS = 30
RETRY_SECONDS = 10


def missing_ids(database_url: str) -> list[str]:
    with psycopg.connect(database_url) as connection:
        rows = connection.execute(
            """
            SELECT i.id FROM innovations i
            WHERE i.status = 'published' AND i.content <> ''
              AND NOT EXISTS (SELECT 1 FROM innovation_chunks c WHERE c.innovation_id = i.id)
            ORDER BY i.id
            """
        ).fetchall()
    return [row[0] for row in rows]


def embed(innovation_id: str) -> None:
    for attempt in range(1, ATTEMPTS + 1):
        response = httpx.post(
            f"{RAG_URL}/embed", json={"innovation_id": innovation_id}, timeout=120.0
        )
        if response.status_code == 201:
            print(f"embedded {innovation_id}: {response.json()['child_count']} chunks")
            return
        # 503 = embeddings container not ready yet
        if response.status_code != 503 or attempt == ATTEMPTS:
            raise RuntimeError(f"{innovation_id}: {response.status_code} {response.text}")
        print(f"{innovation_id}: embeddings not ready, retry {attempt}/{ATTEMPTS}")
        time.sleep(RETRY_SECONDS)


def main() -> int:
    ids = missing_ids(os.environ["DATABASE_URL"])
    print(f"{len(ids)} innovation(s) without chunks")
    for innovation_id in ids:
        embed(innovation_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
