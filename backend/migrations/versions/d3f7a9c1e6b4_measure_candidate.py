"""measure_candidate + measure_override — Discovery→Promote ölçü yaşam-döngüsü (Faz 2d)

+ mevcut tenant'lara admin/analyst Role satırı backfill'i (ölçü-onay reviewer rolü için
dar kapsamlı RBAC açılışı — bkz. admin_app/routers/tenants.py _DEFAULT_ROLES).

Revision ID: d3f7a9c1e6b4
Revises: c9e4a1b6d3f0
Create Date: 2026-07-31 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'd3f7a9c1e6b4'
down_revision: str | None = 'c9e4a1b6d3f0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'measure_candidate',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='draft'),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sql', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sample_rows_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('schema_version', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cube', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('measure_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('expression', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('measure_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='DOUBLE'),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('synonyms_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('lower_is_better', sa.Boolean(), nullable=True),
        sa.Column('golden_case_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('proposed_by', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('reviewed_by', sa.Uuid(), nullable=True),
        sa.Column('review_note', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('superseded_by_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['superseded_by_id'], ['measure_candidate.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_measure_candidate_tenant_id'), 'measure_candidate', ['tenant_id'])
    op.create_index(op.f('ix_measure_candidate_company'), 'measure_candidate', ['company'])
    op.create_index(op.f('ix_measure_candidate_status'), 'measure_candidate', ['status'])
    op.create_index(op.f('ix_measure_candidate_deleted_at'), 'measure_candidate', ['deleted_at'])

    op.create_table(
        'measure_override',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('scope_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('scope_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('cube', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('measure_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('reason', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('candidate_id', sa.Uuid(), nullable=True),
        sa.Column('superseded_by_measure', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['measure_candidate.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_measure_override_scope_type'), 'measure_override', ['scope_type'])
    op.create_index(op.f('ix_measure_override_scope_id'), 'measure_override', ['scope_id'])
    op.create_index(op.f('ix_measure_override_cube'), 'measure_override', ['cube'])
    op.create_index(op.f('ix_measure_override_measure_name'), 'measure_override', ['measure_name'])

    # Backfill: mevcut tenant'lara admin/analyst Role satırı ekle (yoksa) — reviewer rolü
    # bu satırlar OLMADAN kullanılamaz (users.py bir Role.key eşleşmesi arar).
    conn = op.get_bind()
    tenants = conn.execute(sa.text('SELECT id FROM tenant')).fetchall()
    for (tenant_id,) in tenants:
        existing = {row[0] for row in conn.execute(
            sa.text('SELECT key FROM role WHERE tenant_id = :tid'),
            {'tid': tenant_id}).fetchall()}
        for key in ('admin', 'analyst'):
            if key not in existing:
                conn.execute(sa.text(
                    'INSERT INTO role (id, tenant_id, key, name) VALUES '
                    '(:id, :tid, :key, :name)'
                ), {'id': str(__import__('uuid').uuid4()), 'tid': tenant_id,
                    'key': key, 'name': key.capitalize()})


def downgrade() -> None:
    # NOT: backfill edilen admin/analyst Role satırları downgrade'de KALDIRILMAZ (o
    # satırlara bağlı Membership/kullanıcı olabilir — geri-alma veri kaybı riski taşır).
    op.drop_index(op.f('ix_measure_override_measure_name'), table_name='measure_override')
    op.drop_index(op.f('ix_measure_override_cube'), table_name='measure_override')
    op.drop_index(op.f('ix_measure_override_scope_id'), table_name='measure_override')
    op.drop_index(op.f('ix_measure_override_scope_type'), table_name='measure_override')
    op.drop_table('measure_override')
    op.drop_index(op.f('ix_measure_candidate_deleted_at'), table_name='measure_candidate')
    op.drop_index(op.f('ix_measure_candidate_status'), table_name='measure_candidate')
    op.drop_index(op.f('ix_measure_candidate_company'), table_name='measure_candidate')
    op.drop_index(op.f('ix_measure_candidate_tenant_id'), table_name='measure_candidate')
    op.drop_table('measure_candidate')
