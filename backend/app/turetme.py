"""🔴 KÖK-7d / KÇ-10 — **TÜRETME KATMANI**, fail-closed. (denetim raporu KN-8)

## Ölçülen kusur

Katalog yalnız **İSİM** biçimini biliyor; kullanıcı **FİİL** kuruyor:

| kullanıcının kelimesi | katalogdaki karşılık | bugün |
|---|---|---|
| `sattık` *(fiil)* | `satış` — `parti.toplam_ciro` | **R10** |
| `ürettik` *(fiil)* | `üretim` · `üretilen` — `oee.toplam_uretim_kg` | **R10** |
| `alacağımız` *(iyelik + yumuşama)* | `alacak` — `cari.toplam_alacak` | **R10** |

> 🔴 **Ayrım kritik:** `_ek_gecerli` **ÇEKİMİ** çözer (satış→satışı, satışlar).
> Bunlar **TÜRETME**dir (sat‑→satış) — *farklı bir dilbilimsel işlem* ve depoda
> karşılığı yoktu.

Türkçede türetme **üretkendir**: her isim bir fiilden türeyebilir. Bu yüzden sözlüğe
kelime eklemek bu sınıfı **kapatmaz** (ADR-0008) — kural gerekir. İki kural yeter ve
ikisi de **kapalı** kümelerdir:

1. **Yumuşama geri alma** — `alacağ` → `alacak` (`ğ→k` · `b→p` · `d→t` · `c→ç`).
   Türkçenin son-ünsüz yumuşaması, ünlüyle başlayan ek geldiğinde **zorunludur**;
   geri alması da o kadar kuralldır.
2. **Ortak fiil kökü** — kullanıcının token'ı ve katalog terimi **aynı fiil köküne**
   iniyorsa aday olur: `sat`+`tık` ↔ `sat`+`ış`.

## 🔴 FAIL-CLOSED — ve bunun neden pazarlık konusu olmadığı

Raporun kendi uyarısı: *"türetme **anlamı kaydırabilir** (`al-`→`alacak` ✓ ama
`al-`→`alıcı` **boyut**)."* Bu yüzden bu modül **CEVAP ÜRETMEZ**; yalnız
**chip** üretir. `route()`e hiç dokunmaz.

⊙ Sonuç: **kapsam riski yapısal olarak SIFIR.** En kötü senaryo bir fazla chip'tir;
bir yanlış sayı değil.

⚠ Ve bu, geçen turun ölçülmüş dersidir. KÖK-7b kapsamı **açarak** benzer bir sınıfı
kapatmayı denedi: §4 probu %31,2 → %90'ı geçti (ölçüt tuttu) ama gerçek-dünya
**kabul 1150 → 1117**, **sessiz_yanlis 12 → 30** oldu — kayıp `kabul`den
`sessiz_yanlis`e **taşındı**. *Bir ölçütü tutturmak, ölçütün ölçmediği şeyi bozmama
garantisi vermez.* 7d aynı hatayı yapamaz, çünkü hiçbir cevabı değiştirmiyor.

## Kök uzunluğu 3 — ve `al-` bu yüzden dışarıda

Kök en az **3 harf** olmalı. Bu tek şart raporun adıyla uyardığı vakayı
(`al-`→`alacak`/`alıcı`) **yapısal olarak** eler: `al` iki harftir.
*Bir riski kural içinde eritmek, ona ayrı bir istisna yazmaktan sağlamdır.*
"""

from __future__ import annotations

from typing import Any

#: Kullanıcının token'ından soyulan **fiil çekimi** ekleri (kapalı envanter, normalize).
#: ⚠ Buradaki iş *çekimi tanımak* değil, **kökü bulmak**tır — bu yüzden `_ek_gecerli`
#: ile aynı tablo değil: o *"kalan geçerli mi?"* sorusunu yanıtlar, bu *"kök hangisi?"*.
_FIIL_CEKIMI = (
    "iyoruz", "iyorum", "iyorsun",
    "acagimiz", "ecegimiz", "acagim", "ecegim",     # alacağımız · vereceğim
    "dik", "duk", "tik", "tuk",                     # sat-TIK · üret-TİK
    "mis", "mus", "yor", "iyor", "uyor",
    "acak", "ecek", "imiz", "umuz", "iniz", "unuz",
    "di", "du", "ti", "tu",
)

#: Katalog teriminden soyulan **türetme** ekleri (isim⇄fiil, kapalı ve üretken küme).
#: `satis`→`sat` · `uretim`→`uret` · `uretilen`→`uret` · `kesme`→`kes`
_TURETME = ("ilen", "ulen", "inti", "unti", "is", "us", "im", "um", "ma", "me",
            "acak", "ecek", "li", "lu", "ci", "cu")

#: Son-ünsüz yumuşamasının GERİ ALINMASI — `alacağ`+`ımız` → `alacak`.
#: Türkçede zorunlu bir ses olayıdır; tersi de o kadar kuralldır.
_SERTLESME = {"g": "k", "b": "p", "d": "t", "c": "c"}

#: 🔴 YARDIMCI/HAFİF FİİLLER — türetmesi **anlam kaydıran** kapalı sınıf.
#:
#: Raporun kendi uyarısı `al-`ı adıyla anıyordu (`al-`→`alacak` ✓ ama `al-`→`alıcı`
#: **boyut**). Kapı yazılırken **ikincisi ölçüldü ve aynı sınıftandı**:
#:
#:     «bu yıl fire verdik»  →  `verdik` → kök `ver` → katalog `verim` → chip **«oee»**
#:
#: Oysa *"fire vermek"* = fire ÜRETMEK; verimlilikle ilgisi yok. Türkçede `ver-` · `et-` ·
#: `ol-` · `yap-` gibi **hafif fiiller** kendi anlamlarını taşımaz, yanlarındaki isme
#: bağlanırlar — bu yüzden köklerinden türetme yapmak **yapısal olarak** güvenilmezdir.
#:
#: ⚠ Bu bir kelime listesi DEĞİL, Türkçenin kapalı bir **dilbilgisi sınıfıdır** (tıpkı
#: `_NEGATION_SUFFIXES` gibi) ve büyümez. ADR-0008 uyumlu.
#: *Bir riski kural içinde eritmek, ona ayrı bir istisna yazmaktan sağlamdır — ama
#: eritilemeyen bir riski adıyla dışarıda bırakmak, onu görmezden gelmekten sağlamdır.*
_HAFIF_FIIL = frozenset({"ver", "al", "et", "ol", "yap", "gel", "git", "kal", "gor", "de"})

#: Kök en az bu kadar harf olmalı. 🔴 Raporun adıyla uyardığı riski (`al-`→`alacak` ✓
#: ama `al-`→`alıcı` BOYUT) tek başına eler: `al` iki harftir.
EN_AZ_KOK = 3

#: Üretilecek chip üst sınırı — cevabı gürültüye boğmamak için (`uyum.py` ile aynı ilke).
EN_FAZLA = 4

#: `Suggestion.kind` — frontend bunu KENDİ açıklamasıyla basar (KÖK-9'da açılan yol).
TUR_TURETME = "turetme"


def _kokler(w: str, ekler: tuple[str, ...], *, kendisi: bool) -> set[str]:
    """`w`'den `ekler`den birini soyarak elde edilen kök adayları.

    ## 🔴 `kendisi` — ölçümle doğan asimetri

    İlk yazımda **her iki tarafta** kelimenin kendisi de aday sayılıyordu. Korpusta
    ölçüldü: 2 116 reddin **191'i (%9,0)** chip üretti ama **çoğu SAHTEYDİ**, çünkü
    eşleşme bir türetme değil bir **kimlik**ti:

        «may ıstan bugüne en yüksek bonus»  →  chip **«prim»**
        «ogrnim ve vardiya bazında marj»    →  chip **«kar oranı»**
        «…kg başına enerji maliyeti ile iade…» → chip **«iade»**  *(kelimenin kendisi)*

    ⚠ Ve fail-closed olması bunu mazur GÖSTERMEZ: *"prim mi demek istedin?"* diye soran
    bir chip, kullanıcıyı yanlış yere bakmaya davet eder. **Bir tahminin ucuz olması,
    yanlış olmasını ucuzlaştırmaz.**

    🔴 Kural asimetrik olmalı ve sebebi dilbilimsel:
      · **kullanıcı tarafı** GERÇEK bir çekim soymalı (`kendisi=False`) — çünkü bu
        katmanın var olma sebebi *"kullanıcı FİİL kurdu"*dur; çekimsiz bir token zaten
        `_syn_hit`in işidir ve orada eşleşmediyse burada da eşleşmemeli.
      · **katalog tarafı** kendisi olabilir (`kendisi=True`) — `alacak` gibi terimler
        hiçbir türetme eki taşımaz ve `alacağımız` yine onlara inmelidir.
    """
    out = {w} if (kendisi and len(w) >= EN_AZ_KOK) else set()
    for ek in ekler:
        if w.endswith(ek) and len(w) - len(ek) >= EN_AZ_KOK:
            kok = w[: -len(ek)]
            out.add(kok)
            # Yumuşamayı geri al: `alacag` → `alacak`
            if kok[-1] in _SERTLESME:
                out.add(kok[:-1] + _SERTLESME[kok[-1]])
    return {k for k in out if k not in _HAFIF_FIIL}


def adaylar(bilinmeyen: list[str], schema: dict[str, Any]) -> list[dict[str, str]]:
    """Anlaşılmayan kelimeler için **türetme chip'leri** — `[{label, query, kind}]`.

    🔴 Sözleşme: bu fonksiyon **hiçbir cevabı değiştirmez.** Çağıran onu yalnız bir
    reddin yanına chip koymak için kullanır. `route()` bu modülü **hiç görmez**.

    ⚠ Aynı ölçüye birden çok kelimeden ulaşılırsa **bir kez** listelenir: kullanıcıya
    aynı seçeneği iki kez göstermek, seçeneği bir karara değil bir gürültüye çevirir.
    """
    if not bilinmeyen:
        return []
    soru_kokleri: set[str] = set()
    for w in bilinmeyen:
        soru_kokleri |= _kokler(w, _FIIL_CEKIMI, kendisi=False)
    if not soru_kokleri:
        return []

    out: list[dict[str, str]] = []
    gorulen: set[str] = set()
    for c in schema.get("cubes") or []:
        gosterim = c.get("measure_synonyms_display") or {}
        for m, syns in (c.get("measure_synonyms") or {}).items():
            anahtar = f"{c.get('name')}.{m}"
            if anahtar in gorulen:
                continue
            for x in syns or []:
                terim = str(x).removesuffix("!").lower()
                if " " in terim:
                    # ⚠ Çok kelimeli sinonimlerde türetme belirsizdir (*"satış tutarı"*
                    # hangi kelimeden türedi?) ve fail-closed bir katmanda belirsizlik
                    # eklemek, katmanın var olma sebebine aykırıdır.
                    continue
                if _kokler(terim, _TURETME, kendisi=True) & soru_kokleri:
                    etiket = str(gosterim.get(m) or terim)
                    # ⚠ Dedup ETİKET üzerinden — ölçüldü: `alacağımız` iki cube'un
                    # (`cari` · `mizan`) aynı adlı ölçüsüne iniyordu ve kullanıcı
                    # **aynı chip'i iki kez** görüyordu. *Aynı seçeneği iki kez
                    # göstermek, seçeneği bir karara değil bir gürültüye çevirir.*
                    # 🔴 Ve bu bir belirsizliktir: hangi cube'un `alacak`ı? Onu
                    # `app/belirsizlik_chipi.py` (KÖK-9) cevap ANINDA beyan eder;
                    # burada, cevap daha kurulmadan, iki kez sormanın anlamı yok.
                    if etiket in gorulen:
                        break
                    out.append({"label": etiket, "query": etiket,
                                "kind": TUR_TURETME})
                    gorulen.add(anahtar)
                    gorulen.add(etiket)
                    break
    return out[:EN_FAZLA]


def not_metni(bilinmeyen: list[str], chip_sayisi: int) -> str:
    """Reddin notuna eklenen cümle — **soruyu soran**, iddia etmeyen.

    ⚠ *"Şunu demek istedin"* DENMEZ: türetme bir tahmindir ve fail-closed bir katmanın
    metni de fail-closed olmalıdır. *Bir tahmini bir bilgi gibi sunmak, tahmini yanlış
    yapmaktan daha zararlıdır.*
    """
    if not chip_sayisi:
        return ""
    kelime = " ".join(w for w in bilinmeyen[:2] if w)
    # ⚠ Kelime listesi boş olabilir (çağıran onu taşımıyorsa) ve o zaman «» diye BOŞ bir
    # tırnak basılıyordu — ölçüldü, kullanıcıya anlamsız bir cümle gidiyordu.
    # *Bir metin şablonu, verisi eksik geldiğinde de okunabilir olmalıdır.*
    bas = f"«{kelime}» bir fiil gibi görünüyor — k" if kelime else "K"
    return f"{bas}atalogda karşılığı şunlar olabilir. Hangisini kastettin?"
