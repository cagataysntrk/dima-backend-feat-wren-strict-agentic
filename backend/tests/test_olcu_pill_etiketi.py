"""🔴 `§69` — **KÜP ADI BİR AYIRT EDİCİDİR; AYIRT ETMİYORSA GÜRÜLTÜDÜR.**

## Ölçülen kusur (canlı `s33`, kararsız garson teklifi)

```
[olcu] OEE · OEE           [olcu] performans · OEE
[olcu] kullanılabilirlik · OEE      [olcu] kalite · OEE
```

Dört aday da **aynı** küpten (`oee`) geliyordu. `_olcu_metni` küp etiketini *«birden çok
aday var»* diye ekliyordu; oysa şerhinin kendi gerekçesi *«küp adı **ayırt edicidir**»*.
Aynı küpten gelen dört adayda o ad hiçbir şeyi ayırmaz — yalnız her satırı uzatır. Ve
`ort_oee`@`oee`'de etiketler **birebir aynı** sözcük olunca satır *«OEE · OEE»* oluyor.

## İki kural, ve ikisi de mevcut gerekçeden türedi

| # | kural |
|---|---|
| 1 | küp adı yalnız adaylar **birden çok küpten** geliyorsa yazılır |
| 2 | küp etiketi **ölçü etiketinin aynısıysa** hiç yazılmaz |

⚠ Ölçüt `silinebilir`den **ayrıldı** ⑯: silinebilirlik *«birden çok ADAY var mı»*, etiket
*«hangi KATALOGDAN»* sorusudur. Tek bayrakla sürmek, bir ekranı öteki uğruna bozardı.

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | aynı küpten çok aday → küp adı **yok** |
| 2 | 🆃 **iki küpten** aday → küp adı **var** (ayırt edicilik korunur) |
| 3 | etiketler aynıysa yinelenmez (*«OEE · OEE»* yok) |
| 4 | 🆃 tek aday **hâlâ silinemez** — etiket kuralı silinebilirliği bozmasın |
"""

from __future__ import annotations

from app import pill
from app.niyet import Niyet


def _metinler(adaylar):
    return [p.metin for p in pill.pillerden(Niyet(soru="", olcu_adaylari=adaylar), None)
            if p.alan == pill.ALAN_OLCU]


def test_AYNI_KUPTEN_ADAYLARDA_KUP_ADI_YOK():
    """🔴 **ASIL DEĞİŞMEZ.** Ayırt etmeyen bir ek, bir bilgi değil bir gürültüdür."""
    m = _metinler([("oee", "ort_performans"), ("oee", "ort_kalite")])
    assert m == ["ort performans", "ort kalite"], f"🔴 küp adı gereksiz yere eklendi: {m}"


def test_ZIT_OLCUT_IKI_KUPTEN_ADAYDA_KUP_ADI_VAR():
    """🆃 Kapının kurbanı: küp adını **tümden** atmak `t13`'ü (`elektrik` ↔ `tep`) bozardı —
    iki pill aynı metni taşır ve kullanıcı hangisini sildiğini bilemezdi."""
    m = _metinler([("enerji_makine", "toplam_elektrik"), ("enerji_tesis", "toplam_elektrik")])
    assert all(" · " in x for x in m), f"🔴 iki küpten adayda ayırt edici kayboldu: {m}"
    assert len(set(m)) == 2, f"🔴 iki pill aynı metni taşıyor: {m}"


def test_ETIKET_AYNIYSA_YINELENMEZ():
    """*«OEE · OEE»* iki kez aynı sözcüktür."""
    sema = {"cubes": [{"name": "oee", "display": "OEE",
                       "measure_synonyms_display": {"ort_oee": "OEE"}},
                      {"name": "bakim", "display": "Bakım"}]}
    m = [p.metin for p in pill.pillerden(
        Niyet(soru="", olcu_adaylari=[("oee", "ort_oee"), ("bakim", "ariza_sayisi")]), sema)
        if p.alan == pill.ALAN_OLCU]
    assert "OEE · OEE" not in m, f"🔴 etiket yinelendi: {m}"
    assert any("Bakım" in x for x in m), f"🔴 komşu aday ayırt ediciliğini kaybetti: {m}"


def test_ZIT_OLCUT_TEK_ADAY_SILINEMEZ():
    """🆃 Etiket kuralı **silinebilirliği** bozmamalı: ölçüsüz bir fiş bir sorgu değildir."""
    piller = [p for p in pill.pillerden(
        Niyet(soru="", olcu_adaylari=[("oee", "ort_oee")]), None) if p.alan == pill.ALAN_OLCU]
    assert piller and not piller[0].silinebilir, f"🔴 tek ölçü silinebilir oldu: {piller}"
    coklu = [p for p in pill.pillerden(
        Niyet(soru="", olcu_adaylari=[("oee", "a"), ("oee", "b")]), None)
        if p.alan == pill.ALAN_OLCU]
    assert all(p.silinebilir for p in coklu), "🔴 çok adayda silinebilirlik kayboldu"
