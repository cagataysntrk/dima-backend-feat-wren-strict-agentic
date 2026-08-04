"""FAZ 5.16 — `TenantConfig.netlestirme_duzeyi`.

⚠ Nullable ve varsayılan `None` → `normal` → **bugünkü davranış BİREBİR**. Bir göç,
sessizce bir ürün kararı veremez: sütunu `"normal"` ile doldurmak da aynı sonucu verirdi
ama o zaman *"kimse seçmedi"* ile *"herkes normal seçti"* ayırt edilemezdi.

Revision ID: c7f4a1e9b263
Revises: b3e9c1f7a482
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "c7f4a1e9b263"
down_revision: str | None = "b3e9c1f7a482"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenant_config",
                  sa.Column("netlestirme_duzeyi", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenant_config", "netlestirme_duzeyi")
