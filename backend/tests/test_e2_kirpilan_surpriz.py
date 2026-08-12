r"""🔴🔴 `§E2` — **KIRPMA SÜZGECİ SÜRPRİZ ADAYINI YİYORDU.**

## Kusur — iki bağımsız ölçüm, aynı sınıf

`decompose` segmentleri `|delta| / brüt ≥ %1` ile kırpar. Bu **`|delta|` merceğidir** —
ve `§E2`'nin **bütün tezi** *«`|delta|` yanlış mercek»*tir (Adtributor, NSDI'14). İkisi
çakışınca ölçü **kendi süzgecinin altında** kalıyordu: `surpriz_notu(bulgular)` adayını
**kırpılmış** listeden seçiyordu.

| girdi | kırpılan segment | hareketi | **sürpriz payı** | eski `surpriz_notu` |
|---|---|---|---|---|
| denetim ajanının vakası (`§E` raporu) | `Web` | %0,19 | **%43,3** *(en yüksek)* | `""` — hiç |
| kendi vakam (⟳ 08-12) | `C` | %0,20 | **%97,6** | *«A sebep değil»* — **ve susuyor** |

İkinci vakada kurucu örneğin can alıcı **ikinci yarısı** (*«dağılımı en çok değişen: …»*)
tam da **en gerekli olduğu anda** kayboluyordu: not *«en büyük kalem bir sebep değil»*
deyip, sebebin **kim olduğunu** söylemeden bitiyordu.

## Onarım — İKİ parçalı, ikisi de gerekli

① aday havuzu **kırpılmamış** liste; aday kırpıldıysa bu **söylenir**
② kırpılanların toplam JS payı `≥ KIRPILAN_SURPRIZ_ESIGI_YUZDE` ise **kütlesi** beyan edilir

⊙ **Neden ikisi birden:** ① tek başına yetmez — not **yalnız** en büyük kalemin payı
*değişmediğinde* üretiliyor (`SURPRIZ_ESIGI_PUAN`), oysa ajanın vakasında not `""` idi ve
%43,3 yine de kayboluyordu. ② tek başına yetmez — kütleyi söyler ama **adı** vermez.

> *Bir beyanı, ancak başka bir cümlenin üretildiği durumda vermek, onu beyan değil süs
> yapar.*
"""

from __future__ import annotations

from app.contribution import (
    KIRPILAN_SURPRIZ_ESIGI_YUZDE,
    contributions,
    decompose,
    surpriz_notu,
)

_CQ = {"cube": "c", "measures": ["v"]}

#: Denetim ajanının ölçtüğü vaka — `Web` toplam JS'in **%43,3**'ünü taşır, hareketi
#: `10/5220 = %0,19` olduğu için **kırpılır**.
_AJAN = [{"s": "X", "v": 4700.0, "v_gecen": 9400.0},
         {"s": "Mobile", "v": 100.0, "v_gecen": 500.0},
         {"s": "Tablet", "v": 210.0, "v_gecen": 100.0},
         {"s": "Web", "v": 4990.0, "v_gecen": 5000.0}]

#: Kendi vakam — `C` toplam JS'in **%97,6**'sını taşır; burada not **üretiliyor**
#: (`A`'nın payı %90→%90 değişmedi), yani beyanın **notun yanına** eklendiği yol.
_BENIM = [{"s": "A", "v": 4500.0, "v_gecen": 9000.0},
          {"s": "B", "v": 480.0, "v_gecen": 990.0},
          {"s": "C", "v": 20.0, "v_gecen": 10.0}]


def _kirpilan_js(satirlar: list[dict]) -> float:
    """Kırpılanların toplam sürpriz payı — **ölçümün kendisi**, kodun iddiası değil."""
    hepsi = contributions(satirlar, "s", "v")
    r = decompose(satirlar, "s", "v", _CQ)
    gos = {b["deger"] for b in r["bulgular"]}
    return sum(k.get("surpriz_pay") or 0.0 for k in hepsi if k["deger"] not in gos)


def test_OLCUM_TABANI_KIRPMA_GERCEKTEN_ATESLIYOR():
    """⊘ **Boş yeşil avı.** Bu iki fikstürde kırpma ateşlemiyorsa aşağıdaki üç yüklem
    de boşa düşer — ve kapı *«kusur yok»* diye okunur."""
    for ad, F in (("ajan", _AJAN), ("benim", _BENIM)):
        r = decompose(F, "s", "v", _CQ)
        assert r["kirpilan_segment"] >= 1, (
            f"⊘ ölçüm tabanı çöktü: `{ad}` fikstüründe kırpma ATEŞLEMEDİ — gürültü "
            f"payı ({r['kirpilan_esik_yuzde']}) değişmiş olabilir.")
        assert _kirpilan_js(F) >= KIRPILAN_SURPRIZ_ESIGI_YUZDE, (
            f"⊘ ölçüm tabanı çöktü: `{ad}` fikstüründe kırpılanların JS payı eşiğin "
            f"altında ({_kirpilan_js(F):.1f} < {KIRPILAN_SURPRIZ_ESIGI_YUZDE}).")


def test_NOT_URETILMESE_BILE_KIRPILAN_KUTLE_BEYAN_EDILIYOR():
    """🔴🔴 **ASIL KAPI — ajanın vakası.**

    Burada `surpriz_notu` **boş** döner (X'in payı %62,7→%47 *değişmiştir*, yani
    *«ölçeğin kendisi»* cümlesi geçerli değil). Eski kod bu yüzden **hiçbir şey**
    söylemiyordu — ve dağılım değişiminin **%43,3**'ü sessizce siliniyordu.
    """
    m = decompose(_AJAN, "s", "v", _CQ)["surpriz_notu"] or ""
    assert "43,3" in m, (
        "🔴 kırpılan segmentlerin JS kütlesi BEYAN EDİLMİYOR — dağılım değişiminin "
        f"%{_kirpilan_js(_AJAN):.1f}'i listeden çıkıyor ve kullanıcı bunu soramıyor:\n{m!r}")
    assert "listeye girmeyen" in m, (
        f"🔴 beyan, kütlenin **nereden** eksildiğini söylemiyor:\n{m!r}")


def test_NOT_VARSA_BEYAN_NOTU_SILMIYOR_YANINA_EKLENIYOR():
    """⚠ Kendi vakam: not **üretiliyor**. Beyan onun **yerine** geçerse `§E2`'nin
    kurucu cümlesi kaybolur — *bir eksiği kapatırken ötekini kapatmak, kapatmamaktır.*"""
    m = decompose(_BENIM, "s", "v", _CQ)["surpriz_notu"] or ""
    assert "ölçeğin kendisi" in m, f"🔴 kurucu cümle KAYBOLDU:\n{m!r}"
    assert "97,6" in m, f"🔴 kırpılan kütle beyanı yok:\n{m!r}"


def test_ADAY_KIRPILMISSA_NEREDE_OLMADIGI_SOYLENIYOR():
    """🔴 Aday havuzu artık **kırpılmamış** liste. Bir segmenti adıyla anıp onu
    listeden çıkarmak, kullanıcıyı **var olmayan bir satırı** aramaya gönderir.

    ⚠ Yüklem **birim düzeyinde**: adayın hem kırpılacak kadar küçük hem de `≥1 puan`
    kayacak kadar oynamış olduğu bir *veri* kurgusu, kütle-ağırlıklı JS yüzünden
    fikstürle üretilemiyor (denendi). Kural yine de yüklemin kendisiyle kilitleniyor —
    *bir davranışı ölçmek için onu üreten veriyi uydurmak gerekmiyorsa, uydurma.*
    """
    h = [{"deger": "BUYUK", "surpriz": 0.0, "pay_onceki": 90.0, "pay_simdi": 90.0},
         {"deger": "KIRPIK", "surpriz": 0.9, "pay_onceki": 1.0, "pay_simdi": 9.0}]
    yok = surpriz_notu(h, gosterilen={"BUYUK"})
    var = surpriz_notu(h, gosterilen={"BUYUK", "KIRPIK"})
    assert "«KIRPIK»" in yok, f"🔴 kırpılmış aday HİÇ ANILMIYOR:\n{yok!r}"
    assert "listede yok" in yok, (
        f"🔴 aday adıyla anılıyor ama **listede olmadığı** söylenmiyor:\n{yok!r}")
    assert "listede yok" not in var, (
        f"🔴 GÖRÜNÜR aday için de *«listede yok»* yazılıyor — yanlış uyarı (`§101.1`):\n{var!r}")


def test_ESIK_ALTINDA_BEYAN_YOK_yanlis_uyari_uretmiyor():
    """⚠ `§101.1` — *«bir yanlış-pozitif, kusurdan pahalıdır.»* Kırpma olsa bile JS
    kütlesi eşiğin altındaysa **susulur**; yoksa her raporun altına bir uyarı düşer ve
    beyan gürültüye karışır."""
    # 41 segment: biri dev, kırkı küçük — kırpma ateşler ama hepsi **oransal** hareket
    # ettiği için dağılım (ve dolayısıyla JS) neredeyse hiç değişmez.
    satirlar = ([{"s": "DEV", "v": 2000.0, "v_gecen": 1000.0}]
                + [{"s": f"S{i}", "v": 2.0, "v_gecen": 1.0} for i in range(40)])
    r = decompose(satirlar, "s", "v", _CQ)
    assert r["kirpilan_segment"] > 0, "⊘ ölçüm tabanı: bu veride kırpma ateşlemedi"
    assert "listeye girmeyen" not in (r["surpriz_notu"] or ""), (
        f"🔴 JS kütlesi %{_kirpilan_js(satirlar):.1f} olmasına rağmen beyan basıldı — "
        f"eşik ({KIRPILAN_SURPRIZ_ESIGI_YUZDE}) çalışmıyor:\n{r['surpriz_notu']!r}")


def test_TURKCE_EKI_BELIRTME_HALINDE():
    """🔴 *«%43,3'ü taşıyor»* değil *«%43,3'ünü taşıyor»* — cümlenin nesnesi belirtme
    hâlinde olmalı. `sayi_bicimi.ek(..., belirtme=True)` bunu **zaten** biliyor; ikinci
    bir ek üreticisi yazılmadı (`KAT-1`)."""
    m = decompose(_AJAN, "s", "v", _CQ)["surpriz_notu"] or ""
    assert "%43,3'ünü" in m, (
        f"🔴 belirtme eki düşmüş — Türkçe eki **ikinci bir yerde** üretiliyor olabilir:\n{m!r}")
