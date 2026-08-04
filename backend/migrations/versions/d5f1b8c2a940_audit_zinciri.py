"""audit_log zincir hash'leri — silme/değiştirme TESPİT EDİLEBİLİR olsun (FAZ 1.8)

"Append-only" bir BEYANDIR, bir mekanizma değil: bir satır DELETE edilirse geriye hiçbir
iz kalmaz. Her kayıt bir öncekinin hash'ini taşır; ilki `genesis`.

Revision ID: d5f1b8c2a940
Revises: c3d8a1f5b724
Create Date: 2026-08-04 16:25:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'd5f1b8c2a940'
down_revision: str | None = 'c3d8a1f5b724'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('audit_log', sa.Column('onceki_kayit_hash',
                                         sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('audit_log', sa.Column('kayit_hash',
                                         sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('audit_log', 'kayit_hash')
    op.drop_column('audit_log', 'onceki_kayit_hash')
