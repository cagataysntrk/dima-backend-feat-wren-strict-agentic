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
import sys

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """`dima.*` logger ağacını bir kez yapılandırır (startup'ta çağrılır). İdempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return
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
