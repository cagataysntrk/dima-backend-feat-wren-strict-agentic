"""🌳 FAZ 4B kapısı — kök-neden haritasının **dört durumu** ve puanlaması.

Planın kapı tanımı birebir:
> *Düğüm durumu testi: dört durumun dördü de üretilebiliyor; **silik olan tıklanabilir**.*

⚠ İkinci şart birincisinden önemli. Bir düğümü *"veri yok"* diye **kapatmak**, bu
tasarımın tek fikrini öldürür: **bazen verinin yokluğu bulgunun kendisidir**
(*"o vardiyada hiç kayıt yok"*).
"""

from __future__ import annotations

import pytest

from app import kok_neden as kn


def _rapor(dim: str, paylar: list[float]) -> dict:
    """`contribution.decompose` çıktısının kapı için gereken **en küçük** hâli.

    ⚠ Gerçek `decompose` çağrılmıyor: bu kapı **puanlamayı** ölçer, ayrıştırmayı değil
    (onun kendi kapısı var — `test_contribution.py`). *Bir kapının neyi ölçmediğini
    bilmek, neyi ölçtüğünü bilmek kadar önemlidir.*
    """
    return {"dimension": dim, "dimension_label": dim,
            "bulgular": [{"deger": f"s{i}", "brut_pay": p, "delta": p}
                         for i, p in enumerate(paylar)]}


# ═══════════════════════════════════════════════════════════════════════════════
# EŞİK — kardinaliteden türer, uydurulmaz
# ═══════════════════════════════════════════════════════════════════════════════

def test_ESIK_KARDINALITEDEN_TUREDI():
    """🔴 Mutlak bir eşik (*"%25 üstü kanıtlı"*) **kardinaliteyi görmez**.

    3 segmentli bir boyutta %25 hiçbir şey söylemez (adil pay zaten %33); 40 segmentlide
    çok şey söyler (adil pay %2,5). Eşik bu yüzden boyutun **kendi** kardinalitesinden
    türer: *bilgi taşımayan bir boyut değişimi eşit dağıtır.*"""
    assert kn.esik(2) == 100.0          # iki-değerli boyutta açıklanacak dağılım YOK
    assert kn.esik(4) == 50.0           # adil pay %25 → iki katı
    assert kn.esik(10) == 20.0          # adil pay %10 → %20; taban da tam burada
    assert kn.esik(50) == kn.SINYAL_TABANI  # taban devreye girer, %4 değil


def test_ESIK_TABANI_YUKSEK_KARDINALITEDE_KORUR():
    """⚠ Taban olmasaydı 50 segmentli bir boyutta **%4'lük** bir pay *"kanıt"* diye
    gösterilirdi. *Göreli bir ölçüt, sınırsız bölündüğünde anlamını kaybeder.*"""
    for n in (30, 50, 200):
        assert kn.esik(n) == kn.SINYAL_TABANI


def test_ESIK_SIFIR_SEGMENTTE_ULASILAMAZ():
    """⊘ Segmentsiz bir boyut `kanitli` olamaz — ve bu bir hata değil, bir **durum**."""
    assert kn.esik(0) == 100.0


# ═══════════════════════════════════════════════════════════════════════════════
# DÖRT DURUM — planın kapı şartı
# ═══════════════════════════════════════════════════════════════════════════════

def test_DORT_DURUM_URETILEBILIYOR():
    """Planın kapısı: *dört durumun dördü de üretilebiliyor.*"""
    kanitli, s1 = kn.durum_of(_rapor("makine", [70, 20, 10]), tarandi=True)
    zayif, _ = kn.durum_of(_rapor("gun", [12, 11, 11, 10, 10, 10, 10, 9, 9, 8]), tarandi=True)
    olculemedi, s3 = kn.durum_of(_rapor("renk", [90, 10]), tarandi=False)
    assert (kanitli, zayif, olculemedi) == (kn.KANITLI, kn.ZAYIF, kn.OLCULEMEDI)
    assert s1 == 70.0 and s3 == 0.0
    # KAPSAM_DISI `durum_of`tan çıkmaz — o bir ÖLÇÜM sonucu değil, bir KATALOG olgusudur
    # (cube o boyutu taşımıyor). `harita()` onu `related_cubes`tan üretir.
    assert kn.KAPSAM_DISI in kn.DURUMLAR


def test_TARANMADI_ILE_BULGUSUZ_AYNI_SEY_DEGIL():
    """🔴 **Bu modülün varlık sebebi.** Biri *"bakmadım"*, öteki *"baktım, yok"*.

    Bugün `contribution.arastir` ikisini de görünmez kılıyor (`if not bulgular: continue`
    + `MAX_BOYUT` sınırı) ve kullanıcıya ikisi de **yok** gibi okunuyor.

    *Yalnız bulduğunu gösteren bir ağaç, bakmadığını gizler.*"""
    baktim_yok, _ = kn.durum_of({"bulgular": []}, tarandi=True)
    bakmadim, _ = kn.durum_of(None, tarandi=False)
    assert baktim_yok == kn.ZAYIF
    assert bakmadim == kn.OLCULEMEDI
    assert baktim_yok != bakmadim


def test_SILIK_DUGUM_TIKLANABILIR():
    """🔴 Planın kapısının **ikinci** şartı — ve birincisinden önemli.

    ⚠ Silik ≠ kapalı. Bir düğümü *"veri yok"* diye kapatmak bu tasarımın tek fikrini
    öldürür: **bazen verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt yok"*).

    Tıklanabilirliğin sözleşmedeki karşılığı: `⊘ olculemedi` bir düğüm de kendi
    `cube_query`'sini **taşır** — yani tıklandığında koşacak bir sorgusu vardır."""
    d = kn.dugum(boyut="vardiya", etiket="Vardiya", olcu="toplam_fire_kg",
                 durum=kn.OLCULEMEDI, sinyal=0.0,
                 cube_query={"cube": "parti", "dimensions": ["vardiya"]})
    assert d["cube_query"] is not None, "🔴 ⊘ düğüm tıklanamaz hâle gelmiş"
    assert d["durum"] == kn.OLCULEMEDI


def test_BILINMEYEN_DURUM_REDDEDILIR():
    """*Bir sözleşmenin dört değeri varsa, beşincisi bir yazım hatasıdır — ve sessizce
    kabul edilirse arayüzde görünmeyen bir düğüme dönüşür.*"""
    with pytest.raises(ValueError):
        kn.dugum(boyut="x", etiket="X", olcu="m", durum="belki", sinyal=0)


# ═══════════════════════════════════════════════════════════════════════════════
# SÖZLEŞME — ajanın ve arayüzün AYNI şekli görmesi
# ═══════════════════════════════════════════════════════════════════════════════

ALANLAR = {"boyut", "etiket", "deger", "olcu", "sinyal", "durum",
           "gerekce", "makbuz", "cube_query", "cocuklar"}


def test_DUGUM_SEMASI_TEK_URETICIDEN():
    """⚠ Alanları elle sözlük yazarak üretmek, ajanın ve arayüzün **farklı şekilli**
    düğümler görmesine yol açardı. Bu depoda *"bir alan adını okumadan yazmak"* dört kez
    kusur üretti; tek bir yapıcı o sınıfı kapatır."""
    d = kn.dugum(boyut="makine", etiket="Makine", olcu="ort_oee",
                 durum=kn.KANITLI, sinyal=61.3)
    assert set(d) == ALANLAR
    assert d["cocuklar"] == []


def test_SEMA_PYDANTIC_ILE_ORTUSUYOR():
    """🔴 *Beyan var, kod onu tanımıyor* — bu deponun ölçülmüş kusur sınıfı.

    `KokNedenDugum` alanları ile `kok_neden.dugum()` çıktısı **ayrışırsa** uç sessizce
    alan düşürür: ajanın gördüğü şema ile arayüzün gördüğü şema farklılaşır."""
    from app.schemas import KokNedenDugum

    assert set(KokNedenDugum.model_fields) == ALANLAR


def test_GEREKCE_SAYIYI_DEGIL_SEBEBI_ANLATIR():
    """*Bir ağırlık, sebebi okunmadıkça bir süstür* — deponun güven rozeti kararının aynısı.

    Kullanıcıya `z=2.4` göstermek bir gerekçe değildir; **kaç segmente dağıldığı** ve
    **eşit dağılsa ne olurdu** bir gerekçedir."""
    for durum, rapor, tarandi in ((kn.KANITLI, _rapor("m", [70, 20, 10]), True),
                                  (kn.ZAYIF, _rapor("g", [26, 25, 25, 24]), True),
                                  (kn.OLCULEMEDI, None, False)):
        st, sinyal = kn.durum_of(rapor, tarandi=tarandi)
        assert st == durum
        _, n = kn._sinyal(rapor) if rapor else (0.0, 0)
        metin = kn._gerekce(st, sinyal, n, "Makine")
        assert metin and "Makine" in metin and len(metin) > 20


def test_SIRALAMA_KARARLI_VE_DURUMA_GORE():
    """⚠ `sorted` kararlıdır: eşit ağırlıkta `available_dimensions`ın **maliyet sırası**
    korunur. Yoksa aynı soru iki kez sorulduğunda farklı bir ağaç görünürdü."""
    ham = [
        kn.dugum(boyut="c", etiket="c", olcu="m", durum=kn.KAPSAM_DISI, sinyal=0),
        kn.dugum(boyut="a", etiket="a", olcu="m", durum=kn.ZAYIF, sinyal=8),
        kn.dugum(boyut="b", etiket="b", olcu="m", durum=kn.KANITLI, sinyal=40),
        kn.dugum(boyut="d", etiket="d", olcu="m", durum=kn.OLCULEMEDI, sinyal=0),
        kn.dugum(boyut="e", etiket="e", olcu="m", durum=kn.KANITLI, sinyal=70),
    ]
    sirali = sorted(ham, key=lambda x: (kn.DURUMLAR.index(x["durum"]), -x["sinyal"]))
    assert [x["boyut"] for x in sirali] == ["e", "b", "a", "d", "c"]


def test_YENI_ISTATISTIK_MOTORU_YOK():
    """🔴 Kapı, modülün **kendi iddiasını** denetler: sinyal `rank_dimensions` ile *aynı*
    büyüklük olmalı — yani kendi z-skoru/entropisi **hesaplanmamalı**.

    ⚠ Bu deponun kuralı: *"mevcut sinyal-outlier tespiti yeniden kullanılır, yeni bir
    istatistik motoru İCAT EDİLMEZ."* Bir modülün docstring'i bunu söylerken gövdesinin
    formülü ikinci kez yazması **bu depoda bir kez oldu** (`flag_outliers`)."""
    import inspect

    kaynak = inspect.getsource(kn)
    for yasak in ("import statistics", "math.sqrt", "stdev", "z_skorlari"):
        assert yasak not in kaynak, f"🔴 kök_neden kendi istatistiğini kuruyor: {yasak}"


def test_SIFIR_BRUT_SIFIRA_BOLMEZ():
    """⚠ Tüm delta'ları 0 olan bir rapor (dönem değişmemiş) — sıfıra bölme adayı."""
    r = {"bulgular": [{"delta": 0}, {"delta": 0}]}
    st, sinyal = kn.durum_of(r, tarandi=True)
    assert st == kn.ZAYIF and sinyal == 0.0
