"""Phase 2 schema for Organization Profiles, Evidence Repository, ProofLink, Compliance, Proposals, Audits, Human Approvals, Switch Rooms, and Workflow State.

Revision ID: 002_phase2_models
Revises: 001_initial_schema
Create Date: 2026-11-05 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase2_models'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Organization Profiles
    op.create_table(
        'organization_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('trade_name', sa.String(length=255), nullable=True),
        sa.Column('registration_number', sa.String(length=128), nullable=False),
        sa.Column('tax_id', sa.String(length=128), nullable=False),
        sa.Column('jurisdiction', sa.String(length=128), nullable=False),
        sa.Column('incorporation_date', sa.DateTime(), nullable=True),
        sa.Column('headquarters_address', sa.String(length=512), nullable=True),
        sa.Column('primary_contact_name', sa.String(length=255), nullable=True),
        sa.Column('primary_contact_email', sa.String(length=255), nullable=True),
        sa.Column('financial_metrics', sa.JSON(), nullable=True),
        sa.Column('core_capabilities', sa.JSON(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )

    # 2. Company Evidence
    op.create_table(
        'company_evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('evidence_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('issuer', sa.String(length=255), nullable=True),
        sa.Column('issue_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('reference_number', sa.String(length=128), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_company_evidence_org_type', 'company_evidence', ['organization_id', 'evidence_type'])

    # 3. Evidence Requirement Links (ProofLink)
    op.create_table(
        'evidence_requirement_links',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=False),
        sa.Column('match_status', sa.String(length=32), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('source_excerpt', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('verified_by_user_id', sa.String(length=128), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['requirement_id'], ['tender_requirements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['company_evidence.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_evidence_req_link', 'evidence_requirement_links', ['requirement_id', 'evidence_id'])

    # 4. Compliance Matrices
    op.create_table(
        'compliance_matrices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('overall_status', sa.String(length=32), nullable=False),
        sa.Column('overall_risk_level', sa.String(length=32), nullable=False),
        sa.Column('evaluated_by_agent', sa.String(length=128), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('items', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Proposals
    op.create_table(
        'proposals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('current_version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('docx_file_path', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Proposal Sections
    op.create_table(
        'proposal_sections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('section_number', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('claims', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Proposal Revisions
    op.create_table(
        'proposal_revisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('author_type', sa.String(length=32), nullable=False),
        sa.Column('author_id', sa.String(length=128), nullable=False),
        sa.Column('change_summary', sa.String(length=512), nullable=False),
        sa.Column('snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Bid Audits
    op.create_table(
        'bid_audits',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('auditor_type', sa.String(length=32), nullable=False),
        sa.Column('auditor_id', sa.String(length=128), nullable=False),
        sa.Column('readiness_score', sa.Float(), nullable=False),
        sa.Column('verdict', sa.String(length=64), nullable=False),
        sa.Column('total_claims', sa.Integer(), nullable=False),
        sa.Column('verified_claims', sa.Integer(), nullable=False),
        sa.Column('unsupported_claims', sa.Integer(), nullable=False),
        sa.Column('contradicted_claims', sa.Integer(), nullable=False),
        sa.Column('findings', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Human Approvals
    op.create_table(
        'human_approvals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=True),
        sa.Column('audit_id', sa.String(length=36), nullable=True),
        sa.Column('decision', sa.String(length=32), nullable=False),
        sa.Column('user_id', sa.String(length=128), nullable=False),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('user_role', sa.String(length=128), nullable=False),
        sa.Column('comments', sa.Text(), nullable=False),
        sa.Column('signature_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['audit_id'], ['bid_audits.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Switch Rooms
    op.create_table(
        'switch_rooms',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('room_name', sa.String(length=255), nullable=False),
        sa.Column('channel_id', sa.String(length=128), nullable=False),
        sa.Column('channel_type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. Workflow States
    op.create_table(
        'workflow_states',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('current_stage', sa.String(length=64), nullable=False),
        sa.Column('stage_history', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tender_id')
    )


def downgrade() -> None:
    op.drop_table('workflow_states')
    op.drop_table('switch_rooms')
    op.drop_table('human_approvals')
    op.drop_table('bid_audits')
    op.drop_table('proposal_revisions')
    op.drop_table('proposal_sections')
    op.drop_table('proposals')
    op.drop_table('compliance_matrices')
    op.drop_index('ix_evidence_req_link', table_name='evidence_requirement_links')
    op.drop_table('evidence_requirement_links')
    op.drop_index('ix_company_evidence_org_type', table_name='company_evidence')
    op.drop_table('company_evidence')
    op.drop_table('organization_profiles')
