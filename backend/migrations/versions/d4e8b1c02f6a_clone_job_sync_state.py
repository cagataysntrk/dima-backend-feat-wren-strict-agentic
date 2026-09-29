"""clone_job + sync_state — DB clone/sync yönetimi (ADR-0017 K9 api_sync ayna)

Revision ID: d4e8b1c02f6a
Revises: f2a9c3b81d47
Create Date: 2026-07-26 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'd4e8b1c02f6a'
down_revision: str | None = 'f2a9c3b81d47'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'clone_job',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('source_conn_id', sa.Uuid(), nullable=False),
        sa.Column('target_conn_id', sa.Uuid(), nullable=True),
        sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='clone'),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='pending'),
        sa.Column('target_db', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('total_tables', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('done_tables', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('ok_tables', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('skip_tables', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('fail_tables', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('rows_total', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('current_table', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('error', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['source_conn_id'], ['db_connection.id']),
        sa.ForeignKeyConstraint(['target_conn_id'], ['db_connection.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_clone_job_tenant_id'), 'clone_job', ['tenant_id'])
    op.create_index(op.f('ix_clone_job_source_conn_id'), 'clone_job', ['source_conn_id'])
    op.create_index(op.f('ix_clone_job_status'), 'clone_job', ['status'])

    op.create_table(
        'sync_state',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('connection_id', sa.Uuid(), nullable=False),
        sa.Column('table_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('watermark_column', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('watermark_mode', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('watermark_value', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_synced_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['connection_id'], ['db_connection.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sync_state_connection_id'), 'sync_state', ['connection_id'])
    op.create_index(op.f('ix_sync_state_table_name'), 'sync_state', ['table_name'])


def downgrade() -> None:
    op.drop_index(op.f('ix_sync_state_table_name'), table_name='sync_state')
    op.drop_index(op.f('ix_sync_state_connection_id'), table_name='sync_state')
    op.drop_table('sync_state')
    op.drop_index(op.f('ix_clone_job_status'), table_name='clone_job')
    op.drop_index(op.f('ix_clone_job_source_conn_id'), table_name='clone_job')
    op.drop_index(op.f('ix_clone_job_tenant_id'), table_name='clone_job')
    op.drop_table('clone_job')
