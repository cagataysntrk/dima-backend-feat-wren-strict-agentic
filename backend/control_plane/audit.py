"""Audit yazıcı — her veri erişimi/yetki eylemi AuditLog'a (ADR-0014 Karar 6).

Tek giriş noktası: ``record(...)``. Sorgu yolu principal'ı request.state'ten alır;
admin eylemleri principal'ı doğrudan geçirir.

DAYANIKLILIK (ADR-0014 mamut invariant #4 "başarı, audit yazılmadan raporlanmaz"):
audit KAYBOLMAZ. Yol:
  1. DB'ye yaz (normal).
  2. DB yazılamazsa → yerel **durable spool** dosyasına (``logs/audit-spool.jsonl``)
     ekle; istek AKMAYA devam eder (audit dayanıklı biçimde yakalandığından başarı
     raporlanabilir). ``replay_spool()`` startup'ta bunu DB'ye boşaltır.
  3. Hem DB HEM spool yazılamazsa → **fail-closed**: hata yükseltilir (gerçekten
     kurtarılamaz durum; başarı audit'siz raporlanamaz).
Disk-tabanlı spool prod'da volume'da yaşar; Postgres kısa süreli düşse bile istek
kırılmaz ve tek bir audit bile kaybolmaz.
"""

from __future__ import annotations

import json
import sys
import uuid as _uuid
from datetime import datetime

from sqlmodel import Session

from app.config import BASE_DIR
from control_plane.authorize import Principal
from control_plane.db import engine
from control_plane.models import AuditLog

_SPOOL_PATH = BASE_DIR / "logs" / "audit-spool.jsonl"


def _uuid_or_none(val: str | None) -> _uuid.UUID | None:
    try:
        return _uuid.UUID(val) if val else None
    except (ValueError, TypeError):
        return None


def _row_from_payload(p: dict) -> AuditLog:
    """Serileştirilmiş payload → AuditLog satırı (DB insert / spool replay ortak yolu)."""
    return AuditLog(
        tenant_id=_uuid_or_none(p.get("tenant_id")),
        actor_user_id=_uuid_or_none(p.get("actor_user_id")),
        actor_kind=p.get("actor_kind") or "system",
        role_key=p.get("role_key"),
        action=p.get("action") or "query",
        nl_question=p.get("nl_question"),
        generated_sql=p.get("generated_sql"),
        rows_returned=p.get("rows_returned"),
        contract_id=p.get("contract_id"),
        ip=p.get("ip"),
        touched_models_json=p.get("touched_models_json"),
        masked_columns_json=p.get("masked_columns_json"),
        ts=datetime.fromisoformat(p["ts"]) if p.get("ts") else datetime.utcnow(),
    )


def _persist(row: AuditLog) -> None:
    with Session(engine) as session:
        session.add(row)
        session.commit()


def _spool_append(payload: dict) -> None:
    _SPOOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _SPOOL_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def record(
    principal: Principal | None,
    action: str,
    *,
    nl_question: str | None = None,
    generated_sql: str | None = None,
    rows_returned: int | None = None,
    contract_id: str | None = None,
    ip: str | None = None,
    touched_models_json: str | None = None,
    masked_columns_json: str | None = None,
) -> None:
    # Alanlar bir kez çözülür → DB satırı ve spool payload'ı AYNI kaynaktan üretilir
    # (ts dahil; spool'a düşse de orijinal zaman korunur).
    payload = {
        "tenant_id": principal.tenant_id if principal else None,
        "actor_user_id": principal.user_id if principal else None,
        "actor_kind": (
            ("superadmin" if principal.is_superadmin else "user") if principal else "system"
        ),
        "role_key": (principal.roles[0] if principal and principal.roles else None),
        "action": action,
        "nl_question": nl_question,
        "generated_sql": generated_sql,
        "rows_returned": rows_returned,
        "contract_id": contract_id,
        "ip": ip,
        "touched_models_json": touched_models_json,
        "masked_columns_json": masked_columns_json,
        "ts": datetime.utcnow().isoformat(),
    }
    try:
        _persist(_row_from_payload(payload))
        return
    except Exception as db_exc:
        # DB yazılamadı → dayanıklı spool'a al (kayıp yok, istek akmaya devam eder).
        try:
            _spool_append(payload)
            print(f"[audit] DB yazılamadı, spool'a alındı: {db_exc}", file=sys.stderr)
            return
        except Exception as spool_exc:
            # Hem DB HEM spool başarısız → fail-closed: başarı audit'siz raporlanamaz.
            print(
                f"[audit] KRİTİK — DB ve spool yazılamadı: {db_exc} / {spool_exc}",
                file=sys.stderr,
            )
            raise


def replay_spool() -> int:
    """Startup'ta spool'daki bekleyen audit'leri DB'ye boşaltır. Boşaltılan satır
    sayısını döner. Boşaltılamayanlar (DB hâlâ down) dosyada KALIR → sonraki
    startup'ta yeniden denenir. Idempotent değil (çift-kayıt nadir ve zararsız);
    kayıp asla olmaz."""
    if not _SPOOL_PATH.exists():
        return 0
    try:
        lines = _SPOOL_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return 0
    if not any(ln.strip() for ln in lines):
        try:
            _SPOOL_PATH.unlink()
        except Exception:
            pass
        return 0

    remaining: list[str] = []
    flushed = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            _persist(_row_from_payload(json.loads(line)))
            flushed += 1
        except Exception:
            remaining.append(line)  # DB hâlâ yazılamıyor → sakla, sonra dene

    try:
        if remaining:
            _SPOOL_PATH.write_text("\n".join(remaining) + "\n", encoding="utf-8")
        else:
            _SPOOL_PATH.unlink()
    except Exception:
        pass
    if flushed:
        print(f"[audit] spool boşaltıldı: {flushed} kayıt DB'ye yazıldı", file=sys.stderr)
    return flushed
