CREATE TABLE IF NOT EXISTS grant_calls (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    deadline date NOT NULL,
    open boolean NOT NULL DEFAULT false,
    sections jsonb NOT NULL DEFAULT '[]',
    created_at timestamptz NOT NULL DEFAULT now()
);
