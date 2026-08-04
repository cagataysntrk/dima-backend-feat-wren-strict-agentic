"""FAZ 4.3 kapısı — **çok-turlu sharding benchmark'ının kendisi ölçülür.**

🔴 *Ölçüm aracının kendisi de bir bağımlılıktır.* Bu dosya benchmark'ın **sonucunu**
kilitlemez (sonuç değişir, değişmeli); **ölçüm disiplinini** kilitler:

1. **Yeniden üretilebilirlik** — aynı tohum → aynı dağılım.
2. **Önek özelliği** — derinlik *N*, derinlik *N+1*'in önekidir (sıra ≠ derinlik).
3. **Etiket dürüstlüğü** — `tur N` satırına yalnız **gerçekten N turluk** konuşma girer.
4. **Üçüncü hâl** — küçük kohortta karar `⊘ ÖLÇÜLEMEDİ`, *"geçti"* değil.
5. **Deterministik recap** — taşınan şey `cube_query`'nin **kendisi**, bir metin özeti değil.
6. **Kötü sonuç yayımlanır** — rapor, düşüşü ve kaldığı kararı **saklamaz**.
"""

from __future__ import annotations

import ast
import random
from pathlib import Path

import pytest

from lab.sharding import (
    HEDEF_DUSUS,
    TOHUM,
    YETER_KOHORT,
    atomlar,
    birlestir,
    cube_query_ac,
    hedef_karari,
    rapor_metni,
    turlara_dagit,
)

_KAYNAK = Path(__file__).resolve().parents[1] / "lab/sharding.py"

_CQ = {
    "cube": "ticaret",
    "measures": ["satis_tutari", "toplam_maliyet"],
    "dimensions": ["cari_adi", "urun_adi"],
    "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
    "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}],
}


def test_route_sarmalayicisi_acilir():
    """🔴 İlk sürüm bunu kaçırdı ve eğri **tamamen boş** çıktı.

    `route()` `{"cube_query": {...}, "measure": …}` döner; üst düzey sözlüğü `cube_query`
    sanmak `atomlar()`'ı boş bırakıyordu. *Boş bir eğri, kötü bir eğriden tehlikelidir:
    hiçbir şey söylemez ama tablo dolu görünür.*
    """
    assert cube_query_ac({"cube_query": _CQ, "measure": "x"}) == _CQ
    assert cube_query_ac(_CQ) == _CQ           # zaten açık gelirse dokunmaz
    assert cube_query_ac(None) == {}


def test_atomlar_tek_baslarina_ANLAMLI():
    """Atom bir **tur** olmalı: *"aylara göre"* evet, *"aylara"* hayır."""
    a = atomlar(_CQ)
    assert "satis tutari" in a
    assert "cari adi bazinda" in a
    assert "aylara gore" in a
    # Tarih filtresi bir atom DEĞİL: `2026-01-01` bir konuşma turu değildir.
    assert not any("2026" in x for x in a)
    assert all(x.strip() and len(x) > 3 for x in a)


def test_derinlik_ONEK_ozelligini_korur():
    """🔴 **Sıra ≠ derinlik.** Derinlik-N, derinlik-N+1'in ÖNEKİ olmalı.

    İlk sürüm `Random(TOHUM + tur)` kullanıyordu: her derinlikte **sıralama da**
    değişiyordu, yani eğri derinlikle karıştırmayı **karıştırıyordu** ve ölçtüğü düşüş
    derinliğin değil shuffle'ın eseri olabilirdi.
    """
    a = atomlar(_CQ)
    assert len(a) >= 4
    onceki = turlara_dagit(a, 1, random.Random(TOHUM + 7))
    for tur in range(2, len(a) + 1):
        simdi = turlara_dagit(a, tur, random.Random(TOHUM + 7))
        assert simdi[: len(onceki)] == onceki, (
            f"tur {tur}: derinlik-{tur - 1} artık derinlik-{tur}'in ÖNEKİ değil — "
            f"eğri 'derinlik' yerine 'sıra'yı ölçüyor")
        onceki = simdi


def test_ilk_tur_HER_ZAMAN_olcu_tasir():
    """Makalenin senaryosu *"eksik bilgiyle başla"*, *"anlamsız başla"* değil."""
    for tur in range(1, 6):
        t = turlara_dagit(atomlar(_CQ), tur, random.Random(TOHUM + tur))
        if t:
            assert t[0] == "satis tutari", "ilk tur ölçü taşımazsa test boş girdiyi ölçer"


def test_ayni_tohum_AYNI_dagilim():
    """*Rastgele bir benchmark, karşılaştırılamaz bir benchmarktır.*"""
    a = atomlar(_CQ)
    assert (turlara_dagit(a, 4, random.Random(TOHUM))
            == turlara_dagit(a, 4, random.Random(TOHUM)))


def test_birlestir_yalniz_AYNI_cube():
    """Birleştirme bir **küme birleşimidir** — ikinci bir ayrıştırıcı değil."""
    b = birlestir(_CQ, {"cube": "ticaret", "measures": ["adet"], "dimensions": ["il"]})
    assert b["measures"][:2] == ["satis_tutari", "toplam_maliyet"]
    # Farklı cube → birleştirme YOK (yoksa cross-cube uydurma bir konuşma doğardı).
    y = birlestir(_CQ, {"cube": "ik", "measures": ["ort_brut_maas"]})
    assert y["measures"] == _CQ["measures"]


def test_kucuk_kohortta_karar_UCUNCU_HALDIR():
    """🔴 `n=8`'de bir konuşma **%12,5 puan** — hedefin (%10) tamamından fazla.

    *Bu çözünürlükte "geçti" demek, "kaldı" demek kadar uydurmadır.* İkili bir karar
    burada bir **örneklem kazasını** başarı diye satardı.
    """
    kucuk = {1: {"tam_cevaplanan": 1.0, "konusma": 8, "yapi_kaybi": 0},
             5: {"tam_cevaplanan": 1.0, "konusma": 8, "yapi_kaybi": 0}}
    k = hedef_karari(kucuk)
    assert k["karar"] == "olculemedi", "küçük kohortta 'geçti' YAZILAMAZ"
    assert str(YETER_KOHORT) in k["neden"]

    yeter = {1: {"tam_cevaplanan": 0.90, "konusma": 40, "yapi_kaybi": 0},
             5: {"tam_cevaplanan": 0.85, "konusma": 40, "yapi_kaybi": 0}}
    assert hedef_karari(yeter)["karar"] == "gecti"
    kotu = {1: {"tam_cevaplanan": 0.90, "konusma": 40, "yapi_kaybi": 0},
            5: {"tam_cevaplanan": 0.60, "konusma": 40, "yapi_kaybi": 0}}
    assert hedef_karari(kotu)["karar"] == "kaldi"
    assert hedef_karari({})["karar"] == "olculemedi"


def test_hedef_esigi_MAKALEYE_gore_yazili():
    """Hedef **−%10**; makalenin ölçtüğü **−%39**. Eşik uydurulmadı, kıyaslandı."""
    assert HEDEF_DUSUS == 0.10
    assert YETER_KOHORT >= 20


def test_KOTU_SONUC_saklanmaz():
    """§C/16 *ilan edilmiş puanlama kuralı* — şart, sonucun **yönünden bağımsızdır**."""
    metin = rapor_metni({"x": {
        "ornek": 40, "azami_atom": 5,
        "egri": {1: {"konusma": 40, "tam_cevaplanan": 0.9, "yapi_kaybi": 0,
                     "cq_surekliligi": 0.9},
                 5: {"konusma": 40, "tam_cevaplanan": 0.5, "yapi_kaybi": 9,
                     "cq_surekliligi": 0.6}},
        "kohort": {1: {"konusma": 40, "tam_cevaplanan": 0.9, "yapi_kaybi": 0},
                   5: {"konusma": 40, "tam_cevaplanan": 0.5, "yapi_kaybi": 9}},
        "hedef": {"karar": "kaldi", "dusus": 0.4, "n": 40}}})
    assert "KALDI" in metin, "kötü karar rapordan DÜŞÜRÜLEMEZ"
    assert "%40.0" in metin, "düşüşün büyüklüğü yazılmalı"
    assert "−%39" in metin, "makalenin sayısı kıyas için durmalı"


def test_ucuncu_hal_RAPORDA_gorunur():
    """`⊘` bir başarısızlık değil, bir **dürüstlüktür** — ve rapora yazılır."""
    metin = rapor_metni({"x": {
        "ornek": 8, "azami_atom": 5, "egri": {1: {"konusma": 8, "tam_cevaplanan": 1.0,
                                                  "yapi_kaybi": 0, "cq_surekliligi": 1.0}},
        "kohort": {1: {"konusma": 8, "tam_cevaplanan": 1.0, "yapi_kaybi": 0},
                   5: {"konusma": 8, "tam_cevaplanan": 0.875, "yapi_kaybi": 1}},
        "hedef": hedef_karari({1: {"konusma": 8, "tam_cevaplanan": 1.0, "yapi_kaybi": 0},
                               5: {"konusma": 8, "tam_cevaplanan": 0.875,
                                   "yapi_kaybi": 1}})}}) 
    assert "⊘ ÖLÇÜLEMEDİ" in metin
    assert "ÖLÇÜLEMEDİ" in metin and "AYIRT EDİLEMEZ" in metin


def test_ONCEKI_TABLODAN_EGIM_okunmaz_uyarisi_var():
    """Her satırı farklı popülasyon olan bir tablodan **eğim okunamaz** — yazılı olmalı."""
    metin = rapor_metni({"x": {"ornek": 9, "azami_atom": 3,
                               "egri": {1: {"konusma": 9, "tam_cevaplanan": 0.5,
                                            "yapi_kaybi": 0, "cq_surekliligi": 0.5}},
                               "kohort": {}, "hedef": {"karar": "olculemedi"}}})
    assert "her satır farklı bir popülasyondur" in metin
    assert "eğim buradan okunmaz" in metin


def test_DETERMINISTIK_RECAP_metin_ozeti_DEGIL():
    """🔴 Makalenin azaltması *recap* (bir **metin**); bizimki **yapının kendisi**.

    ⚠ Belirteç **YAPISAL (AST)**: modülün docstring'i tam da bu farkı **anlatıyor**, yani
    bir alt-dize taraması kendi belgesini ölçerdi. *Beyan ile beyanın anlatımı farklı
    şeylerdir* — bu deponun on kez ödediği ders.
    """
    agac = ast.parse(_KAYNAK.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "konusma_kos")
    cagrilar = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "deterministic_refine" in cagrilar, (
        "🔴 Deterministik recap DÜŞTÜ: `konusma_kos` artık `deterministic_refine` "
        "çağırmıyor. Bu benchmark'ın TEK iddiası, taşınanın bir metin özeti değil "
        "`cube_query`'nin KENDİSİ olmasıydı.")
    # Bir "özetleyici"/LLM çağrısı SIZMAMALI: benchmark LLM'siz ve kotasızdır.
    assert not {"generate_sql", "complete", "chat"} & cagrilar, (
        "🔴 Benchmark'a bir LLM çağrısı sızmış — ölçüm kotaya ve rastgeleliğe bağlanırdı.")


@pytest.mark.parametrize("alan", ["measures", "dimensions", "timeDimensions"])
def test_atomlar_cube_query_ALANLARINDAN_turer(alan):
    """İkinci bir ayrıştırıcı **yazılmadı**: alan silinince atom da kaybolmalı."""
    eksik = {k: v for k, v in _CQ.items() if k != alan}
    assert len(atomlar(eksik)) < len(atomlar(_CQ)), (
        f"`{alan}` silindi ama atom sayısı düşmedi — demek ki atomlar `cube_query`'den "
        f"değil, aracın KENDİ yorumundan türüyor")
