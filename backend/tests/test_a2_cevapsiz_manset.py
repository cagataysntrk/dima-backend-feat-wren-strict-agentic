"""🔴🔴 `§A2`/`§A3` — **CEVAPSIZ VE SEMANTİK PAYDA MANŞETE GİRER** *(rapor `§14` FAZ 0)*.

⊙ Kusur: bu iki sayı **zaten hesaplanıyordu** ve şirket başına markdown'a yazılıyordu,
ama **kapı özetine hiç çıkmıyordu**. Manşet yalnız *«doğru-cube %»* diyordu — ve o oran
**SQL üretebilmiş** turların içindedir; cevapsız kalanlar o paydanın **dışındadır**.
Yani kapı, ürünün en görünür kusurunu **tanım gereği** göremiyordu.

⊙ Canlı ölçüm (uygulandıktan sonra):

    TOPLAM doğru-cube: %95.1 (taban %94.4) ✅
    🔴 cevapsız: 2980/14957 (%19.9)
    semantik vaka: 554/590 (%94) · ham tur: 14957 (şişme 25.4×)

*Ölçülmeyen bir kusur, kapatılmadığı için değil, bakılmadığı için kalır.*
"""

from __future__ import annotations


def test_MANSET_UC_SATIRI_DA_OZETE_TASIR():
    """`_son_anlamli` **son** işaretli satırı seçiyordu; üç satırlık korpus manşetinde
    bu, cevapsız ve semantik payda satırlarını **düşürürdü** — ölçüm eklendiği hâlde
    görünmezdi."""
    from lab.kapi import _son_anlamli

    cikti = "\n".join([
        "bazı gürültü",
        "  TOPLAM doğru-cube: %95.1 (taban %94.4) ✅",
        "  🔴 cevapsız: 2980/14957 (%19.9) — cevap yok",
        "  semantik vaka: 554/590 (%94) · ham tur: 14957 (şişme 25.4×)",
    ])
    out = _son_anlamli(cikti)
    assert "doğru-cube" in out and "cevapsız" in out and "semantik vaka" in out, out


def test_TEK_SATIRLIK_ADIMLAR_BOZULMAZ():
    """⚠ Öteki adımlar (süit, `eval`) **tek satır** basar — davranışları değişmemeli."""
    from lab.kapi import _son_anlamli

    assert _son_anlamli("x\n4993 passed, 58 skipped in 220s") == \
        "4993 passed, 58 skipped in 220s"
    assert _son_anlamli("hiç işaret yok\nson satır") == "son satır"
    assert _son_anlamli("") == "(çıktı yok)"


def test_CEVAPSIZ_BIR_ESIK_DEGIL_GORUNURLUK():
    """⚠ Bu satır kapıyı **kırmızı yapmaz**. Gerileme kapısı `doğru-cube` ve
    `sessiz_yanlış`ta kalır; `§A2` yalnız *«iyileşme nerede olmalı»*yı görünür kılar.
    Aksi hâlde bugünkü %19,9 **anında kırmızı** olurdu ve kapı kullanılamaz hâle gelirdi."""
    import inspect

    from lab import nl_corpus

    src = inspect.getsource(nl_corpus.kapi_degerlendir)
    blok = src.split("cevapsız:")[1].split("semantik vaka:")[0]
    assert "gecti = False" not in blok, "cevapsız satırı kapıyı kırmızı yapıyor"


def test_HAM_PAYDA_KORUNUR_KURAL_A():
    """`KURAL A` — ham tur paydası **korunur** (geçmiş tabanlar ona bağlı); semantik
    payda **yanına** yazılır, yerine değil."""
    import inspect

    from lab import nl_corpus

    src = inspect.getsource(nl_corpus.kapi_degerlendir)
    assert "ham tur:" in src and "şişme" in src
