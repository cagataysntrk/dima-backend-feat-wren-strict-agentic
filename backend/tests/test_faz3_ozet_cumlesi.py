"""🔴 `FAZ 3` — «ROBOTİK»İN EN SAF HÂLİ: **ETİKET-İKİ NOKTA-SAYI**.

## Canlıda ölçülen kusur (2026-08-12)

    «bu yıl toplam ciro»
      → answer   : None
      → narration: None
      → summary  : «ciro: ₺74.022.836,94.»          ← kullanıcının gördüğü TEK metin
      → facts    : 1 (`single`)

Kullanıcı bir soru soruyor ve bir **veritabanı etiketi** okuyor. Ve şablon basamağı
**doğru** davranıyor: tek olguda özetin üstüne katacağı ek bilgi yok, o yüzden susuyor
(`narration_kaynak="sablon"`). Yani kusur anlatıcıda değil, **özetin kendisindeydi**.

## Düzeltme — ve neden bu kadar dar

`interpret._ozet()` yalnız **tek olgulu `single`** vakasında etiketi cümleye çevirir:

    «ciro: ₺74.022.836,94»  →  «Ciro ₺74.022.836,94.»

* **Çok olgulu özetler birebir aynı** — orada olgular birbirini zaten cümleye bağlıyor,
  ve değiştirmek `narration_guard`'ın altındaki zemini oynatırdı.
* **Sayı/birim `_fmt`'ten aynen gelir**; bir karakteri yeniden yazılmaz. *Bir sunum
  düzeltmesi, sayıya dokunduğu anda sunum düzeltmesi olmaktan çıkar.*
* **Olgunun `text`'i DEĞİŞMEZ** — guard'ın ve testlerin dayandığı zemin odur.

## ⚠ ÖLÇÜLEN SINIR — ve sahibi KOD DEĞİL KATALOG

Canlıda `«Oee 0,58 %.»` çıktı. Ölçüldü: `oee` küpünde **`measure_labels["ort_oee"]` YOK**
(`None`), küp düzeyinde ise `display: OEE` **var**. Yani kısaltmanın bozulması bir kod
kusuru değil bir **katalog boşluğudur** — ve görünen adın sahibi katalogdur.

🔴 **Koda büyük-küçük harf kuralı YAZILMADI** (`ADR-0008`: liste/heuristik ile dil
kovalamak yasak). Doğru düzeltme ölçüsüz ölçülere **etiket yazmaktır**; borç olarak
kaydedildi. *Bir sunum kusurunu kodda yamamak, kataloğun sorumluluğunu koda taşımaktır.*
"""

from __future__ import annotations

from app.interpret import interpret

_CQ = {"cube": "parti", "measures": ["toplam_ciro"]}
_SONUC = {"rows": [{"toplam_ciro": 1500.0}], "columns": ["toplam_ciro"], "row_count": 1}
#: ⚠ Anahtarlar **ölçüldü**: `interpret()` etiketi `etiketler=`, birimi `units=`
#: parametresinden alır — `cube_meta` içinden DEĞİL. İlk fikstür ikisini de `cube_meta`'ya
#: koydu ve test sahte bir kırmızı verdi (bu turda **onuncu** kez araç ürünü suçladı).
_ETIKET = {"toplam_ciro": "toplam ciro"}
_BIRIM = {"toplam_ciro": "₺"}


def _yorum(sonuc=None, cq=None):
    return interpret(sonuc or _SONUC, cube_query=cq or _CQ,
                     units=_BIRIM, etiketler=_ETIKET)


def test_TEK_DEGER_ozeti_CUMLE():
    """🔴 Kusurun ta kendisi: iki nokta gitti, cümle geldi."""
    o = _yorum()
    assert o["summary"].startswith("Toplam ciro "), o["summary"]
    assert ":" not in o["summary"], "etiket-iki nokta biçimi geri geldi"
    assert o["summary"].endswith("."), "cümle noktayla bitmeli"


def test_SAYI_BIREBIR_korunur():
    """*Bir sunum düzeltmesi, sayıya dokunduğu anda sunum düzeltmesi olmaktan çıkar.*"""
    o = _yorum()
    ham = o["facts"][0]["text"]
    deger = ham.split(":", 1)[1].strip()
    assert deger in o["summary"], f"biçimlenmiş değer değişti: {deger!r} ∉ {o['summary']!r}"


def test_OLGUNUN_METNI_DEGISMEZ():
    """`narration_guard` ve testler olgunun `text`'ine dayanır — orası zemindir."""
    o = _yorum()
    assert o["facts"][0]["text"] == "toplam ciro: ₺1.500"
    assert o["facts"][0]["type"] == "single"


def test_COK_OLGULU_ozet_DEGISMEDI():
    """⚠ Kapsam kilidi: kural yalnız tek-olgulu `single`'a dokunur."""
    sonuc = {"rows": [{"musteri": "A", "toplam_ciro": 900.0},
                      {"musteri": "B", "toplam_ciro": 600.0}],
             "columns": ["musteri", "toplam_ciro"], "row_count": 2}
    o = interpret(sonuc, cube_query={**_CQ, "dimensions": ["musteri"]},
                  units=_BIRIM, etiketler=_ETIKET)
    assert len(o["facts"]) > 1
    beklenen = " ".join(f["text"].rstrip(".") + "." for f in o["facts"])
    assert o["summary"] == beklenen, "çok olgulu özet oynatıldı"


def test_IKI_NOKTASIZ_olgu_ELLENMEZ():
    """İki noktası olmayan bir `single` metni (gelecekte biçim değişirse) **olduğu gibi**
    geçer — uydurma bir ayrıştırma yapılmaz."""
    sonuc = {"rows": [{"parti_sayisi": 7}], "columns": ["parti_sayisi"], "row_count": 1}
    o = interpret(sonuc, cube_query={"cube": "parti", "measures": ["parti_sayisi"]})
    assert o["summary"].endswith(".")
