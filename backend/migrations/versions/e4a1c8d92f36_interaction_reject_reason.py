"""interaction_log.reject_reason — RED GEREKÇESİ (Faz 0)

`cube_router.route()` **on ayrı yerde** `None` döner ve bugüne kadar HANGİSİNDE pes ettiği
yalnız `trace` metninde/`source=None`'da görünüyordu — **sayısal olarak gruplanamıyordu**.

Planın §2.3 tezi tam bu: *"çoğu soru LLM'e gidiyor"* bir HİPOTEZ, ölçüm değil. Deterministik
tavanın %64 olduğu ölçüldü ama kalan %36'nın **nasıl dağıldığı** bilinmiyor — netleştirme
chip'i mi, Intent-JSON mu, Discovery mi? Hangi kaldıraca yatırım yapılacağı bu dağılım
görülmeden karar verilemez. Faz 0'ın çıktısı bu yüzden *"en sık 20 red gerekçesi"*.

AYRI kolon, `note`'a sıkıştırılmadı: `note` serbest METİNDİR ve
`admin_app/routers/synonyms.py::mine_candidates` onu zaten başarısızlık açıklaması olarak
okuyor. Sabit bir kod (R1…R10) ayrı ve indeksli bir kolonda durursa GRUPLANABİLİR.

Nullable + indeksli: `route()` pes etmediyse (cevap geldi) NULL kalır — yani bu kolonun
DOLULUĞU doğrudan "deterministik yoldan çıkamayan sorular" kümesini verir.

Revision ID: e4a1c8d92f36
Revises: d3f8b1c60e29
Create Date: 2026-08-02 20:55:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'e4a1c8d92f36'
down_revision: str | None = 'd3f8b1c60e29'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('interaction_log',
                  sa.Column('reject_reason', sqlmodel.sql.sqltypes.AutoString(),
                            nullable=True))
    op.create_index('ix_interaction_log_reject_reason', 'interaction_log', ['reject_reason'])


def downgrade() -> None:
    op.drop_index('ix_interaction_log_reject_reason', table_name='interaction_log')
    op.drop_column('interaction_log', 'reject_reason')
