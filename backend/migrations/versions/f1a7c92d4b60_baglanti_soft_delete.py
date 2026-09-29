"""bağlantı soft-delete — hard-delete kuralı ihlali kapandı

🔴 **Ölçülen ihlal.** `app/routers/connections.py::delete_connection` `s.delete(conn)`
yapıyordu — bir **hard-delete**. Oysa `app/routers/conversations.py:121` kuralı birebir
yazıyor: *"SOFT DELETE (proje kuralı: hard-delete YOK): kayıt+mesajlar kalır
(audit/kurtarma)."*

⚠ Ve en pahalı nesnede: `db_connection` **AES-256-GCM ile şifrelenmiş kimlik bilgisi**
(`secret_ciphertext`) taşıyor. Satır silindiğinde:
  · kimlik bilgisi **geri getirilemez** — kullanıcı bağlantıyı sıfırdan kurar,
  · `audit.record(..., "connection_delete", nl_question=cid)` kaydı **konusu olmayan bir
    kimliğe** işaret eder, yani denetim izi *"neyin silindiğini"* söyleyemez.

*Bir silme kaydı, sildiği şeye artık ulaşamıyorsa, bir kayıt değil bir dipnottur.*

Revision ID: f1a7c92d4b60
Revises: e9b2d4a71c58
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f1a7c92d4b60"
down_revision = "e9b2d4a71c58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ⚠ `nullable=True` **zorunlu**: mevcut satırlar silinmemiştir ve onlara bir silme
    # damgası uydurmak, geçmişi yeniden yazmak olurdu.
    op.add_column("db_connection",
                  sa.Column("deleted_at", sa.DateTime(), nullable=True))
    # ⚠ İndeks: her okuma yolu `deleted_at IS NULL` süzecek; süzgeçsiz bir indeks,
    # süzgecin kendisi kadar gereklidir.
    op.create_index("ix_db_connection_deleted_at", "db_connection", ["deleted_at"])


def downgrade() -> None:
    # 🔴 Geri alma **veri kaybeder**: silinmiş sayılan satırlar geri alındığında yeniden
    # "canlı" görünür. Bu yazılı, çünkü sessiz bir geri alma daha kötüdür.
    op.drop_index("ix_db_connection_deleted_at", table_name="db_connection")
    op.drop_column("db_connection", "deleted_at")
