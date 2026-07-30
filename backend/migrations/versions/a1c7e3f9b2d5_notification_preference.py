"""notification_preference — kullanıcı bildirim tercihi matrisi (ADR-0011)

Birleşik teslim mimarisinin tercih katmanı: KATEGORİ × KANAL (report/alert/anomaly/
system × inapp/email/push/…). Kullanıcı her kategoriyi hangi kanaldan alacağını seçer.
inapp varsayılan açık; email/push opt-in. address = kanal-özel hedef. Soft-delete.

Revision ID: a1c7e3f9b2d5
Revises: f4c6a2b9e1d3
Create Date: 2026-07-28 11:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'a1c7e3f9b2d5'
down_revision: str | None = 'f4c6a2b9e1d3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'notification_preference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('channel', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notification_preference_user_id'),
                    'notification_preference', ['user_id'])
    op.create_index(op.f('ix_notification_preference_tenant_id'),
                    'notification_preference', ['tenant_id'])
    op.create_index(op.f('ix_notification_preference_category'),
                    'notification_preference', ['category'])
    op.create_index(op.f('ix_notification_preference_deleted_at'),
                    'notification_preference', ['deleted_at'])


def downgrade() -> None:
    for ix in ('deleted_at', 'category', 'tenant_id', 'user_id'):
        op.drop_index(op.f(f'ix_notification_preference_{ix}'), table_name='notification_preference')
    op.drop_table('notification_preference')
