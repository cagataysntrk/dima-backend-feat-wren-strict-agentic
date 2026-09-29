"""tenant_config.diller_json — tenant AKTİF DİL SETİ (§7b çok-dil)

Admin firma ayarlarından firmanın kullandığı dilleri seçer (desteklenen: tr, en).
Sıralı liste = öncelik (soft-prior). None = varsayılan (tr+en). company.yml `diller:`
olarak materialize edilir → routing aktif dilleri union'lar. Nullable → mevcut satırlar
etkilenmez (varsayılana düşer).

Revision ID: c5a2e8b1f9d4
Revises: b3e9d1f7a4c2
Create Date: 2026-07-28 13:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'c5a2e8b1f9d4'
down_revision: str | None = 'b3e9d1f7a4c2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('tenant_config',
                  sa.Column('diller_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenant_config', 'diller_json')
