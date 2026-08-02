"""decision_record — KARAR KAYDI (Faz E-4)

Query Contract *"bu sayı nasıl hesaplandı"* sorusunu cevaplıyordu. Karar Kaydı bir üst
soruyu cevaplar: **"bu sayıya bakarak NE KARAR VERDİK ve neden?"** BI ürünlerinde eksik
olan halka budur — rapor kalır, kararın kendisi kaybolur ve altı ay sonra *"bunu neden
yapmıştık"* sorusunun cevabı kimsede olmaz.

`content_hash` gizli anahtarlı bir imza DEĞİL: bu bir kimlik doğrulama değil **kurcalama
tespitidir**. Kayıt sonradan değiştirilirse hash tutmaz ve okuma ucu bunu söyler.

Revision ID: c2a7e9f31b48
Revises: b9e4c1d70a25
Create Date: 2026-08-02 13:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'c2a7e9f31b48'
down_revision: str | None = 'b9e4c1d70a25'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_S = sqlmodel.sql.sqltypes.AutoString


def upgrade() -> None:
    op.create_table(
        'decision_record',
        sa.Column('id', _S(), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', _S(), nullable=True),
        sa.Column('user_id', _S(), nullable=True),
        sa.Column('session_id', _S(), nullable=True),
        sa.Column('question', _S(), nullable=True),
        sa.Column('chosen_json', _S(), nullable=True),
        sa.Column('options_json', _S(), nullable=True),
        sa.Column('rationale', _S(), nullable=True),
        sa.Column('note', _S(), nullable=True),
        sa.Column('contract_ids_json', _S(), nullable=True),
        sa.Column('content_hash', _S(), nullable=True),
        sa.Column('supersedes', _S(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_decision_record_ts', 'decision_record', ['ts'])
    op.create_index('ix_decision_record_tenant_id', 'decision_record', ['tenant_id'])
    op.create_index('ix_decision_record_user_id', 'decision_record', ['user_id'])
    op.create_index('ix_decision_record_session_id', 'decision_record', ['session_id'])
    op.create_index('ix_decision_record_content_hash', 'decision_record', ['content_hash'])


def downgrade() -> None:
    op.drop_table('decision_record')
