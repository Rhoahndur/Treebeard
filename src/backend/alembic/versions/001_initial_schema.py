"""Initial database schema with all tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-10 15:00:00.000000

This migration creates all tables for the TreeBeard Energy Recommendation System:
1. Users and related tables (users, user_preferences, current_plans)
2. Usage tracking (usage_history)
3. Plan catalog (suppliers, plan_catalog)
4. Recommendations (recommendations, recommendation_plans)
5. Feedback (feedback)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all database tables and indexes."""

    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('customer_service_phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_name'),
        comment='Energy suppliers with ratings and contact information'
    )
    op.create_index('idx_suppliers_active', 'suppliers', ['is_active'])
    op.create_index('idx_suppliers_name', 'suppliers', ['supplier_name'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('zip_code', sa.String(length=10), nullable=False),
        sa.Column('property_type', sa.String(length=50), nullable=False),
        sa.Column('consent_given', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        comment='User profiles with basic information and consent tracking'
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_zip_code', 'users', ['zip_code'])

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cost_priority', sa.Integer(), nullable=False, server_default='40'),
        sa.Column('flexibility_priority', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('renewable_priority', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('rating_priority', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        comment='User preferences for plan recommendation algorithm weighting'
    )
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])

    # Create current_plans table
    op.create_table(
        'current_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('plan_name', sa.String(length=255), nullable=True),
        sa.Column('current_rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('contract_start_date', sa.Date(), nullable=True),
        sa.Column('contract_end_date', sa.Date(), nullable=False),
        sa.Column('early_termination_fee', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('monthly_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        comment="User's current energy plan details for comparison"
    )
    op.create_index('idx_current_plans_contract_end_date', 'current_plans', ['contract_end_date'])
    op.create_index('idx_current_plans_user_id', 'current_plans', ['user_id'])

    # Create usage_history table
    op.create_table(
        'usage_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('kwh_consumed', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('data_source', sa.String(length=50), nullable=False, server_default='upload'),
        sa.Column('data_quality', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Daily energy usage history for pattern analysis and projections'
    )
    op.create_index('idx_usage_history_date', 'usage_history', ['usage_date'])
    op.create_index('idx_usage_history_user_date', 'usage_history', ['user_id', 'usage_date'])
    op.create_index('idx_usage_history_unique_user_date', 'usage_history', ['user_id', 'usage_date'], unique=True)

    # Create plan_catalog table
    op.create_table(
        'plan_catalog',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_name', sa.String(length=255), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('rate_structure', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('contract_length_months', sa.Integer(), nullable=False),
        sa.Column('early_termination_fee', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('renewable_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('monthly_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('connection_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('available_regions', postgresql.ARRAY(sa.String(length=10)), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('plan_description', sa.Text(), nullable=True),
        sa.Column('terms_url', sa.String(length=500), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Energy plan catalog with all attributes for matching and recommendations'
    )
    op.create_index('idx_plan_catalog_regions', 'plan_catalog', ['available_regions'], postgresql_using='gin')
    op.create_index('idx_plan_catalog_renewable', 'plan_catalog', ['renewable_percentage'])
    op.create_index('idx_plan_catalog_supplier_active', 'plan_catalog', ['supplier_id', 'is_active'])
    op.create_index('idx_plan_catalog_type_length', 'plan_catalog', ['plan_type', 'contract_length_months'])

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usage_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('algorithm_version', sa.Text(), nullable=False, server_default='1.0.0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Recommendation sessions with usage profile context'
    )
    op.create_index('idx_recommendations_expires', 'recommendations', ['expires_at'])
    op.create_index('idx_recommendations_user_generated', 'recommendations', ['user_id', 'generated_at'])

    # Create recommendation_plans table
    op.create_table(
        'recommendation_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('composite_score', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('cost_score', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('flexibility_score', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('renewable_score', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('rating_score', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('projected_annual_cost', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('projected_annual_savings', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('break_even_months', sa.Integer(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('risk_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plan_catalog.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Top 3 recommended plans per recommendation with scoring and explanations'
    )
    op.create_index('idx_recommendation_plans_plan', 'recommendation_plans', ['plan_id'])
    op.create_index('idx_recommendation_plans_rec_rank', 'recommendation_plans', ['recommendation_id', 'rank'])
    op.create_index('idx_recommendation_plans_unique_rec_rank', 'recommendation_plans', ['recommendation_id', 'rank'], unique=True)

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommended_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('feedback_type', sa.String(length=50), nullable=False),
        sa.Column('sentiment_score', sa.Numeric(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plan_catalog.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommended_plan_id'], ['recommendation_plans.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='User feedback on recommendations for quality tracking and improvement'
    )
    op.create_index('idx_feedback_plan', 'feedback', ['plan_id'])
    op.create_index('idx_feedback_rating', 'feedback', ['rating'])
    op.create_index('idx_feedback_recommendation', 'feedback', ['recommendation_id', 'created_at'])
    op.create_index('idx_feedback_user_created', 'feedback', ['user_id', 'created_at'])


def downgrade() -> None:
    """Drop all tables in reverse order."""

    op.drop_table('feedback')
    op.drop_table('recommendation_plans')
    op.drop_table('recommendations')
    op.drop_table('plan_catalog')
    op.drop_table('usage_history')
    op.drop_table('current_plans')
    op.drop_table('user_preferences')
    op.drop_table('users')
    op.drop_table('suppliers')
