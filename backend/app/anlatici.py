"""🔴 **T2'NİN DETERMİNİSTİK İLK BASAMAĞI** — basit olanı sistem kendi yazar.
[bayrak: `t2_sablon`]

## Ölçülen eksik

`answer._anlati_ekle` **tek basamaklıydı**: `t2_anlatici` açıksa LLM'e gider, kapalıysa
anlatı **hiç** olmaz. Oysa merdiven ilkesi (`MIMARI §4`) *"her basamak bir öncekinin
yapamadığını yapar"* der — ve anlatının **ilk** basamağı yazılmamıştı.

Kullanıcının cümlesi bu eksiği aynen tarif ediyor:

> *"T2 çok da zor değil — ne yüksek ne düşük vs, onları sistem de yazabilir. Sadece
> karışık, daha komplike olanlarda T2 LLM'e gitsin."*

⊙ Ve `interpret()` **zaten** yapılandırılmış olgular üretiyor (`type` + `text`):
`trend` · `peak` · `delta` · `streak` · `top` · `bottom` · `single` · `count` …
Yani ilk basamağın **girdisi hazırdı**, çıktısı yazılmamıştı.

## 🔴 Bu basamak neden SAYI UYDURAMAZ

Cümleyi `interpret()`'in **kendi metinlerinden** kurar; tek bir sayıyı ne hesaplar ne
biçimlendirir. Yani `narration_guard`'dan geçmesi bir **tesadüf değil, yapısal**:
guard'ın aradığı her rakam zaten sonuç kümesinden gelmiştir.

*Bir anlatıcı sayıya dokunmuyorsa, onu doğrulamak bir kontrol değil bir teyittir.*

## Sınır: NE ZAMAN LLM'E DEVREDİLİR

| durum | basamak |
|---|---|
| tanınan olgu türleri, tek ölçü, ≤ `_AZAMI_OLGU` olgu | ✅ **şablon** (0 LLM · 0 token) |
| tanınmayan bir olgu türü var | ⏭ LLM |
| birden çok ölçü ya da segment kırılımı | ⏭ LLM |
| olgu yok | ⊘ ikisi de değil — deterministik `summary` yerinde kalır |

⚠ **Devir koşulu tanınmayanın VARLIĞIDIR, olgu sayısı değil.** Bilmediği bir türü
görmezden gelip kalanları anlatmak, kullanıcıya **eksik ama tam görünen** bir özet
vermek olurdu — ve bu, susmaktan kötüdür.

*Bir merdivenin basamağı, ne yapamadığını bilmiyorsa basamak değil bir tahmindir.*
"""

from __future__ import annotations

from app.logging_setup import get_logger

_log = get_logger("anlatici")

#: Şablonun anlatabildiği olgu türleri — **kapalı** küme. Yeni bir tür `interpret()`'e
#: eklenirse bu basamak onu tanımaz ve turu LLM'e devreder; sessizce atlamaz.
TANINAN = ("trend", "delta", "peak", "streak", "top", "bottom", "single", "count",
           "kpi_value", "shape", "kiyas", "segment_delta")
#: 🔴 `kiyas` + `segment_delta` — **bu modülün kendi uyarısı işledi.** Yukarıdaki not
#: *«yeni bir tür eklenirse bu basamak onu tanımaz ve turu LLM'e devreder»* diyordu ve
#: tam olarak öyle oldu: `§D11-kıyas` ile eklenen `kiyas`, ve **zaten üretilmekte olan**
#: `segment_delta` (`interpret.py:572`, tam iki segmentte) burada yoktu — yani ikisini
#: taşıyan her cevap şablon yerine **LLM'e** düşüyordu.
#:
#: ⚠ İkisi de eklenmeye uygun çünkü metinleri `interpret()`'in **kendi** cümleleridir;
#: burada hiçbir sayı hesaplanmaz, biçimlendirilmez. Ölçülen kazanç bir üslup değil bir
#: **fatura**: canlıda anlatı LLM'i bir turda 22,5 sn / %93 pay almıştı.
#:
#: ⚠ Ve genişletme **kapıyı gevşetmez**: `basit_mi`'nin öteki iki şartı (`≤4 olgu`,
#: `tek ölçü`) yerinde. Çok ölçülü bir kıyas (dört ölçünün dördü birden) hâlâ LLM'e
#: gider — iki ölçüyü tek cümlede yan yana koymak bir **ilişki** ima eder ve o çıkarım
#: bu basamağın yetkisinde değildir.

#: Bu sayıdan fazla olgu varsa anlatı bir **liste**ye dönüşür; liste zaten `facts`
#: alanında var ve kullanıcı onu görüyor. İkinci kez, cümle biçiminde tekrarlamak
#: bir özet değil bir gürültüdür.
_AZAMI_OLGU = 4

#: Anlatının ilk cümlesi bu türlerden biriyle başlar — okuyucu **önce olguyu**, sonra
#: ayrıntıyı görsün. Sıra rastgele değil: `trend` bir yön, `delta` bir büyüklük,
#: `single` bir değer verir; üçü de *"ne oldu"* sorusuna doğrudan cevaptır.
#: ⊙ `kiyas` **`single`'dan hemen sonra**: tek değer *"ne kadar"*, kıyas *"neye göre"*
#: sorusunu cevaplar — okuyucu önce değeri, sonra ölçüsünü görmeli. `segment_delta` ise
#: bir **büyüklük**tir, `delta` ile aynı ailede.
_ONCELIK = ("trend", "delta", "segment_delta", "single", "kiyas", "kpi_value", "shape",
            "streak", "peak", "top", "bottom", "count")


def basit_mi(yorum: dict | None) -> bool:
    """Bu tur şablonla anlatılabilir mi? — **fail-closed**: şüphede `False`."""
    if not isinstance(yorum, dict):
        return False
    olgular = [f for f in (yorum.get("facts") or []) if isinstance(f, dict)]
    if not olgular or len(olgular) > _AZAMI_OLGU:
        return False
    if any(str(f.get("type")) not in TANINAN for f in olgular):
        return False
    # 🔴 Tek ölçü şartı: iki ölçüyü tek cümlede anlatmak, aralarında bir **ilişki** ima
    # eder (*"ciro arttı, fire düştü"* → bir neden-sonuç okunur). O çıkarım bu basamağın
    # yetkisinde değil. *Bir yan yana koyma, cümlede bir bağlaca dönüşür.*
    #
    # ⟳ **ÖLÇÜLDÜ (2026-08-12): BU SATIR KURALI HİÇ UYGULAMIYORDU.** İki ölçülü bir
    # yorumda `olculer` yine **tek elemanlıydı** — çünkü `interpret` olguları yalnız
    # `measures[0]` için üretir; ikinci ölçünün adı hiçbir olguda geçmez. Yani yazılı
    # şart **her zaman geçiyordu**.
    #
    # Kuralı fiilen uygulayan **iki kaza** vardı ve ikisi de bu kuralı bilmiyordu:
    #   ① `len(olgular) > _AZAMI_OLGU` — iki ölçüde olgu 5 oluyordu (tavan 4)
    #   ② `measures` tipinin `TANINAN`da olmayışı — kapsam kapısı onu bir
    #      *«bilinen istisna»* diye kaydetmiş, yani **eklenmeye davetiye** çıkarmış
    #
    # ⚠ Tavan 5'e çıkarılsa ya da `measures` tanınanlara eklense, iki ölçülü bir cevap
    # şablona düşer ve yorumun yasakladığı **bağlaç** cümlede belirirdi. Hiçbir kırmızı
    # konuşmazdı: `test_..._COK_OLCULU_KIYAS_hala_LLM_e_gider` yeşildi — **yanlış
    # sebeple**.
    #
    # *Bir kuralın yazılı sahibi onu uygulamıyorsa, kural yoktur; yalnız onu şu an
    # tesadüfen karşılayan bir yan etki vardır.*
    sayi = yorum.get("olcu_sayisi")
    if isinstance(sayi, int):
        return sayi <= 1
    # Geri düşüş: `olcu_sayisi` taşımayan çağrı (dış/eski yorum sözlükleri).
    olculer = {f.get("measure") for f in olgular if f.get("measure")}
    return len(olculer) <= 1


def anlat(yorum: dict | None) -> str | None:
    """Olgulardan Türkçe bir özet — **0 LLM, 0 token**. Anlatamıyorsa `None`.

    ⚠ Cümleler `interpret()`'in **kendi metinlerinden** kurulur; burada hiçbir sayı
    hesaplanmaz ya da biçimlendirilmez. Bu bir üslup tercihi değil bir **değişmez**:
    ikinci bir biçimlendirici, aynı sayının iki farklı yazımı demektir.
    """
    if not basit_mi(yorum):
        return None
    olgular = [f for f in (yorum.get("facts") or []) if isinstance(f, dict)]
    sira = sorted(olgular, key=lambda f: (_ONCELIK.index(str(f["type"]))
                                          if str(f.get("type")) in _ONCELIK else 99))
    parcalar = [str(f.get("text") or "").strip().rstrip(".") for f in sira]
    parcalar = [p for p in parcalar if p]
    if not parcalar:
        return None
    metin = parcalar[0] + "."
    if len(parcalar) > 1:
        # ⚠ Bağlaç YOK: *"ve"* / *"ancak"* bir **ilişki** ima eder ve o çıkarım bu
        # basamağın yetkisinde değil. Olgular yan yana konur, yorumlanmaz.
        metin += " " + " ".join(p + "." for p in parcalar[1:])

    # 🔴 **YANKI KAPISI — ve bu kapı bu modülün yarısını ÇÜRÜTTÜ.**
    #
    # Ölçüldü: `interpret()`'in `summary`'si zaten `" ".join(olgu metinleri)`. Yani
    # *"basit olanı sistem yazsın"* isteği **karşılanmış durumda** — sistem onu `summary`
    # olarak zaten yazıyor, 0 token ile. Buradan çıkan cümle **birebir onun kopyasıydı**.
    #
    # ⊙ Bunu bir kapı yakaladı (`test_VARSAYILAN_KAPALI_ask_zincirinde_narration_YOK`) ve
    # haklıydı: aynı cümleyi ikinci bir alanda tekrarlamak bir basamak değil bir **yankı**.
    # Kullanıcı aynı şeyi iki kez okur ve ikincisinin neden orada olduğunu bilemez.
    #
    # *Bir merdivene, bir öncekinin yaptığını yapan bir basamak eklemek, merdiveni
    # uzatmaz — yalnız ağırlaştırır.*
    #
    # 🔴 Geriye kalan gerçek boşluk **yargıdır** (*"yüksek mi düşük mü"*) ve o **bu
    # basamağın yetkisinde değil**: bir eşik olmadan yüksek/düşük denemez, eşiği uydurmak
    # ise korpusun **açıkça yasakladığı** şeydir (*"iyi/kötü yargısını bir eşik uydurarak
    # vermek"*). Beyan edilmiş bir referans varsa sahibi `app/hedef.py`'dir (`ADR-0028`:
    # **hedef UYDURULMAZ**) — yargı oraya bağlanır, buraya değil.
    ozet = str((yorum or {}).get("summary") or "").strip()
    if ozet and _sade(metin) == _sade(ozet):
        _log.debug("T2 şablon: `summary` ile aynı — yankı yayımlanmaz")
        return None
    _log.info("T2 ŞABLON: %d olgu, 0 token", len(parcalar))
    return metin


def _sade(s: str) -> str:
    """Karşılaştırma için boşluk/noktalama gürültüsünü siler — yankı tespiti biçime
    değil **içeriğe** bakmalı."""
    return "".join(ch for ch in s.lower() if ch.isalnum())
