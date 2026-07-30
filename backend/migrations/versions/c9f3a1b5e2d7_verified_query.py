"""verified_query — VQR Postgres'te (redeploy'da silinen JSONL yerine; ADR-0005/0008)

Öğrenilen soru→CubeQuery çiftleri companies/<şirket>/verified/queries.jsonl'de yaşıyordu;
Railway volume yalnız logs/'u kapsadığından her deploy'da siliniyordu. Kalıcı + admin-
küratörlük için Postgres. Soft-delete (deleted_at, ADR-0019).

Revision ID: c9f3a1b5e2d7
Revises: b8e2d0a4c6f1
Create Date: 2026-07-27 14:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'c9f3a1b5e2d7'
down_revision: str | None = 'b8e2d0a4c6f1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'verified_query',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('question_norm', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('cube_query_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('verified_by', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_verified_query_company'), 'verified_query', ['company'])
    op.create_index(op.f('ix_verified_query_tenant_id'), 'verified_query', ['tenant_id'])
    op.create_index(op.f('ix_verified_query_question_norm'), 'verified_query', ['question_norm'])
    op.create_index(op.f('ix_verified_query_deleted_at'), 'verified_query', ['deleted_at'])


def downgrade() -> None:
    for ix in ('deleted_at', 'question_norm', 'tenant_id', 'company'):
        op.drop_index(op.f(f'ix_verified_query_{ix}'), table_name='verified_query')
    op.drop_table('verified_query')
