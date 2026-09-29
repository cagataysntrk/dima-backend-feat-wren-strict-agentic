"""contract_log — Query Contract kanıtı Postgres'e (tek-kaynak, ADR-0010)

contracts.jsonl (volume dosyası, tek-servis) admin plane (AYRI servis) tarafından
replay/denetim için okunamıyordu + managed backup yok + partial-write riski. Kanıt
artık Postgres'te (admin-erişilir, yedekli). Append-only (soft-delete yok — kanıt silinmez).

Revision ID: b7d3f0a9c2e4
Revises: a2c5e8f1b4d6
Create Date: 2026-07-29 13:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'b7d3f0a9c2e4'
down_revision: str | None = 'a2c5e8f1b4d6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'contract_log',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('session_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cube_query_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('sql', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('result_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('schema_version', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_contract_log_ts'), 'contract_log', ['ts'])
    op.create_index(op.f('ix_contract_log_session_id'), 'contract_log', ['session_id'])
    op.create_index(op.f('ix_contract_log_tenant_id'), 'contract_log', ['tenant_id'])


def downgrade() -> None:
    for ix in ('tenant_id', 'session_id', 'ts'):
        op.drop_index(op.f(f'ix_contract_log_{ix}'), table_name='contract_log')
    op.drop_table('contract_log')
