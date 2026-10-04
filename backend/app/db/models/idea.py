import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    essence: Mapped[str] = mapped_column(Text, nullable=False)
    target_group: Mapped[str] = mapped_column(Text, nullable=False)
    stage: Mapped[str] = mapped_column(Text, nullable=False)
    social_canvas: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="new")
    innovation_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("innovations.id", ondelete="SET NULL")
    )
    email: Mapped[str | None] = mapped_column(Text)
    admin_reply: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    innovation = relationship("Innovation")
    generated_documents = relationship("GeneratedDocument", back_populates="idea")
    grant_applications = relationship("GrantApplication", back_populates="idea")
