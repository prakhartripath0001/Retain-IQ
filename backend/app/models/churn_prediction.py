from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    __table_args__ = (
        CheckConstraint(
            "churn_probability >= 0 AND churn_probability <= 1",
            name="ck_churn_probability_range",
        ),
        Index(
            "ix_churn_predictions_customer_id",
            "customer_id",
        ),
        Index(
            "ix_churn_predictions_predicted_at",
            "predicted_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    model_version_id: Mapped[int] = mapped_column(
        ForeignKey("model_versions.id"),
        nullable=False,
    )

    churn_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    predicted_churn: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    predicted_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    customer = relationship("Customer")
    model_version = relationship("ModelVersion")