"""Add serialized recommendation result payload

Revision ID: 004_add_recommendation_result_payload
Revises: d28c69317dc9
Create Date: 2026-04-26 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_add_recommendation_result_payload"
down_revision: str | None = "d28c69317dc9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "recommendations",
        sa.Column(
            "result_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Serialized API response payload for refreshable MVP results pages",
        ),
    )


def downgrade() -> None:
    op.drop_column("recommendations", "result_payload")
