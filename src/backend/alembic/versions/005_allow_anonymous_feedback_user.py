"""Allow feedback without an authenticated user or recommendation

Revision ID: 005_allow_anonymous_feedback_user
Revises: 004_add_recommendation_result_payload
Create Date: 2026-04-26 12:10:00.000000
"""

from collections.abc import Sequence

from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_allow_anonymous_feedback_user"
down_revision: str | None = "004_add_recommendation_result_payload"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("feedback_user_id_fkey", "feedback", type_="foreignkey")
    op.alter_column("feedback", "user_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_foreign_key(
        "feedback_user_id_fkey",
        "feedback",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint("feedback_recommendation_id_fkey", "feedback", type_="foreignkey")
    op.alter_column("feedback", "recommendation_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_foreign_key(
        "feedback_recommendation_id_fkey",
        "feedback",
        "recommendations",
        ["recommendation_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("feedback_recommendation_id_fkey", "feedback", type_="foreignkey")
    op.alter_column("feedback", "recommendation_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        "feedback_recommendation_id_fkey",
        "feedback",
        "recommendations",
        ["recommendation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("feedback_user_id_fkey", "feedback", type_="foreignkey")
    op.alter_column("feedback", "user_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        "feedback_user_id_fkey",
        "feedback",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
