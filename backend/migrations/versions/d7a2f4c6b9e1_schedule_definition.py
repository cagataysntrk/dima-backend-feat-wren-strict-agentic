"""schedule_definition — zamanlanmış rapor TANIMLARI Postgres'te (ADR-0011)

Tanımlar companies/<şirket>/schedules.yaml'daydı; Railway volume yalnız logs/'u
kapsadığından redeploy'da siliniyordu (state kalıcı ama tanım kayıp). Kalıcı + admin-
yönetilebilir için Postgres. State/notifications dosyada kalır. Soft-delete (deleted_at).

Revision ID: d7a2f4c6b9e1
Revises: c9f3a1b5e2d7
Create Date: 2026-07-27 15:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'd7a2f4c6b9e1'
down_revision: str | None = 'c9f3a1b5e2d7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'schedule_definition',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('cube_query_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('period', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('every', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('at', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('weekday', sa.Integer(), nullable=True),
        sa.Column('threshold_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_schedule_definition_company'), 'schedule_definition', ['company'])
    op.create_index(op.f('ix_schedule_definition_tenant_id'), 'schedule_definition', ['tenant_id'])
    op.create_index(op.f('ix_schedule_definition_deleted_at'), 'schedule_definition', ['deleted_at'])


def downgrade() -> None:
    for ix in ('deleted_at', 'tenant_id', 'company'):
        op.drop_index(op.f(f'ix_schedule_definition_{ix}'), table_name='schedule_definition')
    op.drop_table('schedule_definition')
