import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Feedback(Base):
    """rag owns this table (rag/sql/006); rag /query reads kind='test_signup'."""

    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    innovation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("innovations.id", ondelete="CASCADE"), nullable=False
    )
    # 'rating' | 'test_signup'
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    # api calls it stars; rag's column is rating (nullable there, always set by match-api)
    stars: Mapped[int] = mapped_column("rating", Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    innovation = relationship("Innovation", back_populates="feedback_items")
