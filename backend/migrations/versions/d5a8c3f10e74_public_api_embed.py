"""FAZ 6.5 — idempotency anahtarı + `EmbedToken`.

🔴 Benzersizlik `(client_idempotency_key, tenant_id)` üstünde — tek başına anahtar DEĞİL:
iki kiracının aynı anahtarı seçmesi mümkündür ve o an biri ötekinin işini görürdü.
*Bir idempotency anahtarı, kiracı sınırının içinde benzersizdir.*

⚠ Kısıt **partial**: `client_idempotency_key IS NULL` olan satırlar kapsam dışı —
anahtar göndermeyen çağrılar idempotency İSTEMEMİŞTİR ve hepsini tek bir NULL'a
çarpıştırmak, onları birbirinin işi yapardı.

Revision ID: d5a8c3f10e74
Revises: c7f4a1e9b263
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "d5a8c3f10e74"
down_revision: str | None = "c7f4a1e9b263"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ask_job",
                  sa.Column("client_idempotency_key", sa.String(), nullable=True))
    op.create_index("ix_ask_job_client_idempotency_key", "ask_job",
                    ["client_idempotency_key"])
    op.create_index(
        "uq_ask_job_idem_tenant", "ask_job", ["client_idempotency_key", "tenant_id"],
        unique=True,
        postgresql_where=sa.text("client_idempotency_key IS NOT NULL"),
        sqlite_where=sa.text("client_idempotency_key IS NOT NULL"))
    op.create_table(
        "embed_token",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("scope_json", sa.String(), nullable=False, server_default="{}"),
        sa.Column("kota", sa.Integer(), nullable=True),
        sa.Column("son_kullanim", sa.DateTime(), nullable=True),
        sa.Column("iptal_edildi", sa.Boolean(), nullable=False,
                  server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_embed_token_iptal_edildi", "embed_token", ["iptal_edildi"])


def downgrade() -> None:
    op.drop_table("embed_token")
    op.drop_index("uq_ask_job_idem_tenant", table_name="ask_job")
    op.drop_index("ix_ask_job_client_idempotency_key", table_name="ask_job")
    op.drop_column("ask_job", "client_idempotency_key")
