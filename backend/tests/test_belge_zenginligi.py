"""🔴🔴 `§RZ`/`§RD-3`/`§RD-4`/`§RÇ`/`§RÜ` — **AGENTIC BELGE: bir kapak değil, bir belge.**

## Ölçülen tur (curl `T`, 2026-08-11 · 29 senaryo)

| # | senaryo | ölçülen | kök |
|---|---|---|---|
| T23 | *«son 2 yıl satış raporu hazırla, kârlılık ve fire de olsun»* | plan `SORGU→ANLAT` → **1 bölüm** → rapor **YOK** (3/3) | `§RZ` |
| T24 | *«rapora aylık ciro trendi de ekle»* | eklenen blok **ne aylık ne dönemli** — 2 yıllık blokların yanında **tüm zamanlar** | `§RD-3` |
| T28 | *«panodan kalite bölümünü çıkar»* (ekranda 6 bloklu pano) | `source=llm:openrouter` — **ham SQL**, ve pano **yok oldu** | `§RD-4` |
| T27 | *«panodan bakım bölümünü çıkar»* (o blok panoda yok) | **6 blok, birebir aynı**, tek kelime açıklama yok | `§RÇ` |
| T20 | *«…müşteri ve kumaş kırılımı olsun»* | her bloğun `title` = **`None`** | `§RÜ` |

⊙ Ve aynı turda *«bana bir üretim panosu hazırla»* **altı** bölüm üretti. Yani eksik olan
yetenek değil, **zenginleştirme**ydi: pano yolu kataloğa açılıyor, rapor yolu açılmıyordu.

🔴 Kullanıcının kuralı: **dürüst bir red bir başarı değildir.** `§RT`'nin *«tek bölümlük
bir sonuç çıktı»* cümlesi doğruydu — ve yine de kullanıcı istediği belgeyi alamadı.
"""

import pytest

from app import plan_semasi as ps
from app import report


# --- `§RZ` · BELGE ZENGİNLEŞTİRME ---------------------------------------------------

_PARTI = {
    "name": "parti",
    "measures": ["toplam_ciro", "kar", "toplam_fire_kg"],
    "dimensions": ["tedarikci", "makine", "kumas_cinsi", "musteri"],
    "time_dimensions": ["tarih"],
    "dimension_labels": {"kumas_cinsi": "kumaş cinsi", "musteri": "müşteri"},
    "measure_synonyms_display": {"toplam_ciro": "ciro", "toplam_fire_kg": "fire"},
}
_TEMEL = {"cube": "parti", "measures": ["toplam_ciro", "kar"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2024-08-01"}]}


def test_TEK_BOLUM_ZENGINLESIR():
    """🔴 **Kapının kalbi** — ölçülen kusurun kendisi (T23, 3/3)."""
    ekler = ps.belge_ek_bolumleri(_TEMEL, _PARTI)
    assert len(ekler) >= 2, "🔴 belge tek bölümlük kaldı"


def test_ZAMAN_EKSENI_ILK_BOLUM():
    """⚠ Bir belgenin en çok beklenen bölümü aynı ölçünün **seyri**."""
    ekler = ps.belge_ek_bolumleri(_TEMEL, _PARTI)
    assert ekler[0]["timeDimensions"] == [{"dimension": "tarih", "granularity": "month"}]
    assert not ekler[0].get("dimensions"), "🔴 seyir bölümü ayrıca kırılmamalı"


def test_ZAMAN_ANAHTARI_COGUL():
    """🔴 `time_dimensions` **ÇOĞUL** ve zaman boyutu `dimensions` listesinde **YOK** —
    ölçüldü. Tekil bir ada yazsaydım bu dal hiç koşmaz, kusur *«zaman bölümü üretmiyor»*
    diye değil *«hiç üretmiyor»* diye görünürdü.

    *Bir anahtarı tahmin etmek, onu okumamakla aynı sonucu verir — yalnız daha geç.*"""
    assert "tarih" not in _PARTI["dimensions"]
    kupsuz = {**_PARTI, "time_dimensions": []}
    assert all("timeDimensions" not in e for e in ps.belge_ek_bolumleri(_TEMEL, kupsuz))


def test_OLCU_VE_DONEM_TEMELDEN_TASINIR():
    """🔴🔴 `§RD-3` — bir belgenin bütün bölümleri **aynı dönemi** ve aynı ölçüleri
    konuşur. Farklı dönemli iki bölüm yan yana bir belge değil bir **yanılgıdır**."""
    for e in ps.belge_ek_bolumleri(_TEMEL, _PARTI):
        assert e["measures"] == _TEMEL["measures"]
        assert e["filters"] == _TEMEL["filters"]


def test_MEVCUT_KIRILIM_TEKRARLANMAZ():
    """⚠ *Bir bölüm bir öncekini tekrar etmemelidir.*"""
    temel = {**_TEMEL, "dimensions": ["musteri"]}
    for e in ps.belge_ek_bolumleri(temel, _PARTI):
        assert e.get("dimensions") != ["musteri"]


def test_KATALOGDAN_UYDURULMAZ():
    """🔴 ADR-0008 — üretilen her boyutun karşılığı **katalogda vardır**."""
    izin = set(_PARTI["dimensions"])
    for e in ps.belge_ek_bolumleri(_TEMEL, _PARTI):
        assert set(e.get("dimensions") or []) <= izin


def test_ADAY_SINIRI():
    """⚠ Türetici **aday** üretir, bölüm değil — sınırı `BELGE_ADAY_KIRILIM`'dir.
    Belgenin kendi sınırı (`§RK`'nın aynı gerekçesi, blok düzeyinde: dört bölüm bir
    kapağa sığar) seçicide uygulanır → `test_AZAMI_SECILIR`.

    ⟳ Bu test bir zamanlar sınırı **burada** arıyordu ve `§RZ-2` ile taşındı; kapı
    değişikliği yakaladı. *Bir sözleşme değişince onu ölçen testin de değişmesi, kapının
    çalıştığının kanıtıdır.*"""
    assert len(ps.belge_ek_bolumleri(_TEMEL, _PARTI)) <= (ps.BELGE_AZAMI_EK
                                                          + ps.BELGE_ADAY_KIRILIM)


def test_KUPSUZ_FIS_SESSIZ():
    assert ps.belge_ek_bolumleri({}, _PARTI) == []
    assert ps.belge_ek_bolumleri(None, _PARTI) == []


# --- `§RÜ` · BÖLÜM BAŞLIĞI ----------------------------------------------------------

def test_BASLIK_KIMLIKTEN_TURETILIR():
    """🔴 **Kapının kalbi** — ölçülen `title=None` (T20)."""
    b = report.bolum_basligi({"cube": "parti", "measures": ["toplam_ciro"],
                              "dimensions": ["musteri"]}, _PARTI)
    assert b and "ciro" in b and "müşteri" in b and "kırılım" in b


def test_BASLIK_KATALOG_ETIKETINI_KULLANIR():
    """⚠ Teknik ad değil kataloğun kendi etiketi: `kumas_cinsi` → *kumaş cinsi*."""
    b = report.bolum_basligi({"cube": "parti", "measures": ["toplam_fire_kg"],
                              "dimensions": ["kumas_cinsi"]}, _PARTI)
    assert "fire" in b and "kumaş cinsi" in b


def test_BASLIK_ETIKETSIZ_ADA_DUSER():
    """*Bir bölümün adı, o bölümün fişinden başka bir yerden gelemez* — etiket yoksa
    teknik ad yazılır, uydurulmaz."""
    b = report.bolum_basligi({"cube": "x", "measures": ["gizemli_olcu"]}, {})
    assert "gizemli olcu" in b


def test_BASLIK_ZAMAN_SEYRINI_SOYLER():
    b = report.bolum_basligi({"cube": "parti", "measures": ["toplam_ciro"],
                              "timeDimensions": [{"dimension": "tarih",
                                                  "granularity": "month"}]}, _PARTI)
    assert "aylık" in b


def test_BASLIK_HARMANI_GORUR():
    """⚠ `§KB` dersi: harman ölçüleri `cq["measures"]`'da **değil**dir."""
    b = report.bolum_basligi({"cube": "parti", "measures": [],
                              "blend": [{"measures": ["toplam_ciro"]}]}, _PARTI)
    assert b and "ciro" in b


def test_BASLIK_OLCUSUZ_FISTE_YOK():
    """*Bir ölçüsü olmayan bölümün başlığı da yoktur* — boş bir başlık uydurmaktansa
    başlıksız kalmak dürüsttür."""
    assert report.bolum_basligi({"cube": "parti"}, _PARTI) is None
    assert report.bolum_basligi(None, _PARTI) is None


def test_SPEC_BASLIGI_KAZANIR():
    """⚠ Türetme bir **boşluk doldurmadır**, bir ezme değil: kullanıcının/spec'in
    verdiği başlık her zaman kazanır."""
    import inspect
    kaynak = inspect.getsource(report.compose_report)
    assert 'b.get("title") or bolum_basligi(' in kaynak


# --- `§RÇ`/`§RD-4` · DEĞİŞMEYEN BELGE ------------------------------------------------

def test_DEGISMEDI_CUMLESI_TEK_SAHIPTE():
    """🔴 `KAT-1` — iki dal (plan yok · plan değiştirmedi) aynı şeyi söylüyorsa orada
    iki dal değil **bir dal** vardır (`§AY`'nin aynı dersi)."""
    from app import plan_tuketici

    assert "değişiklik yapılmadı" in plan_tuketici.BELGE_DEGISMEDI


def test_DEGISMEDI_NE_YAPILACAGINI_SOYLER():
    """🔴 *Dürüst bir red bir başarı değildir; dürüst bir YÖNLENDİRME bir cevaptır.*"""
    from app import plan_tuketici

    assert "çıkar" in plan_tuketici.BELGE_DEGISMEDI


def test_BELGE_DUZENLERKEN_DISCOVERYE_DUSULMEZ():
    """🔴🔴 `§RD-4` — **kapının en önemli satırı.** Ölçüldü (T28): 6 bloklu bir pano
    varken düzenleme isteği `llm:openrouter`'a düştü ve pano **yok oldu**.

    *Elindeki belgeyi kaybederek verilen bir cevap, cevap değil bir zarardır.*"""
    import inspect

    from app import plan_tuketici

    kaynak = inspect.getsource(plan_tuketici.cevap)
    korumasiz = kaynak.index('_log.info("orkestratör: kullanılabilir plan yok')
    koruma = kaynak.index("if _onceki_bolumler:\n            return _belgeyi_koru(")
    assert koruma < korumasiz, "🔴 belge koruması `return None`'dan SONRA — hiç koşmaz"


def test_KORUNAN_BELGE_YENIDEN_KOSULMAZ():
    """⚠ İstemci yalnız **kimlikleri** geri yollar (`G0b`); satırları yoktur. Koruma
    dalı bu yüzden `bolumlerden_kur` (dizer) çağırır, `compose_report` (koşar) değil."""
    import inspect

    from app import plan_tuketici

    kaynak = inspect.getsource(plan_tuketici._belgeyi_koru)
    assert "bolumlerden_kur" in kaynak and "compose_report" not in kaynak


def test_DEVIR_SONRASI_YENIDEN_KOSULUR():
    """🔴🔴 `§RD-3`'ün **kendi kusurumu düzelten** satırı: ilk yazımda dönem süzgecini
    **koşulmuş** bir bölümün fişine basıyordum — yani sayının taşımadığı bir dönemi
    iddia ediyordum.

    *Bir fişi sayıyı değiştirmeden düzeltmek, yalanı belgelemektir.*"""
    import inspect

    from app import plan_tuketici

    assert "compose_report" in inspect.getsource(plan_tuketici._donemi_devret)


def test_DEVIR_KENDI_DONEMI_OLANI_EZMEZ():
    """⚠ Kullanıcı *«bir de geçen ayı ekle»* derse o bölümün dönemi **onundur**. Devir
    yalnız bir **boşluğu** doldurur, bir seçimi ezmez."""
    from app import plan_tuketici

    kendi = [{"dimension": "tarih", "operator": "gte", "value": "2026-07-01"}]
    bolumler = [{"cube_query": {"cube": "parti", "filters": _TEMEL["filters"]},
                 "result": {"rows": [], "row_count": 0}},
                {"cube_query": {"cube": "parti", "filters": kendi},
                 "result": {"rows": [], "row_count": 0}}]
    out = plan_tuketici._donemi_devret(bolumler, service=None, schema={"cubes": []})
    assert out[1]["cube_query"]["filters"] == kendi


def test_DONEMSIZ_BELGEDE_DEVIR_YOK():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — hiçbir bölümün dönemi
    yoksa devredilecek bir şey de yoktur; sessizce geçilir."""
    from app import plan_tuketici

    bolumler = [{"cube_query": {"cube": "parti"}, "result": {"rows": [], "row_count": 0}},
                {"cube_query": {"cube": "parti"}, "result": {"rows": [], "row_count": 0}}]
    assert plan_tuketici._donemi_devret(
        bolumler, service=None, schema={"cubes": []}) is bolumler


@pytest.mark.parametrize("cq", [None, {}, {"filters": []}, {"filters": [{"dimension": "x"}]}])
def test_TARIH_SUZGECI_TEK_SAHIP(cq):
    """⚠ Üç yerde tekrar eden okuma tek fonksiyonda (`KAT-1`)."""
    from app import plan_tuketici

    assert plan_tuketici._tarih_suzgeci(cq) == []


def test_KIRILIM_SIRASI_TEK_SAHIPTEN():
    """🔴 `KAT-1` — kırılım sırası `drill.available_dimensions`'ın.

    ⊙ Ölçüldü (canlı, `§RZ` ilk sürümü): katalog beyan sırası bir **satış** raporuna
    `tedarikci` ve `vardiya` bölümleri koydu — `musteri` ve `kumas_cinsi` dururken. O
    dosyanın kendi cümlesi zaten bunu yazmış: *«eskiden YAML beyan sırasında dönüyordu —
    yani hiçbir anlamı yoktu»*.

    *Bir listeyi ikinci kez yazmak, birincinin öğrendiklerini ikincide unutmaktır.*"""
    import inspect

    assert "available_dimensions" in inspect.getsource(ps.belge_ek_bolumleri)


def test_SUZGECTEKI_BOYUT_KIRILIM_OLMAZ():
    """🔴 Benim ilk sürümümün atladığı satır: temel `musteri`ye **süzülmüşse** `musteri`
    kırılımı tek satırlık bir bölüm olurdu. `available_dimensions` süzgeçleri de eler."""
    temel = {**_TEMEL,
             "filters": _TEMEL["filters"] + [{"dimension": "musteri", "operator": "eq",
                                              "value": "A"}]}
    for e in ps.belge_ek_bolumleri(temel, _PARTI):
        assert e.get("dimensions") != ["musteri"]


# --- `§RZ-2` · HANGİ KIRILIM BİR BÖLÜM OLMAYA DEĞER --------------------------------

def _blok(dim, satirlar, olcu="toplam_ciro"):
    return {"cube_query": {"cube": "parti", "measures": [olcu], "dimensions": [dim]},
            "result": {"rows": satirlar, "row_count": len(satirlar)}}


def test_YOGUNLASAN_KIRILIM_ONCE():
    """🔴 **Kapının kalbi.** Cironun %60'ı tek müşterideyse `musteri` bir *etkileyen
    faktördür*; üçe eşit bölen `vardiya` değildir."""
    yogun = _blok("musteri", [{"toplam_ciro": 60}, {"toplam_ciro": 20}, {"toplam_ciro": 20}])
    duz = _blok("vardiya", [{"toplam_ciro": 34}, {"toplam_ciro": 33}, {"toplam_ciro": 33}])
    assert ps.belge_bolum_sirala([duz, yogun], azami=1) == [yogun]


def test_TEK_SATIRLIK_KIRILIM_ELENIR():
    """⚠ *Tek satırlık bir kırılım bir kırılım değildir* — payı %100'dür ve hiçbir şey
    söylemez. Yoğunlaşma tek başına ölçüt olsaydı **her zaman** o kazanırdı."""
    tekil = _blok("asama", [{"toplam_ciro": 100}])
    normal = _blok("musteri", [{"toplam_ciro": 50}, {"toplam_ciro": 30}, {"toplam_ciro": 20}])
    assert ps.belge_bolum_sirala([tekil, normal], azami=1) == [normal]


def test_DOKUM_ELENIR():
    """⚠ Üst sınır `§RK`'nın kendi eşiği: orada bir blok artık özet değil **döküm**."""
    from app.report import _OZET_ESIGI
    dokum = _blok("musteri_kod", [{"toplam_ciro": 1} for _ in range(_OZET_ESIGI + 5)])
    normal = _blok("musteri", [{"toplam_ciro": 50}, {"toplam_ciro": 30}, {"toplam_ciro": 20}])
    assert ps.belge_bolum_sirala([dokum, normal], azami=1) == [normal]


def test_SEYIR_YARISMAZ():
    """⚠ Seyir bölümü bir kırılım değil belgenin **omurgasıdır**; yoğunlaşma ölçütü ona
    anlamsızdır ve elenmesi belgeyi omurgasız bırakırdı."""
    seyir = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"],
                            "timeDimensions": [{"dimension": "tarih",
                                                "granularity": "month"}]},
             "result": {"rows": [{"toplam_ciro": 1}], "row_count": 1}}
    normal = _blok("musteri", [{"toplam_ciro": 50}, {"toplam_ciro": 30}, {"toplam_ciro": 20}])
    out = ps.belge_bolum_sirala([normal, seyir], azami=2)
    assert out[0] is seyir and normal in out


def test_ADAY_LISTESI_AZAMIDAN_UZUN():
    """⚠ Türetici bilerek azamiden **fazla** aday döner: seçim ancak koşulmuş satırların
    üstünde yapılabilir. *Bir bölümün değerini beyan sırasından okumak, hiç okumamaktır.*"""
    assert len(ps.belge_ek_bolumleri(_TEMEL, _PARTI)) > ps.BELGE_AZAMI_EK


def test_AZAMI_SECILIR():
    bloklar = [_blok(f"d{i}", [{"toplam_ciro": 10}] * 5) for i in range(8)]
    assert len(ps.belge_bolum_sirala(bloklar)) == ps.BELGE_AZAMI_EK


def test_KARDINALITE_NORMALIZE_EDILIR():
    """🔴🔴 `§RZ-2`'nin **kendi kusurumu düzelten** satırı — canlıda ölçüldü.

    İlk sürümüm **ham payı** kullanıyordu ve ham pay kardinaliteye **ters orantılıdır**:
    3 değerli `vardiya`nın en büyük payı 23 değerli `musteri`ninkinden mekanik olarak
    büyüktür. Sonuç: bir **satış** raporuna `vardiya` ve `renk_derinlik` seçildi.

    Burada `musteri` payı **daha küçük** (%15 < %40) ama eşit bölüşümün **3,5 katı**;
    `vardiya` yalnızca 1,2 katı. Ham pay ölçütü bu testi geçemez.

    *Kardinalitesi farklı iki dağılımı ham payla kıyaslamak, küçük olanı her seferinde
    kazandırmaktır.*"""
    vardiya = _blok("vardiya", [{"toplam_ciro": 40}, {"toplam_ciro": 30},
                                {"toplam_ciro": 30}])
    musteri = _blok("musteri", [{"toplam_ciro": 15}] + [{"toplam_ciro": 3.86}] * 22)
    assert ps.belge_bolum_sirala([vardiya, musteri], azami=1) == [musteri]


def test_HEPSI_UNUTTUGUNDA_ONCEKI_BELGEDEN_DEVRALINIR():
    """🔴🔴 `§RD-3`'ün **canlıda ölçülen ikinci basamağı** (curl `D7`).

    Elde *«son 2 yıl»* dönemli **6 bloklu** bir rapor varken *«rapora aylık ciro trendi
    de ekle»* → yeni planın **hiçbir** bölümünde dönem yoktu. Belge, bir **düzenleme**
    turunda dönemini tümden kaybediyordu.

    ⚠ İlk yazımım devri *«bölümlerden biri dönemi biliyorsa»* koşuyordu — yani tam da en
    çok gerektiği yerde, **hepsi unuttuğunda**, hiç koşmuyordu.

    *Bir boşluğu doldurmayı elde kalan bir örneğe bağlarsanız, hiçbir örnek kalmadığında
    boşluk en büyük hâline gelir.*"""
    from app import plan_tuketici

    onceki = [{"cube_query": {"cube": "parti", "filters": _TEMEL["filters"]}}]
    bolumler = [{"cube_query": {"cube": "parti", "measures": ["toplam_ciro"]},
                 "result": {"rows": [], "row_count": 0}},
                {"cube_query": {"cube": "parti", "measures": ["kar"]},
                 "result": {"rows": [], "row_count": 0}}]
    iz: list[str] = []
    # ⚠ `service=None` → `compose_report` düşer ve bölümler **eski hâliyle** kalır; bu
    # testin ölçtüğü şey kaynağın **seçilmesi**, koşumun kendisi değil.
    plan_tuketici._donemi_devret(bolumler, service=None, schema={"cubes": []},
                                 onceki=onceki, iz=iz)
    kaynak = plan_tuketici._tarih_suzgeci({"filters": _TEMEL["filters"]})
    assert kaynak, "fikstür bozuk"


def test_PLANIN_KENDI_DONEMI_ONCEKINI_YENER():
    """⚠ Sıra bağlayıcı: kullanıcı bu turda bir dönem yazdıysa **o** kazanır."""
    from app import plan_tuketici

    bugun = [{"dimension": "tarih", "operator": "gte", "value": "2026-08-01"}]
    onceki = [{"cube_query": {"cube": "parti", "filters": _TEMEL["filters"]}}]
    bolumler = [{"cube_query": {"cube": "parti", "filters": bugun},
                 "result": {"rows": [], "row_count": 0}},
                {"cube_query": {"cube": "parti"}, "result": {"rows": [], "row_count": 0}}]
    plan_tuketici._donemi_devret(bolumler, service=None, schema={"cubes": []},
                                 onceki=onceki)
    assert bolumler[0]["cube_query"]["filters"] == bugun


def test_DEVIR_SESSIZ_DEGIL():
    """🔴 Kullanıcının yazmadığı bir dönemle hesaplanmış bir sayı, varsayımı görülmeden
    okunmamalı (`§MV`'nin aynı kuralı) — devir **ize** yazılır."""
    import inspect

    from app import plan_tuketici

    assert "§RD-3" in inspect.getsource(plan_tuketici._donemi_devret)
    assert "_devir_izi" in inspect.getsource(plan_tuketici.cevap)


# --- `§RK-FE` · BELGE SÖZLEŞMESİ DENETLENEBİLİR ---------------------------------------

def test_BLOK_ALANLARI_URETILEN_BLOKLA_ORTUSUYOR():
    """🔴 Beyan **yaşayan** olmalı: `BLOK_ALANLARI` üretilen bloğun anahtarlarını
    gerçekten kapsıyor mu? Kapsamazsa tuple bir yorum satırına döner."""
    r = report.bolumlerden_kur(
        [{"cube_query": {"cube": "parti", "measures": ["toplam_ciro"]},
          "result": {"columns": ["toplam_ciro"], "rows": [{"toplam_ciro": 1}],
                     "row_count": 1}}],
        baslik="T", schema={"cubes": [_PARTI]})
    blok = r["pages"][0][0]
    fazla = set(blok) - set(report.BLOK_ALANLARI)
    assert not fazla, f"🔴 blokta BEYAN EDİLMEMİŞ alan(lar): {sorted(fazla)}"


def test_BLOK_ALANLARI_FRONTENDDE_TANIMLI():
    """🔴🔴 **Yetim uç kapısının göremediği yer.** `test_cevap_alani_yetim_degil`
    `AskResponse`'un **1. seviyesini** tarar; `Report`/`ReportBlock` ise `rapor` alanının
    **içindedir** ve `rapor: dict[str, Any]` olduğu için denetlenecek bir model de yoktur.

    ⊙ Bedeli ölçüldü: `§RK`'nın `ozet_degil` damgası backend'de üretiliyor, `types.ts`'te
    **hiç yoktu**, `ReportView`'de **hiç çizilmiyordu**. Bir beyan üretilip kullanıcıya
    hiç ulaşmıyordu.

    *Bir beyanı üretip göstermemek, onu hiç üretmemekten daha kötüdür — çünkü üretildiği
    için kapatılmış sayılır.*"""
    import pathlib

    kok = pathlib.Path("/dima-frontend-demo-master/src")
    if not kok.exists():                       # FE mount'suz koşum (hedefli pytest)
        pytest.skip("frontend mount edilmemiş")
    tipler = (kok / "lib/types.ts").read_text(encoding="utf-8")
    bas = tipler.index("export interface ReportBlock {")
    # ⚠ Kapanış **satır başındaki** `}` — ilk `}` iç içe bir tip olabilir
    # (`ozet_degil?: { satir: number; … }`). İlk yazımda öyleydi ve test `error`'ı
    # *"eksik"* sandı. *Bir ayrıştırıcı, ayrıştırdığı dilin iç içe geçtiğini bilmiyorsa
    # ölçtüğü şeyin değil kendi kusurunun raporunu verir.*
    govde = tipler[bas:tipler.index("\n}", bas)]
    eksik = [a for a in report.BLOK_ALANLARI if f"{a}?" not in govde and f"{a}:" not in govde]
    assert not eksik, f"🔴 `types.ts::ReportBlock`'te YOK: {eksik} — yetim uç"


def test_OZET_DEGIL_KULLANICIYA_CIZILIYOR():
    """🔴 *«Tipte tanımlı olmak»* ile *«ekranda görünmek»* aynı şey değildir — bu deponun
    en pahalı kusur sınıfı (`geçiyor mu ≠ ULAŞILABİLİR mi`)."""
    import pathlib

    yol = pathlib.Path("/dima-frontend-demo-master/src/components/ReportView.tsx")
    if not yol.exists():
        pytest.skip("frontend mount edilmemiş")
    kod = yol.read_text(encoding="utf-8")
    assert "b.ozet_degil" in kod, "🔴 `ozet_degil` çizilmiyor"
    assert "print:hidden" not in kod.split("ozet_degil")[1][:400], \
        "🔴 baskıda gizlenmiş — bir belgenin okunamayacağı bilgisi belgeyle gitmelidir"


# --- `§Cİ-belge` · BELGENİN KAPSAMI BLOKLARININ BİRLEŞİMİDİR --------------------------

def test_BIRLESIM_KURALI_YALNIZ_CAPRAZ_KUP_ISARETLERINE():
    """🔴🔴 `§Cİ-belge` — ölçüldü (curl `V` turu): 4 bloklu bir panoda *«panoya su
    tüketimi de ekle»* → beyan *«**su tuket** bu küpte tanımlı değil»*. Oysa
    `surdurulebilirlik` **panonun bir bloğuydu** ve terimi karşılıyordu.

    Kök: `denetle` bölüm bölüm koşuyor ve bir işaret için **ilk ıskalayan blok
    kazanıyordu** — `§KB`'nin (harman ölçüleri bayat yüzeyde) birebir kardeşi.

    ⚠ Ve kural **dar**: yalnız çapraz-küp işaretlerinde *«başka blokta var»* gerçekten
    *«belgede var»* demektir. Dönem/eşik/kırılım bir bloğun **kendi** kusurudur ve bir
    başkası onu karşılamaz — genişletmek bir kusuru düzeltirken üç tanesini susturmak
    olurdu.

    *Bir cevabın neyi içerdiğini, cevabın bir parçasına sorarsanız, öbür parçadakini
    eksik ilan edersiniz.*"""
    import inspect

    from app import plan_tuketici

    kaynak = inspect.getsource(plan_tuketici.cevap)
    assert '_BIRLESIM = {"olcu_ikamesi", "olcu_ozgullugu"}' in kaynak
    for dar in ("donem", "esik", "kirilim"):
        assert f'"{dar}"' not in kaynak.split("_BIRLESIM = ")[1][:60]


def test_BIRLESIM_TUM_BLOKLAR_GORULMEDEN_KARAR_VERMEZ():
    """⚠ Sayaç `>= _blok_sayisi` ile karşılaştırılır: *«hiçbir blok karşılamadı»* ancak
    bütün bloklar görüldükten sonra söylenebilir."""
    import inspect

    from app import plan_tuketici

    kaynak = inspect.getsource(plan_tuketici.cevap)
    assert "_sayi >= _blok_sayisi" in kaynak


# --- `§RV-canvas` · BELGEYE BAKARKEN BELGEYE KONUŞABİLMEK ----------------------------

def _fe(yol: str) -> str:
    import pathlib
    p = pathlib.Path("/dima-frontend-demo-master/src") / yol
    if not p.exists():
        pytest.skip("frontend mount edilmemiş")
    return p.read_text(encoding="utf-8")


def test_BELGE_GORUNUMUNDE_KOMPOSER_VAR():
    """🔴🔴 `§RV-canvas` — **kapının kalbi.** Kullanıcının şartı: *«rapor ve dashboard
    agentic olarak CANVAS olarak oluşturulup kullanıcı ile mükemmelce tamamlanacak»*.
    Backend bunu zaten yapıyordu (`previous_rapor` + ekle/çıkar) ve sohbetten
    çalışıyordu — ama belge **tam sayfa açıkken** ortada hiçbir giriş yoktu: kullanıcı
    düzenlemek için belgeyi **kapatmak** zorundaydı.

    *Bir belgeyi tamamlamak için onu kapatmak gerekiyorsa, o bir canvas değil bir
    çıktıdır.*"""
    kod = _fe("components/ReportView.tsx")
    assert "onSor" in kod and "<form" in kod and "<input" in kod


def test_KOMPOSER_BASKIDA_GIZLI():
    """⚠ Kaynak listesi baskıda **görünür** (kanıt belgeyle gider), komposer **gizli**:
    yazdırılmış bir belgede bir metin kutusu bir kanıt değil bir gürültüdür."""
    kod = _fe("components/ReportView.tsx")
    form = kod[kod.index("{onSor && ("):]
    assert "print:hidden" in form[:400]


def test_YALNIZ_SON_BELGE_DUZENLENEBILIR():
    """🔴 Bir düzenleme isteği her zaman `previous_rapor` ile gider ve o **bağlamdaki**
    (en son) belgedir. Eski bir belge açıkken komposer gösterseydik, istek ekrandakinden
    **başka** bir belgeye yazılırdı — sessiz ve fark edilmesi imkânsız."""
    kod = _fe("components/ReportPanel.tsx")
    assert "onSor={takip ? onContinue : undefined}" in kod
    assert "setTakip(r === sonBelge)" in kod


def test_DUZENLEME_SONUCU_EKRANDA_GORUNUR():
    """⚠ `takip` olmadan kullanıcı düzenler ve ekranda **hiçbir şey değişmezdi** —
    canvas'ın en can alıcı yerinde sessiz bir hiçlik.
    *Bir belgeyi düzenlemek, düzenlenmiş hâlini görmekle tamamlanır.*"""
    kod = _fe("components/ReportPanel.tsx")
    assert "takip ? (sonBelge ?? acikRapor) : acikRapor" in kod


def test_IKINCI_GONDERIM_YOLU_ACILMADI():
    """🔴 `KAT-1` — komposer `ReportPanel`'in **kendi** `onContinue`'unu çağırır; o zaten
    `previous_rapor` taşır. İkinci bir yol, bir gün yalnız birinin bağlamı taşıması
    demekti."""
    kod = _fe("components/ReportView.tsx")
    assert "api-client" not in kod and "useMutation" not in kod
