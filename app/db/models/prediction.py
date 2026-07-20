from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    LargeBinary,
    String,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prediction(Base):
    """Represent a stored SMS classification result."""
    __tablename__ = "predictions"

    __table_args__ = (
        CheckConstraint(
            "label IN ('ham', 'spam')",
            name="ck_predictions_name",
        ),
        CheckConstraint(
            "spam_probability BETWEEN 0 AND 1",
            name="ck_predictions_spam_probability",
        ),
        CheckConstraint(
            "threshold BETWEEN 0 AND 1",
            name="ck_predictions_threshold",
        ),
        CheckConstraint(
            "message_length > 0",
            name="ck_predictions_message_length",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    message_ciphertext: Mapped[bytes] = mapped_column(
        LargeBinary, 
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
    )

    spam_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    message_length: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Use PostgreSQL's clock instead of the application server's clock.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )