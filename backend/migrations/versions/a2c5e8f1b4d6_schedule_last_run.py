"""schedule_definition.last_run — koşum durumu Postgres'e (double-fire fix)

schedule-state.json (dosya, tek-servis volume) her instance'ın kendi state'ini okuyup
aynı zamanlanmış raporu iki kez koşuyordu (double-fire). Koşum durumu artık DB'de
(schedule_definition.last_run) + atomik CAS claim → çok-instance güvenli tek koşum.

Revision ID: a2c5e8f1b4d6
Revises: f1a9c3e5b7d2
Create Date: 2026-07-29 13:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a2c5e8f1b4d6'
down_revision: str | None = 'f1a9c3e5b7d2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('schedule_definition', sa.Column('last_run', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('schedule_definition', 'last_run')
