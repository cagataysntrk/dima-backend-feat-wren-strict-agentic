r"""🔴🔴 `FAZ 8` — **NAİF SAYIM KENDİNİ BESLEMİYOR** (planın kapı adı).

Bir öneri listesinde tıklar **konuma** bağlıdır: birinci sıra en çok tıklanır çünkü
**birincidir**. Naif bir sayım bunu *«en iyi aday»* diye okur, sözlüğe yazar, aday bir
dahaki sefere **yine birinci** çıkar — ve ölçüt kendi ürettiği veriyle beslenir.

Bu dosyanın **asıl** yüklemi `test_NAIF_SAYIM_KENDINI_BESLERDI`: aynı kayıt kümesini
iki kuralla okur ve **ayrıştıklarını** gösterir. Ayrışmıyorlarsa koruma **yoktur**.
"""

from __future__ import annotations

from app.hasat import (
    SINYAL_GUCLU,
    SINYAL_NEGATIF,
    SINYAL_ZAYIF,
    Tiklama,
    hasat_adaylari,
    negatif_kanit,
    sinyal,
)


def _naif(kayitlar: list[Tiklama]) -> list[tuple[str, str]]:
    """**Karşı-kural**: her tıkı kanıt sayan naif sayım. Ürün kodunda **yok**; burada
    yalnız *«bizimki ondan farklı mı»* diye sormak için var ㉘."""
    return [(t.ham_ifade, t.gosterilen[t.konum])
            for t in kayitlar if 0 <= t.konum < len(t.gosterilen)]


# ── 🔴🔴 ASIL KAPI ──────────────────────────────────────────────────────────

def test_NAIF_SAYIM_KENDINI_BESLERDI():
    """🔴🔴 **Planın literal şartı.** Aynı kayıtlar, iki kural, **ayrı** sonuç.

    Senaryo: kullanıcılar hep 1. sırayı tıklıyor (konum yanlılığının saf hâli). Naif
    kural bunu *«bu eşleşme doğrulandı»* diye okur ve sözlüğe yazar → aday bir daha
    **kesin** birinci olur. Bizim kuralımız **hiçbir aday üretmez**.

    🅑 Mutasyon: `sinyal()`'de `konum == 0` dalı `GUCLU`'ya çevrilirse bu yüklem kırılır.
    """
    kayitlar = [Tiklama("fire", ("parti.fire", "oee.fire"), 0) for _ in range(50)]
    assert _naif(kayitlar), "karşı-kural aday üretmeliydi (fikstür bozuk ㉒)"
    assert hasat_adaylari(kayitlar) == [], (
        "🔴 KENDİNİ BESLEYEN DÖNGÜ: 1. sıraya yapılan tık sözlüğe girdi — o aday bir "
        "dahaki sefere yine birinci çıkar ve ölçüt kendi ürettiği veriyi ölçer.")


def test_SIRAYI_ATLAYAN_tik_GUCLU():
    """🟢 Kullanıcı sıralamaya **rağmen** seçtiyse, seçim konumla açıklanamaz — bu
    gerçek bir çeviri kanıtıdır."""
    t = Tiklama("fire", ("parti.fire", "oee.fire"), 1)
    assert sinyal(t) == SINYAL_GUCLU
    assert hasat_adaylari([t]) == [("fire", "oee.fire")]


def test_HICBIRINI_SECMEDI_NEGATIF_ve_ADAY_URETMEZ():
    """`8.4` — *«yazdı, hiçbirini tıklamadı»*: gösterilenler **yanlıştı**.

    ⚠ Negatif sinyal aday **üretmez** ve üretmemeli 🆋: *«bu liste yanlıştı»* bir
    eşleşme **vermez**; yalnız sıralamaya karşı kanıttır. Ama **sayılır** — sayılmayan
    bir olumsuzluk, hiç yaşanmamış gibidir 🆆.
    """
    t = Tiklama("zurnalama", ("parti.fire", "oee.fire"), -1)
    assert sinyal(t) == SINYAL_NEGATIF
    assert hasat_adaylari([t]) == []
    assert negatif_kanit([t]) == {"parti.fire": 1, "oee.fire": 1}


def test_BIRINCI_SIRA_ZAYIF_ama_ATILMIYOR():
    """⚪ Zayıf sinyal sözlüğe girmez — ama sınıfı **beyan edilir** 🅖; bir gün konum
    düzeltmesi kalibre edilirse veri orada durur."""
    assert sinyal(Tiklama("fire", ("a", "b"), 0)) == SINYAL_ZAYIF
    assert sinyal(Tiklama("fire", (), 0)) == SINYAL_ZAYIF   # gösterilen yok → öğrenme yok


def test_AYNI_CIFT_TEKILLESTIRILIR():
    """㉛ Aynı `(ifade, alan)` iki kez tıklandıysa **bir** adaydır; yoksa kuyruk aynı
    satırı çoğaltır ve onaylayan kişi aynı kararı iki kez verir."""
    k = [Tiklama("fire", ("a", "b"), 1), Tiklama("fire", ("a", "b"), 1)]
    assert hasat_adaylari(k) == [("fire", "b")]


def test_NAIF_GIRDI_PATLAMIYOR():
    """🅡 Konum sınır dışıysa, ifade boşsa — kayıt **sessizce düşer**, çökme yok."""
    assert hasat_adaylari([Tiklama("fire", ("a",), 5)]) == []
    assert hasat_adaylari([Tiklama("  ", ("a", "b"), 1)]) == []
    assert hasat_adaylari([]) == []
    assert negatif_kanit([]) == {}


# ── `KAT-1` + `E-8` — kuyruğun sahibi TEK, ve uç yalnız ÇAĞIRIR ─────────────

def test_UC_SINYALI_KENDI_HESAPLAMIYOR():
    """`KAT-1`: sinyal sınıfının **tek sahibi** `hasat.sinyal`. Uç onu **çağırır**;
    ikinci bir eşik/kural yazsaydı ikisi bir gün ayrışırdı ㊲.

    🅑 Mutasyon: uçtaki `hasat.sinyal(t)` çağrısı elle bir `if konum == 0` ile
    değiştirilirse bu yüklem kırılır.
    """
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1] / "app" / "routers"
           / "oneri.py").read_text(encoding="utf-8")
    assert "hasat.sinyal(t)" in src, (
        "🔴 uç sinyali kendisi hesaplıyor olabilir — `hasat.sinyal` tek sahip olmalı.")
    for kotu in ("konum == 0", "konum > 0", "konum >= 1"):
        assert kotu not in src, f"🔴 uçta ikinci bir konum kuralı: {kotu!r} ㊲"


def test_UC_KUYRUGA_DOGRUDAN_YAZMIYOR():
    """🔴 `8.5`'in sınırı: kuyruğa yazan **yalnız** `sinonim_onerici.kuyruga_koy`'dur
    ve `approved=False` orada **sabittir**. Bir HTTP ucu doğrudan yazsaydı, onaysız
    bir öneri kullanıcı isteğiyle **canlıya** girebilirdi.

    ⚠ `E-8` kapısı (`test_sinonim_onerici.py`) bunu zaten tutuyor; buradaki yüklem
    **aynı yasağın öteki ucu**: uç, kuyruk modülünü **import bile etmez**.
    """
    import ast
    import pathlib

    agac = ast.parse((pathlib.Path(__file__).resolve().parents[1] / "app" / "routers"
                      / "oneri.py").read_text(encoding="utf-8"))
    for d in ast.walk(agac):
        adlar: list[str] = []
        if isinstance(d, ast.Import):
            adlar = [a.name for a in d.names]
        elif isinstance(d, ast.ImportFrom):
            adlar = [d.module or ""] + [a.name for a in d.names]
        assert not any("sinonim_onerici" in a for a in adlar), (
            "🔴 öneri ucu kuyruk modülünü import ediyor — onaysız bir öneri kullanıcı "
            "isteğiyle canlıya girebilir.")


# ── ⊘ `8.3` (`ε`) ERTELEMESİNİN KAPISI ㊻ ───────────────────────────────────

def test_EPSILON_ERTELEMESI_HALA_GECERLI():
    """🔴 `8.3` ⊘: `ε` karıştırmanın faydası ancak **tıklama verisiyle** ölçülür
    (*«karıştırılmış turlarda güçlü sinyal oranı arttı mı»*). Ölçmeden konan bir `ε`
    listeyi bozar ve karşılığında **hiçbir sayı** üretmez 🆕.

    Bu yüklem, `ε`'nin **sessizce** sızmamasını tutar: sıralamaya rastgelelik girerse
    kapı kırmızı verir ve o gün ölçüm de **istenir**.
    """
    import inspect

    from app import oneri

    kaynak = inspect.getsource(oneri)
    for kotu in ("random.", "shuffle", "randint", "uniform("):
        assert kotu not in kaynak, (
            f"🔴 öneri sıralamasına rastgelelik girmiş ({kotu!r}) — `8.3` ölçüme "
            "bağlıydı; ölçüm yapılmadan `ε` bir deneyim borcudur.")


# ── 🅡 BOZUK GÖVDE BİR HÂLDİR, BİR ÇÖKME DEĞİL (denetim ajanı bulgusu) ───────

def test_BOZUK_GOVDE_500_URETMEZ():
    """🔴 **Ölçülmüş kusur** (denetim ajanı, 2026-08-13): uç `int(govde["konum"])`'i
    `try` dışında çağırıyordu → `konum:"abc"` **ValueError**, `konum:null`
    **TypeError** → işlenmemiş **500**.

    Yani uç, kendi docstring'inin *«kayıt başarısız olsa da `{"kaydedildi": false}`
    döner»* vaadini bozuk gövdede **tutmuyordu** 🆅. `§101.1`: öneri katmanı cevabı
    bozmaz — **kendi ucunu da** bozmamalı.

    🅑 Mutasyon: `govdeden`'deki `try/except` kaldırılırsa bu yüklem kırılır.
    """
    from app.hasat import govdeden

    for kotu in ({"konum": "abc"}, {"konum": None}, {"konum": [1]}, {}, None, 42):
        t = govdeden(kotu)
        assert t.konum == -1, f"🔴 {kotu!r} → konum={t.konum} (okunamayan konum «seçim yok» olmalı)"


def test_GOSTERILEN_DIZE_ISE_KARAKTERLERE_ACILMAZ():
    """🔴 Ölçülen ikinci yarı: `{"gosterilen": "abc"}` **üç sahte adaya** (`'a','b','c'`)
    açılıyordu — hasat kuyruğuna **çöp kimlik** yolu.

    ⚠ Bir dize bir dizidir ama bir **liste değildir**; üzerinde döngü kurmak onu
    karakterlere böler. Bu, Python'un en sessiz naif-girdi tuzağıdır 🅡.
    """
    from app.hasat import govdeden

    assert govdeden({"gosterilen": "abc", "konum": 1}).gosterilen == ()
    assert govdeden({"gosterilen": ["a", "b"], "konum": 1}).gosterilen == ("a", "b")


def test_UC_GOVDEYI_KENDI_AYRISTIRMIYOR():
    """`KAT-1`: gövde biçiminin sahibi `hasat.govdeden`; uç yalnız **çağırır** ㊲."""
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1] / "app" / "routers"
           / "oneri.py").read_text(encoding="utf-8")
    assert "hasat.govdeden(govde)" in src
    assert "int(govde" not in src, "🔴 uç konumu kendisi ayrıştırıyor — ikinci sahip ㊲"
