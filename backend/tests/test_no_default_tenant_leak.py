"""Statik-analiz regresyon kilidi (Faz 0-c): `request.app.state.wren`'i doğrudan kullanan
router kodu, non-default tenant için SÜREÇ VARSAYILANI şirketin servisini/veritabanını
kullanır — kanıtlanmış cross-tenant sızıntı sınıfı (schedules.py'deki zamanlanmış rapor
sızıntısı + dashboards.py'deki pano-veri sızıntısı buradan çıktı, ikisi de düzeltildi).

Doğru desen HER ZAMAN `app.company_registry.wren_for_request(request)` — o da isteğin
`request.state.wren` (require_company'nin bağladığı tenant-özel servis) ile
`request.app.state.wren` (süreç varsayılanı) arasında doğru seçimi yapan TEK yer.

Bu test yeni bir router bu deseni yeniden ihlal ederse (geliştirici `wren_for_request`
kullanmayı unutursa) CI'da KIRMIZI yanar — davranışsal test değil, ama regresyonu
davranışsal bir hata canlıya çıkmadan yakalayan ucuz bir statik kilit."""

from __future__ import annotations

import re
from pathlib import Path

_ROUTERS_DIR = Path(__file__).resolve().parent.parent / "app" / "routers"

# health.py: process-level readiness kontrolü — kasıtlı olarak tenant'tan bağımsız
# (MDL derlenmiş mi / DB erişilebilir mi), bu yüzden süreç varsayılanını kullanması DOĞRU.
_ALLOWED = {"health.py"}

_BAD_PATTERN = re.compile(r"request\.app\.state\.wren\b")


def test_no_router_bypasses_wren_for_request():
    offenders: list[str] = []
    for py_file in sorted(_ROUTERS_DIR.glob("*.py")):
        if py_file.name in _ALLOWED:
            continue
        text = py_file.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # yorum satırındaki geçmiş-hata açıklamaları (bkz. dashboards.py) sayılmaz
            if _BAD_PATTERN.search(line):
                offenders.append(f"{py_file.name}:{i}: {stripped}")
    assert not offenders, (
        "request.app.state.wren doğrudan kullanılmış (tenant-özel wren_for_request(request) "
        "yerine) — bu, kanıtlanmış cross-tenant veri sızıntısı sınıfının aynısı "
        "(bkz. app/schedules.py, app/routers/dashboards.py düzeltmeleri):\n" + "\n".join(offenders)
    )
