import os
from uuid import uuid4

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_RAG_INTEGRATION") != "1",
    reason="set RUN_RAG_INTEGRATION=1 to run against the Compose services",
)

RAG_URL = os.getenv("RAG_URL", "http://localhost:8001")


def test_embedded_text_is_returned_by_semantic_query() -> None:
    marker = f"opieka domowa seniorów w gminie {uuid4()}"
    embed_response = httpx.post(
        f"{RAG_URL}/embed/test",
        json={"text": f"Program zapewnia {marker} oraz pomoc w codziennych zakupach."},
        timeout=180.0,
    )
    assert embed_response.status_code == 201, embed_response.text
    innovation_id = embed_response.json()["innovation_id"]

    stored_response = httpx.get(
        f"{RAG_URL}/query/test/{innovation_id}",
        timeout=30.0,
    )
    assert stored_response.status_code == 200, stored_response.text
    assert marker in stored_response.json()["content"]

    query_response = httpx.post(
        f"{RAG_URL}/query",
        json={"query": marker, "top_k": 3},
        timeout=180.0,
    )
    assert query_response.status_code == 200, query_response.text
    matches = query_response.json()["matches"]
    assert innovation_id in [match["innovation_id"] for match in matches]
