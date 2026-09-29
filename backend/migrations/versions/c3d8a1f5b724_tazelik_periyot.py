"""tenant_config.tazelik_periyot_saat — tazelik merdiveni (FAZ 1.7)

Yapılandırılan TEK sayı: beklenen senkron periyodu. Eşikler ondan TÜRER (uyarı 2×,
hata 5×) ve ayrı ayrı ayarlanamaz — çelişebilen iki ayar, çelişecek demektir.

Revision ID: c3d8a1f5b724
Revises: b7e2f4a9c631
Create Date: 2026-08-04 15:45:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'c3d8a1f5b724'
down_revision: str | None = 'b7e2f4a9c631'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('tenant_config',
                  sa.Column('tazelik_periyot_saat', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenant_config', 'tazelik_periyot_saat')
