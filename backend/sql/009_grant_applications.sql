-- full ROPS application form (Zał. 3); AI pre-fills 1+3–9, user fills 2, 10–12
CREATE TABLE IF NOT EXISTS grant_applications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id uuid REFERENCES ideas(id) ON DELETE SET NULL,
    grant_call_id uuid REFERENCES grant_calls(id) ON DELETE SET NULL,
    status text NOT NULL DEFAULT 'draft',
    -- 1
    title text NOT NULL DEFAULT '',
    -- 2 Dane pomysłodawcy
    applicant_type text NOT NULL DEFAULT 'person',
    applicant jsonb NOT NULL DEFAULT '{}',
    -- 3–8
    description text NOT NULL DEFAULT '',
    innovativeness text NOT NULL DEFAULT '',
    problem_diagnosis text NOT NULL DEFAULT '',
    beneficiaries text NOT NULL DEFAULT '',
    expected_change text NOT NULL DEFAULT '',
    future_vision text NOT NULL DEFAULT '',
    -- 9 Plan działania i koszty
    action_plan jsonb NOT NULL DEFAULT '{}',
    -- 10
    grant_amount_pln numeric,
    -- 11
    team text NOT NULL DEFAULT '',
    -- 12 Oświadczenia (który wariant + zaznaczenia)
    declarations jsonb NOT NULL DEFAULT '{}',
    email text,
    generated_by text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS grant_applications_idea_idx
    ON grant_applications (idea_id);

CREATE INDEX IF NOT EXISTS grant_applications_call_idx
    ON grant_applications (grant_call_id);

CREATE INDEX IF NOT EXISTS grant_applications_status_idx
    ON grant_applications (status);
