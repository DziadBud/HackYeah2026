DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'innovations' AND column_name = 'locale'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'innovations' AND column_name = 'city'
    ) THEN
        ALTER TABLE innovations RENAME COLUMN locale TO city;
    ELSIF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'innovations' AND column_name = 'locale'
    ) AND EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'innovations' AND column_name = 'city'
    ) THEN
        UPDATE innovations
        SET city = locale
        WHERE city = '' AND locale IS NOT NULL;
    ELSIF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'innovations' AND column_name = 'city'
    ) THEN
        ALTER TABLE innovations ADD COLUMN city text NOT NULL DEFAULT '';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS innovations_city_idx
ON innovations (city);