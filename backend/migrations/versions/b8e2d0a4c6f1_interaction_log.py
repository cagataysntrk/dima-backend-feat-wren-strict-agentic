"""interaction_log — sorgu telemetrisi Postgres'te (ADR-0020; admin AYRI servis → ortak DB şart)

Revision ID: b8e2d0a4c6f1
Revises: a7c3f1e9d5b2
Create Date: 2026-07-27 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'b8e2d0a4c6f1'
down_revision: str | None = 'a7c3f1e9d5b2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'interaction_log',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('session_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('follow_up', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sql', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('rows', sa.Integer(), nullable=True),
        sa.Column('note', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('cube_query_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('trace_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('interpretation_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interaction_log_ts'), 'interaction_log', ['ts'])
    op.create_index(op.f('ix_interaction_log_session_id'), 'interaction_log', ['session_id'])
    op.create_index(op.f('ix_interaction_log_user_id'), 'interaction_log', ['user_id'])
    op.create_index(op.f('ix_interaction_log_tenant_id'), 'interaction_log', ['tenant_id'])
    op.create_index(op.f('ix_interaction_log_source'), 'interaction_log', ['source'])
    op.create_index(op.f('ix_interaction_log_kind'), 'interaction_log', ['kind'])


def downgrade() -> None:
    for ix in ('kind', 'source', 'tenant_id', 'user_id', 'session_id', 'ts'):
        op.drop_index(op.f(f'ix_interaction_log_{ix}'), table_name='interaction_log')
    op.drop_table('interaction_log')
