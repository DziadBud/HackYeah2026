CREATE TABLE IF NOT EXISTS innovation_chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    source text NOT NULL,
    page integer,
    text text NOT NULL,
    embedding vector(384) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (innovation_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS innovation_chunks_innovation_idx
ON innovation_chunks (innovation_id);

-- feedback is owned by rag (rag /query reads kind='test_signup'), written by match-api
CREATE TABLE IF NOT EXISTS feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    kind text NOT NULL CHECK (kind IN ('rating', 'test_signup')),
    rating integer CHECK (rating IS NULL OR rating BETWEEN 1 AND 5),
    comment text,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- older match-api shape had stars + test_signup_id and no kind; bring it in line
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'feedback' AND column_name = 'stars'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'feedback' AND column_name = 'rating'
    ) THEN
        ALTER TABLE feedback RENAME COLUMN stars TO rating;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'feedback' AND column_name = 'kind'
    ) THEN
        ALTER TABLE feedback ADD COLUMN kind text;
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'feedback' AND column_name = 'test_signup_id'
        ) THEN
            UPDATE feedback
            SET kind = CASE
                WHEN test_signup_id IS NOT NULL THEN 'test_signup'
                ELSE 'rating'
            END
            WHERE kind IS NULL;
        ELSE
            UPDATE feedback SET kind = 'rating' WHERE kind IS NULL;
        END IF;
        ALTER TABLE feedback ALTER COLUMN kind SET NOT NULL;
        ALTER TABLE feedback
            ADD CONSTRAINT feedback_kind_check CHECK (kind IN ('rating', 'test_signup'));
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'feedback' AND column_name = 'test_signup_id'
    ) THEN
        ALTER TABLE feedback DROP COLUMN test_signup_id;
    END IF;

    -- old stars check may linger after rename
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'feedback_stars_check' AND conrelid = 'feedback'::regclass
    ) THEN
        ALTER TABLE feedback DROP CONSTRAINT feedback_stars_check;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'feedback_rating_check' AND conrelid = 'feedback'::regclass
    ) THEN
        ALTER TABLE feedback
            ADD CONSTRAINT feedback_rating_check
            CHECK (rating IS NULL OR rating BETWEEN 1 AND 5);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS feedback_innovation_kind_idx
ON feedback (innovation_id, kind);
