"""🔴🔴 `§B9` — SParC'ın **DÖRT TEMATİK İLİŞKİSİ**, oranlarıyla birlikte kapıda.

## Rapor ne diyordu, ölçüm ne buldu

`§21.14` (arXiv:1906.02285) dört kovayı oranlarıyla veriyor ve şunu yazıyor:

> *«Bu dört kova, `niyet.py`'nin taşıması gereken TAM listedir — ve bugün **yok**.»*
> *«Answer refinement (%8,1) … bu, «odak varlığı yok» kusurunun **akademik adıdır**
> (`«o makine»` → süzgeç kurulamıyor, **33 satır** dönüyor).»*

⟳ **ÖLÇÜLDÜ (2026-08-12, CANLI curl + birim) — İDDİA BAYAT.** Dördü de çalışıyor, dördü
de `source=cube` (**sıfır LLM**), ve odak **beyan ediliyor**:

| SParC ilişkisi | oran | canlı tur | sonuç |
|---|---|---|---|
| **theme-entity** | %48,4 | *«o makinenin oee'si ne kadar»* | `makine eq RAM-2`, küp `parti`→`oee` |
| **refinement** | %33,8 | *«peki geçen yıl»* | dönem 2025'e kaydı, **varlık korundu** |
| **theme-property** | %9,7 | *«peki RAM-3 için»* | `makine eq RAM-3` — RAM-2 **düştü** |
| **answer-refinement** | %8,1 | RAM-2 **cevaptan** geldi (soruda yok) | + beyan: *«bir önceki turun seçtiği makine»* |

⊙ Eksik olan **ürün değil, ad**: `niyet.py` bu dört ilişkiyi *adlandırmıyor*. Ad eklemek
tek başına bir tüketici doğurmaz (`KAT-1`: aynı kuralın ikinci sahibi). Taksonominin
verdiği asıl değer bir **kontrol listesiydi** — bu dosya o listeyi kapıya çeviriyor.

## 🔴 VE BİR KAPI, İDDİASININ YALNIZ YARISINI ÖLÇÜYORDU

`test_odak_varlik.py::test_KAPSAM_BIR_PIN_DEGILDIR` şunu **yazıyor**:

> *«Var olan bir **aralık** atfı engellemez; bir **`eq` pini** engeller.»*

Ama yalnız **birinci** yarıyı ölçüyor (aralık → süzgeç kurulur). İkinci yarı — `eq` pini
varken odağın **kurulMAması** — hiç ölçülmüyordu.

⚠ Ve korunan şey tam olarak yukarıdaki iki satır: `refinement` (%33,8) ve
`theme-property` (%9,7). O yarı bozulursa *«peki RAM-3 için»* sorusu **iki** `makine eq`
süzgeci alır (`RAM-3` **ve** `RAM-2`) ve cevap sessizce **0 satır** olur — kullanıcı için
en pahalı arıza: kapısız, gerekçesiz bir boşluk.

> *Bir kapı, iddiasının yalnız bir yarısını ölçüyorsa, öteki yarı yazılı bir
> temenniden ibarettir.*
"""

from __future__ import annotations

from app.diyalog import odak_suzgeci

_SEMA = {"cubes": [{"name": "oee", "dimensions": ["makine", "vardiya"],
                    "time_dimensions": ["tarih"]},
                   {"name": "parti", "dimensions": ["makine"],
                    "time_dimensions": ["tarih"]}]}
#: Bir önceki turun **cevabından** gelen varlık — soruda hiç geçmiyor.
_ODAK = {"odak": {"boyut": "makine", "deger": "RAM-2"}}


def _cq(filtreler: list[dict] | None = None) -> dict:
    return {"cube": "oee", "dimensions": ["makine"], "filters": filtreler or []}


def test_THEME_ENTITY_ayni_varlik_baska_ozellik():
    """**%48,4** — en sık ilişki. *«o makinenin oee'si»*: varlık aynı, özellik başka."""
    s = odak_suzgeci("o makinenin oee'si ne kadar", _cq(), _ODAK, _SEMA)
    assert s == [{"dimension": "makine", "operator": "eq", "value": "RAM-2"}], (
        "🔴 theme-entity (%48,4) çöktü: *«o makinenin …»* takibi bir önceki turun "
        "varlığına daralmıyor. Sonuç: kırılımın TAMAMI döner ve kullanıcı kendi "
        "sorusunun cevabını satırlar arasında arar.")


def test_ANSWER_REFINEMENT_varlik_CEVAPTAN_gelir():
    """**%8,1** — raporun *«odak varlığı yok»* kusurunun akademik adı.

    🔴 Ayırt edici nokta: `RAM-2` **soruda geçmiyor**; yalnız bir önceki turun
    **cevabında** var. Bu, metin eşleştirmenin çözemeyeceği tek koladır."""
    soru = "o makinede neden düşük"
    assert "RAM" not in soru, "⊘ ölçüm tabanı çöktü: varlık soruya sızmış"
    s = odak_suzgeci(soru, _cq(), _ODAK, _SEMA)
    assert s and s[0]["value"] == "RAM-2", (
        "🔴 answer-refinement (%8,1) çöktü — varlık CEVAPTAN taşınamıyor.")


def test_REFINEMENT_ayni_tur_farkli_kisit_ODAK_TEKRARLANMAZ():
    """**%33,8** — *«peki geçen yıl»*: varlık zaten pinli, yalnız dönem değişir.

    🔴 Odak **yeniden uygulanmamalı**: `makine eq RAM-2` ikinci kez eklenirse süzgeç
    listesi ikilenir ve bir gün farklı bir değerle çakışır."""
    cq = _cq([{"dimension": "makine", "operator": "eq", "value": "RAM-2"}])
    assert odak_suzgeci("peki geçen yıl", cq, _ODAK, _SEMA) is None, (
        "🔴 refinement (%33,8): var olan bir `eq` pini varken odak YİNE uygulandı — "
        "aynı boyutta iki süzgeç.")


def test_THEME_PROPERTY_varlik_DEGISIR_eskisi_SIZMAZ():
    """**%9,7** — *«peki RAM-3 için»*: özellik aynı, **varlık başka**.

    🔴🔴 **EN PAHALI ARIZANIN KAPISI.** Odak burada uygulanırsa sorgu hem `RAM-3` hem
    `RAM-2` süzgeci taşır ve cevap **0 satır** olur: kapısız, gerekçesiz bir boşluk.
    *Bir kullanıcı için en kötü cevap yanlış cevap değil, sebebi söylenmeyen boş
    cevaptır.*"""
    cq = _cq([{"dimension": "makine", "operator": "eq", "value": "RAM-3"}])
    assert odak_suzgeci("peki RAM-3 için", cq, _ODAK, _SEMA) is None, (
        "🔴 theme-property (%9,7): kullanıcı YENİ bir varlık verdi ama bir önceki turun "
        "varlığı da süzgece eklendi → `RAM-3 AND RAM-2` → **0 satır**.")


def test_EQ_PINI_ENGELLER_ARALIK_ENGELLEMEZ():
    """🔴🔴 **BİR KAPININ ÖLÇÜLMEYEN YARISI.**

    `test_odak_varlik.py::test_KAPSAM_BIR_PIN_DEGILDIR` şunu **yazıyor**: *«Var olan bir
    aralık atfı engellemez; bir `eq` pini engeller»* — ama yalnız **birinci** yarıyı
    ölçüyor. Bu test ikisini **yan yana** ölçer; ayrım bozulursa hangi yönde bozulduğu
    da görünür.
    """
    aralik = _cq([{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}])
    assert odak_suzgeci("o makinede neden düşük", aralik, _ODAK, _SEMA), (
        "🔴 bir ARALIK süzgeci odağı engelledi — kapsam bir pin değildir; "
        "*bir kapsamı pin sanmak, hatırlamayı imkânsız kılar.*")
    pin = _cq([{"dimension": "makine", "operator": "eq", "value": "RAM-9"}])
    assert odak_suzgeci("o makinede neden düşük", pin, _ODAK, _SEMA) is None, (
        "🔴 var olan bir `eq` PİNİ odağı engellemedi → aynı boyutta iki çelişen süzgeç "
        "(`RAM-9` ve `RAM-2`) → 0 satır. Bu, kapının yazılı ama ölçülmemiş yarısıydı.")


def test_TAKSONOMI_ADI_KODA_KOPYALANMADI():
    """⏸ **KARAR:** dört kovanın **adları** `niyet.py`'ye eklenMEDİ, ve bu bir karardır.

    Ad eklemek tek başına bir tüketici doğurmaz; doğurmayan bir ad, aynı kuralın ikinci
    sahibi olur (`KAT-1`). Taksonominin değeri bir **kontrol listesiydi** — o liste bu
    dosyada kapıya çevrildi. Kararın kendisi burada yazılı ki bir gün *«yapılmadı»* diye
    okunmasın.

    ⚠ Yüklem sahte-yeşil olmasın diye **çift yönlü**: bir gün adlar eklenirse (yani
    gerçek bir tüketici doğarsa) bu test kırılır ve karar yeniden okunur.
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent / "app" / "niyet.py").read_text(
        encoding="utf-8")
    adlar = [a for a in ("theme_entity", "answer_refinement", "theme_property")
             if a in kaynak]
    assert not adlar, (
        f"✅ SParC adları `niyet.py`'ye girmiş: {adlar}. Bu bir kusur değil bir "
        "DEĞİŞİKLİKTİR — ama bir tüketicisi var mı? Yoksa `KAT-1` gereği geri alınmalı; "
        "varsa bu testin gerekçesi güncellenmelidir.")
