"""Phase 3 schema for Bid Intelligence, Advanced ProofLink, Financial Workspace, Evaluation Criteria, Proposal Optimization, Bid Risks, Deadlines, and RBAC.

Revision ID: 003_phase3_models
Revises: 002_phase2_models
Create Date: 2026-11-05 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_phase3_models'
down_revision: Union[str, None] = '002_phase2_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Bid Evaluations
    op.create_table(
        'bid_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('evaluator_type', sa.String(length=32), nullable=False),
        sa.Column('evaluator_id', sa.String(length=128), nullable=False),
        sa.Column('dimensions', sa.JSON(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('eligibility_gates_passed', sa.Boolean(), nullable=False),
        sa.Column('failed_gates', sa.JSON(), nullable=False),
        sa.Column('recommendation', sa.String(length=64), nullable=False),
        sa.Column('conditions', sa.JSON(), nullable=False),
        sa.Column('executive_summary', sa.Text(), nullable=False),
        sa.Column('human_decision', sa.String(length=32), nullable=False),
        sa.Column('human_decision_by', sa.String(length=128), nullable=True),
        sa.Column('human_decision_rationale', sa.Text(), nullable=True),
        sa.Column('human_decision_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Evidence Contradictions
    op.create_table(
        'evidence_contradictions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id_1', sa.String(length=36), nullable=False),
        sa.Column('evidence_id_2', sa.String(length=36), nullable=True),
        sa.Column('claim_field', sa.String(length=128), nullable=False),
        sa.Column('value_1', sa.Text(), nullable=False),
        sa.Column('value_2', sa.Text(), nullable=False),
        sa.Column('contradiction_severity', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.String(length=128), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id_1'], ['company_evidence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id_2'], ['company_evidence.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Claim Lineages
    op.create_table(
        'claim_lineages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=True),
        sa.Column('requirement_id', sa.String(length=36), nullable=True),
        sa.Column('evidence_id', sa.String(length=36), nullable=True),
        sa.Column('section_number', sa.String(length=32), nullable=True),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('evidence_extract', sa.Text(), nullable=False),
        sa.Column('review_status', sa.String(length=32), nullable=False),
        sa.Column('auditor_verdict', sa.String(length=64), nullable=True),
        sa.Column('approval_status', sa.String(length=32), nullable=False),
        sa.Column('lineage_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requirement_id'], ['tender_requirements.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['evidence_id'], ['company_evidence.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_claim_lineage_tender_req', 'claim_lineages', ['tender_id', 'requirement_id'])

    # 4. Evaluation Criteria
    op.create_table(
        'evaluation_criteria',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('criterion_code', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('weight_percentage', sa.Float(), nullable=False),
        sa.Column('max_marks', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scoring_rules', sa.JSON(), nullable=False),
        sa.Column('mandatory', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Proposal Optimizations
    op.create_table(
        'proposal_optimizations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('criterion_id', sa.String(length=36), nullable=True),
        sa.Column('section_number', sa.String(length=32), nullable=True),
        sa.Column('coverage_status', sa.String(length=32), nullable=False),
        sa.Column('gap_analysis', sa.Text(), nullable=False),
        sa.Column('current_score_estimate', sa.Float(), nullable=False),
        sa.Column('potential_score_estimate', sa.Float(), nullable=False),
        sa.Column('before_text', sa.Text(), nullable=True),
        sa.Column('after_text', sa.Text(), nullable=True),
        sa.Column('improvement_rationale', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['criterion_id'], ['evaluation_criteria.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Financial Proposals
    op.create_table(
        'financial_proposals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('subtotal', sa.String(length=32), nullable=False),
        sa.Column('tax_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('tax_amount', sa.String(length=32), nullable=False),
        sa.Column('contingency_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('contingency_amount', sa.String(length=32), nullable=False),
        sa.Column('overhead_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('overhead_amount', sa.String(length=32), nullable=False),
        sa.Column('margin_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('margin_amount', sa.String(length=32), nullable=False),
        sa.Column('total_price', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.Column('assumptions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Financial Line Items
    op.create_table(
        'financial_line_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('financial_proposal_id', sa.String(length=36), nullable=False),
        sa.Column('item_code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('unit', sa.String(length=32), nullable=False),
        sa.Column('quantity', sa.String(length=32), nullable=False),
        sa.Column('unit_rate', sa.String(length=32), nullable=False),
        sa.Column('tax_percent', sa.String(length=16), nullable=False),
        sa.Column('line_total', sa.String(length=32), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['financial_proposal_id'], ['financial_proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Financial Scenarios
    op.create_table(
        'financial_scenarios',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('financial_proposal_id', sa.String(length=36), nullable=False),
        sa.Column('scenario_name', sa.String(length=64), nullable=False),
        sa.Column('margin_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('contingency_rate_percent', sa.String(length=16), nullable=False),
        sa.Column('discount_percent', sa.String(length=16), nullable=False),
        sa.Column('calculated_total', sa.String(length=32), nullable=False),
        sa.Column('summary_metrics', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['financial_proposal_id'], ['financial_proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Bid Risks
    op.create_table(
        'bid_risks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('likelihood', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('severity_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=32), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('consequences', sa.Text(), nullable=True),
        sa.Column('mitigation_strategy', sa.Text(), nullable=False),
        sa.Column('contingency_plan', sa.Text(), nullable=True),
        sa.Column('owner', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('source_module', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bid_risks_tender_sev', 'bid_risks', ['tender_id', 'severity_score'])

    # 10. Proposal Quality Checks
    op.create_table(
        'proposal_quality_checks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('checked_by', sa.String(length=128), nullable=False),
        sa.Column('formatting_score', sa.Float(), nullable=False),
        sa.Column('placeholder_count', sa.Integer(), nullable=False),
        sa.Column('placeholders_found', sa.JSON(), nullable=False),
        sa.Column('broken_references_count', sa.Integer(), nullable=False),
        sa.Column('citations_verified_count', sa.Integer(), nullable=False),
        sa.Column('citations_missing_count', sa.Integer(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('page_count_estimate', sa.Integer(), nullable=False),
        sa.Column('issues', sa.JSON(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. Tender Deadlines
    op.create_table(
        'tender_deadlines',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('deadline_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('deadline_date', sa.DateTime(), nullable=False),
        sa.Column('timezone_name', sa.String(length=64), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('reminder_intervals_hours', sa.JSON(), nullable=False),
        sa.Column('last_notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. User Roles (RBAC)
    op.create_table(
        'user_roles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=128), nullable=False),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_roles_ws_user', 'user_roles', ['workspace_id', 'user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_roles_ws_user', table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_table('tender_deadlines')
    op.drop_table('proposal_quality_checks')
    op.drop_index('ix_bid_risks_tender_sev', table_name='bid_risks')
    op.drop_table('bid_risks')
    op.drop_table('financial_scenarios')
    op.drop_table('financial_line_items')
    op.drop_table('financial_proposals')
    op.drop_table('proposal_optimizations')
    op.drop_table('evaluation_criteria')
    op.drop_index('ix_claim_lineage_tender_req', table_name='claim_lineages')
    op.drop_table('claim_lineages')
    op.drop_table('evidence_contradictions')
    op.drop_table('bid_evaluations')
