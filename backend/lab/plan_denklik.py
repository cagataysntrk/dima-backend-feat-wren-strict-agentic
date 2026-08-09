"""`O-13` — **DENKLİK KAPISI.** Göçün kabul ölçütü bir A/B değil, bir **eşitliktir**.

## Neden A/B yanlış alet

`EE` turunun aleti (arıza oranı) bu karar için yanlıştı: paydası **küçülüyor** (mutfak
iyileştikçe orkestratörün toprağı daralıyor), LLM'e/kotaya/konteynere bağımlı, ve
*"cevap **tam** mı"* sorusunu **hiç göremiyor** — bir cevap üçte biri eksik olsa da
`source=cube+llm` rozetiyle ✅ sayılıyor.

## Ölçüt — tek cümle

> Bugün tek adımda cevaplanan **her** soru için, plan **1 adım** çıkarmalı ve
> `tek_adimli()`'nin döndürdüğü `cube_query`, bugünkü `select_cube`'un ürettiğiyle
> **birebir aynı** olmalı.

Üç işi birden yapar:

* route↔garson sınırını (~100 testin kazandığı ayrım) **koruyor** — bozulursa **kapı**
  kırmızı yanar, canlıda değil
* *«soru tek adımlaysa tek adım yaz»* dileğini bir **kapıya** çevirir (`R2`)
* `payda kutsaldır`: aynı sorular, aynı sırayla, tek payda

⚠ Kanonikleştirme `cube_router._canon_cq` ile — ikinci bir karşılaştırıcı yazmak, iki
farklı *"aynı"* tanımı demekti (`KAT-1`).

## Kullanım

    python lab/plan_denklik.py --sorular korpus.txt
    python lab/plan_denklik.py --kapi          # çıkış kodu: 0 geçti, 1 kaldı
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: 🔴 **TEK ADIMLI** olması beklenen sorular — göçün asıl riski (`R2`) burada.
#: İstem 15 fiile genişledi; basit bir sorunun **basit kalması** artık bir dilek değil
#: bir iddia olmalı.
SONDALAR: tuple[str, ...] = (
    "bu yıl toplam ciro",
    "makinelere göre ortalama oee",
    "geçen ay toplam fire",
    "müşterilere göre ciro bu yıl",
    "bu yıl aylara göre üretim miktarı",
    "en yüksek cirolu 5 müşteri",
    "vardiyaya göre ilk seferde tamam oranı",
    "bu çeyrek toplam enerji tüketimi",
)

#: 🔴🔴 **EŞİK MUTLAK DEĞİL, TABANA GÖRELİDİR — ve bu bir gevşetme değil, bir DÜZELTMEDİR.**
#:
#: İlk hâl `AZAMI_SAPMA = 0` idi. Ölçüldü (`§86.6` — *önce tabanı ölç*): bugünkü
#: `select_cube` **kendisiyle bile** 5 sorunun 1'inde anlaşmıyor. Yani sıfır eşik,
#: plandan `select_cube`'un **kendinden bile isteyemediği** bir tutarlılık istiyordu.
#:
#: ⊙ Kalan sapmaların hepsi aynı sınıftan çıktı: `toplam_fire_kg` · `ilk_seferde_tamam_
#: yuzde` · enerji ölçüleri **iki küpte birden** tanımlı. Bu bir plan kusuru değil,
#: deponun **kayıtlı** belirsizlik sınıfı (`measure_cube_candidates` · netleştirme).
#:
#: Doğru ölçüt: **plan sapması ≤ tabanın kendi sapması**. Plan, bugünkü yoldan daha
#: kararsız olmamalı — daha kararlı olması *istenir*, ama şart koşulan bu değil.
#:
#: *Bir eşiği, ölçmediğin bir tabana göre koymak, kendi beklentini ölçü sanmaktır.*
PAY = 0     # tabanın üstüne izin verilen ek sapma; 0 = "daha kötü olamaz"


def _kur():
    from app.config import get_settings
    from app.katalog_metni import metin_ve_indeks
    from app.llm import build_generator
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    catalog, index = metin_ve_indeks(svc.schema(), None)
    return build_generator(s), catalog, index


def olc(sorular, llm, catalog, index) -> dict:
    from app import plan_garson
    from app.cube_router import parse_cube_query
    from app.routers.ask import _canon_cq   # ⚠ ÇAĞRILIYOR: ikinci bir «aynı» tanımı KAT-1 olurdu
    from app.plan_semasi import tek_adimli

    ayni, sapan, cok_adimli, cevapsiz = [], [], [], []
    for q in sorular:
        bugun = parse_cube_query(llm.select_cube(q, catalog, None), index)
        plan = plan_garson.plan_uret(llm, q, catalog, index)
        yeni_cq = tek_adimli(plan) if plan else None
        yeni = parse_cube_query(json.dumps(yeni_cq, ensure_ascii=False), index) \
            if yeni_cq else None
        if bugun is None:
            # ⚠ Bugün cevaplanamayan soru **paydaya girmez**: denklik, bugünkü davranışın
            # korunmasını ölçer; olmayan bir cevabı korumak diye bir şey yok.
            cevapsiz.append(q)
        elif plan and len(plan["adimlar"]) > 1:
            cok_adimli.append(q)
        elif plan is None:
            # ⚠ İki farklı kusur, iki farklı iş: **plan kurulamadı** bir istem/sözleşme
            # sorunudur; **plan kuruldu ama beyaz listeden düştü** bir katalog eşleme
            # sorunudur. Tek etikete toplamak, ikisini de yanlış yere yönlendirir.
            sapan.append((q, "🔴 PLAN KURULAMADI (istem/sözleşme)"))
        elif yeni is None:
            sapan.append((q, "🔴 plan kuruldu ama BEYAZ LİSTEDEN DÜŞTÜ: "
                             + json.dumps(yeni_cq, ensure_ascii=False)[:160]))
        elif _canon_cq(bugun) == _canon_cq(yeni):
            ayni.append(q)
        else:
            sapan.append((q, f"{_canon_cq(bugun)} ≠ {_canon_cq(yeni)}"))
    return {"ayni": ayni, "sapan": sapan, "cok_adimli": cok_adimli, "cevapsiz": cevapsiz}


def _uretim_yolu(llm, q, catalog, index, k: int = 3):
    """🔴🔴 **ÜRETİMİN GERÇEKTEN KULLANDIĞI YOL — ve ilk ölçümüm bunu ATLIYORDU.**

    `ask.py` `select_cube`'u **tek** çağırmaz: `_select_consistent` `k=3` örnekler,
    kanonikleştirir ve **oylar**. Ham tek çağrıyı ölçmek, üretimin hiç koşmadığı bir
    yolu ölçmektir — ve *"taban kararsız"* diye bir sonuç üretir ki sistem o kararsızlığı
    zaten **oylamayla** düşürüyordu.

    ⚠ `_select_consistent` `ask.py`'nin içinde ve istek bağlamı ister; burada onun
    **çekirdeği** (k örnek → kanonik oylama) yeniden yazılmıyor, aynı iki fonksiyon
    (`parse_cube_query` + `_canon_cq`) ile aynı sıraya uygulanıyor. *Bir mekanizmayı
    ölçerken taklit etmek zorundaysan, en az onun kullandığı parçaları kullan.*

    *Bir sistemin kararsızlığını, o sistemin kullanmadığı bir yoldan ölçmek, başka bir
    sistemi ölçmektir.*
    """
    from collections import Counter

    from app.cube_router import parse_cube_query
    from app.routers.ask import _canon_cq

    adaylar = []
    for _ in range(k):
        cq = parse_cube_query(llm.select_cube(q, catalog, None), index)
        if cq is not None:
            adaylar.append(cq)
    if not adaylar:
        return None
    sayim = Counter(_canon_cq(c) for c in adaylar)
    kazanan = sayim.most_common(1)[0][0]
    for c in adaylar:
        if _canon_cq(c) == kazanan:
            return c
    return adaylar[0]


def oz_tutarlilik(sorular, llm, catalog, index, *, uretim: bool = False) -> dict:
    """🔴 **TABANIN KENDİ SAPMASI — ve bu ölçüm olmadan denklik eşiği UYDURMADIR.**

    `AZAMI_SAPMA = 0` ancak bugünkü yolun **kendisi** deterministikse anlamlı. Değilse
    plandan, `select_cube`'un kendinden bile isteyemediği bir tutarlılık istenmiş olur.

    ⊙ `§86.6`'nın bu katmandaki karşılığı: **önce tabanı ölç.** Aynı soru iki kez
    `select_cube`'a sorulur ve kanonik çıktıları karşılaştırılır.

    *Bir eşiği, ölçmediğin bir tabana göre koymak, kendi beklentini ölçü sanmaktır.*
    """
    from app.cube_router import parse_cube_query
    from app.routers.ask import _canon_cq

    def _bir(q):
        return (_uretim_yolu(llm, q, catalog, index) if uretim
                else parse_cube_query(llm.select_cube(q, catalog, None), index))

    ayni, farkli = [], []
    for q in sorular:
        a1, a2 = _bir(q), _bir(q)
        if a1 is None or a2 is None:
            continue
        (ayni if _canon_cq(a1) == _canon_cq(a2) else farkli).append(q)
    return {"ayni": ayni, "farkli": farkli}


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan denklik kapısı (O-13)")
    ap.add_argument("--sorular")
    ap.add_argument("--kapi", action="store_true")
    ap.add_argument("--taban", action="store_true",
                    help="bugünkü yolun KENDİ sapmasını ölç (§86.6)")
    ap.add_argument("--uretim", action="store_true",
                    help="ölçümü ÜRETİM yolundan yap (k=3 oylama) — ham tek çağrı değil")
    a = ap.parse_args()

    sorular = ([s.strip() for s in Path(a.sorular).read_text(encoding="utf-8").splitlines()
                if s.strip()] if a.sorular else list(SONDALAR))
    llm, catalog, index = _kur()
    if not getattr(llm, "plan_kurabilir", False):
        print("⊘ ÖLÇÜLEMEDİ: sağlayıcı plan kuramıyor.")
        return 2
    if a.taban:
        t = oz_tutarlilik(sorular, llm, catalog, index, uretim=a.uretim)
        n = len(t["ayni"]) + len(t["farkli"])
        _yol = "ÜRETİM YOLU (k=3 oylama)" if a.uretim else "HAM TEK ÇAĞRI"
        print(f"\n{_yol} — KENDİ SAPMASI: {len(t['farkli'])}/{n}  {t['farkli']}")
        print("⊙ Plan sapması bu sayıdan büyük değilse, fark plandan DEĞİL modelin "
              "kararsızlığından gelir.")
        return 0
    r = olc(sorular, llm, catalog, index)
    n = len(sorular)
    print(f"\npayda {n}  (bugün cevapsız {len(r['cevapsiz'])} → paydadan düştü)")
    print(f"  ✅ BİREBİR AYNI      {len(r['ayni']):>3}")
    print(f"  🔴 SAPAN             {len(r['sapan']):>3}")
    print(f"  ⚠ çok adımlı oldu   {len(r['cok_adimli']):>3}  {r['cok_adimli']}")
    for q, neden in r["sapan"]:
        print(f"      • «{q}» → {neden[:150]}")
    # 🔴 Çok adımlı olmak da bir **sapmadır**: basit bir soru basit kalmalı (`R2`).
    _sapma = len(r["sapan"]) + len(r["cok_adimli"])
    t = oz_tutarlilik(sorular, llm, catalog, index)
    _taban = len(t["farkli"])
    print(f"\nPLAN SAPMASI  {_sapma}")
    print(f"TABAN SAPMASI {_taban}   {t['farkli']}")
    print(f"⊙ Ölçüt: plan ≤ taban + {PAY}  →  "
          + ("✅ GEÇTİ" if _sapma <= _taban + PAY else "🔴 KALDI"))
    print("⚠ Taban da ölçülür çünkü bugünkü yol da deterministik DEĞİL: plandan, "
          "`select_cube`'un kendinden bile isteyemediği bir tutarlılık istenemez.")
    if a.kapi:
        return 0 if _sapma <= _taban + PAY else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
