from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "assigned_at",
            name="uq_customer_segment_assignment",
        ),
        Index("ix_customer_segments_name", "segment_name"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    segment_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    cluster_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    customer = relationship("Customer")