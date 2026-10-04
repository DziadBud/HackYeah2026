import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InnovationLike(Base):
    __tablename__ = "innovation_likes"

    innovation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("innovations.id", ondelete="CASCADE"), primary_key=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
