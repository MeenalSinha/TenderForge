"""Initial schema for TenderForge

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-05 10:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # 2. Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=False),
        sa.Column('file_extension', sa.String(length=16), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('document_category', sa.String(length=64), nullable=False),
        sa.Column('processing_status', sa.String(length=32), nullable=False),
        sa.Column('parser_name', sa.String(length=64), nullable=True),
        sa.Column('parser_version', sa.String(length=32), nullable=True),
        sa.Column('ocr_required', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_checksum_sha256', 'documents', ['checksum_sha256'])
    op.create_index('ix_documents_workspace_status', 'documents', ['workspace_id', 'processing_status'])

    # 4. Document Versions
    op.create_table(
        'document_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Processing Jobs
    op.create_table(
        'processing_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('stage', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Extracted Contents
    op.create_table(
        'extracted_contents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('start_char', sa.Integer(), nullable=True),
        sa.Column('end_char', sa.Integer(), nullable=True),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_extracted_chunk_order', 'extracted_contents', ['document_id', 'chunk_index'])

    # 7. Tenders
    op.create_table(
        'tenders',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('reference_number', sa.String(length=128), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('issuing_authority', sa.String(length=255), nullable=True),
        sa.Column('procurement_category', sa.String(length=128), nullable=True),
        sa.Column('estimated_value', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('submission_deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tenders_reference_number', 'tenders', ['reference_number'])

    # 8. Tender Documents (Link Table)
    op.create_table(
        'tender_documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('relationship_type', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Tender Requirements
    op.create_table(
        'tender_requirements',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('source_document_id', sa.String(length=36), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('classification', sa.String(length=32), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_offset', sa.Integer(), nullable=True),
        sa.Column('source_excerpt', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('human_review_status', sa.String(length=32), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_requirements_tender_cat', 'tender_requirements', ['tender_id', 'category'])

    # 10. Extraction Results
    op.create_table(
        'extraction_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tender_id', sa.String(length=36), nullable=False),
        sa.Column('provider_id', sa.String(length=64), nullable=False),
        sa.Column('model_id', sa.String(length=128), nullable=False),
        sa.Column('prompt_version', sa.String(length=32), nullable=False),
        sa.Column('raw_response', sa.JSON(), nullable=True),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('validation_status', sa.String(length=32), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('extraction_results')
    op.drop_index('ix_requirements_tender_cat', table_name='tender_requirements')
    op.drop_table('tender_requirements')
    op.drop_table('tender_documents')
    op.drop_index('ix_tenders_reference_number', table_name='tenders')
    op.drop_table('tenders')
    op.drop_index('ix_extracted_chunk_order', table_name='extracted_contents')
    op.drop_table('extracted_contents')
    op.drop_table('processing_jobs')
    op.drop_table('document_versions')
    op.drop_index('ix_documents_workspace_status', table_name='documents')
    op.drop_index('ix_documents_checksum_sha256', table_name='documents')
    op.drop_table('documents')
    op.drop_table('workspaces')
    op.drop_table('organizations')

