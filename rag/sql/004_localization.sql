ALTER TABLE rag_documents
    ADD COLUMN IF NOT EXISTS city text NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS rag_documents_city_idx
ON rag_documents (city);