CREATE TABLE IF NOT EXISTS rag_documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source text NOT NULL,
    page integer,
    text text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id uuid NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    source text NOT NULL,
    page integer,
    text text NOT NULL,
    embedding vector(384) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (parent_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS rag_chunks_embedding_idx
ON rag_chunks USING hnsw (embedding vector_cosine_ops);