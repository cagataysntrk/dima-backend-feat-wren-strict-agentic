"""verified_query küratörlük alanları (Faz 4.1)

`verified_at` — doğrulamanın NE ZAMAN yapıldığı (bugüne kadar yalnız `verified_by` vardı).
`use_as_onboarding_question` — kaydın yeni kullanıcıya örnek soru olarak gösterilmeye uygun
olup olmadığı. Ayrı bir alandır çünkü "doğru" ile "temsili" aynı şey değildir.

Bu göç ŞEMA'yı değiştirir; güven kapısının kendisi `source` alanı üzerinden çalışır ve kod
tarafındadır (`app/vqr.py::_TRUSTED_SOURCES`). Mevcut `source="auto"` satırları BİLEREK
dönüştürülmez: hangi yoldan geldikleri (Intent-JSON mı, ham Discovery SQL'i mi) kayıtta
YOK ve tahmin etmek, güvenilmez kayıtları güvenilir sayma riski taşır. Kökeni bilinmeyen
kayıt güvenilmezdir; yeni yazımlar `auto_cube` / `auto_discovery` olarak ayrışır.

Revision ID: a4d8f2c6e903
Revises: f7b3d9a2c5e1
Create Date: 2026-08-02 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a4d8f2c6e903"
down_revision: str | None = "f7b3d9a2c5e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("verified_query", sa.Column("verified_at", sa.DateTime(), nullable=True))
    op.add_column(
        "verified_query",
        sa.Column("use_as_onboarding_question", sa.Boolean(), nullable=False,
                  server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("verified_query", "use_as_onboarding_question")
    op.drop_column("verified_query", "verified_at")
