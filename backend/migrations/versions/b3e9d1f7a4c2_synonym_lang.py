"""synonym_override.lang — dil-etiketli sinonim overlay (§7b çok-dil admin)

Admin bir sinonimi HANGİ dilde eklediğini işaretler (tr/en/…): yerel dil tam sözlük,
yardımcı dil teknik alt-küme (yanlış-dost disiplini). None = yerel/belirsiz. Nullable →
mevcut satırlar etkilenmez. Routing tüm havuzu union'lar; lang şimdilik metadata +
ileride per-dil filtreleme için.

Revision ID: b3e9d1f7a4c2
Revises: a1c7e3f9b2d5
Create Date: 2026-07-28 12:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'b3e9d1f7a4c2'
down_revision: str | None = 'a1c7e3f9b2d5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('synonym_override',
                  sa.Column('lang', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('synonym_override', 'lang')
