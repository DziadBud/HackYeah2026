CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS innovations (
    id text PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL DEFAULT '',
    summary text NOT NULL DEFAULT '',
    tags text[] NOT NULL DEFAULT '{}',
    city text,
    page_url text,
    status text NOT NULL DEFAULT 'draft',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS innovation_chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    source text NOT NULL,
    page integer,
    text text NOT NULL,
    embedding vector(384) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (innovation_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS innovation_chunks_embedding_idx
ON innovation_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS innovation_chunks_innovation_idx
ON innovation_chunks (innovation_id);

CREATE INDEX IF NOT EXISTS innovations_tags_idx
ON innovations USING gin (tags);

CREATE INDEX IF NOT EXISTS innovations_title_idx
ON innovations USING gin (title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS innovations_city_idx
ON innovations (city);
