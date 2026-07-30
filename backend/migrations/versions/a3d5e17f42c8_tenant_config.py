"""tenant_config — tenant sektör/modül yapılandırması (materializer kaynağı)

Revision ID: a3d5e17f42c8
Revises: 8f21c4a90b17
Create Date: 2026-07-23 21:05:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel  # control-plane migration'ları SQLModel tiplerini kullanır


revision: str = 'a3d5e17f42c8'
down_revision: str | None = '8f21c4a90b17'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'tenant_config',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('sektorler_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('moduller_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tenant_config_tenant_id'), 'tenant_config',
                    ['tenant_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_tenant_config_tenant_id'), table_name='tenant_config')
    op.drop_table('tenant_config')
