ALTER TABLE innovations
    ADD COLUMN IF NOT EXISTS summary text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS page_url text;