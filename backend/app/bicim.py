"""§D3 — CEVAP BİÇİMİ BİR **KARARDIR** (ADR-0024'ün kardeşi).

Grafik kararı `viz.py`'de deterministik ve ölçülmüş (§2: canlı **10/10** doğru tip).
Ama cevabın öteki yarısı — **öneri şeridi** — hiçbir yerde bir karar değildi:
`cube_router.suggest_next_steps` beş kovayı sabit kotalarla (2·2·1·1·1) doldurup
`_MAX_NEXT_STEPS=6`'da kesiyordu ve **soru türü bu hesaba hiç girmiyordu**.

## Ölçüm — kusur kapanmamış, DERİNLEŞMİŞ

Raporun `§18`'i sekiz soru türünde chip sayısını ölçmüştü; 2026-08-11'de aynı sekiz
soru curl ile tekrarlandı:

    §18 (rapor) :  6, 6, 5, 6, 6, 4, 6, 3
    bugün       :  6, 6, 6, 6, 5, 6, 6, 5      ← daha da sabit

`§18.1`'in teşhisi: *«Soru ne olursa olsun aynı boyda bir öneri şeridi — **katalog
hissinin birinci kaynağı budur**; mobilya her cevapta aynı.»*

## 🔴 Ve asıl kusur SAYI değil, ALÂKASIZ KOVA

Ölçüldü — *«bu yıl toplam ciro»*nun altı chip'i:

    tedarikçi kırılımı · **+ ortalama hız** · Aylık trend ·
    Geçen yıla göre kıyasla · kısım kırılımı · **+ fire**

Bir **ciro** sorusuna *«+ fire»* teklif etmek soruyu **derinleştirmez, DEĞİŞTİRİR**.
Kullanıcı tek bir sayı istedi; ona başka bir ölçü önermek, cevabın devamı değil bir
**katalog gezintisidir**. *Bir öneri şeridi, sorulmuş sorunun devamıdır; küpün
içindekilerin listesi değil.*

## Karar tablosu — hangi kova hangi soru türünde ANLAMLI

`niyet.py`'nin **kapalı** altı türü satır, `suggest_next_steps`'in beş kovası sütun.
Her ❌'in gerekçesi tablonun altında yazılıdır — ve gerekçe **karardan türetilir,
uydurulmaz** (`viz._neden`'in aynı deseni).

⚠ **Karar DETERMİNİSTİK ve TABLOLUDUR — LLM seçmez.** `D3`'ün kendi risk maddesi:
*«aşırı çeşitlilik de tutarsızlık üretir → karar deterministik olsun»*, ADR-0024'ün
aynı ilkesi.

⚠ **KURAL B:** tür çözülemezse (boş küme ya da tabloda olmayan tür) `None` döner ve
çağıran bugünkü sabit kotayı kullanır — davranış **bayt bayt** eski.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.niyet import (
    TUR_KIRILIM,
    TUR_KIYAS,
    TUR_LISTE,
    TUR_TOPLAM,
    TUR_TREND,
    TUR_USTUNLUK,
)

#: `suggest_next_steps`'in ürettiği beş öneri sınıfı. Adlar orada da kullanılır;
#: `KAT-1` gereği kova adları **tek yerde** tanımlıdır: burada.
KOVA_KIRILIM = "kirilim"
KOVA_OLCU = "olcu"
KOVA_ZAMAN = "zaman"
KOVA_KIYAS = "kiyas"
KOVA_TOPN = "topn"

KOVALAR: tuple[str, ...] = (KOVA_KIRILIM, KOVA_OLCU, KOVA_ZAMAN, KOVA_KIYAS, KOVA_TOPN)

#: 🔴 Bugünkü davranış — bayrak kapalıyken ve tür çözülemediğinde kullanılan kota.
#: Değerleri `cube_router.suggest_next_steps`'in eski sabit dilimlerinden alınmıştır
#: (`secilen` zaten ≤2, `meases[:2]`, `times[:1]`, `cmp_steps[:1]`, `topn_steps[:1]`).
VARSAYILAN_KOTA: dict[str, int] = {
    KOVA_KIRILIM: 2, KOVA_OLCU: 2, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 1,
}

#: Tür → kova kotası. **0 = o kova bu soru türünde anlamsız.**
_TABLO: dict[str, dict[str, int]] = {
    # Tek sayı istendi. Kırılım/zaman/kıyas o sayıyı **derinleştirir**; başka bir ölçü
    # eklemek **soruyu değiştirir** (ölçülen kusur: ciro sorusuna «+ fire»). Sıralanacak
    # bir şey de yoktur — sonuç tek satırdır.
    TUR_TOPLAM:   {KOVA_KIRILIM: 2, KOVA_OLCU: 0, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 0},
    # En zengin dal: bir dağılımın üstünde beş sorunun beşi de anlamlı. Bugünkü davranış.
    TUR_KIRILIM:  {KOVA_KIRILIM: 2, KOVA_OLCU: 2, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 1},
    # Sıralama **zaten kuruldu**. «En yüksek 5» teklifi, kullanıcının az önce yaptığı
    # şeyi tekrar teklif etmektir. ⊙ Bugün bu yalnız `cube_query.order` doluysa
    # bastırılıyordu — yani sorgudan; artık **niyetten**, yani route sıralamayı
    # kuramasa bile.
    TUR_USTUNLUK: {KOVA_KIRILIM: 1, KOVA_OLCU: 1, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 0},
    # Zaman ekseni kuruldu: granülerlik ve kıyas doğal devam. Bir zaman serisinde
    # sıralama ekseni yoktur.
    TUR_TREND:    {KOVA_KIRILIM: 2, KOVA_OLCU: 1, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 0},
    # Kıyas **zaten kuruldu** → ikinci bir kıyas teklifi tekrardır. Sıradaki soru
    # «bu farkı kim sürüklüyor» yani KIRILIM.
    TUR_KIYAS:    {KOVA_KIRILIM: 2, KOVA_OLCU: 1, KOVA_ZAMAN: 1, KOVA_KIYAS: 0, KOVA_TOPN: 1},
    # Döküm: kullanıcı satırları görmek istedi; hepsi anlamlı.
    TUR_LISTE:    {KOVA_KIRILIM: 2, KOVA_OLCU: 2, KOVA_ZAMAN: 1, KOVA_KIYAS: 1, KOVA_TOPN: 1},
}

#: Kovanın insan okunur adı — makbuz/gerekçe metni için.
_AD = {KOVA_KIRILIM: "kırılım", KOVA_OLCU: "+ölçü", KOVA_ZAMAN: "zaman",
       KOVA_KIYAS: "kıyas", KOVA_TOPN: "top-N"}


def oneri_kotasi(turler: Iterable[str] | None) -> tuple[dict[str, int], str] | None:
    """Niyet türlerinden **öneri kovası kotaları** + gerekçe. Çözülemezse `None`.

    Birden çok tür eşleşirse kova başına **en küçük** kota alınır. Sebebi bir
    sadelik tercihi değil bir **anlam** kuralı: her ❌ *«bu soruda o kova zaten
    karşılandı»* demektir, ve bir soru iki türü birden taşıyorsa **iki karşılanma da
    geçerlidir**. *«en kötü 3 makine»* hem `kirilim` hem `ustunluk`tur; sıralama
    kurulmuştur, dolayısıyla top-N teklifi **yine** tekrardır.

    ⚠ `None` dönüşü bir hata değil bir **kapıdır**: çağıran `VARSAYILAN_KOTA`'ya düşer
    ve davranış bugünküyle birebir kalır (`KURAL B`).
    """
    eslesen = [_TABLO[t] for t in (turler or ()) if t in _TABLO]
    if not eslesen:
        return None
    kota = {k: min(e[k] for e in eslesen) for k in KOVALAR}
    kapali = [_AD[k] for k in KOVALAR if kota[k] == 0 and VARSAYILAN_KOTA[k] > 0]
    turler_ad = "+".join(sorted(t for t in (turler or ()) if t in _TABLO))
    gerekce = f"soru türü «{turler_ad}»"
    if kapali:
        gerekce += f" — kapatılan kova: {', '.join(kapali)}"
    return kota, gerekce
