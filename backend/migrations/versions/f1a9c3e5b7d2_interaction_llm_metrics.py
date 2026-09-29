"""interaction_log LLM metrikleri (model/token/latency)

InteractionLog'a LLM çağrı telemetrisi kolonları: yalnız LLM yoluna düşen istekte
dolar (cube/rule yolunda NULL). Maliyet/performans görünürlüğü — model bazında
token toplamı ve gecikme. Hepsi nullable (geriye dönük kayıtlar NULL kalır).

Revision ID: f1a9c3e5b7d2
Revises: d8f4b2a6c1e7
Create Date: 2026-07-29 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = 'f1a9c3e5b7d2'
down_revision: str | None = 'd8f4b2a6c1e7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('interaction_log', sa.Column('llm_model', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('interaction_log', sa.Column('llm_input_tokens', sa.Integer(), nullable=True))
    op.add_column('interaction_log', sa.Column('llm_output_tokens', sa.Integer(), nullable=True))
    op.add_column('interaction_log', sa.Column('llm_latency_ms', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('interaction_log', 'llm_latency_ms')
    op.drop_column('interaction_log', 'llm_output_tokens')
    op.drop_column('interaction_log', 'llm_input_tokens')
    op.drop_column('interaction_log', 'llm_model')
