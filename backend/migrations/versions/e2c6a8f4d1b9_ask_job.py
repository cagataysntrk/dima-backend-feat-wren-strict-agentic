"""ask_job — /ask Discovery yolu için hafif arka-plan iş kuyruğu (Faz 4.1)

Revision ID: e2c6a8f4d1b9
Revises: d3f7a9c1e6b4
Create Date: 2026-07-31 00:00:00.000001
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'e2c6a8f4d1b9'
down_revision: str | None = 'd3f7a9c1e6b4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'ask_job',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('session_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='pending'),
        sa.Column('request_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='{}'),
        sa.Column('result_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('error', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ask_job_tenant_id'), 'ask_job', ['tenant_id'])
    op.create_index(op.f('ix_ask_job_session_id'), 'ask_job', ['session_id'])
    op.create_index(op.f('ix_ask_job_status'), 'ask_job', ['status'])


def downgrade() -> None:
    op.drop_index(op.f('ix_ask_job_status'), table_name='ask_job')
    op.drop_index(op.f('ix_ask_job_session_id'), table_name='ask_job')
    op.drop_index(op.f('ix_ask_job_tenant_id'), table_name='ask_job')
    op.drop_table('ask_job')
