"""Phase 5 schema for Procurement Sources, Opportunities, Monitoring, Amendments, Market Awards, Outcomes, and Knowledge Assets.

Revision ID: 005_phase5_procurement_intelligence
Revises: 004_phase4_auth_models
Create Date: 2026-11-06 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_phase5_procurement_intelligence'
down_revision: Union[str, None] = '004_phase4_auth_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. procurement_sources
    op.create_table(
        'procurement_sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('connector_type', sa.String(length=64), nullable=False),
        sa.Column('endpoint_url', sa.String(length=1024), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('auth_type', sa.String(length=64), server_default='none', nullable=False),
        sa.Column('auth_config', sa.JSON(), nullable=False),
        sa.Column('polling_interval_minutes', sa.Integer(), server_default='60', nullable=False),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=64), server_default='idle', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. connector_runs
    op.create_table(
        'connector_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=64), server_default='running', nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('items_discovered', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_ingested', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('run_log', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['procurement_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. source_opportunities
    op.create_table(
        'source_opportunities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('buyer_name', sa.String(length=255), nullable=False),
        sa.Column('procurement_category', sa.String(length=128), server_default='general', nullable=False),
        sa.Column('estimated_budget', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('published_date', sa.DateTime(), nullable=True),
        sa.Column('submission_deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=64), server_default='open', nullable=False),
        sa.Column('opportunity_url', sa.String(length=1024), nullable=True),
        sa.Column('canonical_summary', sa.Text(), nullable=True),
        sa.Column('raw_payload', sa.JSON(), nullable=False),
        sa.Column('deduplication_hash', sa.String(length=64), nullable=False),
        sa.Column('match_status', sa.String(length=64), server_default='unmatched', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['procurement_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_source_opp_org_hash', 'source_opportunities', ['organization_id', 'deduplication_hash'])
    op.create_index('ix_source_opportunities_deduplication_hash', 'source_opportunities', ['deduplication_hash'])

    # 4. opportunity_matches
    op.create_table(
        'opportunity_matches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('opportunity_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('overall_match_score', sa.Float(), nullable=False),
        sa.Column('recommendation_tier', sa.String(length=64), nullable=False),
        sa.Column('mandatory_gates_passed', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('dimension_scores', sa.JSON(), nullable=False),
        sa.Column('explainability_breakdown', sa.JSON(), nullable=False),
        sa.Column('missing_evidence_requirements', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['source_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. tender_monitor_subscriptions
    op.create_table(
        'tender_monitor_subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('check_frequency_minutes', sa.Integer(), server_default='60', nullable=False),
        sa.Column('last_checked_at', sa.DateTime(), nullable=True),
        sa.Column('last_snapshot_hash', sa.String(length=64), nullable=True),
        sa.Column('notify_channels', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['procurement_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. tender_snapshots
    op.create_table(
        'tender_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('subscription_id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('snapshot_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('raw_content', sa.Text(), nullable=True),
        sa.Column('metadata_payload', sa.JSON(), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['tender_monitor_subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tender_snapshots_content_hash', 'tender_snapshots', ['content_hash'])

    # 7. tender_amendments
    op.create_table(
        'tender_amendments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('amendment_number', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('publication_date', sa.DateTime(), nullable=False),
        sa.Column('materiality', sa.String(length=64), server_default='minor', nullable=False),
        sa.Column('diff_summary', sa.Text(), nullable=False),
        sa.Column('affected_clauses', sa.JSON(), nullable=False),
        sa.Column('downstream_impact', sa.JSON(), nullable=False),
        sa.Column('approval_invalidated', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('acknowledged_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['acknowledged_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. award_records
    op.create_table(
        'award_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('tender_reference', sa.String(length=255), nullable=False),
        sa.Column('buyer_name', sa.String(length=255), nullable=False),
        sa.Column('winning_bidder', sa.String(length=255), nullable=False),
        sa.Column('award_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('award_date', sa.DateTime(), nullable=False),
        sa.Column('procurement_category', sa.String(length=128), server_default='general', nullable=False),
        sa.Column('source_provenance', sa.String(length=512), nullable=False),
        sa.Column('verification_status', sa.String(length=64), server_default='verified', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. competitor_records
    op.create_table(
        'competitor_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('competitor_name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('observed_tenders_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('estimated_win_rate', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('key_strengths', sa.JSON(), nullable=False),
        sa.Column('known_weaknesses', sa.JSON(), nullable=False),
        sa.Column('pricing_strategy_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_competitor_org_name', 'competitor_records', ['organization_id', 'competitor_name'], unique=True)

    # 10. bid_submission_records
    op.create_table(
        'bid_submission_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('lifecycle_stage', sa.String(length=64), server_default='submitted_to_buyer', nullable=False),
        sa.Column('submission_reference', sa.String(length=255), nullable=False),
        sa.Column('submitted_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.Column('final_bid_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('submission_receipt_hash', sa.String(length=64), nullable=False),
        sa.Column('verification_status', sa.String(length=64), server_default='submitted', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submitted_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. bid_outcome_records
    op.create_table(
        'bid_outcome_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('submission_id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('outcome', sa.String(length=64), nullable=False),
        sa.Column('winning_bidder', sa.String(length=255), nullable=True),
        sa.Column('winning_amount', sa.Float(), nullable=True),
        sa.Column('our_score', sa.Float(), nullable=True),
        sa.Column('winning_score', sa.Float(), nullable=True),
        sa.Column('primary_loss_reason', sa.String(length=128), nullable=True),
        sa.Column('debrief_notes', sa.Text(), nullable=True),
        sa.Column('win_factors', sa.JSON(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submission_id'], ['bid_submission_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_id')
    )

    # 12. knowledge_assets
    op.create_table(
        'knowledge_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('category', sa.String(length=128), server_default='technical_approach', nullable=False),
        sa.Column('asset_type', sa.String(length=64), server_default='text', nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('plain_text', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=False),
        sa.Column('author_user_id', sa.String(length=36), nullable=True),
        sa.Column('review_status', sa.String(length=64), server_default='approved', nullable=False),
        sa.Column('approved_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('times_reused', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['author_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. knowledge_asset_versions
    op.create_table(
        'knowledge_asset_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('asset_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), server_default='1', nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('change_summary', sa.String(length=512), nullable=True),
        sa.Column('modified_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['knowledge_assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['modified_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('knowledge_asset_versions')
    op.drop_table('knowledge_assets')
    op.drop_table('bid_outcome_records')
    op.drop_table('bid_submission_records')
    op.drop_index('ix_competitor_org_name', table_name='competitor_records')
    op.drop_table('competitor_records')
    op.drop_table('award_records')
    op.drop_table('tender_amendments')
    op.drop_index('ix_tender_snapshots_content_hash', table_name='tender_snapshots')
    op.drop_table('tender_snapshots')
    op.drop_table('tender_monitor_subscriptions')
    op.drop_table('opportunity_matches')
    op.drop_index('ix_source_opportunities_deduplication_hash', table_name='source_opportunities')
    op.drop_index('ix_source_opp_org_hash', table_name='source_opportunities')
    op.drop_table('source_opportunities')
    op.drop_table('connector_runs')
    op.drop_table('procurement_sources')
