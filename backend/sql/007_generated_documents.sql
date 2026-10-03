CREATE TABLE IF NOT EXISTS generated_documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kind text NOT NULL,
    innovation_id text REFERENCES innovations(id) ON DELETE SET NULL,
    idea_id uuid REFERENCES ideas(id) ON DELETE SET NULL,
    grant_call_id uuid REFERENCES grant_calls(id) ON DELETE SET NULL,
    input jsonb NOT NULL DEFAULT '{}',
    output text NOT NULL,
    email text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS generated_documents_kind_idx
    ON generated_documents (kind);

CREATE INDEX IF NOT EXISTS generated_documents_innovation_idx
    ON generated_documents (innovation_id);
