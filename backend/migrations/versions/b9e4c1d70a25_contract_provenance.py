"""contract_log.provenance_json — cevabın KÖKEN kanıtı (Faz D2)

Query Contract bugüne kadar *"hangi sayı, hangi SQL, hangi şema sürümü"* sorusunu
cevaplıyordu. Cevaplayamadığı soru: **"bu kırılım nereden geldi ve o join ölçüldü mü?"**

`relationships.yml`'de beyan edilen her join'in fan-out / NULL / öksüz sağlığı
`tests/test_relationship_health.py` içinde ölçülüyordu ama hiçbir yerde SAKLANMIYORDU —
yani ölçüm koşum anında doğuyor, koşum bitince ölüyordu. MIMARI §9.1 bu ölçümü "dünyada
ilk" sayan bir iddia taşıyor; artefakt ve makbuz olmadan iddia karşılıksızdır.

Bu kolon, cevabın kullandığı ilişki-türevi boyutların kökenini ve sertifika damgasını
taşır (`{"dimensions": {"kisim": {"relationship": ..., "hops": 1, "certified":
"olculdu:saglikli"}}}`). Nullable: yalnız ilişki-türevi boyut kullanan cevaplarda dolar,
geriye dönük kayıtlar NULL kalır.

Revision ID: b9e4c1d70a25
Revises: a4d8f2c6e903
Create Date: 2026-08-02 09:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'b9e4c1d70a25'
down_revision: str | None = 'a4d8f2c6e903'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('contract_log',
                  sa.Column('provenance_json', sqlmodel.sql.sqltypes.AutoString(),
                            nullable=True))


def downgrade() -> None:
    op.drop_column('contract_log', 'provenance_json')
