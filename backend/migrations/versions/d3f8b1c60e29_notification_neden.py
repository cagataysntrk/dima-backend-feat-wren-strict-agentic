"""notification_log.neden_json — UYARININ NEDENİ (Faz F3)

Uyarı bugüne kadar *"ne oldu"* diyordu: `⚠ fire: eşik ihlali — makine M-07: 45 (> eşik 30)`.
*"Neyin değişmesi bunu getirdi"* sorusunun cevabını üretecek motor (`app/contribution.py`)
elimizde duruyordu ama arka plan işi onu çağıramıyordu — gövde `/ask/contribution`
router'ının içindeydi. Faz F3'te `contribution.arastir` HTTP'den ayrıldı; uyarı artık
nedenini de taşıyor ve o neden bell'e kadar hayatta kalmalı.

AYRI bir kolon, `delivery_json`'ın içine sıkıştırılmadı: teslim TELEMETRİSİ ile cevabın
İÇERİĞİ farklı şeylerdir ve birini ötekinin içinde saklamak ikisini de sorgulanamaz yapardı.

Nullable: eski satırlarda neden YOKTUR ve olmaması bir eksiklik değil bir OLGUDUR —
"boş neden" ile "neden üretilmedi" ayrı okunmalı.

Revision ID: d3f8b1c60e29
Revises: c2a7e9f31b48
Create Date: 2026-08-02 16:40:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'd3f8b1c60e29'
down_revision: str | None = 'c2a7e9f31b48'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('notification_log',
                  sa.Column('neden_json', sqlmodel.sql.sqltypes.AutoString(),
                            nullable=True))


def downgrade() -> None:
    op.drop_column('notification_log', 'neden_json')
