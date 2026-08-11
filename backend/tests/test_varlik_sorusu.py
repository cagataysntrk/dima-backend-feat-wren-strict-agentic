"""🔴🔴 `§KV` — **«KAÇ MAKİNEMİZ VAR» BİR METRİK SORUSU DEĞİLDİR.**

## Ölçülen kusur (curl `V` turu, 2026-08-11 · dört vaka + bir negatif kontrol)

    «kaç makinemiz var»        → 11 satır `makine × ort_oee` + uydurma 12 aylık dönem
    «hangi müşterilerimiz var» → `cari_kodu × hareket_sayisi` + uydurma dönem
    «kaç müşterimiz var»       → 🔴 TEK satır `{M1001, hareket_sayisi: 23}`
    «makineleri listele»       → 11 satır `makine × ort_oee` + uydurma dönem
    «kaç parti üretildi bu yıl» → `parti_sayisi = 7595`  ✅ ← ÖLÇÜ sorusu, doğru

Üçüncüsü en kötüsü: *«kaç müşterimiz var»* sorusuna **bir müşterinin hareket sayısı**.
"""

import pytest

from app import sayim

_SEMA = {"cubes": [
    {"name": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
     "time_dimensions": ["tarih"], "measure_synonyms": {"ort_oee": ["oee"]},
     "dimension_synonyms": {"makine": ["makine", "tezgah"]}},
    {"name": "parti", "measures": ["parti_sayisi"], "dimensions": ["musteri"],
     "time_dimensions": ["tarih"],
     "measure_synonyms": {"parti_sayisi": ["kac parti", "parti sayisi"]},
     "dimension_synonyms": {"musteri": ["musteri", "müşteri"]}},
]}


@pytest.mark.parametrize("q", ["kaç makinemiz var", "hangi müşterilerimiz var",
                               "kaç müşterimiz var", "makineleri listele"])
def test_VARLIK_SORUSU_TANINIR(q):
    """🔴 **Kapının kalbi** — ölçülen dört vakanın kendisi."""
    assert sayim.sorusu(q, _SEMA) is True, q


@pytest.mark.parametrize("q", ["kaç parti üretildi bu yıl", "bu yıl toplam oee",
                               "makine bazında oee listele"])
def test_OLCU_SORUSUNA_KARISMAZ(q):
    """🔴🔴 **Yanlış-pozitif kapısı** — `§101.1`: bir metrik sorusunu varlık sorusu
    sanmak, kullanıcının istediği sayıyı **silmek** olurdu.

    ⊙ `«kaç parti üretildi»` canlıda ölçülmüş **negatif kontroldür**: orada `parti` bir
    **ölçünün** sinonimidir (`kac parti`), bir boyut değil."""
    assert sayim.sorusu(q, _SEMA) is False, q


def test_YUKLEM_ALAN_TERIMI_ICERMEZ():
    """🔴 ADR-0008 — tetikleyici kapalı bir **dilbilgisi sınıfıdır** (soru zamiri +
    varlık yüklemi); içinde tek bir **alan** kelimesi yoktur. Alan bilgisi katalogdan
    gelir. *Bir yüklem alan kelimesi taşımaya başladığında, o bir yüklem değil bir
    sözlüktür.*"""
    kalip = sayim._VARLIK_RE.pattern
    for alan in ("makine", "musteri", "ciro", "fire", "oee", "parti"):
        assert alan not in kalip


def test_FIS_OLCUYU_DUSURUR():
    """⚠ `measures: []` motorun desteklediği biçimdir — ölçüldü:
    `SELECT makine AS makine FROM oee_vardiya GROUP BY 1`."""
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2025-06-01"}]}
    yeni, beyan = sayim.fisi("kaç makinemiz var", cq, _SEMA)
    assert yeni["measures"] == []
    assert yeni["dimensions"] == ["makine"]
    assert beyan and "ölçü hesaplanmadı" in beyan


def test_FIS_VARSAYILAN_DONEMI_DUSURUR():
    """🔴 Bir makinenin listesi bir döneme ait değildir; *«son 12 ayı aldım»* burada bir
    varsayım değil bir **yanlıştır**."""
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2025-06-01"}]}
    yeni, _ = sayim.fisi("kaç makinemiz var", cq, _SEMA)
    assert not [f for f in yeni["filters"] if f["dimension"] == "tarih"]


def test_KULLANICININ_DONEMI_EZILMEZ():
    """⚠ Bir **seçim** ezilmez, bir **boşluk** doldurulur: kullanıcı dönem yazdıysa
    süzgeç kalır."""
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    yeni, beyan = sayim.fisi("bu yıl hangi makinelerimiz var", cq, _SEMA)
    assert [f for f in yeni["filters"] if f["dimension"] == "tarih"]
    assert "dönem varsayılmadı" not in beyan


def test_BOYUTSUZ_FISE_DOKUNULMAZ():
    """*Boyutsuz bir varlık sorusu, cevaplanacak bir liste değildir* — orada susmak
    doğrudur (`§101.1`)."""
    cq = {"cube": "oee", "measures": ["ort_oee"]}
    assert sayim.fisi("kaç makinemiz var", cq, _SEMA) == (cq, None)


def test_FIS_HER_ZAMAN_TUPLE():
    """⚠ Bir üslup tercihi değil bir **tavan** kararı: dallanma çağırana yazılsaydı
    `ask()`e iki satır daha ekleyecekti. *Bir tavan, kodu modüle iterken imzayı da
    biçimlendirir.*"""
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    for q in ("bu yıl toplam oee", "kaç makinemiz var"):
        out = sayim.fisi(q, cq, _SEMA)
        assert isinstance(out, tuple) and len(out) == 2
    assert sayim.fisi("x", None, _SEMA) == (None, None)


def test_DARALTMA_SESSIZ_DEGIL():
    """🔴 Sessiz bir daraltma bu deponun en pahalı kusur sınıfıdır."""
    class _R:
        note = "önceki not"
        trace = ["a"]
    r = _R()
    sayim.beyan_ekle(r, "beyan")
    assert r.note.startswith("beyan") and "önceki not" in r.note
    assert any("§KV" in t for t in r.trace)


def test_BEYAN_YOKSA_CEVAP_BOZULMAZ():
    """`KURAL B` — yüklem susarsa cevap bayt bayt bugünküdür."""
    class _R:
        note = "n"
        trace = ["t"]
    r = _R()
    sayim.beyan_ekle(r, None)
    assert r.note == "n" and r.trace == ["t"]
    sayim.beyan_ekle(None, "x")          # düşmez


def test_OLCUSUZ_FISTE_DONEM_SORULMAZ():
    """🔴 Ölçüldü (curl `V` turu): fiş `measures: []` olduğu hâlde dönem kapısı
    *«dönemi çözemedim, son 12 ayı aldım»* deyip **filtre ekliyordu** — yani cevabın
    kendi beyanı (*«bir dönem varsayılmadı»*) ile fişi çelişiyordu.

    *Bir listeye «hangi dönem» diye sormak, listeyi bir toplam sanmaktır.*"""
    from app import cube_router

    assert cube_router.is_period_optional(None, {"semi_additive": []}) is True
    assert cube_router.is_period_optional("ort_oee", {"semi_additive": []}) is False
