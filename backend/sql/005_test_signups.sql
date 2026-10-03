CREATE TABLE IF NOT EXISTS test_signups (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    problem_report_id uuid NOT NULL REFERENCES problem_reports(id) ON DELETE CASCADE,
    email text NOT NULL,
    status text NOT NULL DEFAULT 'applied',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS test_signups_innovation_idx
    ON test_signups (innovation_id);

CREATE INDEX IF NOT EXISTS test_signups_status_idx
    ON test_signups (status);
