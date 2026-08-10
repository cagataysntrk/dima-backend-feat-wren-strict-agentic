"""🔴 `F6`/`D1` — **HEDEF KIYASI**: `beta`'ya çıkmadan önce kapı.

Rapor `F6`: *"`hedef_kiyasi` — `off`, 🔴 **0 test**. Önce **kapı**, sonra aç."*
Ve sebebi bir sessiz-yanlış: grafikteki referans çizgisi bugün **hedef değil
ortalama** — *"kod bunu `interpret.py`'de itiraf ediyor"*.

## Bu bayrağın sözleşmesi — üç sert kural

| kural | neden |
|---|---|
| beyan yoksa `None` | **hedef UYDURULMAZ**; `pvm:` eşleştirmesinde reddedilen şeyin aynısı |
| `None` ≠ `0` | *sıfır hedef **ulaşılmış** bir hedeftir; hedefsizlik **ölçülemezliktir**"* |
| `gerceklesen` **sonuçtan** okunur | hedeften türetmek, kullanıcının sayısını sistemin sayısıyla değiştirmek olurdu |

⚠ Ve `yon` yeniden beyan edilmez, `lower_is_better`'dan **türer** — yani `B-5`'in
173/173 yön beyanı bu bayrağın **ön koşuludur**: yön yanlışsa *«hedefe ulaşıldı»*
kararı da ters çıkar.
"""

from __future__ import annotations

from app.hedef import beyan, blok, yon

_SEMA = {"cubes": [{
    "name": "oee",
    "measures": ["ort_oee", "toplam_fire_kg"],
    "lower_is_better": ["toplam_fire_kg"],
    "hedefler": {"ort_oee": 0.75, "toplam_fire_kg": 1000, "bozuk": "abc", "sifir": 0},
}, {"name": "parti", "measures": ["toplam_ciro"]}]}


# ── beyan ────────────────────────────────────────────────────────────────────
def test_BEYAN_YOKSA_HEDEF_UYDURULMAZ():
    """🔴 *Demo için hedef uydurmak, `pvm:` eşleştirmesinde reddedilenin aynısıdır.*"""
    assert beyan(_SEMA, "parti", "toplam_ciro") is None
    assert beyan(_SEMA, "oee", "olmayan_olcu") is None
    assert beyan(_SEMA, None, "ort_oee") is None


def test_SIFIR_HEDEF_HEDEFSIZLIK_DEGILDIR():
    """🔴🔴 `None` *«hedef 0»* DEĞİLDİR.

    *Sıfır hedef **ulaşılmış** bir hedeftir; hedefsizlik ise **ölçülemezliktir**.*
    Bu ayrım kaybolursa hedefi olmayan her ölçü *«hedefe ulaştı»* diye raporlanır.
    """
    assert beyan(_SEMA, "oee", "sifir") == 0.0
    assert beyan(_SEMA, "oee", "sifir") is not None


def test_BOZUK_BEYAN_BEYAN_YOKTUR():
    """⚠ Bozuk bir sayı, *«0»* diye okunsaydı sessizce ulaşılmış bir hedef üretirdi."""
    assert beyan(_SEMA, "oee", "bozuk") is None


# ── yön ──────────────────────────────────────────────────────────────────────
def test_YON_YENIDEN_BEYAN_EDILMEZ_TUREYIR():
    """🔴 `B-5`'in 173/173 yön beyanı bu bayrağın ÖN KOŞULUDUR.

    Yön yanlışsa *«hedefe ulaşıldı»* kararı da **ters** çıkar — ve o, doğru görünen
    bir yanlıştır.
    """
    assert yon(_SEMA, "oee", "toplam_fire_kg") != yon(_SEMA, "oee", "ort_oee")


# ── blok ─────────────────────────────────────────────────────────────────────
def test_COK_OLCULU_RAPORDA_BLOK_URETILMEZ():
    """⚠ *Hangi hedef?* — belirsiz. Birini seçmek sessiz bir karar olurdu."""
    cq = {"cube": "oee", "measures": ["ort_oee", "toplam_fire_kg"]}
    assert blok(_SEMA, cq, {"rows": [{"ort_oee": 0.8, "toplam_fire_kg": 5}]}) is None


def test_SATIR_YOKSA_BLOK_URETILMEZ():
    cq = {"cube": "oee", "measures": ["ort_oee"]}
    assert blok(_SEMA, cq, {"rows": []}) is None


def test_GERCEKLESEN_SONUCTAN_OKUNUR():
    """🔴 Hedeften türetmek, kullanıcının sayısını sistemin sayısıyla değiştirmektir."""
    cq = {"cube": "oee", "measures": ["ort_oee"]}
    b = blok(_SEMA, cq, {"rows": [{"ort_oee": 0.60}, {"ort_oee": 0.80}]})
    assert b is not None
    assert abs(b["gerceklesen"] - 0.70) < 1e-9, "iki satırın ortalaması alınmalı"
    assert b["hedef"] == 0.75
    assert b["ulasildi"] is False, "0.70 < 0.75 ve yüksek=iyi → ulaşılmadı"


def test_DUSUK_IYI_OLCUDE_ULASILDI_TERS_CALISIR():
    """🔴 Yönün asıl sınavı: fire'de **az** olmak hedefe ulaşmaktır."""
    cq = {"cube": "oee", "measures": ["toplam_fire_kg"]}
    b = blok(_SEMA, cq, {"rows": [{"toplam_fire_kg": 800}]})
    assert b is not None and b["ulasildi"] is True, b
    kotu = blok(_SEMA, cq, {"rows": [{"toplam_fire_kg": 1200}]})
    assert kotu is not None and kotu["ulasildi"] is False


def test_HEDEFSIZ_KUP_BLOK_URETMEZ():
    """`KURAL B`'nin veri tarafı: beyansız küpte bayrak açık olsa bile çıktı **yok**."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"]}
    assert blok(_SEMA, cq, {"rows": [{"toplam_ciro": 100}]}) is None
