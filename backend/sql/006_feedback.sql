CREATE TABLE IF NOT EXISTS feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    test_signup_id uuid REFERENCES test_signups(id) ON DELETE SET NULL,
    stars integer NOT NULL CHECK (stars >= 1 AND stars <= 5),
    comment text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS feedback_innovation_idx
    ON feedback (innovation_id);
