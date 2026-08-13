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
    # 🔴 `FAZ 8.6` — **İKİNCİ KAYNAK: KULLANIM.** Birincisi katalogdaki *çıplak* alanlar
    # (LLM'e sorulur); bu ise kullanıcının **gerçekten** yaptığı çeviri. İkisi ayrı
    # şeylerdir ve ayrı sayılır 🆋: biri *«sözlüğümüz eksik»*, öteki *«insanlar şuna
    # şu diyor»*. ⚠ Mevcut yol **bozulmadı** (`KURAL B`): `ciplak` hesabı ve kuru mod
    # davranışı aynen duruyor, rapor yalnız **alan kazandı**.
    tiklama = _tiklama_adaylari()
    rapor = {"cube": len((schema or {}).get("cubes") or []), "ciplak": len(ciplak),
             "aday": 0, "yazilan": 0, "kuru": not yaz,
             "tiklama_aday": len(tiklama),
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
        # 🔴 `8.6` — kullanımdan gelen adaylar **aynı kuyruğa**, **aynı kapıdan**:
        # `approved=False` orada sabittir, yani onaysız hiçbir şey `compose`'a girmez.
        # ⊘ İkinci bir kuyruk hattı kurulmadı (`KAT-1`).
        for ifade, kimlik in tiklama:
            cube, _, alan = kimlik.partition(".")
            if not cube or not alan:
                continue
            rapor["aday"] += 1
            kayit = _so.kuyruga_koy(session, cube=cube, field_kind="measure",
                                    field_name=alan, synonyms=[ifade])
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


def _tiklama_adaylari() -> list[tuple[str, str]]:
    """`FAZ 8.6` — `InteractionLog(kind="oneri_tik")` → **güçlü** sinyalli adaylar.

    ⚠ Karar burada **verilmez**: konum yanlılığı kuralının tek sahibi `app/hasat.py`
    (`sinyal`/`hasat_adaylari`) ve not biçiminin tek sahibi de orası (`not_oku`). Bu
    fonksiyon yalnız **satırları getirir** — bir okuyucu, bir yargıç değil.

    ⚠ 🅖 **Bugün bu kaynak BOŞ dönebilir ve bu bir kusur değildir:** `oneri_katmani`
    bayrağı **kapalı**, yani henüz tıklama üretilmiyor. Zincir kurulu; veri akmaya
    bayrak açılınca başlar. *Bir borunun boş olması, bağlı olmadığı anlamına gelmez.*

    ⚠ Oturum açılamazsa (`lab/` çoğu zaman DB'siz koşar) **sessizce boş** döner: hasat
    bir ölçüm aracıdır, ortam eksiğinde çökmesi ölçtüğü şeyi de durdurur.
    """
    from app.hasat import hasat_adaylari, not_oku

    try:
        from sqlmodel import select

        from control_plane.db import get_session_ctx  # type: ignore[attr-defined]
        from control_plane.models import InteractionLog
    except Exception:                                  # noqa: BLE001
        return []
    try:
        with get_session_ctx() as oturum:
            satirlar = oturum.exec(
                select(InteractionLog).where(InteractionLog.kind == "oneri_tik")
                .order_by(InteractionLog.ts.desc()).limit(2000)).all()
    except Exception:                                  # noqa: BLE001
        return []
    kayitlar = [t for r in satirlar
                if (t := not_oku(r.question, r.note)) is not None]
    return hasat_adaylari(kayitlar)


if __name__ == "__main__":                             # pragma: no cover
    raise SystemExit(main())
