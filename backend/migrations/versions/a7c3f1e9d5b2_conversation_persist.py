"""conversation + conversation_message — kullanıcı sohbetlerini kalıcı sakla (per-user, tenant-izole)

Revision ID: a7c3f1e9d5b2
Revises: d4e8b1c02f6a
Create Date: 2026-07-27 10:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'a7c3f1e9d5b2'
down_revision: str | None = 'd4e8b1c02f6a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'conversation',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('session_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=''),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),  # soft delete (proje kuralı)
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversation_tenant_id'), 'conversation', ['tenant_id'])
    op.create_index(op.f('ix_conversation_deleted_at'), 'conversation', ['deleted_at'])
    op.create_index(op.f('ix_conversation_user_id'), 'conversation', ['user_id'])
    op.create_index(op.f('ix_conversation_session_id'), 'conversation', ['session_id'])
    op.create_index(op.f('ix_conversation_updated_at'), 'conversation', ['updated_at'])

    op.create_table(
        'conversation_message',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('conversation_id', sa.Uuid(), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('question', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=''),
        sa.Column('payload_json', sqlmodel.sql.sqltypes.AutoString(), nullable=False,
                  server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversation_message_conversation_id'), 'conversation_message',
                    ['conversation_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_conversation_message_conversation_id'),
                  table_name='conversation_message')
    op.drop_table('conversation_message')
    op.drop_index(op.f('ix_conversation_deleted_at'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_updated_at'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_session_id'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_user_id'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_tenant_id'), table_name='conversation')
    op.drop_table('conversation')
