"""Phase 4 schema for Users, Authentication, Sessions, and Organization Members.

Revision ID: 004_phase4_auth_models
Revises: 003_phase3_models
Create Date: 2026-11-05 19:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_phase4_auth_models'
down_revision: Union[str, None] = '003_phase3_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=64), server_default='Author', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Organization Members
    op.create_table(
        'organization_members',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=64), server_default='Author', nullable=False),
        sa.Column('invited_by', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_org_members_org_user', 'organization_members', ['organization_id', 'user_id'], unique=True)

    # 3. Password Reset Tokens
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'], unique=False)

    # 4. User Sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sessions_token_hash', 'user_sessions', ['token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_sessions_token_hash', table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_index('ix_password_reset_tokens_token_hash', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('ix_org_members_org_user', table_name='organization_members')
    op.drop_table('organization_members')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
