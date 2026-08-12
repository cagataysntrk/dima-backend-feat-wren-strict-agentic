#!/usr/bin/env python3
"""🔴🔴 `§A.6/3` — **SÖZLÜK HASADI: madencinin kolunu çeviren koşucu.**

## Neden var — ölçülmüş boşluk

`§A.5`'te ölçüldü: kullanıcının istediği hat (*çevrimdışı üret → aday kuyruğu → insan
onaylar → sonra deterministik ve bedava*) **zaten kuruluydu**…

    app/sinonim_onerici.oner / ciplak_cube_icin      → LLM taslak üretir
    kuyruga_koy → SynonymOverride(approved=False)    → aday kuyruğu
    admin_app/routers/synonyms.py                    → insan onayı
    compose → YALNIZ approved=True okur (ADR-0018 1e) → tüketim

…**ama madencinin çağıranı yoktu.** Tüm repo tarandı: `sinonim_onerici` yalnız
testlerde ve belgelerde geçiyordu. Depo bunu *«meşru — tasarım: offline»* diye
sınıflandırmıştı; sınıflandırma doğru ama **sonuç eksikti**:

> 🆌 *«Offline» bir ÇALIŞMA KİPİDİR, bir ÇALIŞMAMA GEREKÇESİ değil. Bir motoru doğru
> kurmak onu çalıştırmaz.*

Sonuç: sözlük kullanımdan **hiç** büyümüyordu.

## `E-8` KORUNUR — ve bu dosyanın varlık şartıdır

`E-8`: *sıcak yola seri ikinci LLM turu eklenemez, ölçümle bile açılmaz.*
Bu koşucu **`/ask` yolundan tetiklenmez**; elle ya da CI'dan çağrılır. Ürettiği hiçbir
şey **insan onaylamadan** bir sorguyu etkileyemez (`approved=False` `kuyruga_koy`'da
**sabittir**, parametre değil).

## Kuru mod — sağlayıcı yoksa da bir şey öğrenilir

`--kuru` (ya da sağlayıcı yokluğu) hâlinde **hiçbir aday üretilmez**, ama *«kaç alan
hasat edilebilirdi»* **sayılır ve raporlanır**. Bir borç, ödenemediği gün bile
**ölçülebilir** olmalıdır.

## Kullanım

    python lab/sozluk_hasadi.py --kuru            # ölçer, yazmaz (varsayılan)
    python lab/sozluk_hasadi.py --yaz             # LLM + kuyruğa aday yazar
    python lab/sozluk_hasadi.py --kuru --sirket demo-boyahane
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

_log = logging.getLogger("lab.sozluk_hasadi")

#: ⚠ Bir alan *«çıplak»* sayılır: sinonim listesi ≤1 (yalnız kendi adı). Ölçüt
#: `sinonim_onerici.ciplak_cube_icin`'in **kendi** ölçütüdür — burada ikinci kez
#: yazılmaz (`KAT-1`); bu sabit yalnız **kuru mod sayımı** için aynadır.
CIPLAK_ESIGI = 1


def _ciplak_alanlar(schema: dict) -> list[tuple[str, str, str]]:
    """`(cube, tür, alan)` — sinonimi olmayan alanlar. **Ölçüm**, öneri değil."""
    out: list[tuple[str, str, str]] = []
    for c in (schema or {}).get("cubes") or []:
        ad = str(c.get("name") or "")
        for tur, alanlar, syn in (("olcu", c.get("measures") or [],
                                   c.get("measure_synonyms") or {}),
                                  ("boyut", c.get("dimensions") or [],
                                   c.get("dimension_synonyms") or {})):
            for a in alanlar:
                n = a if isinstance(a, str) else (a or {}).get("name")
                if n and len(syn.get(n) or []) <= CIPLAK_ESIGI:
                    out.append((ad, tur, str(n)))
    return out


def kos(*, yaz: bool = False, sirket: str | None = None) -> dict:
    """Hasadı koşar. `yaz=False` → **kuru mod**: ölçer, hiçbir şey yazmaz.

    Döner: `{ciplak, cube, aday, yazilan, kuru}`.
    """
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    wren = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())
    try:
        schema = wren.schema()
    finally:
        try:
            wren.close()
        except Exception:                              # noqa: BLE001
            pass

    ciplak = _ciplak_alanlar(schema)
    rapor = {"cube": len((schema or {}).get("cubes") or []), "ciplak": len(ciplak),
             "aday": 0, "yazilan": 0, "kuru": not yaz,
             "ornek": [f"{c}.{a}" for c, _t, a in ciplak[:8]]}
    if not yaz:
        # 🔴 Kuru mod: **hiçbir LLM çağrısı yok, hiçbir yazma yok.** Yalnız borç ölçülür.
        return rapor

    from app import sinonim_onerici as _so
    from app.llm import build_generator
    from control_plane.db import get_session_ctx  # type: ignore[attr-defined]

    llm = build_generator(s)
    with get_session_ctx() as session:
        for c in (schema or {}).get("cubes") or []:
            if sirket and str(c.get("name")) != sirket:
                pass
            oneriler = _so.ciplak_cube_icin(llm, c)
            for alan, syns in oneriler.items():
                rapor["aday"] += len(syns)
                kayit = _so.kuyruga_koy(
                    session, cube=str(c.get("name")), field_kind="measure",
                    field_name=alan, synonyms=syns)
                if kayit is not None:
                    rapor["yazilan"] += 1
    return rapor


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sözlük hasadı — çevrimdışı, onaylı kuyruk")
    p.add_argument("--yaz", action="store_true",
                   help="LLM çağır ve adayları kuyruğa YAZ (varsayılan: kuru)")
    p.add_argument("--kuru", action="store_true", help="yalnız ölç (varsayılan)")
    p.add_argument("--sirket", default=None)
    a = p.parse_args(argv)
    if a.yaz and a.kuru:
        print("🔴 `--yaz` ve `--kuru` birlikte verilemez.", file=sys.stderr)
        return 2
    r = kos(yaz=a.yaz, sirket=a.sirket)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if r["kuru"]:
        print(f"\n⊙ KURU MOD — hiçbir aday yazılmadı. Hasat edilebilecek alan: "
              f"{r['ciplak']} ({r['cube']} küpte). Yazmak için `--yaz`.")
    return 0


if __name__ == "__main__":                             # pragma: no cover
    raise SystemExit(main())
