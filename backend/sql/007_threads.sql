CREATE TABLE IF NOT EXISTS threads (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    title text NOT NULL,
    body text NOT NULL,
    author_label text NOT NULL,
    email text,
    status text NOT NULL DEFAULT 'pending',
    helpful_count integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS threads_innovation_idx
    ON threads (innovation_id);

CREATE INDEX IF NOT EXISTS threads_status_idx
    ON threads (status);
