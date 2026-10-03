from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.chunking import split_text
from app.services.embedding import EmbeddingService
from app.services.vector_store import get_vector_store


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    query: str
    top_k: int
    matches: list[dict[str, object]]


class EmbedRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    source: str = Field(default="api", min_length=1, max_length=500)
    page: int | None = Field(default=None, ge=1)
    chunk_size: int = Field(default=800, ge=100, le=4_000)
    chunk_overlap: int = Field(default=120, ge=0, le=1_000)


class EmbedResponse(BaseModel):
    parent_id: str
    child_ids: list[str]
    child_count: int
    dimensions: int
    source: str
    page: int | None


app = FastAPI(title="HackYeah RAG API", version="0.1.0")
embedding_service = EmbeddingService()


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse, tags=["rag"])
def query(request: QueryRequest) -> QueryResponse:
    return QueryResponse(query=request.query, top_k=request.top_k, matches=[])


@app.post("/embed", response_model=EmbedResponse, status_code=201, tags=["rag"])
def embed(request: EmbedRequest) -> EmbedResponse:
    try:
        chunks = split_text(
            request.text,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        vectors = embedding_service.embed_many(chunks)
        parent_id, child_ids = get_vector_store().insert_document(
            text=request.text,
            source=request.source,
            page=request.page,
            chunks=chunks,
            embeddings=vectors,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return EmbedResponse(
        parent_id=str(parent_id),
        child_ids=[str(child_id) for child_id in child_ids],
        child_count=len(child_ids),
        dimensions=len(vectors[0]),
        source=request.source,
        page=request.page,
    )
