"""🔴🔴 `§DK-2` — **UYDURULMUŞ BİR SÜZGEÇ DEĞERİ, SESSİZ BİR SIFIR SATIRDIR.**

Bu kapı iki şeyi birden kilitler ve ikisi **zıt yönlüdür**:

1. Karşılığı olmayan bir değer **sessizce koşturulmaz** (kusurun kendisi)
2. Enum'u **olmayan** bir boyutta kapı **hiçbir şey söylemez** (kapının kendi riski)

⚠ İkincisi birincisinden önemlidir: `§101.1` — *yanlış-pozitif bir yüklem, kapatmaya
çalıştığı kusurdan pahalıdır.* Bir kullanıcının doğru sorgusunu reddeden bir kapı,
sessiz bir sıfır satırdan daha çok zarar verir, çünkü **her seferinde** yanlıştır.
"""

from app import deger_capasi as dk

_SEMA = {
    "cubes": [
        {
            "name": "maliyet",
            "time_dimensions": ["tarih"],
            "dimension_values": {
                # ✅ TAM enum — `wren_service` yalnız sayılabilen boyutu yazar
                "makine": ["RAM-1", "RAM-2", "KONTİNÜ KASAR", "DİJİTAL BASKI"],
                # ⚠ enum YOK: `musteri` çok değerli → kapı burada YARGI VERMEZ
            },
        },
    ]
}


def _cq(**f):
    return {"cube": "maliyet", "measures": ["ort_birim_maliyet"], "filters": [f]}


def test_GECERLI_DEGER_DOKUNULMAZ():
    """`KURAL B`'nin özü: doğru bir sorgu bu kapıdan **fark edilmeden** geçer."""
    assert dk.denetle(_cq(dimension="makine", operator="eq", value="RAM-1"), _SEMA) == []


def test_BUYUK_KUCUK_HARF_VE_AKSAN_FARKI_KUSUR_DEGIL():
    """*«KONTINU KASAR»* bir uydurma değil bir **yazımdır** — `_norm` ikisini eşitler."""
    assert dk.denetle(_cq(dimension="makine", operator="eq",
                          value="kontinü kasar"), _SEMA) == []


def test_UYDURMA_DEGER_YAKALANIR_VE_ONERISI_YOKTUR():
    """🔴 Ölçülen canlı kusur: `makine eq "Bakım"` → 0 satır, beyan yok."""
    b = dk.denetle(_cq(dimension="makine", operator="eq", value="Bakım"), _SEMA)
    assert len(b) == 1 and b[0].deger == "Bakım"
    assert b[0].oneri is None, "«Bakım» hiçbir makineye yakın değil — öneri UYDURULAMAZ"
    assert "listesinde yok" in dk.netlestirme_metni(b)
    # 🔴 Chip'ler **gerçek** değerlerden gelir; kullanıcı bir sonraki turu tıklayabilir.
    assert {s["label"] for s in dk.secenekler(b)} <= set(_SEMA["cubes"][0]
                                                        ["dimension_values"]["makine"])


def test_TEK_HARF_SAPMASI_DUZELTILIR_VE_SOYLENIR():
    """Bir yazım hatası bir netleştirme sebebi değildir — ama **sessiz** düzeltme de
    bir uydurmadır. Düzeltilir **ve söylenir**.

    ⚠ Vaka bilerek **tek adaylı**: ilk yazımda `RAM-l` (küçük L) seçilmişti ve kapı bunu
    reddetti — haklı olarak, çünkü `RAM-l` hem `RAM-1`'e hem `RAM-2`'ye **bir harf**
    uzakta. *Beklentim yanlıştı, kural değil.* Bkz. `test_BERABERE_YAKINLIKTA…`.
    """
    cq = _cq(dimension="makine", operator="eq", value="DİJİTAL BASKII")
    b = dk.denetle(cq, _SEMA)
    assert b and b[0].oneri == "DİJİTAL BASKI"
    metin = dk.duzelt_yerinde(cq, b)
    assert metin and "DİJİTAL BASKI" in metin
    assert cq["filters"][0]["value"] == "DİJİTAL BASKI", "düzeltme YERİNDE olmalı"


def test_ENUMU_OLMAYAN_BOYUTTA_YARGI_YOK():
    """🔴🔴 **Kapının kendi riski.** `musteri` çok değerli → `dimension_values`'ta kaydı
    YOK. Yokluk *«bilmiyorum»* demektir, *«yok»* değil — burada susmak zorunludur."""
    assert dk.denetle(_cq(dimension="musteri", operator="eq",
                          value="TOROS ÖRME"), _SEMA) == []


def test_ZAMAN_BOYUTU_ENUM_DEGILDIR():
    """Bir tarih sayılabilir bir küme değildir; ona enum üyeliği sormak kategorik bir
    hatadır."""
    assert dk.denetle(_cq(dimension="tarih", operator="eq", value="2026-01-01"),
                      _SEMA) == []


def test_ALT_DIZE_OPERATORU_UYELIK_SORMAZ():
    """`contains` bir **alt-dizedir**, enum üyeliği sormaz."""
    assert dk.denetle(_cq(dimension="makine", operator="contains", value="RAM"),
                      _SEMA) == []


def test_SIRALI_OPERATOR_METIN_ENUMDA_TUR_HATASIDIR():
    """🔴🔴 `§TK` — canlı ölçüm: garson *«%20 üstü»* için
    `{"dimension":"hat","operator":"gt","value":"20"}` üretti — **hat adını 20 ile
    karşılaştırdı**. Sekiz hattın hepsi döndü, süzgeç hiçbir şey yapmadı, beyan yok.

    ⚠ Eski beklenti *«sıralı operatörler hiç yargılanmaz»* idi ve bu kusuru **görmüyordu**;
    ölçüm o beklentiyi çürüttü. *Bir kapının kapsamı, kaçırdığı kusurla ölçülür.*
    """
    b = dk.denetle(_cq(dimension="makine", operator="gt", value="20"), _SEMA)
    assert b and b[0].boyut == "makine"
    assert "listesinde yok" in dk.netlestirme_metni(b)


def test_SAYISAL_ENUMDA_SIRALI_OPERATOR_MESRUDUR():
    """⚠ **Fail-closed:** enum'da bir tek sayı bile varsa yargı **verilmez** — kod-benzeri
    boyutlar (`«1»·«2»·«3»`) gerçekten sıralanabilir."""
    sema = {"cubes": [{"name": "maliyet", "time_dimensions": ["tarih"],
                       "dimension_values": {"kademe": ["1", "2", "3"]}}]}
    cq = {"cube": "maliyet", "filters": [{"dimension": "kademe", "operator": "gt",
                                          "value": "1"}]}
    assert dk.denetle(cq, sema) == []


def test_ENUMSUZ_BOYUTTA_SIRALI_OPERATOR_YARGILANMAZ():
    """⚠ Enum yoksa *«bilmiyorum»* — `§101.1`'in aynı disiplini."""
    assert dk.denetle(_cq(dimension="musteri", operator="gt", value="20"), _SEMA) == []


def test_IN_LISTESININ_HER_ELEMANI_AYRI_YARGILANIR():
    """Bir listedeki tek geçersiz eleman, listenin tamamını geçerli yapmaz."""
    cq = _cq(dimension="makine", operator="in", value=["RAM-1", "Bakım", "RAM-2"])
    b = dk.denetle(cq, _SEMA)
    assert [x.deger for x in b] == ["Bakım"]


def test_BERABERE_YAKINLIKTA_TAHMIN_YAPILMAZ():
    """🔴 İki aday eşit yakınsa **seçim yapılmaz** — tahmin, bu kapının kapattığı
    kusurun ta kendisidir."""
    sema = {"cubes": [{"name": "k", "dimension_values": {"d": ["ABC-1", "ABC-2"]}}]}
    cq = {"cube": "k", "filters": [{"dimension": "d", "operator": "eq", "value": "ABC-9"}]}
    b = dk.denetle(cq, sema)
    assert b and b[0].oneri is None, "eşit yakınlıkta öneri üretmek yazı-turadır"


def test_SEMA_YOKSA_SESSIZ():
    """Şema gelmediyse kapı kapalıdır — *bilmediğini yargılamak, bilmemekten kötüdür.*"""
    assert dk.denetle(_cq(dimension="makine", operator="eq", value="X"), None) == []
    assert dk.denetle({"cube": "yok_boyle_bir_kup",
                       "filters": [{"dimension": "makine", "operator": "eq",
                                    "value": "X"}]}, _SEMA) == []


def test_TEKIL_ONEK_COZULUR_VE_SOYLENIR():
    """🔴 Canlı ölçümden doğdu: garson `vardiya eq "3"` yazdı, kapı *«listede yok»* dedi
    ve **haklıydı** — ama kullanıcının kastettiği besbelliydi.

    *Dürüst bir red bir başarı değil, çözülecek bir borçtur.*
    """
    sema = {"cubes": [{"name": "k", "dimension_values": {
        "vardiya": ["1. Vardiya (08-16)", "2. Vardiya (16-24)", "3. Vardiya (00-08)"]}}]}
    cq = {"cube": "k", "filters": [{"dimension": "vardiya", "operator": "eq",
                                    "value": "3"}]}
    b = dk.denetle(cq, sema)
    assert b and b[0].oneri == "3. Vardiya (00-08)"
    assert dk.duzelt_yerinde(cq, b)
    assert cq["filters"][0]["value"] == "3. Vardiya (00-08)"


def test_COK_ADAYLI_ONEK_COZULMEZ_SORULUR():
    """⚠ Önek yolunun sınırı: `«RAM»` hem `RAM-1` hem `RAM-2`'yi çağırır. Orada soru
    sormak doğru kalır — *gevşetilen bir kural, gevşetildiği yerde tahmin üretir.*"""
    b = dk.denetle(_cq(dimension="makine", operator="eq", value="RAM"), _SEMA)
    assert b and b[0].oneri is None


def test_AYNI_BOYUTTAKI_COKLU_HATA_TEK_KEZ_LISTELENIR():
    """🔴 Canlı `D8` turu istedi: garson bir süzgece **beş** geçersiz değer koydu ve kapı
    geçerli listeyi **beş kez** bastı. Doğru bir cevaptı ama okunmuyordu.

    *Bir sınırı söylemek ile onu beş kez söylemek aynı şey değildir: ikincisi kullanıcıya
    cümleyi atlatır ve sınır yine görülmemiş olur.*
    """
    cq = _cq(dimension="makine", operator="in", value=["Bakım", "Depo", "Kalite"])
    b = dk.denetle(cq, _SEMA)
    metin = dk.netlestirme_metni(b)
    assert metin.count("Var olanlar") == 1, metin
    for d in ("Bakım", "Depo", "Kalite"):
        assert f"«{d}»" in metin
    assert "değerleri" in metin, "çoğul dilbilgisi"
    assert "bu değerleri" not in metin, "🔴 bozuk cümle («bu değerleri … yok»)"


def test_TEK_HATADA_CUMLE_DUZGUN():
    """⚠ Tekil vaka **kendi cümlesini** kurar: *«Bakım» makine listesinde yok.*

    ⊙ İlk yazımda tek şablona sıkıştırılmıştı ve canlıda *«20» — bu değeri hat
    listesinde yok»* gibi bozuk bir cümle çıktı. *Bir doğru bilgiyi bozuk bir cümleyle
    vermek, onu yarı yarıya vermektir.*
    """
    metin = dk.netlestirme_metni(
        dk.denetle(_cq(dimension="makine", operator="eq", value="Bakım"), _SEMA))
    assert "«Bakım» **makine** listesinde yok" in metin
    assert "bu değeri" not in metin
