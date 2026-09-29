"""System/app logging (ADR-0020) — best-effort bloklar hatayı SESSİZCE yutmaz, buraya yazar.

Amaç: "kapsamlı log" hedefinin en sinsi düşmanını (kaybolan hatalar) kapatmak. Bu, dört log
yüzeyinden SYSTEM/APP olanıdır (audit/interaction/domain AYRI — ADR-0020). Yanıtı düşürmeyen
best-effort try/except blokları `except Exception: pass` yerine `log.warning(..., exc_info=True)`.

Kullanım:
    from app.logging_setup import get_logger
    log = get_logger("ask")
    ...
    except Exception:
        log.warning("konuşma kaydı yazılamadı (best-effort)", exc_info=True)
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED = False


def configure_logging(level: str | None = None) -> None:
    """`dima.*` logger ağacını bir kez yapılandırır (startup'ta çağrılır). İdempotent.

    Seviye sırası: **açık argüman** → `DIMA_LOG_LEVEL` env → `INFO` (varsayılan).

    ⚡ **Env kapısı neden var** (2026-08-09): tek korpus koşumu **54 180 `INFO` satırı**
    üretiyor ve bu satırlar dört katmandan geçiyor — `logging` biçimlendirme → `stdout`
    → docker `json-file` (JSON kodlama + disk) → kapının **satır satır Python okuması**.
    Korpus bu satırların **hiçbirini okumuyor**; sonucu HTTP yanıtlarından çıkarıyor.

    🔴 **Varsayılan BİLEREK `INFO` kaldı.** Bu depoda log seviyesine bağlı testler var
    (`test_ask_router_logging` · `test_llm_logging` · `test_sql_politikasi` ·
    `test_kapanis_zinciri`); varsayılanı düşürmek onları **sessizce** etkilerdi.
    *Bir hızlandırma, kendi kapsamının dışına taşarsa hızlandırma değil risktir.*

    ⚠ Teşhis için geri açmak tek env: `DIMA_LOG_LEVEL=INFO python lab/nl_corpus.py`
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    level = level or os.environ.get("DIMA_LOG_LEVEL") or "INFO"
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    root = logging.getLogger("dima")
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """`dima.<name>` logger'ı. configure_logging çağrılmamışsa da güvenli (lazy default)."""
    if not _CONFIGURED:
        configure_logging()
    return logging.getLogger(f"dima.{name}")
