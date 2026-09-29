"""dashboard + dashboard_widget — kullanıcı panoları (§9 canlı-izleme, pull ayağı)

PER-USER, kullanıcı başı ≤10 (router guard). Widget = kayıtlı cube_query + göreli dönem
(schedule/VQR ile aynı "kayıtlı sorgu" soyutlaması). Soft-delete (ADR-0019).

Revision ID: e1b3d5a7c9f2
Revises: d7a2f4c6b9e1
Create Date: 2026-07-27 16:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'e1b3d5a7c9f2'
down_revision: str | None = 'd7a2f4c6b9e1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'dashboard',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('visibility', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('layout_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_dashboard_tenant_id'), 'dashboard', ['tenant_id'])
    op.create_index(op.f('ix_dashboard_user_id'), 'dashboard', ['user_id'])
    op.create_index(op.f('ix_dashboard_updated_at'), 'dashboard', ['updated_at'])
    op.create_index(op.f('ix_dashboard_deleted_at'), 'dashboard', ['deleted_at'])

    op.create_table(
        'dashboard_widget',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('dashboard_id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('cube_query_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('view_hint', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('period', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('pos_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('refresh', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_dashboard_widget_dashboard_id'), 'dashboard_widget', ['dashboard_id'])
    op.create_index(op.f('ix_dashboard_widget_deleted_at'), 'dashboard_widget', ['deleted_at'])


def downgrade() -> None:
    op.drop_index(op.f('ix_dashboard_widget_deleted_at'), table_name='dashboard_widget')
    op.drop_index(op.f('ix_dashboard_widget_dashboard_id'), table_name='dashboard_widget')
    op.drop_table('dashboard_widget')
    for ix in ('deleted_at', 'updated_at', 'user_id', 'tenant_id'):
        op.drop_index(op.f(f'ix_dashboard_{ix}'), table_name='dashboard')
    op.drop_table('dashboard')
