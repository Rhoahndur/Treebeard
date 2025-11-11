"""Add authentication and admin fields to users table

Revision ID: 002_add_user_auth_fields
Revises: 001_initial_schema
Create Date: 2025-11-10 16:00:00.000000

This migration adds authentication and role management fields to users table:
- hashed_password: For password-based authentication
- is_active: For soft delete and account status tracking
- is_admin: For role-based access control (RBAC)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_user_auth_fields'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add authentication and admin fields to users table."""

    # Add new columns to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

    # Create indexes for new fields
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_is_admin', 'users', ['is_admin'])

    # Make hashed_password not nullable after adding default
    # (This allows existing records to get a placeholder value)
    op.execute("UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL")
    op.alter_column('users', 'hashed_password', nullable=False)


def downgrade() -> None:
    """Remove authentication and admin fields from users table."""

    # Drop indexes
    op.drop_index('idx_users_is_admin', 'users')
    op.drop_index('idx_users_is_active', 'users')

    # Drop columns
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'hashed_password')
