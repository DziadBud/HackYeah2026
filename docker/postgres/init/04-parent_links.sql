ALTER TABLE innovations
    ADD COLUMN IF NOT EXISTS summary text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_url text,
    ADD COLUMN IF NOT EXISTS parent_url text;