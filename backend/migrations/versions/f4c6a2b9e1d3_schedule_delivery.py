"""schedule_definition.delivery_json — ek teslim kanalları (ADR-0011)

Zamanlanmış rapor/alarm bildirimi in-app bell'e HER ZAMAN düşer; ek kanallar
(e-posta/Resend; ileride Slack/webhook) opsiyonel ve schedule başına saklanır.
Şekil: {"email": {"to": [...]}}. Nullable → mevcut tanımlar etkilenmez.

Revision ID: f4c6a2b9e1d3
Revises: e1b3d5a7c9f2
Create Date: 2026-07-28 10:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'f4c6a2b9e1d3'
down_revision: str | None = 'e1b3d5a7c9f2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'schedule_definition',
        sa.Column('delivery_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('schedule_definition', 'delivery_json')
