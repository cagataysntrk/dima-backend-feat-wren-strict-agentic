"""FAZ 6.6 — `KanalKimlikEslemesi`.

🔴 `onaylayan_admin_id` **nullable DEĞİL**: bir eşlemenin *kim tarafından onaylandığı*
opsiyonel olsaydı, e-postadan çıkarılmış bir eşleme sessizce yazılabilirdi — ve şemanın
kendisi o kısayolu **mümkün** kılardı. *Bir zorunluluğu belgede tutup şemada tutmamak,
onu bir temenniye çevirir.*

Revision ID: e9b2d4a71c58
Revises: d5a8c3f10e74
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "e9b2d4a71c58"
down_revision: str | None = "d5a8c3f10e74"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kanal_kimlik_eslemesi",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kanal", sa.String(), nullable=False, index=True),
        sa.Column("kanal_kullanici_id", sa.String(), nullable=False, index=True),
        sa.Column("dima_user_id", sa.String(), nullable=False, index=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=True, index=True),
        # 🔴 NOT NULL — kısayol şemada da kapalı.
        sa.Column("onaylayan_admin_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True, index=True),
    )
    op.create_index("uq_kanal_kimlik", "kanal_kimlik_eslemesi",
                    ["kanal", "kanal_kullanici_id", "tenant_id"], unique=True,
                    postgresql_where=sa.text("deleted_at IS NULL"),
                    sqlite_where=sa.text("deleted_at IS NULL"))


def downgrade() -> None:
    op.drop_table("kanal_kimlik_eslemesi")
