-- Extend rag innovations with match-api columns (rag ignores them at query time).
ALTER TABLE innovations
    ADD COLUMN IF NOT EXISTS problem text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS innovator text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS challenge_areas text[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS target_group text[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS readiness text,
    ADD COLUMN IF NOT EXISTS cost_level text,
    ADD COLUMN IF NOT EXISTS video_url text;

CREATE INDEX IF NOT EXISTS innovations_challenge_areas_idx
    ON innovations USING gin (challenge_areas);

CREATE INDEX IF NOT EXISTS innovations_status_idx
    ON innovations (status);
