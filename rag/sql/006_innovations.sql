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

CREATE INDEX IF NOT EXISTS innovation_chunks_innovation_idx
ON innovation_chunks (innovation_id);

CREATE TABLE IF NOT EXISTS feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    kind text NOT NULL CHECK (kind IN ('rating', 'test_signup')),
    rating integer CHECK (rating IS NULL OR rating BETWEEN 1 AND 5),
    comment text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS feedback_innovation_kind_idx
ON feedback (innovation_id, kind);