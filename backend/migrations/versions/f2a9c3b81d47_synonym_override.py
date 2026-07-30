"""synonym_override — canlı öğrenilen sinonim overlay'i (ADR-0018 katman 3)

Revision ID: f2a9c3b81d47
Revises: e5b2c7f91a04
Create Date: 2026-07-24 21:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'f2a9c3b81d47'
down_revision: str | None = 'e5b2c7f91a04'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'synonym_override',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('scope_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('scope_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cube', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('field_kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('field_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('synonyms_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='manual'),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_synonym_override_scope_type'), 'synonym_override',
                    ['scope_type'])
    op.create_index(op.f('ix_synonym_override_scope_id'), 'synonym_override',
                    ['scope_id'])
    op.create_index(op.f('ix_synonym_override_cube'), 'synonym_override', ['cube'])
    op.create_index(op.f('ix_synonym_override_approved'), 'synonym_override',
                    ['approved'])


def downgrade() -> None:
    op.drop_index(op.f('ix_synonym_override_approved'), table_name='synonym_override')
    op.drop_index(op.f('ix_synonym_override_cube'), table_name='synonym_override')
    op.drop_index(op.f('ix_synonym_override_scope_id'), table_name='synonym_override')
    op.drop_index(op.f('ix_synonym_override_scope_type'), table_name='synonym_override')
    op.drop_table('synonym_override')
