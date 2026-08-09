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
from dataclasses import dataclass, field

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
    #: 🔴 `G8` — **YAPISAL** kapasite beyanı. `mesaj` içindeki *"Yapabildiğim: …"*
    #: cümlesi bugün **elle yazılmış örnekler** taşıyor; bunlar katalogdan TÜRETİLİR ve
    #: `route()` ile **DOĞRULANIR**. *Çalışmayan bir öneri, öneri değil ikinci bir
    #: duvardır* — `ask.py:428`'in `_dogrulanmis_chipler` disiplininin aynısı.
    oneriler: list = field(default_factory=list)


#: 🔴 FORECAST işaretleri — **kapalı, belgeli** sözlük.
#:
#: ⚠ Bu liste *"Türkçede gelecek nasıl anlatılır"* sorusunu **cevaplamaya çalışmıyor**;
#: o soru açık uçludur ve ADR-0008 tam olarak onu yasaklar. Burada yapılan şey, **v1'de
#: olmadığı ilan edilmiş bir yeteneğin** en yaygın çağırma biçimlerini adlandırmaktır.
#: Kaçan bir biçim Discovery'ye düşer — yani **bugünkü davranış**; bu kapı hiçbir şeyi
#: kötüleştirmez, yalnız yakaladığını dürüstçe reddeder.
#: 🔴 **YARGI SINIRI — canlı bulgu (§18.2).** *"bu ay iyi miyiz kötü müyüz"* →
#: *"ort oee çıkarabilirim — hangi dönem için?"*. Kullanıcı **yargı** istedi; sistemde
#: eşik/hedef yok ve korpusun **açık yasağı** var: *"iyi/kötü yargısını bir eşik
#: uydurarak vermek."*
#:
#: ⚠ Bu bir **sınırdır, bir kapsam eksiği değil**: sayıyı verebiliriz, **yargıyı**
#: veremeyiz. Beyan edilmiş bir referans varsa sahibi `app/hedef.py` (`ADR-0028`:
#: **hedef UYDURULMAZ**) — o beyan geldiğinde bu sınır kendiliğinden dar alır.
#:
#: *Bir eşiği uydurarak verilen yargı, yanlış bir sayıdan daha zor fark edilir: sayı
#: sorgulanır, yargı benimsenir.*
_YARGI = (
    "iyi mi", "iyi miyiz", "kotu mu", "kötü mü", "kotu muyuz", "kötü müyüz",
    "iyi gidiyor mu", "kotu gidiyor mu", "kötü gidiyor mu",
    "yeterli mi", "normal mi", "basarili mi", "başarılı mı",
)


def _yargi_mi(q: str) -> bool:
    """Soru bir **yargı** istiyor mu — sayı değil, hüküm?"""
    qn = _norm(q)
    return any(_norm(w) in qn for w in _YARGI)


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

    # 🔴 **`§63` — «EN» ÖNÜNDEYSE O BİR ÜSTÜNLÜK, OLUMSUZLUK DEĞİL.**
    #
    # Ölçüldü (`h12`): `bu yıl **en verimsiz** hattı bul ve o hattın makinelerini listele`
    # → *"«verimsiz (= «verim» olmayan)» bir olumsuzluk ifadesi ve bunu henüz sorguya
    # çeviremiyorum"*. Oysa kullanıcı *"verimi olmayan"* demedi; **"en düşük verimli"**
    # dedi — ve `cube_router._AZLIK_KUTBU` `verimsiz`'i zaten **azlık kutbu** olarak
    # tanıyor, yani `_direction` ondan `ASC` üretiyor.
    #
    # ⊙ İki okuma da dilbilgisel olarak mümkün; ayıran şey **yapı**: `en` + sıfat bir
    # **üstünlük derecesidir** ve Türkçede olumsuz sıfatın üstünlüğü (`en verimsiz`,
    # `en kârsız`, `en hatasız`) **sıralanabilir** bir niteliktir, bir yokluk değil.
    #
    # ⚠ Kapsam dar: yalnız token'ın **hemen öncesinde** `en` varsa. `firesiz partiler`
    # (üstünlüksüz) aynen olumsuzluk sayılır — o soru gerçekten *"firesi olmayan"* der.
    #
    # *Bir sıfatı derecelendirmek, onu yok saymaktan başka bir şeydir.*
    bilinen = _katalog_terimleri(schema)
    _tokenlar = _TOKEN.findall(_norm(q))
    # 🔴🔴 **`§X2` — KATALOGDA ADI OLAN BİR KELİME, BİR YOKLUK DEĞİLDİR.**
    #
    # Ölçüldü (`X10` — *«makine bazında planlı ve plansız duruşu yan yana göster»*):
    #
    #     «plansiz (= «plan» olmayan)» bir olumsuzluk ifadesi ve bunu henüz
    #     sorguya çeviremiyorum.
    #
    # 🔴 Oysa `oee.plansiz_durus_dakika` **VAR** ve sinonimi **birebir «plansız duruş»**
    # (`expression: SUM(plansiz_durus_dk)`). Yani bir **yetenek sınırı beyanı**, var olan
    # bir ölçüyü gölgeliyordu — `§1.5`'in dersinin bu daldaki hâli: *truthy bir beyan,
    # daha yetenekli bir adımı sessizce öldürür.*
    #
    # ⊙ Ayrım `§63`'ün guard'ıyla **aynı biçimde** yapısal: orada *«`en` önündeyse
    # üstünlüktür»*, burada *«kelimenin KENDİSİ katalogda geçiyorsa bir ADdır»*. Katalog
    # yazarı bir ölçüye *«plansız duruş»* adını verdiyse, o kelime o katalogda **olumlu**
    # bir şeyi gösterir; onu ekine bakıp yokluk saymak, yazarın beyanını ezmektir.
    #
    # ⚠ Yanlış-pozitif kapalı kalır: `firesiz` hiçbir katalog teriminde geçmez, dolayısıyla
    # *«firesiz partiler»* aynen olumsuzluk sayılır (`fire` gövdesi + `firesiz` adı YOK).
    # Kural bir kelime listesi değil, kataloğun kendi sözlüğüne yapılan bir sorgudur.
    #
    # *Bir ekin anlamı, kelimenin katalogda bir adı olup olmadığına bakılmadan okunamaz.*
    _katalog_kelimeleri = {w for t in bilinen for w in t.split()}
    for _i, tok in enumerate(_tokenlar):
        if _i > 0 and _tokenlar[_i - 1] == "en":
            continue
        if tok in _katalog_kelimeleri:
            continue
        for ek in _NEGATION_SUFFIXES:
            if len(tok) > len(ek) + 2 and tok.endswith(ek):
                govde = tok[: -len(ek)]
                if govde in bilinen:
                    return f"{tok} (= «{govde}» olmayan)"
    return None


def _katalog_terimleri(schema: dict) -> set[str]:
    """Katalogdaki tüm terimlerin **normalize** kümesi — cube · ölçü · boyut sinonimleri.

    🔴 **TARAMA ARTIK BURADA DEĞİL** (`app/iddia.py`). Bu fonksiyonun eski gövdesi,
    `iddia`'nın gövdesiyle **aynı soruyu** iki farklı biçimde yanıtlıyordu — ve ikisi
    **ayrışmıştı**: buradaki `schema()` şeklini doğru okuyordu, oradaki `dimension_labels`
    diye var olmayan bir alan arıyordu.

    ⚠ O ders **burada** yazılıydı ve orada uygulanmamıştı:

    > *"`WrenService.schema()` şekli paket YAML'ından farklıdır… ilk yazımda küme boş
    > kaldı — yani olumsuzluk dedektörü sessizce hiçbir şey yakalamıyordu.*
    > *Bir sözlüğü okumayı bilmek, onu okumak değildir."*

    Kalan tek şey **eşleştirme politikası**: bu modül Türkçe düzleştirme (`_norm`) ile
    eşler, `iddia` düz `lower()` ile. Politika çağıranındır; **tarama katalogundur**.
    """
    from app.iddia import katalog_terimleri

    return katalog_terimleri(schema, norm=_norm)


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
    # 🔴🔴 **`§BB2` — `_match_measure` KÜP BAŞINA TEK ÖLÇÜ DÖNDÜRÜR; iki ölçüyü de
    # taşıyan küp, yalnız BİRİNE sayılıyordu ve kesişim yapay olarak boşalıyordu.**
    #
    # Ölçüldü (`AA13` — *«aylık fire oranı ile üretim miktarını aynı grafikte iki eksende
    # göster»*):
    #
    #     «Bu soru **iki ayrı konunun** ölçüsünü birlikte istiyor
    #      («fire» (parti) + «miktar» (oee)) … ilişkiyi hesaplayamıyorum»
    #
    # 🔴 Oysa `parti` küpü **ikisini birden** taşıyor: `fire_orani_yuzde` **ve**
    # `toplam_agirlik_kg`. `_match_measure(q, parti)` en iyi eşleşme olarak yalnız `fire`i
    # döndürünce `parti`, *«miktar»* kelimesinin sahipleri arasında **hiç görünmedi**;
    # kesişim boş çıktı ve sistem yapabildiği bir işi **yapamıyorum** diye ilan etti.
    #
    # ⊙ Bu fonksiyonun kendi docstring'i tam da bu tuzağı başka bir yüzüyle anlatıyor
    # (*"iki sahibi olan bir kavram, iki kavram değildir"*); eksik olan simetriği:
    # **iki kavramı taşıyan bir küp, iki küp değildir.**
    #
    # ⚠ Yanlış-pozitif koruması **korunur**: aşağıdaki *kapsanan kelime* elemesi ve
    # *"en az iki AYRI eşleşen kelime"* şartı aynen yürürlükte. Burada yalnız sahiplik
    # haritası **tamamlanıyor** — yeni bir kelime, yeni bir eşik, yeni bir sözlük yok.
    #
    # *Bir sınırı ilan etmeden önce, sınırın gerçekten orada olup olmadığına bakmak gerekir.*
    for _c in schema.get("cubes") or []:
        _ad = str(_c.get("name") or "")
        for _m in (_c.get("measures") or []):
            if not isinstance(_m, dict):
                continue
            for _t in [_m.get("name"), *(_m.get("synonyms") or [])]:
                _tn = _norm(str(_t or ""))
                if _tn in sahipler and _syn_benzeri(q, str(_t)):
                    sahipler[_tn].add(_ad)

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


def onerileri_kur(schema: dict, *, tur: str, en_fazla: int = 3) -> list[dict]:
    """🔴 `G8` — *"ama şunu yapabilirim"*: **katalogdan türet, `route()` ile doğrula**.

    Bugün `Sinir.mesaj` içindeki örnekler **elle yazılmış** (*"son 6 ayda ciro nasıl
    gitti"*) ve hiçbir tenant'ta doğrulanmıyor — o cube yoksa öneri **ikinci bir duvara**
    çarptırır. Bu fonksiyon önerileri **o tenant'ın kataloğundan** kurar ve her birini
    `route()`'a sorar; cevap açmayan öneri **basılmaz**.

    *Aynı duvara ikinci kez çarptıran bir chip, chip olmamasından kötüdür*
    (`ask.py:428`'in `_dogrulanmis_chipler` disiplini).
    """
    from app import cube_router

    kaliplar = {
        # Sınıra göre **ne yapılabileceği** değişir; kalıp sayısı KAPALI ve gerekçeli.
        "forecast": ["son 6 ayda {olcu}", "bu yıl {olcu}"],
        "olumsuzluk": ["{kirilim} bazında {olcu}"],
        "iki_cube": ["{olcu}"],
    }.get(tur, ["{olcu}"])

    out: list[dict] = []
    for c in (schema or {}).get("cubes", [])[:6]:
        olculer = [m.get("name") if isinstance(m, dict) else m
                   for m in (c.get("measures") or [])][:2]
        boyutlar = [d.get("name") if isinstance(d, dict) else d
                    for d in (c.get("dimensions") or [])][:1]
        etiketler = {**(c.get("measure_synonyms_display") or {}),
                     **(c.get("dimension_labels") or {})}
        for olcu in filter(None, olculer):
            for kalip in kaliplar:
                if "{kirilim}" in kalip and not boyutlar:
                    continue
                soru = kalip.format(
                    olcu=etiketler.get(olcu) or str(olcu).replace("_", " "),
                    kirilim=(etiketler.get(boyutlar[0]) if boyutlar else "") or
                            (str(boyutlar[0]).replace("_", " ") if boyutlar else ""))
                soru = " ".join(soru.split())
                try:
                    if cube_router.route(cube_router._norm(soru), schema) is None:
                        continue                      # 🔴 cevap açmıyor → BASILMAZ
                except Exception:                     # noqa: BLE001 — fail-closed
                    continue
                if soru not in [o["query"] for o in out]:
                    out.append({"label": soru, "query": soru})
                if len(out) >= en_fazla:
                    return out
    return out


#: 🔴🔴 `O-15/D` — **GARSONA DEVREDİLEBİLİR SINIRLAR.**
#:
#: `kapsam_disi` iki yerden çağrılıyor ve bu **bilinçli** (`ask.py:3582` erken · `:4655`
#: Discovery'nin hemen önünde). Aradaki mesafede artık **orkestratör** duruyor.
#:
#: ⊙ Ölçüldü (canlı `II3`/`II4`): *«üretim, fire ve enerji için bir pano taslağı»* ve
#: *«ciro, gecikme ve iade oranına birlikte bakarak sırala»* — ikisi de erken kapıda
#: `iki_cube` diye **reddedildi**. Oysa kapının kendi metni şunu söylüyor:
#:
#:     *"İkisini **ortak bir eksende yan yana** koyabilirim — ama aralarındaki
#:      **ilişkiyi** (etki, korelasyon) hesaplayamıyorum."*
#:
#: Ve `PANO`/`RAPOR`/`MATRIS` tam olarak **yan yana**dır: her bölüm kendi küpünden gelir,
#: hiçbir ilişki iddia edilmez. Yani kapı, metninde **yapabildiğini söylediği** şeyi
#: reddediyordu. Bu, bu dosyanın `iki_cube` dalındaki uyarısının **bir seviye yukarıdaki
#: tekrarıdır**: *bir sınır beyanı, sınır değiştiğinde kendiliğinden güncellenmez.*
#:
#: ⚠ **Sınır KALDIRILMADI, ERTELENDİ.** Erken kapı bu türde susar; plan koşarsa cevap
#: bölümlü gelir, koşmazsa **birebir aynı** `Sinir` geç kapıda konuşur ve Discovery'ye
#: yine inilmez. Yani en kötü durum bugünküyle **bayt bayt aynı**, kazanç tek yönlü.
#: ⚠ Ve yalnız `iki_cube`: `forecast`·`yargi`·`olumsuzluk` ertelenmez — onlar bir
#: **çıktı biçimi** eksikliği değil, bir **yetenek** eksikliğidir ve plan da yapamaz.
#: *Bir sınırı ertelemek ancak arkasında onu aşabilecek bir basamak varsa doğrudur;
#: yoksa erteleme, reddi geciktirmekten başka bir şey değildir.*
DEVREDILEBILIR = frozenset({"iki_cube"})


def kapsam_disi(q: str, schema: dict, *, erken: bool = False) -> Sinir | None:
    """İlan edilmiş bir yetenek sınırına çarpıldı mı? Yoksa `None`.

    🔴 **Yalnız deterministik yol tükendiğinde çağrılır** (Discovery'nin hemen önünde).
    Bu, modülün en önemli güvencesidir ve kodda değil **çağrı yerinde** yaşar.

    ⚠ `erken=True` → `DEVREDILEBILIR` türler `None` döner (orkestratöre yol verilir).
    Varsayılan `False`; yani **geç** kapı ve tüm öteki çağıranlar bayt bayt aynı kalır.
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
            gerekce="v1 kapsam kararı (yol haritası: forecast dışarıda)",
            oneriler=onerileri_kur(schema, tur="forecast"))

    olm = _olumsuzluk(q, schema)
    if olm:
        return Sinir(
            tur="olumsuzluk", kutu=KUTU_YAPAMIYORUM,
            mesaj=(f"«{olm}» bir **olumsuzluk** ifadesi ve bunu henüz sorguya "
                   "çeviremiyorum. Bir şeyin *olmadığı* kayıtları saymak, *olduğu* "
                   "kayıtları saymanın tersi değil; ayrı bir filtre türü.\n\n"
                   "Yapabildiğim: olumlu hâlini sorabilirsin — sonra kırılıma inip "
                   "sıfır olan grubu görebiliriz."),
            gerekce="olumsuzluk filtresi (neq/not_in) v1'de bağlı değil",
            oneriler=onerileri_kur(schema, tur="olumsuzluk"))

    if _yargi_mi(q):
        # 🔴 §18.2 — sınır **netleştirmeden önce** konuşur (`_guvenli_kapsam_disi`
        # dönem dalından da çağrılıyor). Aksi hâlde sistem ölçü + dönem sorar, kullanıcı
        # ikisini de verir, ve sonunda **yargı yerine bir sayı** alır.
        return Sinir(
            tur="yargi", kutu=KUTU_YAPMIYORUM,
            mesaj=("Bu bir **yargı** sorusu — *iyi mi, kötü mü*. Sayıyı verebilirim ama "
                   "hükmü veremem: bunun için bir **eşik ya da hedef** gerekir ve "
                   "katalogda beyan edilmiş bir hedef yok.\n\n"
                   "Bir eşik **uydurmam** — uydurulmuş bir eşikle verilen yargı, yanlış "
                   "bir sayıdan daha zor fark edilir; sayı sorgulanır, yargı benimsenir."
                   "\n\nYapabildiğim: sayıyı ve **değişimini** göstermek — "
                   "*«geçen aya göre»* dersen yönü birlikte okuruz."),
            gerekce="yargı için beyan edilmiş eşik/hedef yok (ADR-0028)",
            oneriler=onerileri_kur(schema, tur="yargi"))

    ikili = _iki_cube_olcusu(q, schema)
    # ⚠ Koşul `DEVREDILEBILIR`'i **okur**, tür adını burada tekrar etmez: bir kümeyi
    # tanımlayıp yanında sabit bir dize karşılaştırmak, kümeyi bir süse çevirir ve
    # ikinci bir tür eklendiğinde iki yerden yalnız biri güncellenir.
    if ikili and not (erken and "iki_cube" in DEVREDILEBILIR):
        # 🔴 `G6.8` (`Ö12`'nin chip yarısı) — **BU BEYAN BAYATLADI ve düzeltildi.**
        #
        # Eski metin *"onları tek bir tabloda birleştirmiyorum"* diyordu. `G6.5`'ten sonra
        # bu **artık doğru değil**: çapraz-cube harman (`blend`) mutfakta çalışıyor, kapı
        # grain uyumunu doğruluyor (`cube_router.blend_uyumlu`) ve Intent-JSON onu **ifade
        # edebiliyor**. Yapamadığımız şey **birleştirme** değil, **ilişki**.
        #
        # ⚠ Bir sınır beyanı, sınır değiştiğinde **kendiliğinden** güncellenmez — ve
        # güncellenmeyen bir sınır beyanı, kullanıcıya sahip olduğumuz yeteneği
        # **yok** diye söyler. *Yanlış bir «yapamam», yanlış bir «yapabilirim» kadar
        # pahalıdır: ikisi de kullanıcının kararını yanlış bilgiyle değiştirir.*
        #
        # 🔴 Ayrım şudur ve `Ö12`'nin ikiye bölünmesi tam budur:
        #   · **iki ayrı seri, ortak eksende** → ✅ var (`blend`, `G6.5`)
        #   · **aralarındaki ilişki/etki/korelasyon** → ⊘ v2 · II-D (§8'in gerekçesi)
        return Sinir(
            tur="iki_cube", kutu=KUTU_YAPMIYORUM,
            mesaj=(f"Bu soru **iki ayrı konunun** ölçüsünü birlikte istiyor ({ikili}). "
                   "İkisini **ortak bir eksende yan yana** koyabilirim — ama "
                   "aralarındaki **ilişkiyi** (etki, korelasyon) hesaplayamıyorum.\n\n"
                   "İki şey karıştırılmasın: yan yana koymak iki **ayrı** seridir ve "
                   "her sayı kendi cube'undan gelir; ilişki ise bir **çıkarımdır** ve "
                   "onu ancak ölçebildiğimde söylerim.\n\n"
                   "Yapabildiğim: birini sorup üstüne *«bir de … ekle»* diyebilirsin — "
                   "ortak kırılım varsa ikisi aynı tabloda gelir."),
            gerekce="Ö12: yan yana ✅ (blend) · ilişki ⊘ (v2 · II-D)",
            oneriler=onerileri_kur(schema, tur="iki_cube"))

    return None


def yanit_alanlari(sinir: Sinir, soru: str | None, _sema: dict | None = None) -> dict:
    """`AskResponse` alanları — **tek yerden**.

    ⚠ Router'ın işi HTTP'dir; bir sınırın nasıl ANLATILDIĞI bu modülün işi. İkiye
    bölünürse mesaj burada değişir, iz orada eski kalır. *Bir cevabın metni ile izinin
    ayrı sahipleri olursa, biri güncellenip öteki unutulur.*
    """
    _log.info("YETENEK KAPISI: %s (%s) — Discovery'ye GİDİLMEDİ · %d öneri",
              sinir.tur, sinir.kutu, len(sinir.oneriler))
    # 🔴 `G8.4` — **BEYAN `iddia.py`'DEN GEÇER.** Metin deterministik diye muaf değildir:
    # kapının işi *"bu cümle tutulabilir bir söz mü"* sorusudur ve bir şablon da katalogdan
    # **ayrışabilir** (bu turda tam olarak öyle bir ayrışma bulundu — bkz. `katalog_terimleri`).
    # Denetim **bedava**: 0 LLM, 0 token (`G4.7`).
    #
    # ⚠ Ve düşme burada **sessizleşmek değildir**: bir sınır beyanının yerini boşluk alsaydı
    # kullanıcı cevapsız kalırdı — oysa kapının koruduğu şey **vaat**, sınırın kendisi değil.
    # Düşerse iz kaydedilir ve metin **öneri yarısına** iner (*"şunu yapabilirim"* düşer,
    # *"bunu yapamam"* kalır). *Fail-closed, sessiz-closed demek değildir.*
    mesaj, dusen = sinir.mesaj, None
    try:
        from app import iddia as _iddia

        _r = _iddia.dogrula(sinir.mesaj, _sema)
        if not _r.gecti and _r.temiz_metin.strip():
            mesaj, dusen = _r.temiz_metin.strip(), _r.gerekceler
        elif not _r.gecti:
            dusen = _r.gerekceler
    except Exception:                                  # noqa: BLE001 — sınır beyanı DÜŞMEZ
        _log.warning("iddia kapısı yetenek beyanında çalışmadı", exc_info=True)

    out = {
        "question": soru,
        "source": None,
        "note": mesaj,
        "trace": [f"Yetenek sınırı: {sinir.tur} · kutu={sinir.kutu} · {sinir.gerekce}"]
                 + ([f"🔴 iddia kapısı düşürdü: {', '.join(dusen)}"] if dusen else []),
    }
    # 🔴 `G8` — *"ama şunu yapabilirim"*. Üçüncü bir öneri kanalı AÇILMAZ: mevcut
    # `suggestions` kullanılır. `AskResponse` zaten `suggestions` ve `next_steps`
    # taşıyor; üçüncüsü kullanıcıya *"hangisi gerçek öneri"* sorusunu sordururdu.
    if sinir.oneriler:
        from app.schemas import Suggestion

        out["suggestions"] = [Suggestion(label=o["label"], query=o["query"])
                              for o in sinir.oneriler]
    return out
