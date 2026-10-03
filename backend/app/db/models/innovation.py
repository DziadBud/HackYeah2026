from datetime import datetime

from sqlalchemy import DateTime, Text, func, text as sa_text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Innovation(Base):
    """Shared with rag. match-api owns CRUD; rag owns chunks + retrieval filters."""

    __tablename__ = "innovations"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    problem: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    innovator: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    challenge_areas: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=sa_text("'{}'")
    )
    target_group: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=sa_text("'{}'")
    )
    readiness: Mapped[str | None] = mapped_column(Text)
    cost_level: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=sa_text("'{}'")
    )
    city: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    page_url: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    test_signups = relationship("TestSignup", back_populates="innovation")
    feedback_items = relationship("Feedback", back_populates="innovation")
    threads = relationship("Thread", back_populates="innovation")
    generated_documents = relationship("GeneratedDocument", back_populates="innovation")
