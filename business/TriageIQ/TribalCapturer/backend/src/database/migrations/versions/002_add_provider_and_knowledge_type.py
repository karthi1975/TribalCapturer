"""Add provider, knowledge_type, and continuity_care fields

Revision ID: 002
Revises: 001
Create Date: 2025-12-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create knowledgetype enum
    knowledge_type_enum = postgresql.ENUM(
        'diagnosis_specialty',
        'provider_preference',
        'continuity_care',
        'pre_visit_requirement',
        'scheduling_workflow',
        'general_knowledge',
        name='knowledgetype',
        create_type=True
    )
    knowledge_type_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to knowledge_entries table
    op.add_column('knowledge_entries',
        sa.Column('provider_name', sa.String(length=255), nullable=True)
    )
    op.add_column('knowledge_entries',
        sa.Column('knowledge_type',
            sa.Enum(
                'diagnosis_specialty',
                'provider_preference',
                'continuity_care',
                'pre_visit_requirement',
                'scheduling_workflow',
                'general_knowledge',
                name='knowledgetype'
            ),
            nullable=False,
            server_default='general_knowledge'
        )
    )
    op.add_column('knowledge_entries',
        sa.Column('is_continuity_care', sa.Boolean(), nullable=False, server_default='false')
    )

    # Create indexes
    op.create_index('idx_knowledge_provider', 'knowledge_entries', ['provider_name'])
    op.create_index('idx_knowledge_type', 'knowledge_entries', ['knowledge_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_knowledge_type', 'knowledge_entries')
    op.drop_index('idx_knowledge_provider', 'knowledge_entries')

    # Drop columns
    op.drop_column('knowledge_entries', 'is_continuity_care')
    op.drop_column('knowledge_entries', 'knowledge_type')
    op.drop_column('knowledge_entries', 'provider_name')

    # Drop enum
    sa.Enum(name='knowledgetype').drop(op.get_bind(), checkfirst=True)
