"""🔴 `§78` — **LEKSİK KAPI: daraltma sürüyor, ama vektörün EN EMİN adayı geçiyor.**

## Hikâye — bir satır hem çare hem kusurdu ㊸

`ara()`'daki `if lek:` kapısı gürültüyü kesmek için konmuştu (*«`fire` yazan kullanıcı
«doğalgaz» okuyor»*) ve **işini yapıyordu**. Ama aday kümesini leksiğe **kapatınca**
vektör ayağı *sıralayabilen ama aday ekleyemeyen* bir şeye dönüştü — `MIMARI`'nin
*«vektör bir sıralayıcıdır, süzgeç değil»* cümlesinin tersi.

Ölçüldü (`§77`, 37 vaka): üç **anlamsal/İngilizce** ifade `sıra=None` ile düşüyordu —
aşağı itilmiş değil, **hiç listede yok**.

## Tarama (`§78`) — ve sınırın **aynı taramada** görünmesi 🅜

```
k=0 (eski)  R@3 83,8 · R@5 83,8 · MRR 0,806   gürültü: temiz
k=1         R@3 86,5 · R@5 86,5 · MRR 0,820   gürültü: TEMİZ   ← seçilen
k=2         R@3 86,5 · R@5 91,9 · MRR 0,832   🔴 «ciro» → ik.toplam_prim
k=5         R@3 86,5 · R@5 91,9 · MRR 0,832   🔴 «fire» → parti.toplam_metre
```

🔴 `k≥2`'nin `R@5` kazancı **kapının kurulma sebebini geri getiriyor**: `k=5`'te *«fire»*
yine *«metre»* gösteriyor — kapının kendi şerhinde **adıyla** yazan kusur. *Bir sayı
iyileşirken ekranın bozulabileceğinin kanıtı, aynı taramanın içindeydi.*

⊘ Kalan açık (86,5 ↔ vektör tavanı **91,9**) **kapanmadı**: iki vaka daha ancak **gürültü
ödeyerek** gelir 🆖. Kapatılmaması bir eksik değil, ölçülmüş bir **karar** 🆂.

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | daraltma **duruyor** — kapı kaldırılmadı |
| 2 | vektörün **en emin** adayı geçiyor (`_VEK_GECIS`) |
| 3 | 🆃 geçiş **dar** kalıyor (`≤1`) — `k≥2` gürültüyü geri getirir |
| 4 | 🆃 leksik **boşken** vektör tek çare — o dal korunuyor |
"""

from __future__ import annotations

import inspect

from app import oneri


def _ara_kaynagi() -> str:
    return inspect.getsource(oneri.ara)


def test_DARALTMA_DURUYOR():
    """🔴 Kapı **kaldırılmadı**: gürültü kesmesi hâlâ orada."""
    k = _ara_kaynagi()
    assert "if lek:" in k, "🔴 leksik kapı kaldırılmış — `fire` → `metre` gürültüsü döner"
    assert "puan.items() if i in lek_kume" in k, "🔴 daraltma deseni değişmiş"


def test_VEKTORUN_EN_EMIN_ADAYI_GECIYOR():
    """🔴 **ASIL DEĞİŞMEZ.** Anlamsal aday listeye **girebilmeli**."""
    k = _ara_kaynagi()
    # ⚠ `§79`'da geçiş **koşullu** oldu; yüklem satırın **şekline** değil, **vektörün
    # kümeye eklendiği** gerçeğine bakar ⑭.
    assert "lek_kume.update(vek[:" in k, (
        "🔴 vektör adayı kapıdan geçmiyor — `§77`'nin üç anlamsal vakası yine `sıra=None` "
        "ile düşer (`«makine verimliliği»` · `«delivery performance»` · `«complaint count»`)")


def test_ZIT_OLCUT_GECIS_DAR_KALIYOR():
    """🆃🅜 Kapının **kurbanı**: geçişi genişletmek `R@5`'i 91,9'a çıkarır **ama** `k=5`'te
    *«fire»* sorgusu yine *«metre»* gösterir. Sayı iyileşirken ekran bozulur."""
    assert oneri._VEK_GECIS <= 1, (
        f"🔴 `_VEK_GECIS={oneri._VEK_GECIS}` — tarama `k≥2`'de gürültü ölçtü "
        "(«ciro» → `ik.toplam_prim`, «fire» → `parti.toplam_metre`). Büyütüyorsan "
        "`§78` taramasını **yeniden koş** ve gürültü kontrolünü ㊳ raporla.")
    assert oneri._VEK_GECIS >= 1, "🔴 geçiş kapatılmış — anlamsal vakalar geri düşer"


def test_ZIT_OLCUT_LEKSIK_BOSKEN_VEKTOR_TEK_CARE():
    """🆃 Kapı **koşullu** kalmalı: leksik hiçbir şey bulamadığında (`zayiat` · `vardya`)
    liste vektörden kurulur. `if lek:` koşulsuz hâle gelirse o dal ölür."""
    k = _ara_kaynagi()
    onces = k.split("if lek:")[0][-140:]
    assert "if not lek" not in onces, "🔴 daraltma koşulsuz olmuş — leksik boşken de susar"

def test_ZAYIF_LEKSIKTE_KAPI_GEVSIYOR():
    """🔴 `§79` — **ölçülmüş bir hâl**, sezgi değil: önek kovası boşken kapı gevşer.

    Ayırt edici kova ölçüldü ㊷:

    | sorgu | `onek` | sınıf |
    |---|---|---|
    | *«makine verimliliği»* · *«delivery performance»* · *«complaint count»* | **0** | 🔴 düşen |
    | *«fire»* 3 · *«ciro»* 2 · *«ram 3»* 2 | **>0** | ✅ gürültüsüz |

    Yani kullanıcının yazdığı hiçbir sözcük bir adayın **başına** oturmuyorsa, vektör o
    listeye daha çok katkı verebilir. Önek varken kapı **dar** kalır — `§78` taraması
    orada `k≥2`'nin gürültü ürettiğini ölçmüştü.
    """
    k = _ara_kaynagi()
    assert "_VEK_GECIS if _onek_var else _VEK_GECIS_ZAYIF" in k, (
        "🔴 geçiş sayısı leksiğin **gücüne** bağlı değil — ya koşulsuz gevşedi (gürültü) "
        "ya da koşulsuz daraldı (`R@5` 91,9 → 86,5)")
    assert oneri._VEK_GECIS_ZAYIF == 2, (
        f"🔴 `_VEK_GECIS_ZAYIF={oneri._VEK_GECIS_ZAYIF}` — `§79` taraması **2**'yi ölçtü "
        "(`R@5` 91,9 · gürültü temiz); `3` fazladan hiçbir şey getirmiyor 🆕. "
        "Değiştiriyorsan taramayı yeniden koş.")


def test_ONEK_SINYALI_DONUSLE_TASINIYOR():
    """⑨`§65` — bu bilgi bir **modül globaliyle** taşınamaz: ısıtma ayrı bir **iplikte**
    koşuyor ve bir global her iplikte aynı değeri gösterir. *Bir çağrının ürettiği bilgi,
    o çağrının dönüşüyle taşınır.*"""
    import inspect

    kaynak = inspect.getsource(oneri._leksik_sira)
    assert kaynak.rstrip().endswith("return _sira, bool(onek)"), (
        "🔴 önek sinyali dönüşle taşınmıyor — global bir bayrak `§65`'in ölçülmüş "
        "kusurunu tekrarlar")

def test_ONEK_YOKKEN_LEKSIK_ESITLIGI_BOZMAZ():
    """🔴 `§85` — *«eşitlikte leksik önde»* kuralı **gerekçesiyle sınırlıdır** ㊸.

    Kuralın kendi cümlesi: *«bir **önek** eşleşmesi kullanıcının yazdığının **birebir**
    karşılığıdır»* ㊼. Önek **hiç yokken** o cümle geçmez — leksik sırası orada da bir
    tahmindir, üstelik ölçülen vakalarda vektörünkinden **daha kötü** olanı:

        «makine verimliliği»  onek=0 → leksik 1.'si yanlış, hedef 2.
        «delivery performance» onek=0 → hedef 4.

    ⊙ `R@1` **78,4 → 81,1** *(vektör tavanı 81,1)* · `MRR` 0,832 → **0,845** · gürültü
    kontrolü ㊳ **birebir aynı**. 🆃 Önek **varken** kural sürüyor — o dal ayrıca sınanır.
    """
    k = _ara_kaynagi()
    assert "if _onek_var else {}" in k, (
        "🔴 leksik sıra, önek yokken de eşitliği bozuyor — `R@1` 81,1 → 78,4'e düşer "
        "(`§85` ölçümü). Değiştiriyorsan ölçümü **yeniden koş**.")


def test_ZIT_OLCUT_ONEK_VARKEN_LEKSIK_HALA_ONDE():
    """🆃 Kapının kurbanı: kuralı **tümden** kaldırmak *«fire»* gibi **önek** sorgularında
    kullanıcının birebir yazdığını ikinci sıraya düşürebilirdi."""
    k = _ara_kaynagi()
    assert "lek_yer = {i: y for y, i in enumerate(lek)}" in k, (
        "🔴 leksik sıra tümden kaldırılmış — önek eşleşmesi artıklığını kaybeder")
