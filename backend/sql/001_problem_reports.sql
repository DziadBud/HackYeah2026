CREATE TABLE IF NOT EXISTS problem_reports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    text text NOT NULL,
    challenge_area text,
    city text NOT NULL,
    support_count integer NOT NULL DEFAULT 0,
    matched_innovation_ids text[] NOT NULL DEFAULT '{}',
    email text,
    admin_reply text,
    hidden boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS problem_reports_city_idx
    ON problem_reports (city);

CREATE INDEX IF NOT EXISTS problem_reports_challenge_area_idx
    ON problem_reports (challenge_area);

CREATE INDEX IF NOT EXISTS problem_reports_created_at_idx
    ON problem_reports (created_at DESC);

CREATE INDEX IF NOT EXISTS problem_reports_text_trgm_idx
    ON problem_reports USING gin (text gin_trgm_ops);
