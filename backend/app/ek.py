"""🔴 `G7` — **TÜRKÇE EK MOTORU**: enjekte edilen yuvalar doğru çekimlenir.

## Kapsam KAPALI ve küçük

Yalnız anlatıcının **enjekte ettiği** dört şey: *metrik adı · boyut değeri · sayı ·
tarih*. 🔴 **Serbest metne UYGULANMAZ** — o, bu motorun işi değil ve testte kilitli.

## Neden Zemberek ALINMADI — üç somut gerekçe

| # | engel |
|---|---|
| 1 | Son sürüm **0.17.1 · Temmuz 2019**; README'si *"slow maintenance mode"* |
| 2 | Sağlıklı Python bağlayıcısı **yok** → **JVM** taşımak gerekir |
| 3 | `pip install` **ağ ister**; CI `--network none` (`MIMARI.md:1929`) |

⚠ Ve google-research'ün FST'si **19 Nisan 2026'da arşivlendi** — kurumsal ilgi çekiliyor.

## ⚠ `_SUFFIX_ATOMS` ile tablo PAYLAŞILAMADI — ve sebebi yazılı

Yol haritası *"kural tablosu ORTAK olmalı, ikinci tablo KAT-1 ihlali"* diyordu.
**Ölçüldü ve uygulanamaz:**

| | `cube_router._SUFFIX_ATOMS` | bu modül |
|---|---|---|
| yön | **doğrulama** (*"bu kuyruk ek mi?"*) | **üretim** (*"eki nasıl yazarım?"*) |
| alfabe | **ASCII-normalize** (`_norm`: ı→i, ü→u, ş→s) | **gerçek imlâ** (ü/ö/ı ayrımı ŞART) |

🔴 Ünlü uyumu **tam olarak** normalizasyonun sildiği bilgiye dayanır: `ü` ile `u` aynı
harfe indiğinde *"ince mi kalın mı"* sorusu **cevapsız** kalır. Yani tabloyu paylaşmak
teknik olarak mümkün değil — **aynı kural değil, ters iki kural**.
*İki fonksiyon aynı konuyu konuşuyor diye aynı sahibe ait olmaz.*

## Sayı → OKUNUŞ zorunlu

⚠ Danışman belgesinin *"son harfe bakar"* önerisi **yanlıştır**: ek sayının
**okunuşuna** göre değişir. `3` → *üç* → `3'te`; `1.000.000` → *milyon* → `1.000.000'a`.
Son harfe bakan bir motor ikisini de yanlış yazardı.
"""

from __future__ import annotations

import re

from app.logging_setup import get_logger

_log = get_logger("ek")

_KALIN = "aıou"          # arka ünlüler
_INCE = "eiöü"           # ön ünlüler
_DUZ = "aeıi"
_UNLU = _KALIN + _INCE

#: Sert ünsüzler — ardından gelen `d` **t**'ye döner (*"Mart'ta"*, *"kg'ta"*).
_SERT = "fstkçşhp"

#: 🔴 **İSTİSNA SÖZLÜĞÜ** — TDK'nın belgelediği **kapalı** liste.
#:
#: Kural: son ünsüzü `p/ç/t/k` olan çok heceli sözcükler ünlüyle başlayan ek alınca
#: yumuşar (*kitap→kitabı*). Ama bazıları **yumuşamaz** (*saat→saati*, *devlet→devleti*)
#: ve bunlar bir kuralla değil bir **liste**yle bilinir. Liste kapalı ve gerekçeli —
#: büyümesi bir sözlük işidir, bir düzeltme değil.
_YUMUSAMAZ = frozenset({
    "saat", "devlet", "millet", "sanat", "hukuk", "kat", "sept",
    "bilet", "paket", "market", "kredi", "tikat",
})

_YUMUSAMA = {"p": "b", "ç": "c", "t": "d", "k": "ğ"}

#: 🔴 **İNCE OKUNAN SÖZCÜKLER** — ikinci kapalı liste, ve onu bir TEST buldurdu.
#:
#: `saat` son ünlüsü `a` (kalın) olduğu için kural `saatı` üretir; **doğrusu `saati`**.
#: Sebep kuralla türetilemez: bunlar yabancı kökenli ve **ince** çekimlenen sözcükler.
#: `sanat` → `sanatı` (kalın, düzenli) ama `dikkat` → `dikkati` (ince) — aynı yazım,
#: farklı çekim. *Bir dilin istisnası bir kuralın eksiği değil, sözlüğün kendisidir.*
#:
#: ⚠ Liste **dar** tutuldu: bu motorun kapsamı metrik adı · boyut değeri · sayı · tarih.
#: Oralarda geçebilecek olanlar alındı (`saat` bir **birim**), gerisi alınmadı — bir
#: sözlüğü buraya kopyalamak, kapsamı sessizce genişletmek olurdu.
_INCE_OKUNAN = frozenset({
    "saat", "kalp", "dikkat", "harf", "hal", "usul", "vakit", "rol", "gol",
})

#: Sayı → okunuş. Yalnız **son okunan sözcük** eki belirler, o yüzden tam bir
#: sayı-yazıcıya gerek yok: basamak gruplarının son anlamlı parçası yeter.
_BIRLER = ("", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
_ONLAR = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen",
          "doksan")
_BASAMAK = ((10 ** 12, "trilyon"), (10 ** 9, "milyar"), (10 ** 6, "milyon"),
            (10 ** 3, "bin"), (100, "yüz"))


def son_okunus(sayi: str | int | float) -> str:
    """Bir sayının **son okunan sözcüğü** — eki o belirler.

    `3` → *üç* · `40` → *kırk* · `1.000.000` → *milyon* · `2026` → *altı*
    (iki bin yirmi **altı**).
    """
    ham = re.sub(r"[^\d]", "", str(sayi).split(",")[0])
    if not ham:
        return ""
    n = int(ham)
    if n == 0:
        return "sıfır"
    for buyukluk, ad in _BASAMAK:
        if n >= buyukluk:
            kalan = n % buyukluk
            return son_okunus(kalan) if kalan else ad
    if n >= 10:
        birler = n % 10
        return _BIRLER[birler] if birler else _ONLAR[n // 10]
    return _BIRLER[n]


def _son_unlu(s: str) -> str:
    for ch in reversed(s.lower()):
        if ch in _UNLU:
            return ch
    return ""


def _ikili(unlu: str) -> str:
    """2'li uyum: `-e` / `-a`."""
    return "a" if unlu in _KALIN else "e"


def _dortlu(unlu: str) -> str:
    """4'lü uyum: `-i` / `-ı` / `-u` / `-ü`."""
    if unlu in "ei":
        return "i"
    if unlu in "aı":
        return "ı"
    if unlu in "ou":
        return "u"
    return "ü"


def _yumusat(govde: str) -> str:
    """Ünlüyle başlayan ek öncesi son ünsüz yumuşaması — istisnalar hariç."""
    if len(govde) < 3 or govde.lower() in _YUMUSAMAZ:
        return govde
    son = govde[-1].lower()
    if son in _YUMUSAMA and _son_unlu(govde):
        return govde[:-1] + _YUMUSAMA[son]
    return govde


def ek_bagla(sozcuk: str, ek_tipi: str, *, sayi: bool = False,
             kesme: bool = False) -> str:
    """`sozcuk` + doğru çekim eki. `ek_tipi ∈ {de, den, e, i, in}`.

    `sayi=True` ise ek **okunuşa** göre seçilir ve **kesme işaretiyle** yazılır
    (`3'te` · `1.000.000'a`) — TDK kuralı ve danışman belgesinin *"son harfe bak"*
    önerisinin **düzeltilmiş** hâli.

    🔴 **Fail-open değil, fail-same:** bilinmeyen bir ek tipi ya da boş sözcükte
    **sözcüğün kendisi** döner. Bir eki yanlış yazmaktansa hiç yazmamak yeğdir —
    yanlış çekim, uydurma bir sayı kadar görünür bir kusurdur.

    🔴 `kesme=True` → **ÖZEL AD** kipi: kesme işaretiyle yazılır ve **yumuşama
    uygulanmaz** (`Mart'ta` · `Ahmet'i`, `Ahmed'i` DEĞİL). TDK kuralı: özel adlarda ünsüz
    yumuşaması **yazıya geçmez**. Bu ayrım `app/yayilim.py`'nin yer tutucu geri koymasında
    zorunlu: boyut değerleri (`Mart` · `Merkez` · `Kadıköy`) özel addır ve model zaten
    kesme işaretiyle yazar — *modelin yazdığı kesme, sözcüğün özel ad olduğunun beyanıdır.*
    """
    if not sozcuk or not str(sozcuk).strip():
        return str(sozcuk or "")
    s = str(sozcuk).strip()

    # Ek, SAYININ OKUNUŞUNA göre seçilir; gövde ise olduğu gibi yazılır.
    temel = son_okunus(s) if sayi else s
    unlu = _son_unlu(temel)
    if not unlu:
        return s
    # 🔴 İnce okunan sözcükler kalın ünlü taşısa da İNCE ek alır (`saat` → `saati`).
    if not sayi and temel.lower() in _INCE_OKUNAN:
        unlu = "e"

    a = _ikili(unlu)
    i = _dortlu(unlu)
    son_harf = (temel[-1] if temel else "").lower()
    sert = son_harf in _SERT
    unlu_bitis = son_harf in _UNLU

    if ek_tipi == "de":
        ek = ("t" if sert else "d") + a
    elif ek_tipi == "den":
        ek = ("t" if sert else "d") + a + "n"
    elif ek_tipi == "e":
        ek = ("y" if unlu_bitis else "") + a
    elif ek_tipi == "i":
        ek = ("y" if unlu_bitis else "") + i
    elif ek_tipi == "in":
        ek = ("n" if unlu_bitis else "") + i + "n"
    else:
        _log.warning("bilinmeyen ek tipi %r — sözcük olduğu gibi döndü", ek_tipi)
        return s

    if sayi or kesme:
        return f"{s}'{ek}"          # özel ad / sayı: kesme + yumuşama YOK
    if ek_tipi in ("e", "i", "in") and not unlu_bitis:
        return _yumusat(s) + ek
    return s + ek
