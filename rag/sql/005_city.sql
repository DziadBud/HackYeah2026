DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_documents' AND column_name = 'locale'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_documents' AND column_name = 'city'
    ) THEN
        ALTER TABLE rag_documents RENAME COLUMN locale TO city;
    ELSIF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_documents' AND column_name = 'locale'
    ) AND EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_documents' AND column_name = 'city'
    ) THEN
        UPDATE rag_documents
        SET city = locale
        WHERE city = '' AND locale IS NOT NULL;
    ELSIF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_documents' AND column_name = 'city'
    ) THEN
        ALTER TABLE rag_documents ADD COLUMN city text NOT NULL DEFAULT '';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS rag_documents_city_idx
ON rag_documents (city);