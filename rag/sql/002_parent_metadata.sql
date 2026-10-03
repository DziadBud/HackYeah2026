ALTER TABLE rag_documents
    ADD COLUMN IF NOT EXISTS title text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS summary text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_url text,
    ADD COLUMN IF NOT EXISTS parent_url text;

CREATE INDEX IF NOT EXISTS rag_documents_tags_idx
ON rag_documents USING gin (tags);

CREATE INDEX IF NOT EXISTS rag_documents_title_idx
ON rag_documents USING gin (title gin_trgm_ops);
