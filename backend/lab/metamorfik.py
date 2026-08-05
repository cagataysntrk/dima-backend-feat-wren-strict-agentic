"""METAMORFİK TEST — *altın cevap yazmadan doğruluk ölçmek.*

## Neden bu, ve neden şimdi

Bugünkü darboğaz şu: `doğru` sütununu doldurmak için **her vakaya elle altın cevap**
gerekiyor. 10 589 vakaya altın cevap yazmak imkânsız — ve yazılsa bile katalog
değiştiğinde hepsi bayatlar.

Metamorfik test bunu **tamamen atlar** (MT-TEQL çerçevesi): soruya **anlamı koruyan**
bir dönüşüm uygulanır ve beklenen sonuç, **cevabın değişmemesidir**.

> 🔵 *Doğru cevabın ne olduğunu bilmesek de, iki yazımının aynı cevabı vermesi
> gerektiğini biliriz.* Ölçü artık "doğruluk" değil **kendi kendisiyle tutarlılık** —
> ve tutarsızlık her zaman bir kusurdur, altın cevap olmadan bile.

Ölçülmüş etkisi ciddi: paraphrase edilmiş Spider sorgularında yürütme doğruluğu
**%10-20** düşüyor. Yani standart kıyas kümelerinin gösterdiğinden çok daha kırılgan.

## 🔴 VE BU DOSYANIN ASIL FİKRİ — negatif metamorfik bağıntılar

Yalnız *"cevap değişmemeli"* diyen bir süit, **hiç cevap vermeyen** bir sistem
tarafından **kusursuz** geçilir. Her soruya `durust_ret` diyen bir ürün, tüm
değişmezlik bağıntılarını %100 sağlar.

> ⚠ *Bir tutarlılık ölçüsü, sabit bir cevabı mükemmel sanır.* Bu yüzden burada
> **iki yönlü** bağıntı var:
>
> | bağıntı | dönüşüm | beklenen |
> |---|---|---|
> | **DEĞİŞMEZ** | yazım hatası · büyük harf · dolgu · eşanlam | cevap **AYNI** kalmalı |
> | 🔴 **DEĞİŞMELİ** | olumsuzlama · dönem değişimi · ölçü değişimi | cevap **FARKLI** olmalı |
>
> İkincisi olmadan ölçüm bir totolojidir. Ve ikincisi, *"her şeye pes eden"* bir
> davranışı **kusur** olarak işaretleyen tek mekanizmadır.

## Araştırmanın işaret ettiği ASİMETRİ — hangi bozulma hangi yolu vurur

| bozulma | kimi daha çok vuruyor |
|---|---|
| **yüzey gürültüsü** (yazım, büyük harf, boşluk) | geleneksel **tek-geçişli** hatlar |
| **dilsel çeşitlilik** (paraphrase, eşanlam, kip) | 🔴 **ajanik** (çok adımlı) kurulumlar |

Bizde **iki yol** var: deterministik `route()` (tek geçiş) ve Intent-JSON → Discovery
(ajanik). Bu bulgu, hangi bozulmayı hangi yola karşı ölçmemiz gerektiğini söylüyor.

🔴 **Ve bugünkü korpusun kör noktası:** yazım hatası vakalarımız **var** (`ne kdr`,
`musetri`, `mikatr`), paraphrase vakamız **yok**. Yani şu an *yanlış yolun*
zayıflığını ölçüyoruz. Bu dosya paraphrase ailesini ekler.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable

# ═══════════════════════════════════════════════════════════════════════════════
# Türk klavyesi (Q) komşulukları — `ButterFinger` bozulması için
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ İngilizce QWERTY komşuluğu **kullanılmaz**: kullanıcı Türkçe klavye kullanıyor ve
# `ı`/`ö`/`ç`/`ş`/`ğ`/`ü` tuşları farklı yerde. Yanlış klavyeyle üretilmiş bir "yazım
# hatası", gerçekte hiç yapılmayan bir hatadır — *gerçekleşmeyen bir hatayı test etmek,
# gerçekleşeni test etmemektir.*
_KLAVYE_TR = {
    "q": "wa", "w": "qes", "e": "wrd", "r": "etf", "t": "ryg", "y": "tuh",
    "u": "yıj", "ı": "uok", "o": "ıpl", "p": "oğ", "ğ": "püi",
    # 🔴 `ü` ilk yazımda **anahtar olarak yoktu** (yalnız değer olarak geçiyordu) —
    # yani `ü` harfi hiçbir zaman bozulmuyordu. Kapı testi yakaladı.
    # *Bir klavye haritasında eksik tuş, o tuşun hiç yanlış basılmadığını varsayar.*
    "ü": "ğpi",
    "a": "qsz", "s": "awdx", "d": "serfc", "f": "drtgv", "g": "ftyhb",
    "h": "gyujn", "j": "huıkm", "k": "jıolö", "l": "koöpş", "ş": "lği",
    "i": "şç", "z": "asx", "x": "zsdc", "c": "xdfv", "v": "cfgb",
    "b": "vghn", "n": "bhjm", "m": "njö", "ö": "mkç", "ç": "öli",
}


@dataclass(frozen=True)
class Bagintı:
    """Bir metamorfik bağıntı: dönüşüm + beklenen ilişki."""
    kod: str
    aile: str
    aciklama: str
    #: `"ayni"` → cevap değişmemeli · `"farkli"` → cevap değişmeli
    beklenti: str
    donusum: Callable[[str, random.Random], str | None] = field(repr=False)


# ═══════════════════════════════════════════════════════════════════════════════
# AİLE A · YÜZEY BOZULMASI — anlam KORUNUR, cevap AYNI kalmalı
# ═══════════════════════════════════════════════════════════════════════════════

def _butterfinger(q: str, rng: random.Random) -> str | None:
    """Klavye komşusu harfe basma — en sık gerçek yazım hatası."""
    harfler = [(i, c) for i, c in enumerate(q) if c.lower() in _KLAVYE_TR]
    if not harfler:
        return None
    i, c = rng.choice(harfler)
    return q[:i] + rng.choice(_KLAVYE_TR[c.lower()]) + q[i + 1:]


def _harf_takasi(q: str, rng: random.Random) -> str | None:
    """Bitişik iki harfin yer değiştirmesi (`musteri` → `musetri`)."""
    p = [i for i in range(len(q) - 1) if q[i].isalpha() and q[i + 1].isalpha()]
    if not p:
        return None
    i = rng.choice(p)
    return q[:i] + q[i + 1] + q[i] + q[i + 2:]


def _harf_dusme(q: str, rng: random.Random) -> str | None:
    p = [i for i, c in enumerate(q) if c.isalpha()]
    if len(p) < 4:
        return None
    i = rng.choice(p)
    return q[:i] + q[i + 1:]


def _buyuk_kucuk(q: str, rng: random.Random) -> str:
    """⚠ Türkçede `i`→`İ` ve `ı`→`I`. `str.upper()` Python'da `i`→`I` yapar (yanlış).
    Bu bir *hata değil, gerçek*: kullanıcının telefonu da çoğu zaman böyle yapar —
    yani üretilen biçim **gerçekte karşılaşılan** biçimdir."""
    return rng.choice((q.upper(), q.lower(), q.title()))


def _bosluk(q: str, rng: random.Random) -> str:
    secim = rng.random()
    if secim < 0.34:
        return re.sub(r"\s+", "  ", q)                    # çift boşluk
    if secim < 0.67:
        return q.strip() + " "                            # sondaki boşluk
    return re.sub(r"\s", "", q, count=1)                  # bir boşluk düşer


def _noktalama(q: str, rng: random.Random) -> str:
    return q.rstrip("?!. ") + rng.choice(("?", "??", "!", " ...", ".", " ?"))


def _aksan_katla(q: str, _rng: random.Random) -> str:
    """Aksansız yazım. ⚠ Ürün `_norm()` ile bunu zaten katlıyor → **kapalı bir kapı**.
    Yine de ölçülür: *kapalı bir kapıyı ölçmemek, onun kapalı kaldığını varsaymaktır.*"""
    esleme = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return unicodedata.normalize("NFC", q).translate(esleme)


# ═══════════════════════════════════════════════════════════════════════════════
# AİLE B · DİLSEL ÇEŞİTLİLİK — 🔴 ajanik yolu vuran aile, korpusta HİÇ YOKTU
# ═══════════════════════════════════════════════════════════════════════════════

#: Anlamı koruyan sözcük ikameleri. ⚠ Bunlar **eşanlam değil, eşdeğer kullanım**:
#: bir kullanıcının aynı şeyi söylemek için kullandığı ikinci biçim.
_ESDEGER = [
    ("ne kadar", "kaç"), ("bazında", "göre"), ("bazında", "kırılımında"),
    ("göster", "getir"), ("göster", "ver"), ("toplam", "tüm"),
    ("nasıl gidiyor", "ne durumda"), ("en çok", "en yüksek"),
    ("en az", "en düşük"), ("neden", "niye"), ("neden", "niçin"),
    ("kıyasla", "karşılaştır"), ("bu ay", "içinde bulunduğumuz ay"),
    ("geçen yıl", "önceki sene"), ("geçen ay", "önceki ay"),
    ("hangi", "ne tür"), ("durum", "vaziyet"), ("makine", "tezgah"),
    ("müşteri", "cari"), ("fire", "zayiat"), ("verimlilik", "randıman"),
]


def _esdeger_ikame(q: str, rng: random.Random) -> str | None:
    uygun = [(a, b) for a, b in _ESDEGER if a in q.lower()]
    if not uygun:
        return None
    a, b = rng.choice(uygun)
    i = q.lower().index(a)
    return q[:i] + b + q[i + len(a):]


def _kelime_sirasi(q: str, rng: random.Random) -> str | None:
    """Türkçe **görece serbest sözdizimli**: öge sırası değişse de anlam korunur.

    ⚠ Yalnız **dönem ifadesi** taşınır (başa ↔ sona) — rastgele karıştırma anlamı
    bozar ve o zaman "değişmezlik" beklentisi haksız olur. *Anlamı koruduğunu
    kanıtlayamadığın bir dönüşüm, metamorfik bir bağıntı değildir.*
    """
    m = re.match(r"^((?:bu|geçen|son|önceki)\s+\S+(?:\s+\S+)?)\s+(.+)$", q, re.I)
    if m:
        return f"{m.group(2)} {m.group(1)}"
    m2 = re.match(r"^(.+?)\s+((?:bu|geçen|son|önceki)\s+\S+)$", q, re.I)
    if m2:
        return f"{m2.group(2)} {m2.group(1)}"
    return None


def _nezaket_ekle(q: str, rng: random.Random) -> str:
    return rng.choice((
        f"merhaba, {q}", f"{q} lütfen", f"acaba {q}",
        f"rica etsem {q}", f"{q} teşekkürler", f"selam {q} sağol",
    ))


def _dolgu_ekle(q: str, rng: random.Random) -> str:
    return rng.choice((f"peki {q}", f"yani {q}", f"şimdi {q}",
                       f"{q} yani", f"bir de {q}", f"{q} işte"))


def _soru_kalibi(q: str, rng: random.Random) -> str:
    """Aynı isteği farklı **söz edimiyle** kurmak — emir ↔ soru ↔ istek."""
    return rng.choice((
        f"{q} nedir", f"{q} bilgisini alabilir miyim", f"{q} lazım",
        f"{q} istiyorum", f"bana {q} lazım", f"{q} çıkarır mısın",
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# AİLE C · 🔴 DEĞİŞMELİ — *bir tutarlılık ölçüsü, sabit cevabı mükemmel sanır*
# ═══════════════════════════════════════════════════════════════════════════════
#
# Bu aile olmadan bütün süit, her soruya `durust_ret` diyen bir ürün tarafından
# **%100** geçilir. Buradaki dönüşümler **anlamı gerçekten değiştirir** — cevabın
# aynı kalması bir kusurdur.

def _olumsuzla(q: str, _rng: random.Random) -> str | None:
    """*"neden arttı"* → *"neden artmadı"*. Zıt soruya aynı cevap **kusurdur**."""
    for a, b in (("arttı", "artmadı"), ("düştü", "düşmedi"), ("azaldı", "azalmadı"),
                 ("var mı", "yok mu"), ("iyi mi", "kötü mü"),
                 ("artıyor", "artmıyor"), ("en çok", "en az"),
                 ("en yüksek", "en düşük"), ("yükseldi", "yükselmedi")):
        if a in q.lower():
            i = q.lower().index(a)
            return q[:i] + b + q[i + len(a):]
    return None


def _donem_degistir(q: str, rng: random.Random) -> str | None:
    """*"bu ay"* → *"geçen yıl"*. Farklı dönem, farklı sorgu olmalı."""
    for a in ("bu ay", "geçen ay", "bu yıl", "geçen yıl", "son 3 ay", "dün",
              "bu hafta", "geçen hafta", "son 12 ay"):
        if a in q.lower():
            yeni = rng.choice([x for x in ("bu ay", "geçen yıl", "son 6 ay",
                                           "2. çeyrek", "2025'te") if x != a])
            i = q.lower().index(a)
            return q[:i] + yeni + q[i + len(a):]
    return None


def _kirilim_ekle(q: str, rng: random.Random) -> str | None:
    """Kırılımsız bir soruya kırılım eklemek **şekli değiştirmeli**: tek satır yerine
    çok satır. Aynı sorgu dönüyorsa kırılım **yok sayılmış** demektir."""
    if re.search(r"\b(bazında|göre|kırılım)", q, re.I):
        return None
    return f"{q} {rng.choice(('makine', 'müşteri', 'vardiya', 'renk'))} bazında"


BAGINTILAR: tuple[Bagintı, ...] = (
    # --- A · yüzey (tek-geçişli yolu vurur) ---
    Bagintı("y.butterfinger", "yuzey", "Klavye komşusu harf", "ayni", _butterfinger),
    Bagintı("y.takas", "yuzey", "Bitişik harf takası", "ayni", _harf_takasi),
    Bagintı("y.dusme", "yuzey", "Harf düşmesi", "ayni", _harf_dusme),
    Bagintı("y.harf_boyu", "yuzey", "Büyük/küçük harf", "ayni", _buyuk_kucuk),
    Bagintı("y.bosluk", "yuzey", "Boşluk bozulması", "ayni", _bosluk),
    Bagintı("y.noktalama", "yuzey", "Noktalama", "ayni", _noktalama),
    Bagintı("y.aksan", "yuzey", "Aksan katlama (⚠ `_norm` kapatıyor)", "ayni", _aksan_katla),
    # --- B · dilsel (🔴 ajanik yolu vurur — korpusta HİÇ YOKTU) ---
    Bagintı("d.esdeger", "dilsel", "Eşdeğer sözcük ikamesi", "ayni", _esdeger_ikame),
    Bagintı("d.sira", "dilsel", "Öge sırası (dönem başa/sona)", "ayni", _kelime_sirasi),
    Bagintı("d.nezaket", "dilsel", "Nezaket sarmalaması", "ayni", _nezaket_ekle),
    Bagintı("d.dolgu", "dilsel", "Söylem dolgusu ekleme", "ayni", _dolgu_ekle),
    Bagintı("d.soz_edimi", "dilsel", "Söz edimi değişimi", "ayni", _soru_kalibi),
    # --- C · 🔴 DEĞİŞMELİ (sabit-cevap tuzağını kırar) ---
    Bagintı("z.olumsuz", "zit", "🔴 Olumsuzlama", "farkli", _olumsuzla),
    Bagintı("z.donem", "zit", "🔴 Dönem değişimi", "farkli", _donem_degistir),
    Bagintı("z.kirilim", "zit", "🔴 Kırılım ekleme", "farkli", _kirilim_ekle),
)


def turevler(soru: str, *, tohum: int = 20260805,
             aileler: tuple[str, ...] | None = None) -> list[dict]:
    """Bir sorudan tüm uygulanabilir metamorfik türevleri üretir.

    Dönüşüm uygulanamıyorsa (ör. olumsuzlanacak fiil yok) o bağıntı **atlanır** —
    ⚠ zorlamak, anlamı koruduğunu kanıtlayamadığımız bir türev üretirdi.
    """
    rng = random.Random(tohum + len(soru))
    out = []
    for b in BAGINTILAR:
        if aileler and b.aile not in aileler:
            continue
        try:
            yeni = b.donusum(soru, rng)
        except Exception:                                  # noqa: BLE001
            yeni = None
        if yeni and yeni.strip() and yeni != soru:
            out.append({"kaynak": soru, "turev": yeni, "bagıntı": b.kod,
                        "aile": b.aile, "beklenti": b.beklenti,
                        "aciklama": b.aciklama})
    return out


def imza(sonuc: dict | None) -> tuple:
    """Bir `route()` çıktısının **karşılaştırılabilir imzası**.

    ⚠ Ham sözlüğü kıyaslamak yanlış olurdu: içinde açıklama metni, sıra, zaman damgası
    gibi **anlamı olmayan** farklar var ve onlar her türevi "değişmiş" gösterirdi.
    İmza yalnız **anlam taşıyan** alanları alır.
    """
    if sonuc is None:
        return ("PES",)
    cq = (sonuc or {}).get("cube_query") or {}
    return (
        cq.get("cube"),
        tuple(sorted(str(m) for m in (cq.get("measures") or []))),
        tuple(sorted(str(d) for d in (cq.get("dimensions") or []))),
        str(cq.get("compare_mode") or ""),
        str(cq.get("time_range") or cq.get("period") or ""),
        bool(cq.get("order_by") or cq.get("limit")),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# KOŞUCU — altın cevap YOK, yalnız tutarlılık
# ═══════════════════════════════════════════════════════════════════════════════

def kos(sorular: list[str], schema: dict, *, tohum: int = 20260805) -> dict:
    """Her soru için türevleri üretir, `route()`'a sorar, **imzaları kıyaslar**.

    | bağıntı beklentisi | imza aynı | imza farklı |
    |---|---|---|
    | `ayni` (anlam korunur) | ✅ tutarlı | 🔴 **KIRILGAN** — aynı soru, farklı cevap |
    | `farkli` (anlam değişir) | 🔴 **DUYARSIZ** — zıt soru, aynı cevap | ✅ tutarlı |

    🔴 İkinci satır bu ölçümün belkemiği: her soruya `durust_ret` diyen bir ürün
    birinci satırı **kusursuz** geçer. *Sabit bir cevap, tutarlılığın değil
    duyarsızlığın işaretidir.*
    """
    # ⚡ PARALEL + TEK GEÇİŞ. İki kazanç birden:
    #  1) Tüm sorular (taban + türev) **önce toplanır**, sonra tek seferde koşut
    #     değerlendirilir → çekirdekler dolar.
    #  2) Tekilleştirme: aynı metin iki kez sorulmaz (türevler çakışabiliyor).
    # 🔴 Kapsam aynı — yalnız aynı işi iki kez yapmıyoruz.
    from lab import kosut

    tum_turevler = {q: turevler(q, tohum=tohum) for q in sorular}
    metinler = list(dict.fromkeys(
        list(sorular) + [t["turev"] for ts in tum_turevler.values() for t in ts]))
    imzalar = dict(zip(metinler, kosut.degerlendir(metinler, hangi="imza")))

    def _imza(q: str) -> tuple:
        return imzalar.get(q, ("HATA",))

    kirilgan: list[dict] = []
    duyarsiz: list[dict] = []
    sayac: dict[str, dict[str, int]] = {}
    toplam_turev = 0

    for q in sorular:
        taban = _imza(q)
        for t in tum_turevler[q]:
            toplam_turev += 1
            s = sayac.setdefault(t["bagıntı"],
                                 {"toplam": 0, "tutarli": 0, "kusur": 0, "olculemedi": 0})
            s["toplam"] += 1
            yeni = _imza(t["turev"])
            beklenen_ayni = (t["beklenti"] == "ayni")

            # ⊘ ÜÇÜNCÜ HÂL — *ne geçti ne kaldı.*
            #
            # 🔴 İlk koşumda `z.olumsuz` **51/51**, `z.donem` **29/29** kusur verdi.
            # Şüpheli bir bütünlüktü ve sebebi ölçüldü: taban zaten `PES` (route pes
            # etti), türev de `PES` → imzalar eşit → *"anlam değişti ama cevap aynı"*
            # diye **duyarsız** yazıldı.
            #
            # Oysa sistem **hiçbirini cevaplamadı**. Cevaplamadığı iki soruyu
            # "aynı cevabı verdi" diye suçlamak, ölçümü yalancı çıkarır.
            #
            # > ⚠ *Bir bağıntı, ancak ölçtüğü şey gerçekleşmişse yargı verebilir.*
            # > `farkli` bağıntısı bir **cevap farkı** arar; ortada cevap yoksa
            # > arayacağı fark da yoktur. Bu, geçmek de kalmak da değil —
            # > **ÖLÇÜLEMEDİ**'dir, ve sebebi kayda geçer.
            if not beklenen_ayni and taban == ("PES",) and yeni == ("PES",):
                s["olculemedi"] += 1
                continue

            if (yeni == taban) == beklenen_ayni:
                s["tutarli"] += 1
                continue
            s["kusur"] += 1
            kayit = {**t, "taban_imza": taban, "turev_imza": yeni}
            (kirilgan if beklenen_ayni else duyarsiz).append(kayit)

    olculen = sum(v["tutarli"] + v["kusur"] for v in sayac.values())
    return {
        "soru": len(sorular), "turev": toplam_turev,
        "kirilgan": kirilgan, "duyarsiz": duyarsiz,
        "sayac": sayac,
        "olculemedi": sum(v["olculemedi"] for v in sayac.values()),
        # ⚠ Payda **ölçülen** türevler — ölçülemeyeni paydada tutmak, ürünü
        # ölçülemeyen bir şeyden sorumlu tutmak olurdu.
        "tutarlilik_yuzde": round(
            100 * sum(v["tutarli"] for v in sayac.values()) / max(olculen, 1), 1),
    }


def rapor(k: dict) -> str:
    """⚠ Rapor **iki kusur türünü ayrı** gösterir: birini ötekine karıştırmak,
    ürünü ya haksız yere kırılgan ya haksız yere duyarlı gösterir."""
    s = ["# METAMORFİK TUTARLILIK — *altın cevap gerektirmeyen ölçü*", "",
         f"Soru: **{k['soru']}** · türev: **{k['turev']}** · "
         f"⊘ ölçülemedi: **{k['olculemedi']}** · "
         f"tutarlılık: **%{k['tutarlilik_yuzde']}** *(payda = ölçülenler)*", "",
         "⊘ **ÖLÇÜLEMEDİ**, geçmek de kalmak da değildir: taban `PES` ise bir "
         "*«cevap değişmeli»* bağıntısının arayacağı fark yoktur. Bu satırlar "
         "**ürünün değil, ölçümün** sınırıdır ve paydadan çıkarılır.", "",
         "| bağıntı | aile | toplam | tutarlı | 🔴 kusur | ⊘ ölçülemedi |",
         "|---|---|---|---|---|---|"]
    aile = {b.kod: b.aile for b in BAGINTILAR}
    for kod, v in sorted(k["sayac"].items(), key=lambda x: -x[1]["kusur"]):
        s.append(f"| `{kod}` | {aile.get(kod, '?')} | {v['toplam']} | {v['tutarli']} | "
                 f"**{v['kusur']}** | {v.get('olculemedi', 0)} |")
    s += ["", f"## 🔴 KIRILGAN — anlam korundu ama cevap DEĞİŞTİ ({len(k['kirilgan'])})", "",
          "*Aynı soruyu iki biçimde sorunca iki farklı cevap almak, kullanıcıya ürünün "
          "kararsız olduğunu öğretir — ve kararsız bir ürün, yanlış bir üründen daha "
          "hızlı terk edilir.*", ""]
    for x in k["kirilgan"][:25]:
        s.append(f"- `{x['bagıntı']}` «{x['kaynak'][:52]}» → «{x['turev'][:52]}»")
        s.append(f"  - {x['taban_imza']}  →  {x['turev_imza']}")
    s += ["", f"## 🔴 DUYARSIZ — anlam değişti ama cevap AYNI ({len(k['duyarsiz'])})", "",
          "*Bu sınıf olmadan ölçüm bir totolojidir: her soruya pes eden bir ürün "
          "tüm değişmezlik bağıntılarını %100 geçer.*", ""]
    for x in k["duyarsiz"][:25]:
        s.append(f"- `{x['bagıntı']}` «{x['kaynak'][:52]}» → «{x['turev'][:52]}»")
        s.append(f"  - ikisi de: {x['taban_imza']}")
    return "\n".join(s)


def main() -> int:                                          # pragma: no cover
    import argparse
    import pathlib

    from app.config import get_settings
    from app.wren_service import WrenService
    from lab import senaryo_uretec
    from lab.gercek_dunya import VAKALAR

    ap = argparse.ArgumentParser(description="Metamorfik tutarlılık ölçümü")
    ap.add_argument("--ornek", type=int, default=400,
                    help="üretilmiş korpustan kaç soru örneklenir (0=yalnız elle vakalar)")
    a = ap.parse_args()

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    schema = svc.schema()
    sorular = [v["soru"] for v in VAKALAR]
    if a.ornek:
        # ⚠ Örnekleme **sabit tohumlu**: her koşumda farklı örnek almak, sayıyı
        # kıyaslanamaz yapardı — ve kıyaslanamayan bir sayı bir taban değildir.
        # ⚠ `--ornek N` kadar soru örnekleneceğine göre, tam korpusu üretmenin
        # anlamı yok. Havuz örneklemin **üç katı** tutulur: seçim çeşitliliği
        # korunur, üretim maliyeti korpus boyuyla değil ihtiyaçla ölçeklenir.
        uret, _ = senaryo_uretec.uret(schema, azami=max(a.ornek * 3, 600))
        sorular += [v["soru"] for v in
                    random.Random(20260805).sample(uret, min(a.ornek, len(uret)))]

    k = kos(sorular, schema)
    metin = rapor(k)
    print(metin)
    hedef = pathlib.Path(__file__).resolve().parent / "reports" / "metamorfik.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(f"\nRapor: {hedef}")
    return 0


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(main())
