"""🔴 `§E3` — KAÇ ADAY TARANDI, KAÇI İŞARETLENDİ.

Aykırılık sinyali `|z| ≥ 2` ile N nokta üzerinde koşuyor ve **N kullanıcıya hiç
söylenmiyordu** (ölçüldü, 2026-08-11). Oysa bir eşik, taranan aday sayısı büyüdükçe
**aritmetik gereği** işaret üretir; kullanıcı *«3 aykırılık»* cümlesinin çok mu az mı
olduğunu bilemez.

> *«In our experiment, over 60% of user insights were false.»* — CHI 2018 (`§10.5`)

🔴 **NEDEN BENJAMINI-HOCHBERG DEĞİL:** ölçüldü — bu depoda **p-değeri yok**; eşik bir
z-kesimidir, hipotez testi değil. BH p-değerlerini sıralar; z'yi p'ye çevirmek
**normallik varsayımını dayatmak** olurdu. ⊙ `§E2`'de forecast için verilen kararın
aynısı: *elimizde olmayan bir tabanı uydurmaktansa, elimizdekini beyan etmek.*
"""

from app.stats import ASGARI_GOZLEM, VARSAYILAN_K, tarama_beyani


def test_TARAMA_GENISLIGI_soyleniyor():
    b = tarama_beyani(30, 3)
    assert "30 aday tarandı" in b and "3'i" in b
    assert "|z| ≥ 2" in b


def test_SANS_PAYI_VARSAYIMIYLA_birlikte_yaziliyor():
    """⚠ Gizlenmiş bir varsayım, yapılmamış bir varsayımdan tehlikelidir."""
    b = tarama_beyani(30, 3)
    assert "normal" in b, "şans payının dayandığı varsayım ADIYLA söylenmeli"
    assert "~1.4" in b, "bu adayda kaç işaretin şansa düştüğü sayıyla verilmeli"


def test_ISARET_YOKSA_SUSULUR():
    """Bulgu yoksa tarama genişliği bir gürültüdür."""
    assert tarama_beyani(30, 0) == ""


def test_AZ_GOZLEMDE_SUSULUR():
    """`ASGARI_GOZLEM` altında istatistik zaten anlamsız — beyan da anlamsız olur."""
    assert tarama_beyani(ASGARI_GOZLEM - 1, 1) == ""


def test_BILINMEYEN_esikte_SANS_PAYI_UYDURULMAZ():
    """🔴 Tabloda olmayan bir `k` için oran **hesaplanmaz** — uydurulmaz."""
    b = tarama_beyani(30, 3, k=1.7)
    assert "30 aday tarandı" in b
    assert "normal" not in b and "kendiliğinden" not in b


def test_esik_sabiti_TEK_KAYNAK():
    assert VARSAYILAN_K == 2.0
