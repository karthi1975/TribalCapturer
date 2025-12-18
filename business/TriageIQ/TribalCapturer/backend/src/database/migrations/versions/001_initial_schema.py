"""Initial schema - create users, knowledge_entries, and audit_logs tables

Revision ID: 001
Revises:
Create Date: 2025-12-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('MA', 'Creator', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_user_username', 'users', ['username'])
    op.create_index('idx_user_role', 'users', ['role'])

    # Create knowledge_entries table
    op.create_table(
        'knowledge_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ma_name', sa.String(length=255), nullable=False),
        sa.Column('facility', sa.String(length=255), nullable=False),
        sa.Column('specialty_service', sa.String(length=255), nullable=False),
        sa.Column('knowledge_description', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'published', name='entrystatus'), nullable=False, server_default='published'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_user_id', 'knowledge_entries', ['user_id'])
    op.create_index('idx_knowledge_facility', 'knowledge_entries', ['facility'])
    op.create_index('idx_knowledge_specialty', 'knowledge_entries', ['specialty_service'])
    op.create_index('idx_knowledge_created_at', 'knowledge_entries', [sa.text('created_at DESC')])
    op.create_index('idx_knowledge_status', 'knowledge_entries', ['status'])

    # Create full-text search index for knowledge_description
    op.execute("""
        CREATE INDEX gin_idx_knowledge_description
        ON knowledge_entries
        USING gin(to_tsvector('english', knowledge_description))
    """)

    # Create trigger function for auto-updating updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on knowledge_entries
    op.execute("""
        CREATE TRIGGER set_updated_at
        BEFORE UPDATE ON knowledge_entries
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('knowledge_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['knowledge_entry_id'], ['knowledge_entries.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_knowledge_entry_id', 'audit_logs', ['knowledge_entry_id'])
    op.create_index('idx_audit_timestamp', 'audit_logs', [sa.text('timestamp DESC')])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')

    # Drop trigger and function
    op.execute('DROP TRIGGER IF EXISTS set_updated_at ON knowledge_entries')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    op.drop_table('knowledge_entries')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS entrystatus')
    op.execute('DROP TYPE IF EXISTS userrole')
