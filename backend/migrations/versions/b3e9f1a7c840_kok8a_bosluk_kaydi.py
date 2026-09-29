"""interaction_log.uncovered_words + aday_cubelar — KÖK-8a (denetim raporu)

🔴 SÖZLÜK BOŞLUĞU TAHMİNLE DEĞİL ÖLÇÜMLE KAPANIR.

`reject_reason` "hangi dalda pes ettim" der (R1…R10) ama **hangi kelime yüzünden**
demez. Bu iki kolon o soruyu cevaplanabilir kılar:

    SELECT uncovered_words, COUNT(*) FROM interaction_log
    WHERE reject_reason IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 20;

⚠ Girdi **gerçek kullanıcı cümleleridir** — yani "sistemi kendi aynasında ölçme"
tuzağına yapısal olarak düşemez.

Revision ID: b3e9f1a7c840
Revises: a2d5e81c93f7
Create Date: 2026-08-05 20:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'b3e9f1a7c840'
down_revision: str | None = 'a2d5e81c93f7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("interaction_log", sa.Column("uncovered_words", sa.String(), nullable=True))
    op.add_column("interaction_log", sa.Column("aday_cubelar", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("interaction_log", "aday_cubelar")
    op.drop_column("interaction_log", "uncovered_words")
