"""KPI pin — `dashboard_widget.pinned`

🔴 **FAZ 5.10 bağlandı.** `app/kpi_pin.py` (85 satır, 10 test) üretim kodunda **hiç
import edilmiyordu**: pin semantiği yazılmış, kolonu yokmuş. Denetimin *"12 yetim
modül"* bulgusunun dördüncü kalemi.

⚠ `nullable=False, default=False`: mevcut widget'lar **pin'siz doğar** ve bu doğrudur —
*hiç kimse onları pin'lemedi.* `NULL` bırakmak, "pin'lenmemiş" ile "bilinmiyor"u
karıştırırdı.

Revision ID: a2d5e81c93f7
Revises: f1a7c92d4b60
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a2d5e81c93f7"
down_revision = "f1a7c92d4b60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dashboard_widget",
                  sa.Column("pinned", sa.Boolean(), nullable=False,
                            server_default=sa.false()))


def downgrade() -> None:
    # ⚠ Geri alma **pin kararlarını siler**: kullanıcının kendi eliyle koyduğu işaretler
    # kaybolur. Yazılı, çünkü sessiz bir kayıp fark edilmez.
    op.drop_column("dashboard_widget", "pinned")
