from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    __table_args__ = (
        UniqueConstraint(
            "model_name",
            "version",
            name="uq_model_name_version",
        ),
        Index("ix_model_versions_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    algorithm: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    metrics: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )