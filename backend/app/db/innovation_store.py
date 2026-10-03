from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.services.admin.innovation_upload import NewInnovation


# innovations is owned by rag (rag/sql); match-api only writes rows, never the schema
class SqlInnovationStore:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None:
        with self._sessions.begin() as db:
            db.execute(
                text(
                    """
                    INSERT INTO innovations
                        (id, title, summary, tags, city, image_url, page_url, parent_url, status)
                    VALUES
                        (:id, :title, :summary, :tags, :city, :image_url, :page_url, :page_url, 'draft')
                    """
                ),
                {
                    "id": innovation_id,
                    "title": data.title,
                    "summary": data.summary,
                    "tags": tags,
                    # rag's /query returns city as str, a null breaks it
                    "city": data.city or "",
                    "image_url": data.image_url,
                    "page_url": data.page_url,
                },
            )

    def delete(self, innovation_id: str) -> None:
        with self._sessions.begin() as db:
            db.execute(text("DELETE FROM innovations WHERE id = :id"), {"id": innovation_id})
