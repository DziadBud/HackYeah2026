CREATE TABLE IF NOT EXISTS thread_replies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id uuid NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    body text NOT NULL,
    author_label text NOT NULL,
    email text,
    kind text NOT NULL DEFAULT 'practitioner',
    status text NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS thread_replies_thread_idx
    ON thread_replies (thread_id);

CREATE INDEX IF NOT EXISTS thread_replies_status_idx
    ON thread_replies (status);
