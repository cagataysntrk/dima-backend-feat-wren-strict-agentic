"""notification_log — bildirim/teslim logu Postgres'te (admin görüntüleme, ADR-0011/0020)

Zamanlanmış rapor/alarm koşumları notifications.jsonl'a düşer (in-app bell, public volume);
admin plane AYRI servis → volume okunamaz. Bu tablo aynı olayı ortak store'a yazar →
/sadmin/notifications filtreli görür. Append-only telemetri (soft-delete yok).

Revision ID: d8f4b2a6c1e7
Revises: c5a2e8b1f9d4
Create Date: 2026-07-28 14:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'd8f4b2a6c1e7'
down_revision: str | None = 'c5a2e8b1f9d4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'notification_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('schedule_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('contract_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('delivery_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    for c in ('ts', 'company', 'tenant_id', 'schedule_id', 'kind'):
        op.create_index(op.f(f'ix_notification_log_{c}'), 'notification_log', [c])


def downgrade() -> None:
    for c in ('kind', 'schedule_id', 'tenant_id', 'company', 'ts'):
        op.drop_index(op.f(f'ix_notification_log_{c}'), table_name='notification_log')
    op.drop_table('notification_log')
