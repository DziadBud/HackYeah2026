ALTER TABLE innovations
    ADD COLUMN IF NOT EXISTS city text NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS innovations_city_idx
ON innovations (city);