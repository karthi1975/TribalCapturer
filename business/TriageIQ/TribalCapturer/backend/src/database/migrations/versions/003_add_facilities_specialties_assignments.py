"""Add facilities, specialties, and user assignment tables

Revision ID: 003
Revises: 002
Create Date: 2025-12-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create facilities table
    op.create_table(
        'facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=True, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_facility_name_lower', 'facilities', [sa.text('LOWER(name)')], unique=True)
    op.create_index('idx_facility_active', 'facilities', ['is_active'])

    # 2. Create specialties table
    op.create_table(
        'specialties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=True, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_specialty_name_lower', 'specialties', [sa.text('LOWER(name)')], unique=True)
    op.create_index('idx_specialty_active', 'specialties', ['is_active'])

    # 3. Create user_facilities association table
    op.create_table(
        'user_facilities',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id', 'facility_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_user_facility_user', 'user_facilities', ['user_id'])
    op.create_index('idx_user_facility_facility', 'user_facilities', ['facility_id'])

    # 4. Create user_specialties association table
    op.create_table(
        'user_specialties',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('specialty_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id', 'specialty_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['specialty_id'], ['specialties.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_user_specialty_user', 'user_specialties', ['user_id'])
    op.create_index('idx_user_specialty_specialty', 'user_specialties', ['specialty_id'])

    # 5. Insert unique facilities from existing knowledge_entries
    conn = op.get_bind()
    conn.execute(text("""
        INSERT INTO facilities (name, is_active)
        SELECT DISTINCT facility, true
        FROM knowledge_entries
        WHERE facility IS NOT NULL AND facility != ''
        ON CONFLICT (name) DO NOTHING
    """))

    # 6. Insert unique specialties from existing knowledge_entries
    conn.execute(text("""
        INSERT INTO specialties (name, is_active)
        SELECT DISTINCT specialty_service, true
        FROM knowledge_entries
        WHERE specialty_service IS NOT NULL AND specialty_service != ''
        ON CONFLICT (name) DO NOTHING
    """))

    # 7. Add facility_id and specialty_id columns to knowledge_entries (nullable initially)
    op.add_column('knowledge_entries',
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column('knowledge_entries',
        sa.Column('specialty_id', postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 8. Populate facility_id from existing facility names
    conn.execute(text("""
        UPDATE knowledge_entries ke
        SET facility_id = f.id
        FROM facilities f
        WHERE ke.facility = f.name
    """))

    # 9. Populate specialty_id from existing specialty_service names
    conn.execute(text("""
        UPDATE knowledge_entries ke
        SET specialty_id = s.id
        FROM specialties s
        WHERE ke.specialty_service = s.name
    """))

    # 10. Make facility_id and specialty_id NOT NULL
    op.alter_column('knowledge_entries', 'facility_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )
    op.alter_column('knowledge_entries', 'specialty_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )

    # 11. Add foreign key constraints
    op.create_foreign_key(
        'fk_knowledge_facility',
        'knowledge_entries', 'facilities',
        ['facility_id'], ['id'],
        ondelete='RESTRICT'
    )
    op.create_foreign_key(
        'fk_knowledge_specialty',
        'knowledge_entries', 'specialties',
        ['specialty_id'], ['id'],
        ondelete='RESTRICT'
    )

    # 12. Create indexes on new foreign key columns
    op.create_index('idx_knowledge_facility_id', 'knowledge_entries', ['facility_id'])
    op.create_index('idx_knowledge_specialty_id', 'knowledge_entries', ['specialty_id'])

    # Note: Keeping old facility and specialty_service columns for rollback safety
    # They will be dropped in a future migration after confirming everything works


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_knowledge_specialty_id', 'knowledge_entries')
    op.drop_index('idx_knowledge_facility_id', 'knowledge_entries')

    # Drop foreign key constraints
    op.drop_constraint('fk_knowledge_specialty', 'knowledge_entries', type_='foreignkey')
    op.drop_constraint('fk_knowledge_facility', 'knowledge_entries', type_='foreignkey')

    # Drop new columns from knowledge_entries
    op.drop_column('knowledge_entries', 'specialty_id')
    op.drop_column('knowledge_entries', 'facility_id')

    # Drop association tables
    op.drop_index('idx_user_specialty_specialty', 'user_specialties')
    op.drop_index('idx_user_specialty_user', 'user_specialties')
    op.drop_table('user_specialties')

    op.drop_index('idx_user_facility_facility', 'user_facilities')
    op.drop_index('idx_user_facility_user', 'user_facilities')
    op.drop_table('user_facilities')

    # Drop specialties table
    op.drop_index('idx_specialty_active', 'specialties')
    op.drop_index('idx_specialty_name_lower', 'specialties')
    op.drop_table('specialties')

    # Drop facilities table
    op.drop_index('idx_facility_active', 'facilities')
    op.drop_index('idx_facility_name_lower', 'facilities')
    op.drop_table('facilities')
