"""interaction_log aktör-ID'leri → UUID (AuditLog ile tutarlı)

InteractionLog.user_id/tenant_id STRING'di ama str(uuid) tutuyordu; AuditLog UUID.
Cross-table JOIN cast gerektiriyordu. Tip UUID'ye çekilir → tutarlı, cast'siz analitik.

Değerler zaten geçerli str(uuid) (principal'dan); Postgres `::uuid` cast temiz dönüştürür.
Canlı-öncesi olduğundan geçmiş veri temiz varsayılır — geçersiz (UUID-olmayan) eski değer
kalırsa cast öncesi NULL'lanmalı (tek-seferlik script), ama beklenmiyor.

Revision ID: c9e4a1b6d3f0
Revises: b7d3f0a9c2e4
Create Date: 2026-07-29 14:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'c9e4a1b6d3f0'
down_revision: str | None = 'b7d3f0a9c2e4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('interaction_log') as batch:
        batch.alter_column('user_id', existing_type=sa.String(), type_=sa.Uuid(),
                           existing_nullable=True, postgresql_using='user_id::uuid')
        batch.alter_column('tenant_id', existing_type=sa.String(), type_=sa.Uuid(),
                           existing_nullable=True, postgresql_using='tenant_id::uuid')


def downgrade() -> None:
    with op.batch_alter_table('interaction_log') as batch:
        batch.alter_column('user_id', existing_type=sa.Uuid(), type_=sa.String(),
                           existing_nullable=True, postgresql_using='user_id::text')
        batch.alter_column('tenant_id', existing_type=sa.Uuid(), type_=sa.String(),
                           existing_nullable=True, postgresql_using='tenant_id::text')
