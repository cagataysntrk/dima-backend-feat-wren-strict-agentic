"""ask_job.trace_json — canlı düşünme adımları (Faz 4.12)

Revision ID: f7b3d9a2c5e1
Revises: e2c6a8f4d1b9
Create Date: 2026-08-01 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'f7b3d9a2c5e1'
down_revision: str | None = 'e2c6a8f4d1b9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('ask_job', sa.Column('trace_json', sqlmodel.sql.sqltypes.AutoString(),
                                       nullable=True))


def downgrade() -> None:
    op.drop_column('ask_job', 'trace_json')
