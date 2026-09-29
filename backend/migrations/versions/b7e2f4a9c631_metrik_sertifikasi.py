"""metrik_sertifikasi — metriğin tanımını KİM onayladı (FAZ 1.5)

`source=cube` rozeti "deterministik bir yoldan geldi" der; bu tablo "tanımı kim onayladı"
der. Bir metrik DOĞRU hesaplanıp YANLIŞ tanımlanmış olabilir ve determinizm onu yakalamaz.

Revision ID: b7e2f4a9c631
Revises: e4a1c8d92f36
Create Date: 2026-08-04 15:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'b7e2f4a9c631'
down_revision: str | None = 'e4a1c8d92f36'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'metrik_sertifikasi',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('metric_ref', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('seviye', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sertifikalayan_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('sertifika_notu', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('definition_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('lineage_set_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('son_gecerlilik', sa.DateTime(), nullable=True),
        sa.Column('otomatik_iptal_nedeni', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_metrik_sertifikasi_tenant_id'), 'metrik_sertifikasi',
                    ['tenant_id'], unique=False)
    op.create_index(op.f('ix_metrik_sertifikasi_metric_ref'), 'metrik_sertifikasi',
                    ['metric_ref'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_metrik_sertifikasi_metric_ref'), table_name='metrik_sertifikasi')
    op.drop_index(op.f('ix_metrik_sertifikasi_tenant_id'), table_name='metrik_sertifikasi')
    op.drop_table('metrik_sertifikasi')
