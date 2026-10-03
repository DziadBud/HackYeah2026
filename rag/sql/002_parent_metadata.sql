ALTER TABLE innovations
    ADD COLUMN IF NOT EXISTS title text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS summary text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_url text,
    ADD COLUMN IF NOT EXISTS parent_url text;

CREATE INDEX IF NOT EXISTS innovations_tags_idx
ON innovations USING gin (tags);

CREATE INDEX IF NOT EXISTS innovations_title_idx
ON innovations USING gin (title gin_trgm_ops);
