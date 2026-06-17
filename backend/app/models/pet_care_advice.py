from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


PET_CARE_ADVICE_STATUS_COMPLETED = "completed"
PET_CARE_ADVICE_STATUS_STALE = "stale"


class PetCareAdvice(Base):
    __tablename__ = "pet_care_advices"
    __table_args__ = (
        UniqueConstraint("post_id", name="uq_pet_care_advices_post_id"),
        Index("ix_pet_care_advices_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    action_plan: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    safety_note: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    hospital_candidates: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PET_CARE_ADVICE_STATUS_COMPLETED,
        server_default=PET_CARE_ADVICE_STATUS_COMPLETED,
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    post: Mapped["Post"] = relationship(back_populates="pet_care_advice")
