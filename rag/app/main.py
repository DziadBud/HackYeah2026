from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.chunking import split_text
from app.services.embedding import EmbeddingService
from app.services.vector_store import get_vector_store


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=3, ge=1, le=3)
    city: str | None = Field(default=None, min_length=1, max_length=200)
    title: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=20)


class QueryResponse(BaseModel):
    query: str
    top_k: int
    matches: list["QueryMatch"]


class QueryMatch(BaseModel):
    parent_id: str
    child_id: str
    title: str
    city: str
    summary: str
    image_url: str | None
    parent_url: str | None
    tags: list[str]
    source: str
    page: int | None
    text: str
    score: float


class EmbedRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    title: str = Field(default="", max_length=500)
    city: str = Field(default="", max_length=200)
    summary: str = Field(default="", max_length=5_000)
    image_url: str | None = Field(default=None, max_length=2_000)
    parent_url: str | None = Field(default=None, max_length=2_000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    source: str = Field(default="api", min_length=1, max_length=500)
    page: int | None = Field(default=None, ge=1)
    chunk_size: int = Field(default=800, ge=100, le=4_000)
    chunk_overlap: int = Field(default=120, ge=0, le=1_000)


class EmbedResponse(BaseModel):
    parent_id: str
    child_ids: list[str]
    child_count: int
    dimensions: int
    title: str
    city: str
    summary: str
    image_url: str | None
    parent_url: str | None
    source: str
    page: int | None


app = FastAPI(title="HackYeah RAG API", version="0.1.0")
embedding_service = EmbeddingService()


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse, tags=["rag"])
def query(request: QueryRequest) -> QueryResponse:
    try:
        query_vector = embedding_service.embed(request.query)
        matches = get_vector_store().search(
            query=request.query,
            embedding=query_vector,
            top_k=request.top_k,
            city=request.city,
            title=request.title,
            tags=request.tags,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return QueryResponse(query=request.query, top_k=request.top_k, matches=matches)


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
            title=request.title,
            city=request.city,
            summary=request.summary,
            image_url=request.image_url,
            parent_url=request.parent_url,
            tags=request.tags,
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
        title=request.title,
        city=request.city,
        summary=request.summary,
        image_url=request.image_url,
        parent_url=request.parent_url,
        source=request.source,
        page=request.page,
    )
