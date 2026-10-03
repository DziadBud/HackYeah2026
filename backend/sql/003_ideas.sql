CREATE TABLE IF NOT EXISTS ideas (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    summary text NOT NULL,
    essence text NOT NULL,
    target_group text NOT NULL,
    stage text NOT NULL,
    social_canvas jsonb NOT NULL DEFAULT '{}',
    status text NOT NULL DEFAULT 'new',
    innovation_id text REFERENCES innovations(id) ON DELETE SET NULL,
    email text,
    admin_reply text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ideas_status_idx
    ON ideas (status);

CREATE INDEX IF NOT EXISTS ideas_created_at_idx
    ON ideas (created_at DESC);
