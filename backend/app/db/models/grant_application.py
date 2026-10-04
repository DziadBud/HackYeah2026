import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GrantApplication(Base):
    __tablename__ = "grant_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    idea_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="SET NULL")
    )
    grant_call_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grant_calls.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    title: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    applicant_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="person")
    applicant: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    innovativeness: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    problem_diagnosis: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    beneficiaries: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    expected_change: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    future_vision: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    action_plan: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    grant_amount_pln: Mapped[Decimal | None] = mapped_column(Numeric)
    team: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    declarations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    email: Mapped[str | None] = mapped_column(Text)
    generated_by: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    idea = relationship("Idea", back_populates="grant_applications")
    grant_call = relationship("GrantCall", back_populates="grant_applications")
