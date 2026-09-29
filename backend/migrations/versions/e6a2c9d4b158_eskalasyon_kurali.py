"""eskalasyon_kurali — bir uyarı, görülmezse yükselir (FAZ 1.10)

Bir eşik aşıldığında bildirim gider ve orada BİTER. Bir uyarının işlevi haber vermek
değil, BİR KARARA YOL AÇMAKTIR.

Revision ID: e6a2c9d4b158
Revises: d5f1b8c2a940
Create Date: 2026-08-04 17:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'e6a2c9d4b158'
down_revision: str | None = 'd5f1b8c2a940'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'eskalasyon_kurali',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('ad', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tetikleyici_esik', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sure_dakika', sa.Integer(), nullable=False),
        sa.Column('hedef_rol', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('otomatik_kilitle', sa.Boolean(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_eskalasyon_kurali_tenant_id'), 'eskalasyon_kurali',
                    ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_eskalasyon_kurali_tenant_id'), table_name='eskalasyon_kurali')
    op.drop_table('eskalasyon_kurali')
