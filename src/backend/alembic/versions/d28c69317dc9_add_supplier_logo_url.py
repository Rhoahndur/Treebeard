"""add_supplier_logo_url

Revision ID: d28c69317dc9
Revises: 003_add_audit_logs
Create Date: 2025-11-11 14:38:06.271417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd28c69317dc9'
down_revision: Union[str, None] = '003_add_audit_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add logo_url column to suppliers table
    op.add_column('suppliers', sa.Column('logo_url', sa.String(500), nullable=True, comment="URL to supplier's logo image"))


def downgrade() -> None:
    # Remove logo_url column from suppliers table
    op.drop_column('suppliers', 'logo_url')
