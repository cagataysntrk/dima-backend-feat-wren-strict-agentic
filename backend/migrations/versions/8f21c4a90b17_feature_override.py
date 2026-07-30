"""feature_override — özellik bayrağı override'ları (ADR-0009 DB fazı)

Revision ID: 8f21c4a90b17
Revises: 6e709def77e0
Create Date: 2026-07-23 20:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel  # control-plane migration'ları SQLModel tiplerini kullanır


revision: str = '8f21c4a90b17'
down_revision: str | None = '6e709def77e0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'feature_override',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('feature_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('scope_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('scope_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('stage', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_feature_override_feature_key'), 'feature_override',
                    ['feature_key'], unique=False)
    op.create_index(op.f('ix_feature_override_scope_type'), 'feature_override',
                    ['scope_type'], unique=False)
    op.create_index(op.f('ix_feature_override_scope_id'), 'feature_override',
                    ['scope_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feature_override_scope_id'), table_name='feature_override')
    op.drop_index(op.f('ix_feature_override_scope_type'), table_name='feature_override')
    op.drop_index(op.f('ix_feature_override_feature_key'), table_name='feature_override')
    op.drop_table('feature_override')
