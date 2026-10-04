-- full ROPS Zał. 3 form. API always returns complete shape for FE editing.
-- AI pre-fills 1+3–9; user fills/edits 2, 10–12 (and may edit AI text).
-- applicant jsonb: PersonApplicant | OrganizationApplicant | InformalGroupApplicant
-- declarations jsonb: PersonDeclarations | OrganizationDeclarations (per-checkbox bools)
CREATE TABLE IF NOT EXISTS grant_applications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id uuid REFERENCES ideas(id) ON DELETE SET NULL,
    grant_call_id uuid REFERENCES grant_calls(id) ON DELETE SET NULL,
    status text NOT NULL DEFAULT 'draft',
    title text NOT NULL DEFAULT '',
    applicant_type text NOT NULL DEFAULT 'person',
    applicant jsonb NOT NULL DEFAULT '{}',
    description text NOT NULL DEFAULT '',
    innovativeness text NOT NULL DEFAULT '',
    problem_diagnosis text NOT NULL DEFAULT '',
    beneficiaries text NOT NULL DEFAULT '',
    expected_change text NOT NULL DEFAULT '',
    future_vision text NOT NULL DEFAULT '',
    action_plan jsonb NOT NULL DEFAULT '{}',
    grant_amount_pln numeric,
    team text NOT NULL DEFAULT '',
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
