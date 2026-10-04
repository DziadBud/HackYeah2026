import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TestSignup(Base):
    __tablename__ = "test_signups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    innovation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("innovations.id", ondelete="CASCADE"), nullable=False
    )
    # null for direct signups from an innovation page
    problem_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problem_reports.id", ondelete="CASCADE"),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="applied")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    innovation = relationship("Innovation", back_populates="test_signups")
    problem_report = relationship("ProblemReport", back_populates="test_signups")
