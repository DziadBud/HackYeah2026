-- one row per browser that liked an innovation; client_id is a random uuid kept in localStorage
CREATE TABLE IF NOT EXISTS innovation_likes (
    innovation_id text NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    client_id uuid NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (innovation_id, client_id)
);
