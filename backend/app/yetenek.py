"""🔴 KÖK-6 — **YETENEK BEYANI: üç kutu, iki değil.**

## Ölçülen kusur (denetim raporu KN-3, 2026-08-05)

Discovery'ye giden yolda **tek kapı** var (`ask.py`) ve o kapı bir **kullanıcı tercihi**
okuyor (`yol_siniri`). 🔴 **Yetenek kapsamına bakan bir kapı yok.** Sonuç:

```
route()      →  R-kodu ile pes eder  ("forecast yok" · "olumsuzluk" · "iki cube")
   ↓            ⚠ bu bir TEŞHİSTİR, bir KARAR değil
Intent-JSON  →  boş
   ↓
Discovery    →  LLM ham SQL yazar  →  adhoc cube  →  BİR SAYI DÖNER
```

Ölçülen üç tur:

| Soru | İlan edilmiş sınır | Gelen cevap |
|---|---|---|
| `bu gidişle yılı nerede kapatırız` | **forecast v1'de YOK** | `adhoc.toplam_toplam_ciro` |
| `firesiz partiler kaç tane` | **olumsuzluk desteklenmiyor** | `adhoc.toplam_toplam_uretim_kg` |
| `fire ve rework birlikte` | **MIMARI §9.2** — iki cube'un ölçüsü | `adhoc.toplam_toplam_uretim_kg` |

Rozet **dürüst kalıyor** (`source=llm:*`) — bu bir halüsinasyon **değil**. Ama kullanıcı,
**ilan edilmiş bir sınırın cevabı yerine bir sayı** görüyor.

## Üç kutu — ve neden üçüncüsü ayrı

| kutu | anlamı | yol haritasına girer mi |
|---|---|---|
| `anlamadim` | kelime tanınmadı | ◐ katalog işi |
| `yapamiyorum` | analiz **türü** yok (ölçü→ölçü etki, mutlak dönem kıyası) | ✅ **evet** — bir eksiklik |
| 🔴 `yapmiyorum` | yetenek v1'de **bilinçle** yok (forecast · olumsuzluk · iki cube) | ❌ **hayır** — bir karar |

> ⚠ İkisini aynı mesajla vermek kullanıcıya *"bekle, gelecek"* dedirtir — **oysa
> gelmeyecek.** Bir sınırı bir eksiklik gibi sunmak, kullanıcının zamanını çalar.

## 🔴 Neden yeni bir sözlük DEĞİL

ADR-0008 *"listeye kelime ekleyerek dil kovalama"*yı yasaklar ve bu depo o deseni **on
dört kez** avlamış. Buradaki üç dedektörün **ikisi tamamen yapısal**:

* **olumsuzluk** → `cube_router._NEGATION_SUFFIXES` (tek sahip) + gövdenin **katalogda
  bilinen bir terim** olması şartı. Kelime listesi yok; **biçimbilim + katalog** var.
* **iki cube'un ölçüsü** → `cube_router.measure_cube_candidates` (tek sahip) + bağlaç.
  Yine liste yok.
* **forecast** → ⚠ **kapalı ve belgeli** bir işaret sözlüğü. Bu, dili kovalamak değil
  **bir ürün sınırını adlandırmaktır**; `_SOSYAL` ile aynı kalıp ve aynı gerekçe.

## 🔴 Ve en önemli güvence: bu kapı NEREDE çalışır

Yalnız **deterministik yol tükendikten sonra**, Discovery'ye girilmeden hemen önce.
Yani `route()` ya da Intent-JSON bir cevap ürettiyse bu modül **hiç çağrılmaz**.

*Bir sınır beyanı, cevaplanabilen bir soruyu asla reddetmemelidir* — ve bu güvence
kodun kendisinden değil, **çağrıldığı yerden** gelir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.logging_setup import get_logger

_log = get_logger("yetenek")

#: Yol haritasına **girmeyen** karar. Mesaj *"yapmıyorum"* der.
KUTU_YAPMIYORUM = "yapmiyorum"
#: Yol haritasına **giren** eksiklik. Mesaj *"henüz yapamıyorum"* der.
KUTU_YAPAMIYORUM = "yapamiyorum"


@dataclass(frozen=True)
class Sinir:
    """İlan edilmiş bir yetenek sınırı — ve **hangi kutuda** olduğu."""

    tur: str
    kutu: str
    mesaj: str
    gerekce: str


#: 🔴 FORECAST işaretleri — **kapalı, belgeli** sözlük.
#:
#: ⚠ Bu liste *"Türkçede gelecek nasıl anlatılır"* sorusunu **cevaplamaya çalışmıyor**;
#: o soru açık uçludur ve ADR-0008 tam olarak onu yasaklar. Burada yapılan şey, **v1'de
#: olmadığı ilan edilmiş bir yeteneğin** en yaygın çağırma biçimlerini adlandırmaktır.
#: Kaçan bir biçim Discovery'ye düşer — yani **bugünkü davranış**; bu kapı hiçbir şeyi
#: kötüleştirmez, yalnız yakaladığını dürüstçe reddeder.
_FORECAST = (
    "bu gidisle", "bu gidişle", "gidisat", "gidişat",
    "tahmin", "ongoru", "öngörü", "ongor", "öngör",
    "projeksiyon", "forecast", "beklenti",
    "nerede kapatir", "nerede kapatır", "nasil kapatir", "nasıl kapatır",
    "yil sonunda", "yıl sonunda", "yil sonu tahmini", "yıl sonu tahmini",
    "ne olur", "ne olacak", "kac olur", "kaç olur",
    "gelecek ay", "gelecek yil", "gelecek yıl", "onumuzdeki", "önümüzdeki",
)

#: İki ölçüyü **aynı sorguda** isteyen bağlaçlar. ⚠ Tek başına yeterli DEĞİL —
#: ayrıca iki AYRI cube'un ölçüsünün eşleşmesi gerekir.
_BAGLAC = ("birlikte", "beraber", " ve ", " ile ", "yaninda", "yanında", "hem de")

_TOKEN = re.compile(r"[0-9A-Za-zçÇğĞıİöÖşŞüÜ_]+")


def _norm(s: str) -> str:
    """`cube_router._norm` ile **aynı** düzleştirme (ı→i, ü→u, ş→s…).

    ⚠ Kopya değil zorunluluk: `cube_router`'ı içe aktarmak döngüsel bağımlılık kurardı.
    Davranış farkı olmaması için kapı `test_yetenek.py`'de **iki fonksiyonun aynı çıktıyı
    verdiğini** ölçer — *bir kopyayı güvenli yapan şey niyeti değil, kapısıdır.*
    """
    d = str.maketrans("çÇğĞıİöÖşŞüÜ", "cCgGiIoOsSuU")
    return s.translate(d).lower()


def _forecast_mi(q: str) -> bool:
    qn = _norm(q)
    return any(_norm(w) in qn for w in _FORECAST)


def _olumsuzluk(q: str, schema: dict) -> str | None:
    """🔴 **Yapısal** — kelime listesi yok.

    Bir token olumsuzluk ekiyle bitiyor **ve** ek atılınca kalan gövde katalogda **bilinen
    bir terim** ise, kullanıcı *"X olmayan"* diyor demektir. `firesiz` = `fire`'ın **ZIDDI**;
    `fire` ile kapsanmış saymak sorunun anlamını **tersine çevirir**.

    ⚠ Gövdenin katalogda olması şartı, yanlış-pozitifi kapatan şeydir: `servis`/`analiz`
    gibi ek-olmayan kuyruklar bir ölçü/boyut adı vermez.
    """
    from app.cube_router import _NEGATION_SUFFIXES

    bilinen = _katalog_terimleri(schema)
    for tok in _TOKEN.findall(_norm(q)):
        for ek in _NEGATION_SUFFIXES:
            if len(tok) > len(ek) + 2 and tok.endswith(ek):
                govde = tok[: -len(ek)]
                if govde in bilinen:
                    return f"{tok} (= «{govde}» olmayan)"
    return None


def _katalog_terimleri(schema: dict) -> set[str]:
    """Katalogdaki **tüm** terimlerin normalize kümesi — cube · ölçü · boyut sinonimleri.

    ⚠ `WrenService.schema()` şekli **paket YAML'ından farklıdır**: adlar düz listelerde
    (`measures: [ad, …]`), sinonimler ayrı sözlüklerde (`measure_synonyms: {ad: [syn]}`).
    İlk yazımda yalnız paket şekli okundu ve gerçek şemada küme **boş kaldı** — yani
    olumsuzluk dedektörü sessizce hiçbir şey yakalamıyordu.

    *Bir sözlüğü okumayı bilmek, onu okumak değildir; şekli ölçülmeden yazılan her
    okuyucu boş bir küme döndürebilir ve bu sessizdir.*

    İki şekli de kabul eder — testler paket şekliyle kurulum yapabilsin diye.
    """
    out: set[str] = set()
    for c in schema.get("cubes") or []:
        for t in (c.get("synonyms") or []):
            out.add(_norm(str(t).removesuffix("!")))
        # schema() şekli: ad listeleri + ayrı sinonim sözlükleri
        for anahtar in ("measures", "dimensions", "time_dimensions"):
            for m in (c.get(anahtar) or []):
                if isinstance(m, dict):                       # paket şekli
                    out.add(_norm(str(m.get("name") or "")))
                    for t in (m.get("synonyms") or []):
                        out.add(_norm(str(t).removesuffix("!")))
                else:
                    out.add(_norm(str(m)))
        for anahtar in ("measure_synonyms", "dimension_synonyms"):
            for _ad, syns in (c.get(anahtar) or {}).items():
                for t in (syns or []):
                    out.add(_norm(str(t).removesuffix("!")))
    out.discard("")
    return out


def _syn_benzeri(q: str, terim: str) -> bool:
    """Kelime sınırlı eşleşme — `cube_router._syn_hit`in test şekli için sade karşılığı.

    ⚠ Yalnız paket-şekilli şemalarda (testler) kullanılır; gerçek yolda `_match_measure`
    çalışır. *İki yol varsa hangisinin asıl olduğu yazılı olmalıdır.*"""
    return re.search(rf"(?<![0-9a-z_]){re.escape(_norm(terim))}(?![0-9a-z_])",
                     _norm(q)) is not None


def _iki_cube_olcusu(q: str, schema: dict) -> str | None:
    """MIMARI §9.2 — **tek bir sorgu iki cube'u kapsayamaz.**

    ## 🔴 Ölçüt neden "iki cube" DEĞİL

    İlk yazımda `measure_cube_candidates` kullanıldı ve **yanlış çıktı** — iki sebeple,
    ikisi de ölçülerek görüldü:

    1. O fonksiyon **cube-düzeyi sinonimi eşleşen** cube'ları bilerek dışlıyor
       (*"onlar route'un işi"*), yani `fire ve rework` sorusunda `parti` hiç sayılmıyordu.
    2. Daha önemlisi: **aynı ölçünün iki cube'da bulunması** iki ölçü istemek değildir —
       o bir **belirsizliktir** ve doğru cevabı netleştirmedir, sınır beyanı değil.
       (`toplam_fire_kg` hem `parti`de hem `oee`de var.)

    ## Doğru ölçüt

    **En az iki AYRI SİNONİM METNİ** eşleşecek **ve hiçbir tek cube ikisini birden
    taşımayacak.**

    🔴 **Ölçüt "iki ölçü ADI" değil, "iki EŞLEŞEN KELİME".** Bu ayrım ölçülerek bulundu:
    440 meşru soruda **27 yanlış-pozitif** çıktı ve hepsinin kökü aynıydı —
    *`elektrik ve dönem kıyası`* sorusunda tek kelime (`elektrik`) **iki cube'da farklı
    ölçü adlarıyla** eşleşiyor (`enerji_makine.toplam_elektrik_kwh` ↔
    `surdurulebilirlik.toplam_enerji_kwh`). Kullanıcı **bir şey** istedi; iki sahip çıktı.

    > *İki sahibi olan bir kavram, iki kavram değildir.* Birincisi bir **belirsizliktir**
    > ve doğru cevabı netleştirmedir; ikincisi bir **sınırdır**. Ölçüt bunları ayırmazsa
    > kapı, KN-2'nin katalog çakışmalarını yetenek sınırı diye satar.

    Tek cube ikisini de taşıyorsa soru zaten cevaplanabilir — sınır orada değil.
    *Bir sınırı, gerçekten başladığı yerden dar tanımlamak, cevaplanabilir soruları
    reddetmektir.*

    ⚠ Bağlaç şartı korunuyor: bağlaçsız iki ölçü eşleşmesi çoğu zaman tek bir bileşik
    terimin parçasıdır.
    """
    from app.cube_router import _match_measure

    qn = _norm(q)
    if not any(_norm(b) in qn for b in _BAGLAC):
        return None
    # ölçü adı → onu taşıyan cube'lar
    # anahtar: EŞLEŞEN SİNONİM METNİ (ölçü adı DEĞİL) → o kelimeyi taşıyan cube'lar
    sahipler: dict[str, set[str]] = {}
    for c in schema.get("cubes") or []:
        m, syn = _match_measure(q, c)
        if m and syn:
            sahipler.setdefault(_norm(syn), set()).add(str(c.get("name") or ""))
    # ⚠ `_match_measure` YALNIZ `measure_synonyms` sözlüğünü okur (schema() şekli).
    # Paket şekliyle kurulmuş bir şemada (testler) sessizce boş döner — bu yüzden
    # ikinci şekil burada AÇIKÇA ele alınır, sessiz bir boşluk bırakılmaz.
    if not sahipler:
        for c in schema.get("cubes") or []:
            for m in (c.get("measures") or []):
                if not isinstance(m, dict):
                    continue
                for t in [m.get("name"), *(m.get("synonyms") or [])]:
                    if t and _syn_benzeri(q, str(t)):
                        sahipler.setdefault(_norm(str(t)), set()).add(str(c.get("name") or ""))
                        break
    # 🔴 EN UZUN KAZANIR — cube'lar ARASINDA da. `_match_measure` bu kuralı cube İÇİNDE
    # uyguluyor ama dışında kimse uygulamıyordu; ölçüldü: kalan 21 yanlış-pozitifin
    # hepsi bu boşluktan geliyordu. *`«ariza sayisi»` ve `«ariza»` iki kavram değil,
    # aynı kavramın iki taneliliğidir* (`bakim.ariza_sayisi` ↔ `oee.toplam_durus_dakika`).
    # Bir sinonim başka bir eşleşmiş sinonimin İÇİNDE geçiyorsa, ayrı bir istek sayılmaz.
    kelimeler = sorted(sahipler, key=len, reverse=True)
    kapsanan = {k for k in kelimeler
                if any(k != u and k in u for u in kelimeler)}
    for k in kapsanan:
        sahipler.pop(k, None)
    if len(sahipler) < 2:
        return None
    # Tek bir cube ölçülerin HEPSİNİ taşıyorsa sınır yok — soru cevaplanabilir.
    ortak = set.intersection(*sahipler.values())
    if ortak:
        return None
    return " + ".join(f"«{kelime}» ({'/'.join(sorted(cs))})"
                      for kelime, cs in sorted(sahipler.items()))


def kapsam_disi(q: str, schema: dict) -> Sinir | None:
    """İlan edilmiş bir yetenek sınırına çarpıldı mı? Yoksa `None`.

    🔴 **Yalnız deterministik yol tükendiğinde çağrılır** (Discovery'nin hemen önünde).
    Bu, modülün en önemli güvencesidir ve kodda değil **çağrı yerinde** yaşar.
    """
    if not q:
        return None

    if _forecast_mi(q):
        return Sinir(
            tur="forecast", kutu=KUTU_YAPMIYORUM,
            mesaj=("Geleceğe dönük tahmin (forecast) **v1'de yok** — ve bu bir eksiklik "
                   "değil, bilinçli bir karar: elimdeki sayılar ölçülmüş geçmiştir, "
                   "onlardan bir projeksiyon üretmek başka bir güvence sınıfıdır.\n\n"
                   "Yapabildiğim: **geçmiş eğilimi** gösterebilirim — *«son 6 ayda ciro "
                   "nasıl gitti»* ya da *«bu yıl ile geçen yılı kıyasla»*."),
            gerekce="v1 kapsam kararı (yol haritası: forecast dışarıda)")

    olm = _olumsuzluk(q, schema)
    if olm:
        return Sinir(
            tur="olumsuzluk", kutu=KUTU_YAPAMIYORUM,
            mesaj=(f"«{olm}» bir **olumsuzluk** ifadesi ve bunu henüz sorguya "
                   "çeviremiyorum. Bir şeyin *olmadığı* kayıtları saymak, *olduğu* "
                   "kayıtları saymanın tersi değil; ayrı bir filtre türü.\n\n"
                   "Yapabildiğim: olumlu hâlini sorabilirsin — sonra kırılıma inip "
                   "sıfır olan grubu görebiliriz."),
            gerekce="olumsuzluk filtresi (neq/not_in) v1'de bağlı değil")

    ikili = _iki_cube_olcusu(q, schema)
    if ikili:
        return Sinir(
            tur="iki_cube", kutu=KUTU_YAPMIYORUM,
            mesaj=(f"Bu soru **iki ayrı konunun** ölçüsünü aynı sorguda istiyor "
                   f"({ikili}). Onları tek bir tabloda birleştirmiyorum — çünkü farklı "
                   "tanelilikteki iki ölçüyü yan yana toplamak **sessizce yanlış** bir "
                   "sayı üretir.\n\n"
                   "Yapabildiğim: ikisini **ayrı ayrı** sorabilirsin; ya da birini "
                   "sorup üstüne *«bir de … ekle»* diyebilirsin — takip yolunda aynı "
                   "cube içinde ölçü eklemek çalışıyor."),
            gerekce="MIMARI §9.2 — çapraz-cube ölçü birleştirme kapsam dışı")

    return None


def yanit_alanlari(sinir: Sinir, soru: str | None) -> dict:
    """`AskResponse` alanları — **tek yerden**.

    ⚠ Router'ın işi HTTP'dir; bir sınırın nasıl ANLATILDIĞI bu modülün işi. İkiye
    bölünürse mesaj burada değişir, iz orada eski kalır. *Bir cevabın metni ile izinin
    ayrı sahipleri olursa, biri güncellenip öteki unutulur.*
    """
    _log.info("YETENEK KAPISI: %s (%s) — Discovery'ye GİDİLMEDİ", sinir.tur, sinir.kutu)
    return {
        "question": soru,
        "source": None,
        "note": sinir.mesaj,
        "trace": [f"Yetenek sınırı: {sinir.tur} · kutu={sinir.kutu} · {sinir.gerekce}"],
    }
