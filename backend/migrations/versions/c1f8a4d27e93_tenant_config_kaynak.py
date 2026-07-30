"""tenant_config kaynak faseti — kaynaklar + firma/dönem kapsamı (ADR-0017)

Revision ID: c1f8a4d27e93
Revises: a3d5e17f42c8
Create Date: 2026-07-24 18:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel  # control-plane migration'ları SQLModel tiplerini kullanır


revision: str = 'c1f8a4d27e93'
down_revision: str | None = 'a3d5e17f42c8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('tenant_config',
                  sa.Column('kaynaklar_json', sqlmodel.sql.sqltypes.AutoString(),
                            nullable=True))
    op.add_column('tenant_config', sa.Column('firma_no', sa.Integer(), nullable=True))
    op.add_column('tenant_config', sa.Column('donem_no', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenant_config', 'donem_no')
    op.drop_column('tenant_config', 'firma_no')
    op.drop_column('tenant_config', 'kaynaklar_json')
