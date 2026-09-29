"""tenant_config.audit_saklama_gun — AI Act Md.12/19 saklama POLİTİKASI (FAZ 1.12)

⚠ Bu alan SİLME YAPMAZ, politikayı BEYAN EDER. Bir saklama süresini uygulamak (retention
job) geri alınamaz bir SİLME eylemidir ve FAZ 6'nın "onaysız hiçbir yazma" değişmezine
bağlıdır. Beyan edilmiş ama uygulanmamış bir politika, beyan edilmemiş bir politikadan
iyidir: denetleyici ne beklediğimizi okuyabilir.

Revision ID: f8c1e3a7d259
Revises: e6a2c9d4b158
Create Date: 2026-08-04 18:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'f8c1e3a7d259'
down_revision: str | None = 'e6a2c9d4b158'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('tenant_config',
                  sa.Column('audit_saklama_gun', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenant_config', 'audit_saklama_gun')
