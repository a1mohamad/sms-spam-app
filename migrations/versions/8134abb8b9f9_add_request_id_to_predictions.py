"""Add a unique request correlation ID to predictions.

Revision ID: 8134abb8b9f9
Revises: 49cce5d5863f
Create Date: 2026-07-20 23:00:14.689924

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8134abb8b9f9"
down_revision: str | Sequence[str] | None = "49cce5d5863f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the required request ID and enforce one row per request."""
    op.add_column(
        "predictions",
        sa.Column("request_id", sa.Uuid(), nullable=False),
    )
    op.create_unique_constraint(
        "uq_predictions_request_id",
        "predictions",
        ["request_id"],
    )


def downgrade() -> None:
    """Remove the request ID constraint and column."""
    op.drop_constraint(
        "uq_predictions_request_id",
        "predictions",
        type_="unique",
    )
    op.drop_column("predictions", "request_id")
