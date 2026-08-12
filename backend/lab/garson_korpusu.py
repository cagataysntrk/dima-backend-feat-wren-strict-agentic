#!/usr/bin/env python3
"""🔴🔴 `§B.6/②` · `A1` — **GARSON KORPUSU: kapı route()'u ölçüyordu, garsonu ölçmüyordu.**

## Neden var — deponun KENDİ ilan ettiği ön koşul

`demo/packs/features.yml:222`:

> *«Geniş yayılım için ön koşul `A1` (garson korpusu): **kapı `route()`'u ölçer, garsonu
> ölçmez** — bu bayrağın gerilemesi kapıda **GÖRÜNMEZ**.»*

`§B.5`'te ölçüldü: garson **geliştirilmiş** (istem **161 satır** · tool-calling · few-shot
· `consistency_k=3` · çoğunluk oylaması · şema daraltma). Ama korpus (**%94,9**, LLM'siz)
yalnız `route()` yolunu sınıyor. Sonuç üç yönlü:

- bir garson iyileştirmesinin **kazancı** ölçülemiyor,
- bir garson **gerilemesi** kapıda **görünmüyor**,
- `sema_daraltma` gibi bayraklar `beta`'da **kanıtla** tutuluyor, **sayıyla** değil.

> 🆕 *Ölçülmeyen bir bileşen geliştirilebilir ama iyileştirilemez: iyileştirme, iki
> ölçüm arasındaki farktır.*

## Ne ölçer

Katalogdan **etiketli** vaka üretir — *«bu ölçü hangi küpe ait»* zaten **bilinen** bir
gerçektir, uydurulmaz — ve **garsona** (`llm.select_cube`) sorar: *«hangi küpü seçtin?»*
Doğru küp **katalogdan** gelir, ölçümden değil.

## `E-8` KORUNUR

Bu bir **çevrimdışı ölçüm**tür: `/ask` yolundan tetiklenmez, sıcak yola hiçbir şey
eklemez. `lab/` altında, elle ya da CI'dan koşar.

## Kuru mod — ve neden VARSAYILAN

Sağlayıcı yoksa **hiçbir LLM çağrılmaz**; yalnız *«kaç vaka ölçülebilirdi»* sayılır.
`sozluk_hasadi.py`'nin kalıbı: *bir borç, ödenemediği gün bile ölçülebilir olmalıdır.*

⚠ **Sessizce `rule` ile koşmak YASAK** — `nl_accuracy.py`'nin kendi dersi: *«sessizce
`rule` ile koşan bir kazanç ölçümü, hiç koşmamaktan kötüdür çünkü bayrak kararı ona
dayanır.»* `--canli` verilmişse sağlayıcı **zorunludur**; yoksa **koşmaz**.

⚠ **PAYDA KUTSAL:** bu ölçüm `nl_corpus`'un paydasına **dokunmaz**; ayrı bir rapor üretir.

## Kullanım

    python lab/garson_korpusu.py            # kuru: kaç vaka var, LLM YOK
    python lab/garson_korpusu.py --canli    # gerçek garson; sağlayıcı yoksa KOŞMAZ
"""

from __future__ import annotations

import argparse
import json
import sys

#: ⚠ Vaka **katalogdan** üretilir, elle yazılmaz: *«`toplam_ciro` hangi küpte»* bir
#: ölçüm değil bir **beyandır** ve katalog onun tek sahibidir (`KAT-1`).
#: ⊙ Yalnız **tek sahipli** ölçüler vaka olur — çok sahipli bir terimde *«doğru küp»*
#: diye bir şey **yoktur** (`§B.1`: route zaten çekiliyor, `§A.2`: 73 terim).
#: *Bir ölçütü, cevabı belirsiz olan girdilerle sınamak, ölçümü gürültüye çevirir.*
AZAMI_VAKA = 40


def _vakalar(schema: dict) -> list[dict]:
    """`(soru, beklenen_cube)` — **tek sahipli** ölçülerden."""
    sahip: dict[str, set[str]] = {}
    etiket: dict[str, str] = {}
    for c in (schema or {}).get("cubes") or []:
        disp = c.get("measure_synonyms_display") or {}
        for m in c.get("measures") or []:
            ad = m if isinstance(m, str) else (m or {}).get("name")
            if not ad:
                continue
            sahip.setdefault(str(ad), set()).add(str(c.get("name")))
            etiket.setdefault(str(ad), str(disp.get(ad) or ad).replace("_", " "))
    out = []
    for ad, kupler in sorted(sahip.items()):
        if len(kupler) != 1:
            continue                                   # çok sahipli → doğru cevap YOK
        out.append({"soru": f"bu yıl {etiket[ad]}", "cube": next(iter(kupler)),
                    "olcu": ad})
    return out[:AZAMI_VAKA]


def kos(*, canli: bool = False) -> dict:
    """Döner: `{vaka, olculen, dogru, yanlis, cevapsiz, kuru, oran}`."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    w = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                    connection_info=s.connection_dict())
    try:
        schema = w.schema()
    finally:
        try:
            w.close()
        except Exception:                              # noqa: BLE001
            pass

    vakalar = _vakalar(schema)
    rapor = {"vaka": len(vakalar), "olculen": 0, "dogru": 0, "yanlis": 0,
             "cevapsiz": 0, "kuru": not canli, "oran": None,
             "ornek": [v["soru"] for v in vakalar[:5]]}
    if not canli:
        return rapor

    # 🔴 Sağlayıcı ZORUNLU — sessizce `rule` ile koşmak yasak (`nl_accuracy` dersi).
    from lab.konusma_senaryolari import _canli_ortami_geri_yukle

    _sag = _canli_ortami_geri_yukle()
    if not _sag:
        rapor["hata"] = ("⊘ sağlayıcı yok — `--canli` KOŞMADI. Sessizce `rule` ile "
                         "koşan bir garson ölçümü, hiç koşmamaktan kötüdür.")
        return rapor

    from app.katalog_metni import envanter
    from app.llm import build_generator

    llm = build_generator(s)
    katalog = envanter(schema)
    for v in vakalar:
        try:
            ham = llm.select_cube(v["soru"], katalog, schema)
            secilen = (json.loads(ham) or {}).get("cube")
        except Exception:                              # noqa: BLE001 — vaka düşer, koşum sürer
            secilen = None
        rapor["olculen"] += 1
        if not secilen:
            rapor["cevapsiz"] += 1
        elif str(secilen) == v["cube"]:
            rapor["dogru"] += 1
        else:
            rapor["yanlis"] += 1
    if rapor["olculen"]:
        rapor["oran"] = round(100.0 * rapor["dogru"] / rapor["olculen"], 1)
    return rapor


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Garson korpusu — çevrimdışı ölçüm (A1)")
    p.add_argument("--canli", action="store_true",
                   help="gerçek garsonu çağır (sağlayıcı yoksa KOŞMAZ)")
    a = p.parse_args(argv)
    r = kos(canli=a.canli)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if r["kuru"]:
        print(f"\n⊙ KURU MOD — LLM çağrılmadı. Ölçülebilecek vaka: {r['vaka']}. "
              "Gerçek ölçüm için `--canli`.")
    elif r.get("hata"):
        print(f"\n{r['hata']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":                             # pragma: no cover
    raise SystemExit(main())
