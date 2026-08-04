"""metrik_sahipligi — çakışan terimin SAHİBİ (FAZ 2.2b)

0.18 hakemi kurdu ama kaydı katalogdan taslak üretiyor ve `sahiplenilen_terimler` boş
başlıyordu; boşu dolduracak bir yol olmadığı için hakem HİÇBİR ZAMAN karar veremezdi.
Kurulmuş ama beslenemeyen bir hakem, kurulmamış bir hakemdir.

⚠ Yalnız SAHİPLİK tutulur: display_name/unit/rounding cube YAML'ında zaten var ve
DB'ye kopyalamak "aynı kuralın iki sahibi" olurdu.

Revision ID: a1d7f4c8e250
Revises: f8c1e3a7d259
Create Date: 2026-08-04 21:40:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a1d7f4c8e250'
down_revision: str | None = 'f8c1e3a7d259'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'metrik_sahipligi',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(), sa.ForeignKey('tenant.id'), nullable=False,
                  index=True),
        sa.Column('terim', sa.String(), nullable=False, index=True),
        sa.Column('sahip_cube', sa.String(), nullable=True),
        sa.Column('karar_veren_user_id', sa.Uuid(), sa.ForeignKey('app_user.id'),
                  nullable=True),
        sa.Column('guncellendi', sa.DateTime(), nullable=False),
        # 🔴 Bir terimi İKİ cube sahiplenemez — kısıt YAZMA anını, `metrik_kaydi.
        # cift_sahiplik_denetle` OKUMA anını kollar. Aynı kural, iki koruma; bilinçli.
        sa.UniqueConstraint('tenant_id', 'terim', name='uq_metrik_terim'),
    )


def downgrade() -> None:
    op.drop_table('metrik_sahipligi')
