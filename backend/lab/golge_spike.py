"""FAZ 7 — ARAŞTIRMA SIÇRAMALARI: GÖLGE ölçüm, cevaba KARIŞMAZ.

    python lab/golge_spike.py            # üç spike'ın ölçülebilir kısmı
    python lab/golge_spike.py --json

## Planın disiplini

*"Kör benimseme YOK — önce **ölçülmüş** gölge-mod spike. **Kazanç yoksa entegre
EDİLMEZ.**"* Bu araç kazancın **ÜST SINIRINI** ölçer: bir teknoloji en iyi ihtimalle
kaç soruyu kurtarabilirdi? Üst sınır küçükse teknolojiyi denemenin **maliyeti bile
gereksizdir** — ve bu, kütüphaneyi kurmadan da bilinebilir.

## Ölçülemeyen kısım dürüstçe

* **Zeyrek** (Türkçe morfoloji): `pip install` **ağ ister**, CI reçetesi `--network none`.
  Kütüphanenin kendisi burada koşturulamaz. Ölçülen şey **onun hedefi**: ek kaynaklı
  kayıp ne kadar?
* **Embedding**: `DIMA_VQR_EMBEDDER=off` — CI'da embedder yok. Ölçülen şey yine hedef:
  leksik eşleşmenin **sıfır** olduğu kaç soru var?
* **SLM**: plan zaten *"bugün için erken, yalnız gözlem"* diyor — eğitim verisi hacmi
  ölçülür, karar verilmez.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tests.conftest as _conf  # noqa: E402,F401
from tests.conftest import make_tenant_user  # noqa: E402

#: ⚠️ **İLK SÜRÜM YANLIŞTI ve %100 "kurtarılabilir" gibi anlamsız bir sonuç verdi.**
#: `-(y)İz` (1. çoğul şahıs) **fiile** eklenir, isme DEĞİL: `agirlik+yiz` = *"agirlikyiz"*
#: hiçbir kullanıcının yazmayacağı bir dizidir. Bir kütüphane onu "kurtarsaydı" bu bir
#: kazanç değil bir HATA olurdu. Ölçüm aracının kendisi bir bağımlılıktır (MIMARI §6.4) —
#: bu oturumda ÜÇÜNCÜ kez kendi aracım yanlış ölçtü.
#:
#: Doğru ölçüm: İSME eklenen, GERÇEK Türkçe çekimler. Çoğu zaten `_SUFFIX_ATOMS`'ta —
#: ve bu **beklenen** sonuçtur: whitelist yaygın olanları KAPSIYOR. Spike'ın sorusu
#: "kapsamayan var mı ve kaç tane?" — cevabı "az"sa kütüphane MALİYETİ HAK ETMEZ.
ISIM_CEKIMLERI = (
    "lar", "ler",           # çoğul
    "imiz", "umuz", "iniz", # iyelik (1./2. çoğul)
    "leri", "lari",         # çoğul+iyelik
    "den", "dan", "ten", "tan",   # ayrılma
    "de", "da", "te", "ta",       # bulunma
    "yle", "yla",           # vasıta
    "deki", "daki",         # bulunma+ilgi
    # `_SUFFIX_ATOMS`'ta OLMAYAN adaylar — spike'ın asıl hedefi:
    "cilik", "culuk",       # meslek/alan ("boyacilik")
    "siz", "suz",           # yokluk ("firesiz")
    "lerimiz", "larimiz",   # çoğul+1.çoğul iyelik (BİRLEŞİK zincir)
    "lerinde", "larinda",   # çoğul+iyelik+bulunma
)


def _sema():
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict()).schema()


def morfoloji_spike(schema) -> dict:
    """§4.6 — ek kaynaklı kayıp ne kadar? (Zeyrek'in HEDEFİ)

    Yöntem: her ölçü/boyut sinonimini **çekimli** hâlleriyle sorup `route()`'un çözüp
    çözemediğine bakarız. Çekimsiz çözülüp çekimli çözülemeyen her vaka, bir morfoloji
    kütüphanesinin **kurtarabileceği** bir sorudur — yani kazancın ÜST SINIRI.
    """
    from app import cube_router as cr

    kurtarilabilir: list[dict] = []
    denenen = 0
    _atomlar = set(cr._SUFFIX_ATOMS)
    for c in schema.get("cubes") or []:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                temel = cr._norm(str(sy))
                if not temel or " " in temel or len(temel) < 4:
                    continue
                cr.reddi_sifirla()
                if cr.route(f"bu yil {temel}", schema) is None:
                    continue                       # çekimsiz zaten çözülmüyor → konu dışı
                for ek in ISIM_CEKIMLERI:
                    denenen += 1
                    cr.reddi_sifirla()
                    if cr.route(f"bu yil {temel}{ek}", schema) is None:
                        kurtarilabilir.append({
                            "sinonim": temel, "ek": ek, "red": cr.red_gerekcesi(),
                            # Ek zaten atom listesindeyse kayıp morfoloji DEĞİL başka bir
                            # sebeptendir (ör. belirsizlik) — ayrımı rapor göstersin.
                            "atom_listesinde": ek in _atomlar})
    # Kelime bazında tekilleştir: aynı sinonimin 7 eki 7 ayrı kayıp değildir.
    kelimeler = {k["sinonim"] for k in kurtarilabilir}
    # ASIL SAYI: atom listesinde OLMAYAN eklerden kaynaklanan kayıp.
    # ⚠️ OLUMSUZLUK EKLERİ KURTARILMAMALI. `-sIz` (`firesiz` = fire YOK) sinonimin
    # **zıddıdır**; onu "fire" saymak sessiz-yanlış üretirdi ve `_NEGATION_SUFFIXES` tam
    # bu yüzden var. Yani bu vakalarda `route()`'un reddi **doğru davranıştır** ve bir
    # morfoloji kütüphanesinin "kazancı" değil, olsa olsa **zararı** olurdu.
    _olumsuz = set(cr._NEGATION_SUFFIXES)
    morfolojik = [k for k in kurtarilabilir
                  if not k["atom_listesinde"] and k["ek"] not in _olumsuz]
    olumsuzluk = [k for k in kurtarilabilir if k["ek"] in _olumsuz]
    ekler = {}
    for k in morfolojik:
        ekler[k["ek"]] = ekler.get(k["ek"], 0) + 1
    return {"denenen_varyant": denenen, "kurtarilabilir_varyant": len(kurtarilabilir),
            "olumsuzluk_DOGRU_RED": len(olumsuzluk),
            "morfoloji_kaynakli": len(morfolojik), "ek_dagilimi": ekler,
            "ust_sinir_yuzde": round(100 * len(morfolojik) / denenen, 2) if denenen else 0.0,
            "etkilenen_sinonim": len(kelimeler),
            "ornek": sorted(kurtarilabilir, key=lambda x: x["sinonim"])[:10],
            "_not": "Bu, bir morfoloji kütüphanesinin kurtarabileceği ÜST SINIRDIR — "
                    "gerçek kazanç bundan KÜÇÜKTÜR (kütüphane de her çekimi çözemez)."}


def embedding_spike(schema) -> dict:
    """§4.6b-A — leksik eşleşmenin SIFIR olduğu soru payı (embedding'in HEDEFİ).

    `route()` R1 (cube kimliği hiç eşleşmedi) veriyorsa leksik yol **tamamen** boştur;
    embedding ancak bu kümede yeni bilgi getirebilir. R10 (kapsam kapısı) ise kısmi
    eşleşmedir — embedding orada zaten eşleşen kelimeyi tekrar bulur, yeni bilgi vermez.
    """
    from app import cube_router as cr

    red = {}
    toplam = 0
    for c in schema.get("cubes") or []:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                toplam += 1
                cr.reddi_sifirla()
                if cr.route(f"bu yil {sy}", schema) is None:
                    red[cr.red_gerekcesi()] = red.get(cr.red_gerekcesi(), 0) + 1
    r1 = red.get("R1", 0)
    return {"toplam_sinonim": toplam, "red_dagilimi": red,
            "embeddingin_hedefi_R1": r1,
            "ust_sinir_yuzde": round(100 * r1 / toplam, 1) if toplam else 0.0,
            "_not": "R1 = leksik yol TAMAMEN boş → embedding'in yeni bilgi getirebileceği "
                    "TEK küme. Ama §6.1h ölçtü: R1'in TAMAMI GERÇEK ölçü-düzeyi "
                    "belirsizliği (aynı ad iki cube'da). Embedding belirsizliği ÇÖZMEZ, "
                    "yalnız aday üretir — ve o adaylar zaten netleştirme chip'inde var."}


def slm_spike() -> dict:
    """§4.6b-B — eğitim verisi hacmi. Plan: *"bugün için erken, yalnız gözlem"*."""
    try:
        from sqlmodel import Session, func, select

        from control_plane.db import engine
        from control_plane.models import MeasureCandidate, VerifiedQuery

        with Session(engine) as s:
            vqr = s.exec(select(func.count()).select_from(VerifiedQuery)).one()
            aday = s.exec(select(func.count()).select_from(MeasureCandidate)).one()
        return {"verified_query": vqr, "measure_candidate": aday,
                "karar": "SPIKE BİLE DEĞİL — ince-ayar için gereken hacmin çok altında."}
    except Exception as exc:  # noqa: BLE001
        return {"durum": "ölçülemedi", "aciklama": f"{type(exc).__name__}: {exc}",
                "karar": "SPIKE BİLE DEĞİL (plan zaten böyle diyor)."}


def main() -> None:
    ap = argparse.ArgumentParser(description="Faz 7 — gölge spike ölçümleri")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    schema = _sema()
    out = {"morfoloji": morfoloji_spike(schema),
           "embedding": embedding_spike(schema),
           "slm": slm_spike(),
           "_kisit": {
               "zeyrek": "pip install AĞ ister; CI reçetesi --network none → kütüphane "
                         "burada KOŞTURULAMAZ. Ölçülen şey onun HEDEFİDİR.",
               "embedder": "DIMA_VQR_EMBEDDER=off → embedder yok. Aynı şekilde HEDEF ölçüldü.",
           }}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return

    m, e, s = out["morfoloji"], out["embedding"], out["slm"]
    print("=" * 74)
    print("FAZ 7 — GÖLGE SPIKE (cevaba KARIŞMAZ; kazancın ÜST SINIRI ölçülür)")
    print("=" * 74)
    print("\n(1) TÜRKÇE MORFOLOJİ — Zeyrek'in hedefi")
    print(f"    denenen çekimli varyant     : {m['denenen_varyant']}")
    print(f"    kurtarılabilir varyant      : {m['kurtarilabilir_varyant']}")
    print(f"    etkilenen sinonim           : {m['etkilenen_sinonim']}")
    print(f"    olumsuzluk eki (-sIz) — RED DOĞRU: {m['olumsuzluk_DOGRU_RED']}"
          f"  ← kurtarılmamalı, 'firesiz' ≠ 'fire'")
    print(f"    GERÇEK MORFOLOJİ KAYBI      : {m['morfoloji_kaynakli']} "
          f"(%{m['ust_sinir_yuzde']}) ← Zeyrek'in ÜST SINIRI")
    print(f"    ek dağılımı                 : {m['ek_dagilimi']}")
    for x in m["ornek"][:6]:
        print(f"      {x['sinonim']}+{x['ek']} → red={x['red']} "
              f"(atom={x['atom_listesinde']})")
    print(f"    {m['_not']}")
    print("\n(2) SEMANTİK EŞLEŞTİRME — embedding'in hedefi")
    print(f"    toplam sinonim              : {e['toplam_sinonim']}")
    print(f"    red dağılımı                : {e['red_dagilimi']}")
    print(f"    R1 (leksik TAMAMEN boş)     : {e['embeddingin_hedefi_R1']} "
          f"(%{e['ust_sinir_yuzde']})")
    print(f"    {e['_not']}")
    print("\n(3) SLM — eğitim verisi hacmi")
    for k, v in s.items():
        print(f"    {k:<28}: {v}")
    print("\nKISITLAR (dürüstçe):")
    for k, v in out["_kisit"].items():
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
