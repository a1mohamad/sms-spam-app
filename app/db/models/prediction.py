from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prediction(Base):
    """Represent an encrypted SMS prediction and its request metadata."""

    __tablename__ = "predictions"

    __table_args__ = (
        UniqueConstraint(
            "request_id",
            name="uq_predictions_request_id",
        ),
        CheckConstraint(
            "label IN ('ham', 'spam')",
            name="ck_predictions_label",
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

    # Correlate this row with the API response header and server logs.
    request_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    # Fernet ciphertext is stored; plaintext never reaches PostgreSQL.
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
