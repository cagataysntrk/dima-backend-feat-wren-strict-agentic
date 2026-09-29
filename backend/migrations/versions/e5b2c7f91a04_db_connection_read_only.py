"""db_connection.read_only_verified — müşteri DB kullanıcısı salt-okunur doğrulaması

Revision ID: e5b2c7f91a04
Revises: c1f8a4d27e93
Create Date: 2026-07-24 20:15:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'e5b2c7f91a04'
down_revision: str | None = 'c1f8a4d27e93'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('db_connection',
                  sa.Column('read_only_verified', sa.Boolean(), nullable=False,
                            server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('db_connection', 'read_only_verified')
