"""Add audit_logs table for tracking admin actions

Revision ID: 003_add_audit_logs
Revises: 002_add_user_auth_fields
Create Date: 2025-11-10 16:30:00.000000

This migration creates the audit_logs table for tracking all administrative
actions and system events. The table is append-only (no updates or deletes)
to ensure tamper-proof audit trail for compliance and security.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_audit_logs'
down_revision: Union[str, None] = '002_add_user_auth_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table with indexes."""

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('admin_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Audit log for tracking admin actions and system events (append-only)'
    )

    # Create indexes for efficient querying
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_admin_user', 'audit_logs', ['admin_user_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('idx_audit_logs_resource_id', 'audit_logs', ['resource_id'])

    # Composite indexes for common query patterns
    op.create_index('idx_audit_logs_admin_timestamp', 'audit_logs', ['admin_user_id', 'timestamp'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    """Drop audit_logs table and all its indexes."""

    # Drop indexes (will be dropped automatically with table, but explicit for clarity)
    op.drop_index('idx_audit_logs_resource', 'audit_logs')
    op.drop_index('idx_audit_logs_admin_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_resource_id', 'audit_logs')
    op.drop_index('idx_audit_logs_resource_type', 'audit_logs')
    op.drop_index('idx_audit_logs_action', 'audit_logs')
    op.drop_index('idx_audit_logs_admin_user', 'audit_logs')
    op.drop_index('idx_audit_logs_timestamp', 'audit_logs')

    # Drop table
    op.drop_table('audit_logs')
