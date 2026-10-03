from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from uuid import uuid4

from app.services.chunking import split_text
from app.services.embedding import EmbeddingService
from app.services.pdf import extract_pdf_text
from app.services.tagging import TaggingService
from app.services.answer import AnswerService
from app.services.vector_store import get_vector_store

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=3, ge=1, le=3)
    search_tests: bool = False
    city: str | None = Field(default=None, min_length=1, max_length=200)
    title: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=20)


class QueryResponse(BaseModel):
    query: str
    top_k: int
    answer: str
    matches: list["QueryMatch"]


class QueryMatch(BaseModel):
    innovation_id: str


class QueryTestResponse(BaseModel):
    innovation_id: str
    title: str
    content: str
    tags: list[str]
    status: str
    chunk_count: int


class EmbedRequest(BaseModel):
    innovation_id: str = Field(min_length=1, max_length=100)


class EmbedResponse(BaseModel):
    innovation_id: str
    tags: list[str]
    child_ids: list[str]
    child_count: int
    dimensions: int


class TestEmbedRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


app = FastAPI(title="HackYeah RAG API", version="0.1.0")
embedding_service = EmbeddingService()
tagging_service = TaggingService()
answer_service = AnswerService()


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
            search_tests=request.search_tests,
            city=request.city,
            title=request.title,
            tags=request.tags,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    answer = answer_service.generate(request.query, matches)
    return QueryResponse(
        query=request.query,
        top_k=request.top_k,
        answer=answer,
        matches=matches,
    )


@app.get("/query/test/{innovation_id}", response_model=QueryTestResponse, tags=["rag"])
def query_test(innovation_id: str) -> QueryTestResponse:
    try:
        innovation = get_vector_store().get_innovation(innovation_id)
    except RuntimeError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return QueryTestResponse(**innovation)


@app.post("/embed", response_model=EmbedResponse, status_code=201, tags=["rag"])
def embed(request: EmbedRequest) -> EmbedResponse:
    return _embed_document(request)


@app.post("/embed/test", response_model=EmbedResponse, status_code=201, tags=["rag"])
def embed_test(request: TestEmbedRequest) -> EmbedResponse:
    innovation_id = f"test-{uuid4()}"
    try:
        store = get_vector_store()
        store.create_test_innovation(innovation_id, request.text)
        return _embed_document(
            EmbedRequest(innovation_id=innovation_id),
            text_override=request.text,
            source="test",
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


def _embed_document(
    request: EmbedRequest,
    *,
    text_override: str | None = None,
    source: str = "innovation",
) -> EmbedResponse:
    try:
        store = get_vector_store()
        text = text_override or store.get_content(request.innovation_id)
        chunks = split_text(
            text,
            chunk_size=800,
            chunk_overlap=120,
        )
        tags = tagging_service.generate(text)
        vectors = embedding_service.embed_many(chunks)
        parent_id, child_ids = store.insert_document(
            text=text,
            innovation_id=request.innovation_id,
            source=source,
            page=None,
            tags=tags,
            chunks=chunks,
            embeddings=vectors,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return EmbedResponse(
        innovation_id=parent_id,
        tags=tags,
        child_ids=[str(child_id) for child_id in child_ids],
        child_count=len(child_ids),
        dimensions=len(vectors[0]),
    )


@app.post("/embed/pdf", response_model=EmbedResponse, status_code=201, tags=["rag"])
async def embed_pdf(
    file: UploadFile = File(...),
    innovation_id: str = Form(...),
    source: str | None = Form(default=None),
) -> EmbedResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="file must be a PDF")

    data = await file.read()
    if len(data) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="PDF file is too large")

    try:
        text = extract_pdf_text(data)
        request = EmbedRequest(
            innovation_id=innovation_id,
        )
        return _embed_document(
            request,
            text_override=text,
            source=source or file.filename or "pdf-upload",
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
