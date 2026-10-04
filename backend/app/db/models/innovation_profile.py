from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func, text as sa_text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InnovationProfile(Base):
    """description sections rag's innovations table has no columns for (backend/sql/009)"""

    __tablename__ = "innovation_profiles"

    innovation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("innovations.id", ondelete="CASCADE"), primary_key=True
    )
    tagline: Mapped[str | None] = mapped_column(Text)
    program: Mapped[str | None] = mapped_column(Text)
    problem: Mapped[str | None] = mapped_column(Text)
    target_group: Mapped[str | None] = mapped_column(Text)
    who_can_use: Mapped[str | None] = mapped_column(Text)
    effectiveness: Mapped[str | None] = mapped_column(Text)
    authors: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=sa_text("'{}'"))
    # file names in seed_media/<innovation_id>/
    photos: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=sa_text("'{}'"))
    license_name: Mapped[str | None] = mapped_column(Text)
    license_url: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
