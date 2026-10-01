from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class CustomerFeature(Base):
    __tablename__ = "customer_features"

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "feature_date",
            name="uq_customer_feature_date",
        ),
        Index("ix_customer_features_customer_id", "customer_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    recency_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    frequency: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    monetary: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    feature_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    customer = relationship("Customer")