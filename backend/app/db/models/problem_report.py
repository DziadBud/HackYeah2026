import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func, text as sa_text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProblemReport(Base):
    __tablename__ = "problem_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_area: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    support_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    matched_innovation_ids: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=sa_text("'{}'")
    )
    email: Mapped[str | None] = mapped_column(Text)
    admin_reply: Mapped[str | None] = mapped_column(Text)
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    test_signups = relationship("TestSignup", back_populates="problem_report")
