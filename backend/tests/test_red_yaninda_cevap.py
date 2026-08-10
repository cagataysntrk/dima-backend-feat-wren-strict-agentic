"""🔴🔴 `§AA2` — **BİR TEKNİĞİN REDDİ, TURUN REDDİ OLAMAZ.**

## Ölçülen kusur (7 turluk canlı zincir, 2026-08-10)

Altı tur kusursuz aktı — odak beyanlı taşındı, yoy hesaplandı (`%22,12 vs %18,6`),
ciro eklendi. Yedinci tur *«özetle ne yapmalıyız»* **bomboş** döndü:

    source=None · rows=0 · interpretation=YOK · next_steps=[]
    note: «fire_orani_yuzde toplanabilir değil (non_additive) —
           katkı payı matematiksel olarak tanımsız olur»

Cümle **doğru**: bir oranda katkı payı gerçekten tanımsızdır. Ama kullanıcı *katkı payı*
istemedi, **özet** istedi — ve özet **elde vardı**: aynı sistem *«bunu nasıl
yorumlarsın»*a 2 olgu + 6 chip veriyor.

⊙ Ve bu, kardeş dosyanın (`contribution.py` `§AA1`) yazdığı dersin **birebir tekrarı**:
*«Bir sınırı aşmıyoruz, yanına doğru soruyu koyuyoruz.»*

*«Yapamam» bir cevap değildir; «şunu yapamam ama şunu biliyorum» bir cevaptır.*
"""

import pathlib
import re

_ASK = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"
_KAYNAK = _ASK.read_text(encoding="utf-8")


def _blok() -> str:
    """Katkı reddinin döndüğü dalın kaynağı — işaretten `return`'ün SONUNA kadar.

    ⚠ Pencere `return`'ü **içermek zorunda**: ilk yazımda sabit bir uzunluk (+2200)
    seçtim ve `result=`/`note=` satırları dışarıda kaldı; test kırmızı verdi ama sebep
    koddaki bir eksik değil, **yüklemin dar penceresiydi**. Bugün dördüncü kez aynı
    sınıf — *bir ölçüm aracının penceresi, ölçtüğü şeyi içermek zorundadır.*
    """
    i = _KAYNAK.find("§AA2")
    assert i > 0, "🔴 `§AA2` dalı kayboldu — red yine tek başına dönüyor olabilir"
    j = _KAYNAK.find("prescription=recete_payload)", i)
    assert j > i, "🔴 dalın `return`'ü bulunamadı — yapı değişmiş"
    return _KAYNAK[i - 400:j + 40]


def test_RED_DALI_ELDEKI_FISI_YENIDEN_KOSAR():
    """🔴 **Kapının kalbi.** Katkı raporu üretilemediğinde eldeki `cube_query`
    LLM'siz yeniden koşulur — `D4`'ün checkpoint yeteneği."""
    b = _blok()
    assert "_contrib.yanindaki_rapor(service, prev_cq)" in b, \
        "eldeki fiş yeniden koşulmuyor"


def test_SONUC_YANITA_ILISTIRILIR():
    """⚠ Koşmak yetmez: satırlar **yanıta** konmalı, yoksa `_maybe_interpret` yine
    boş bulur. *Bir cevabı üretmek, onu taşıyan alana koymakla tamamlanır.*"""
    assert re.search(r"result=_sonuc", _blok())


def test_RED_NOTU_KORUNUR():
    """🔴🔴 **Kapı fazla ileri gitmemeli:** sınır **kalkmıyor**, yanına cevap konuyor.
    Red notu silinirse matematiksel olarak tanımsız bir iddia sessizce meşrulaşır."""
    assert "note=not_metni" in _blok()


def test_KATKI_CALISTIYSA_IKINCI_SORGU_KOSULMAZ():
    """⚠ `E6` (gecikme): katkı raporu üretildiyse gövde zaten zengindir; ikinci sorgu
    boşuna maliyettir. Koşul **raporun yokluğuna** bağlı olmalı."""
    assert "if not katki.raporlar else None" in _blok()


def test_KOSUM_BASARISIZSA_RED_YINE_DONER():
    """*Bir en-iyi-çaba, başarısız olduğunda cevabı düşürmemelidir* — yeniden koşum
    patlarsa kullanıcı yine dürüst reddi görür, bir 500 değil."""
    gov = (pathlib.Path(__file__).resolve().parents[1] / "app" / "contribution.py"
           ).read_text(encoding="utf-8")
    i = gov.find("def yanindaki_rapor")
    assert i > 0 and "except Exception:" in gov[i:] and "red yine döner" in gov[i:]


def test_IZ_YENIDEN_KOSUMU_BEYAN_EDER():
    """🔴 Sessiz bir ikinci sorgu, sessiz bir maliyettir. İz onu **söyler**."""
    assert "§AA2" in _blok() and "yeniden koşuldu" in _blok()
