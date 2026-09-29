"""FAZ 5.8 — karar kaydına **şablon** alanı.

`contract_ids` *"o gün hangi sayıya baktık"* der (donmuş kanıt). Şablon bir üst soruyu
cevaplar: **"aynı analizi BUGÜN koşsak ne çıkar?"** İkisi farklı şeylerdir ve biri
ötekinin yerine geçmez — makbuz **geçmişi**, şablon **tekrarı** taşır.

⚠ Nullable: var olan kararların hiçbiri şablon taşımıyor ve **taşımak zorunda değil**.
Geriye dönük bir şablon uydurmak, o kararın dayandığı analizin bugün de aynı olduğunu
**varsaymak** olurdu.

Revision ID: b3e9c1f7a482
Revises: a1d7f4c8e250
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "b3e9c1f7a482"
down_revision: str | None = "a1d7f4c8e250"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("decision_record", sa.Column("sablon_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("decision_record", "sablon_json")
