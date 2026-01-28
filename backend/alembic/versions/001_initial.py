"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('slug', sa.String(), nullable=False, unique=True, index=True),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='READER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=True),
    )
    
    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='ACTIVE'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('secrets_ref', sa.String(), nullable=True),
        sa.Column('config', postgresql.JSON(), nullable=True, server_default='{}'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create repos table
    op.create_table(
        'repos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(), nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create pull_requests table
    op.create_table(
        'pull_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(), nullable=False, index=True),
        sa.Column('raw_data', postgresql.JSON(), nullable=True),
        sa.Column('repo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('repos.id'), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create trello_cards table (replacing jira_issues)
    op.create_table(
        'trello_cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(), nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('list_name', sa.String(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create metrics_daily table
    op.create_table(
        'metrics_daily',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('day', sa.Date(), nullable=False, index=True),
        sa.Column('lead_time_p50', sa.Float(), nullable=True),
        sa.Column('lead_time_p85', sa.Float(), nullable=True),
        sa.Column('wip', sa.Float(), nullable=True),
        sa.Column('throughput', sa.Float(), nullable=True),
        sa.Column('review_time_p50', sa.Float(), nullable=True),
        sa.Column('bug_ratio', sa.Float(), nullable=True),
        sa.Column('pr_size_p50', sa.Float(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create risk_signals table
    op.create_table(
        'risk_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('explanation', sa.String(), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('history', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='NEW'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )
    
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('status', sa.String(), nullable=False, server_default='DRAFT'),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sources_json', postgresql.JSON(), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=True),
        sa.Column('model_info', sa.String(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('period', sa.String(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('alerts')
    op.drop_table('risk_signals')
    op.drop_table('metrics_daily')
    op.drop_table('trello_cards')
    op.drop_table('pull_requests')
    op.drop_table('repos')
    op.drop_table('integrations')
    op.drop_table('users')
    op.drop_table('workspaces')
