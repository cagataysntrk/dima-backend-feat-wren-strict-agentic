r"""🔴🔴 `kok_neden.toplam_turu` — **PAY MUTLAK DEĞERLERLE HESAPLANIYORDU** (yayında).

## Ölçülen kusur (2026-08-12, denetim ajanı + kendi ölçümüm)

Kod payda olarak **mutlak** toplamı alıyordu ama cümle *«toplamının %P'ini taşıyor»*
diyordu; `_akran` da **mutlak** ortalamaydı ama cümle *«öteki ortalaması»* diyordu.
Karışık işaretli bir `SUM` ölçüsünde (`enerji_sapma.toplam_enpg` — `lower_is_better`,
tasarım gereği ±) ölçüldü:

    değerler     : +9000 · −4500 · −3000 · 0
    brüt         : 16.500        net (GERÇEK toplam) : 1.500
    basılan pay  : %54,5         gerçek pay          : %600     ← **11 KAT**
    basılan akran: +2.500        gerçek akran        : −2.500   ← **İŞARET TERS**

⊙ Akıcı, doğru biçimlendirilmiş ve **güvenle yanlış** bir cümle. `§101.1`'in tersi:
bir yanlış-**pozitif** değil, **bir yanlış SAYI** — ve `lower_is_better` yüzünden
ötekilerin *tasarruf ettiği* durum ekranda *kötü* görünüyordu.

## Onarım — kural YENİDEN YAZILMADI

`contribution.contributions()` (`:191-196`) bu cebri **zaten** taşıyor:

    net pay ancak net değişim BRÜT hareketin anlamlı bir kısmıysa yorumlanabilir
    (aksi hâlde +100/−100 götürmesi pay yüzdelerini patlatır)

Aynı eşik (**%1**) `kok_neden`'e uygulandı (`KAT-1` — iki sahip değil, bir kural).
Pay basılamıyorsa cümle **büyüklüğe** iner **ve nedenini söyler**.

> *Bir payı mutlak değerlerle hesaplayıp «toplamın payı» diye sunmak, işaretleri yok
> sayıp güven satmaktır.*
"""

from __future__ import annotations

from app import kok_neden as kn

_BOYUT = "kaynak"
_OLCU = "toplam_enpg"


def _kos_fabrikasi(degerler: list[float]):
    """`toplam_turu`'nun `kos` geri çağrısı — segment satırları döndürür."""
    satirlar = [{_BOYUT: f"S{i}", _OLCU: v} for i, v in enumerate(degerler)]

    def _kos(cq):
        # ⚠ `toplam_turu` `kos(...)` çıktısını **doğrudan satır listesi** olarak
        # kullanıyor (`satirlar = kos({...}) or []`). İlk fikstürüm `{"rows": …}`
        # döndürüyordu ve fonksiyon sessizce `None` verdi — ürün değil, HARNESS hatası.
        return list(satirlar)
    return _kos


#: ⚠ Fikstür **ölçülerek** kuruldu, tahminle değil: `toplam_turu` üç ön koşul istiyor —
#: ① `prev_cq.dimensions` dolu (yoksa `_en_ayristiran` makinesi devreye girer)
#: ② `toplanabilirlik(...) == TAM` → bunun için `measure_expressions` **yayımlanmalı**
#:    (metadata sessizse sınıf `bilinmiyor` olur ve fonksiyon `None` döner)
#: ③ `kos(...)` **doğrudan satır listesi** döndürmeli, `{"rows": …}` değil
#: İlk üç denemem bu üç şartın üçünde de düştü — *ürün değil HARNESS hatası*.
_CQ = {"cube": "enerji_sapma", "measures": [_OLCU], "dimensions": [_BOYUT],
       "filters": []}
_META = {"name": "enerji_sapma", "lower_is_better": [_OLCU],
         "measure_expressions": {_OLCU: f"SUM({_OLCU})"},
         # ⚠ `measures`/`dimensions` **DİZE** listesi: sözlük verince `m in _az`
         # gibi küme testleri `TypeError: unhashable type: 'dict'` veriyor
         # (aynı hatayı `katalog_metni`de de görmüştüm — ders ⑤: ŞEKLİ ÖLÇ).
         "dimensions": [_BOYUT], "measures": [_OLCU]}


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — fonksiyon hiç cümle üretmiyorsa yüklem boşa düşer."""
    r = kn.toplam_turu(_CQ, _META, kos=_kos_fabrikasi([100.0, 50.0, 30.0, 20.0]))
    assert r and (r.get("metin") or r.get("aciklama") or r.get("adimlar")), (
        f"⊘ ölçüm tabanı çöktü: `toplam_turu` cümle üretmedi ({r})")


def _metin(r) -> str:
    """Sonucun **tüm** metinsel alanlarını birleştirir.

    ⚠ Tek bir alana bağlanmıyor: kusur `metin`de görüldü ama `adimlar` da aynı payı
    basıyordu — *bir yüklem, ölçtüğü şeyin tek bir kabına bağlanırsa öteki kaptan
    kaçanı görmez.*
    """
    if not r:
        return ""
    # ⚠ Gerçek anahtarlar ÖLÇÜLDÜ: `{anlati, adimlar, segment, boyut}` — `metin`
    # diye bir alan YOK (o, gövdedeki değişken adı ve `anlati` olarak dönüyor).
    # *Bir alanın adını koddan değil DÖNEN NESNEDEN öğren.*
    parcalar = [str(r.get(k) or "") for k in ("anlati", "metin", "aciklama")]
    parcalar += [str(x) for x in (r.get("adimlar") or [])]
    return " ".join(parcalar)


def test_AYNI_ISARETTE_PAY_BASILIYOR():
    """✅ Normal (tek işaretli) veride pay **basılmalı** — düzeltme kapsamı yutmasın.

    ⚠ Bu yüklem `§101.1`'in koruması: aşırı temkinli bir düzeltme, doğru cümleleri de
    susturur ve kullanıcı *«sistem artık bir şey söylemiyor»* der.
    """
    r = kn.toplam_turu(_CQ, _META, kos=_kos_fabrikasi([100.0, 50.0, 30.0, 20.0]))
    m = _metin(r)
    assert "%" in m, (
        f"🔴 tek işaretli veride pay BASILMIYOR — düzeltme kapsamı yuttu:\n{m[:300]}")
    assert "hesaplanamadı" not in m, (
        f"🔴 normal veride *«hesaplanamadı»* uyarısı çıktı:\n{m[:300]}")


def test_ISARETLER_GOTURUYORSA_PAY_BASILMIYOR():
    """🔴🔴 **ASIL KAPI.** İşaretler birbirini götürüyorsa **yüzde basılmaz**.

    Ölçülen vaka: `+9000 · −4500 · −3000 · 0` → brüt 16.500, net 1.500. Eski kod
    *«toplamın %54,5'ini taşıyor»* diyordu; gerçek pay **%600**. Yeni davranış: pay
    yerine **büyüklük** + *«hesaplanamadı»* beyanı.
    """
    r = kn.toplam_turu(_CQ, _META, kos=_kos_fabrikasi([9000.0, -4500.0, -3000.0, 0.0]))
    m = _metin(r)
    assert "hesaplanamadı" in m, (
        "🔴 karışık işaretli veride hâlâ bir PAY basılıyor — bu, mutlak değerlerle "
        f"hesaplanmış ve toplamın payı diye sunulmuş bir sayıdır:\n{m[:300]}")
    assert "%54" not in m and "%600" not in m, (
        f"🔴 sessiz-yanlış yüzde hâlâ metinde:\n{m[:300]}")


def test_AKRAN_ORTALAMASI_ISARETLI():
    """🔴 `_akran` **işaretli** olmalı — eski hâli mutlak ortalamaydı.

    Ölçülen vaka: ötekiler `−4500 · −3000 · 0` → gerçek ortalama **−2.500**; eski kod
    **+2.500** basıyordu. `lower_is_better` bir ölçüde bu, *tasarruf eden* segmentleri
    ekranda **kötü** gösterir.
    """
    r = kn.toplam_turu(_CQ, _META, kos=_kos_fabrikasi([9000.0, -4500.0, -3000.0, 0.0]))
    m = _metin(r)
    assert "-2.500" in m or "−2.500" in m or "-2500" in m, (
        f"🔴 akran ortalaması İŞARETSİZ görünüyor (beklenen −2.500):\n{m[:300]}")


def test_KURAL_TEK_SAHIPLI():
    """⚠ `KAT-1`: net-vs-brüt eşiği **contribution**'ın kuralıdır; ikinci bir eşik
    doğarsa ikisi bir gün ayrışır.

    Yüklem yapısal: her iki modül de **aynı** `%1` eşiğini kullanmalı.
    """
    import inspect

    from app import contribution

    c = inspect.getsource(contribution.contributions)
    k = inspect.getsource(kn.toplam_turu)
    assert "brut * 0.01" in c, "⊘ ölçüm tabanı çöktü: `contribution`'daki eşik değişmiş"
    assert "_brut * 0.01" in k, (
        "🔴 `kok_neden` artık `contribution`'ın eşiğini kullanmıyor — aynı kuralın iki "
        "sahibi olur ve iki farklı gün ayrışır (`KAT-1`).")
