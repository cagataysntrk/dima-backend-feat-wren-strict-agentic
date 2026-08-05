"""SENARYO ÜRETECİ — *elle vaka yazımı burada biter.*

## Neden üreteç, neden elle değil

Elle yazılmış korpus üç şeyi birden yapamaz: **büyük** olmak, **kopyasız** olmak ve
kataloğun büyümesine **kendiliğinden** ayak uydurmak. `gercek_dunya.VAKALAR` 42 vakada
bunların üçünü de zorluyordu — ve her yeni cube'da elle 20 satır daha yazmak gerekiyordu.

> ⚠ *Elle yazılan bir korpus, yazarının hayal gücü kadar çeşitlidir; üretilmiş bir
> korpus, kataloğun kendisi kadar çeşitlidir.* İkincisi ölçülebilir, birincisi değil.

## 🔴 Neden TAM ÇARPIM DEĞİL — pairwise covering array

Eksenler: **23 cube × 81 ölçü × 10 niyet × 6 söyleyiş × 12 dönem**. Tam çarpım
**yüz binlerce** vaka eder ve neredeyse hepsi birbirinin kopyasıdır — çünkü bir kusur
tipik olarak **tek bir eksenden ya da iki eksenin ETKİLEŞİMİNDEN** doğar, beşinin
aynı anda kesişmesinden değil.

Bu, yazılım testinde çözülmüş bir problem: **kombinatoryal test tasarımı**. Ampirik
bulgu (NIST'in hata-etkileşim çalışmaları) şudur: kusurların büyük çoğunluğu **en çok
iki** parametrenin etkileşimiyle tetiklenir. Dolayısıyla **her İKİLİ kombinasyonu**
kapsayan bir dizi, tam çarpımın kapsamını pratikte yakalar — ama boyu `O(v²)`'dir,
`O(vᵏ)` değil.

| yaklaşım | vaka sayısı | ikili kapsam |
|---|---|---|
| tam çarpım | ~1 300 000 | %100 |
| rastgele N örnekleme | N | ölçülmez, dalgalı |
| **pairwise (bu dosya)** | **binler** | **%100, kanıtlı** |

Ve kapsamın kendisi **raporlanır** (`kapsam_raporu`): *bir korpusun büyüklüğü kapsam
değildir; kapsam ancak ölçülürse kapsamdır.*

## Beklenen davranış KURALDAN türetilir, elle etiketlenmez

Her vakanın `kabul` listesi, sorunun **yapısından** çıkar:

| koşul | beklenen |
|---|---|
| ölçü adı ≥2 cube'un sinonimi | `netlestirme` — belirsizlik **deterministik olarak biliniyor** |
| niyet = karar/tahmin (K5) | `durust_ret` — v1'de forecast/öneri **yok** |
| gürültü / kapsam dışı | `durust_ret` |
| ölçü tek sahipli + dönem var | `dogru` |

*Elle etiketlenen bir beklenti, yazarın o günkü kanaatidir; kuraldan türetilen beklenti
kataloğun kendi gerçeğidir ve katalog değişince kendiliğinden güncellenir.*

## ⚠ ÖLÇÜM ARACININ ÜRÜNLE AYNI YOLU İZLEMESİ — iki turda çözüldü

Bir denetim ajanı önce *"araç ham metin veriyor, ürün `_norm()` uyguluyor"* dedi.
Normalize eden bir sarmalayıcı yazdım. Sonra **çağrı satırını okudum**:

```
ask.py:2473   route_hit = cube_router.route(body.question, schema, ...)
```

Ürün de **ham** soruyu geçiyor. Yani normalize etmek aracı ürüne yaklaştırmıyor,
**uzaklaştırıyordu**. Ajan ikinci turda kendi bulgusunu düzeltti; ben de sarmalayıcıyı
geri aldım.

> 🔴 *Bir aracın ürünle aynı yolu izlediği iddia edilmez — çağrı satırı okunarak
> görülür.* Ve bu deponun defterindeki **"ölçüm aracının kendisi de bir bağımlılıktır"**
> sınıfı, bu kez ölçüm aracını **düzeltirken** tekrarlandı.

## 🔴 CANLI TURDAN GELEN İKİ SINIF — ilk turda YOKTU

Kullanıcı iki gerçek kusur bildirdi ve *"testler bunları yakalar mı"* diye sordu.
Cevap **hayırdı**, ve ikisi de eksen olarak eklendi:

| canlı kusur | eksik olan eksen | eklenen |
|---|---|---|
| `mart cirosunu **şubata** göre kıyasla` → *"«subata» kısmını anlayamadım"* | ay adının **çekimli** hâli | `DONEMLER` + 12 ay × 5 durum eki = **60 form** |
| `…verimliliğini ciro **üzerindeki etkisini ölç yani** kıyasla` | iki-ölçü **ilişkisi** · söylem dolgusu · emir kipi | `NIYET_ETKI` · `NIYET_KOMPOZISYON` · `DOLGULAR` ekseni |

*Bir korpusun değeri, ürettiği vaka sayısında değil, gerçek bir kusurun sınıfını
üretebilmesindedir. Üretemiyorsa o kusur, ne kadar büyürse büyüsün, görünmez kalır.*
"""

from __future__ import annotations

import itertools
import random
import unicodedata
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# EKSEN 1 · NİYET — kullanıcının ne İSTEDİĞİ (SQL zorluğu değil, İŞ zorluğu)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Agent Bain/McKinsey kıyaslamasının ayrımı: SQL karmaşıklığı ile iş karmaşıklığı
# **farklı eksenlerdir**. `SUM(x)` basit SQL'dir ama *"iyi mi kötü mü"* sorusu bir
# eşik/yargı ister — v1'de olmayan bir şey. Zorluk buradan gelir, JOIN sayısından değil.
#
# Her niyet: (kod, kademe, şablon üreteci, beklenen sınıf kuralı)

NIYET_DEGER = "deger"           # "bu ay ciro"
NIYET_KIRILIM = "kirilim"       # "müşteri bazında ciro"
NIYET_USTUNLUK = "ustunluk"     # "en çok satan müşteri"
NIYET_KIYAS = "kiyas"           # "geçen aya göre"
NIYET_TREND = "trend"           # "son 6 ay nasıl gitti"
NIYET_KATKI = "katki"           # "düşüşte kimin payı var"
NIYET_NEDEN = "neden"           # "neden arttı"
NIYET_ESIK = "esik"             # "hedefin neresindeyiz"
NIYET_KARAR = "karar"           # "ne yapmalıyız"  → v1'de YOK
NIYET_TAHMIN = "tahmin"         # "yılı nerede kapatırız" → v1'de YOK
NIYET_YETENEK = "yetenek"       # "neler yapabilirsin"
NIYET_GURULTU = "gurultu"       # "asdf" / "fıkra anlat"
# 🔴 CANLI TURDA ÖLÇÜLEN İKİ SINIF — üretecin ilk turunda YOKTU, eklendi.
NIYET_ETKI = "etki"             # "A'nın B üzerindeki etkisi"  → İKİ ölçü, İLİŞKİ
NIYET_KOMPOZISYON = "kompozisyon"   # "A ve B'yi birlikte göster" → İKİ ölçü, TOPLAM
# 🔴 KAPSAM KAPISININ AÇTIĞI ÜÇ DELİK — hiçbiri üretilmiyordu
NIYET_OLUMSUZ = "olumsuz"       # "neden düşmedi" · "X hariç"
NIYET_COKLU_SORU = "coklu_soru" # "ciro ne kadar, fire nasıl"  → tek mesaj, iki soru
NIYET_COK_KIRILIM = "cok_kirilim"   # "makine ve vardiya bazında"

#: Niyet → zorluk kademesi. ⚠ Kademe **niyetten türetilir**, elle atanmaz — aynı
#: niyetin iki vakası farklı kademede olamaz, yoksa merdiven anlamını yitirir.
NIYET_KADEME = {
    NIYET_DEGER: "K1", NIYET_GURULTU: "K1", NIYET_YETENEK: "K1",
    NIYET_KIRILIM: "K2", NIYET_USTUNLUK: "K2",
    NIYET_KIYAS: "K3", NIYET_TREND: "K3",
    NIYET_KATKI: "K4", NIYET_NEDEN: "K4", NIYET_ESIK: "K4",
    # ⚠ Kompozisyon K2 (iki ölçüyü yan yana koymak), ETKİ ise K4 — ikisi aynı şey
    # DEĞİL: biri toplama, öteki NEDENSELLİK ister. Aynı kademeye koymak, ürünün
    # birini yapıp ötekini yapamadığını görünmez kılardı.
    NIYET_KOMPOZISYON: "K2", NIYET_ETKI: "K4",
    NIYET_COK_KIRILIM: "K2", NIYET_OLUMSUZ: "K3", NIYET_COKLU_SORU: "K3",
    NIYET_KARAR: "K5", NIYET_TAHMIN: "K5",
}

#: 🔴 v1'de YAPISAL OLARAK OLMAYAN yetenekler. Bunları soran bir vaka **dürüst ret**
#: bekler — ve bu bir kusur değil, **beyan edilmiş bir sınır**dır.
#: *Olmayan bir yeteneği test etmemek onu var saymaktır; test edip başarısız saymak
#: ise ölçümü yalancı çıkarır. Doğrusu: sınırı beklenti olarak yazmak.*
#: ⚠ `NIYET_ETKI` de buraya girer ve **gerekçesi belgelidir**: MIMARI §9.2 + B1 notu,
#: kompozisyonun evinin **takip yolu** olduğunu, taze soruda iki ölçünün R1/R10 verdiğini
#: ölçmüş. Yani *"A'nın B üzerindeki etkisi"* taze soruda **yapısal olarak** yok.
#: *Olmayan bir yeteneği başarısızlık saymak ölçümü yalancı çıkarır; beklenti olarak
#: yazmak ise sınırı görünür kılar — ve sınır görünürse kapatılabilir.*
V1_DISI_NIYETLER = frozenset({NIYET_KARAR, NIYET_TAHMIN, NIYET_ETKI})


# ═══════════════════════════════════════════════════════════════════════════════
# EKSEN 2 · SÖYLEYİŞ KAYDI — aynı sorunun gerçek insan ağzındaki hâlleri
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 Katalog korpusunun **yazılı körlüğü** tam burada: soruları katalogdan ürettiği
# için hepsi **doğru yazılmış** ve **tam cümle**. Gerçek kullanıcı böyle yazmaz.

KAYIT_RESMI = "resmi"           # "müşteri bazında satış tutarı"
KAYIT_KONUSMA = "konusma"       # "müşterilere göre ne kadar sattık"
KAYIT_KISALTMA = "kisaltma"     # "bu ayki ciro ne kdr"
KAYIT_YAZIM = "yazim"           # "musetri bazinda cro"
KAYIT_ELIPTIK = "eliptik"       # "peki müşteri bazında"
KAYIT_ARGO = "argo"             # "tezgahta durum ne alemde"

KAYITLAR = (KAYIT_RESMI, KAYIT_KONUSMA, KAYIT_KISALTMA,
            KAYIT_YAZIM, KAYIT_ELIPTIK, KAYIT_ARGO)

# ═══════════════════════════════════════════════════════════════════════════════
# EKSEN 2b · SÖYLEM DOLGUSU ve EMİR KİPİ — 🔴 canlı turda ölçülen engelleyiciler
# ═══════════════════════════════════════════════════════════════════════════════
#
# Canlı vaka: *"…etkisini ölç **yani** kıyasla"* → engelleyen kelimeler arasında
# **`yani`** ve **`olc`** vardı. İkisi de anlam taşımaz: biri düşünceyi düzelten bir
# bağlaç, öteki bir emir kipi fiil. Ama ikisi de kapsam kapısına takılıyor.
#
# > ⚠ Bunlar `KAYITLAR`dan **ayrı bir eksen**dir, çünkü her kayıtla birlikte
# > görünebilirler: resmî bir cümlede de *"hesapla"* olur, argoda da *"yani"* olur.
# > Kayıt eksenine karıştırmak, ikisinin **etkileşimini** ölçülemez yapardı — ve
# > pairwise'ın tüm değeri etkileşimi ölçmesindedir.

DOLGU_YOK = ""
#: ⚠ ATIF (anafora) dolgu önekine katıldı — kapsam kapısı `s.anafora`yı **1 vakada**
#: buldu. Bir özelliğin "kapsanıyor" görünmesi yetmez: tek vaka, o sınıfta bir kusuru
#: yakalamak için **istatistiksel olarak sıfıra yakın** bir şanstır.
#: *Sıfır kapsam bir delik, bir kapsam bir yanılsamadır.*
_DOLGU_ONEK = ("peki", "yani", "bir de", "hani", "şimdi", "bak", "e",
               "bunu", "şunu", "az önceki", "demin dediğin", "yukarıdaki")
_EMIR_FIIL = ("ölç", "kıyasla", "hesapla", "getir", "göster", "ver", "çıkar", "listele")

DOLGULAR = (DOLGU_YOK, "onek", "emir", "onek+emir")


# ═══════════════════════════════════════════════════════════════════════════════
# EKSEN 2c · YÜZEY BİÇİMİ — 🔴 kapsam kapısının açtığı dört delik
# ═══════════════════════════════════════════════════════════════════════════════
#
# `dil_ozellikleri.kapsam_olc()` dört yazım özelliğinin **hiç üretilmediğini** söyledi:
# boşluk hatası · büyük harf · noktalama · sayı biçimi. Dördü de gerçek kullanıcıda
# sık; hiçbiri korpusta yoktu.
#
# > ⚠ *Bir korpusun 9000 vakaya çıkması, kapsamının arttığı anlamına gelmez.* Dokuz bin
# > vaka aynı dört biçimi tekrarlıyorsa, beşincisi hâlâ görünmez. Sayı kapsam değildir.

BICIM_DUZ = ""
BICIMLER = (BICIM_DUZ, "bosluk", "buyuk", "noktalama", "sayi")

_BOSLUK_HATASI = {
    "ne kadar": "nekadar", "kaç tane": "kactane", "bu ay": "bu ay ki",
    "her hangi": "herhangi", "bir kaç": "birkaç", "nasıl": "nasil bir",
}


def _bicim_uygula(soru: str, bicim: str, rng: random.Random) -> str:
    if bicim == BICIM_DUZ:
        return soru
    if bicim == "bosluk":
        for dogru, hatali in _BOSLUK_HATASI.items():
            if dogru in soru:
                return soru.replace(dogru, hatali, 1)
        # Hiçbiri geçmiyorsa rastgele bir kelimeyi ikiye böl — boşluk hatası budur.
        p = soru.split()
        if len(p) > 1:
            j = max(range(len(p)), key=lambda k: len(p[k]))
            if len(p[j]) > 5:
                p[j] = p[j][:3] + " " + p[j][3:]
        return " ".join(p)
    if bicim == "buyuk":
        # ⚠ `upper()` DEĞİL: gerçek kullanıcı ya hepsini büyük yazar ya da Caps Lock
        # yarıda kalır. İkincisi daha sık ve daha zorlayıcı.
        return soru.upper() if rng.random() < 0.5 else soru[:len(soru) // 2].upper() + soru[len(soru) // 2:]
    if bicim == "noktalama":
        return soru + rng.choice(("??", "!!!", " ...", " ?!", " 🙏", " 📊"))
    # sayı biçimi — Türk yazımı (binlik nokta, ondalık virgül)
    return soru + rng.choice((" 1.000,50 üstü", " 1,5 milyon üzeri", " 100 ile 200 arasında",
                              " 50.000 altı", " %15 üzeri"))


def _dolgu_uygula(soru: str, dolgu: str, rng: random.Random) -> str:
    if dolgu == DOLGU_YOK:
        return soru
    if dolgu == "onek":
        return f"{rng.choice(_DOLGU_ONEK)} {soru}"
    if dolgu == "emir":
        return f"{soru} {rng.choice(_EMIR_FIIL)}"
    return f"{rng.choice(_DOLGU_ONEK)} {soru} {rng.choice(_EMIR_FIIL)} yani {rng.choice(_EMIR_FIIL)}"

#: Kısaltma sözlüğü — **gözlemlenmiş** kısaltmalar (uydurma değil): saha kullanıcısı
#: telefondan yazarken bunları kullanıyor.
_KISALTMALAR = {
    "ne kadar": "ne kdr", "kaç": "kc", "bazında": "bznd", "müşteri": "mşt",
    "ortalama": "ort", "toplam": "tpl", "geçen": "gçn", "makine": "mkn",
    "vardiya": "vrd", "üretim": "ürtm", "değil": "dgl", "için": "icn",
}

#: Üretim sahasının argosu — **katalogda geçmez**, kullanıcı ağzında geçer.
_ARGO = {
    "makine": "tezgah", "üretim": "iş", "duruş": "makine yattı",
    "fire": "zayiat", "verimlilik": "randıman", "personel": "eleman",
    "müşteri": "cari", "sipariş": "iş emri", "arıza": "makine bozuldu",
    "nasıl": "ne alemde", "durum": "vaziyet",
}


def _yazim_boz(kelime: str, rng: random.Random) -> str:
    """🔴 Yazım hatası **ölçülebilir** olmalı: rastgele harf değil, **gerçek**
    klavye/dizgi hatası desenleri.

    ⚠ Aksan kaldırma BİLEREK YOK: ürün `_norm()` ile aksanı zaten katlıyor, yani
    *"gecen hafta"* ile *"geçen hafta"* onun için aynı. Aksanı bir hata sanmak,
    kapalı bir kapıyı test etmek olurdu. Ölçülen gerçek hata **harf devrikliği**
    (musteri→musetri) ve **harf düşmesi** (miktar→mikatr).
    """
    if len(kelime) < 5:
        return kelime
    i = rng.randrange(1, len(kelime) - 2)
    tur = rng.choice(("devrik", "dusme", "cift"))
    if tur == "devrik":                                   # bitişik iki harf yer değiştirir
        return kelime[:i] + kelime[i + 1] + kelime[i] + kelime[i + 2:]
    if tur == "dusme":                                    # bir harf düşer
        return kelime[:i] + kelime[i + 1:]
    return kelime[:i] + kelime[i] + kelime[i:]            # bir harf çiftlenir


def _kayit_uygula(soru: str, kayit: str, rng: random.Random) -> str:
    """Bir soruyu verilen söyleyiş kaydına çevirir."""
    if kayit == KAYIT_RESMI:
        return soru
    if kayit == KAYIT_KISALTMA:
        for uzun, kisa in _KISALTMALAR.items():
            soru = soru.replace(uzun, kisa)
        return soru
    if kayit == KAYIT_ARGO:
        for resmi, argo in _ARGO.items():
            soru = soru.replace(resmi, argo)
        return soru
    if kayit == KAYIT_YAZIM:
        kelimeler = soru.split()
        if not kelimeler:
            return soru
        # ⚠ TEK kelime bozulur: iki bozuk kelime, hangisinin kapıyı kapattığını
        # ayırt edilemez yapar — *bir testin teşhis gücü, değişkenlerinin azlığıyla artar.*
        j = max(range(len(kelimeler)), key=lambda k: len(kelimeler[k]))
        kelimeler[j] = _yazim_boz(kelimeler[j], rng)
        return " ".join(kelimeler)
    if kayit == KAYIT_ELIPTIK:
        # Eksik cümle: ilk iki kelime düşer, başa bir bağlaç gelir.
        parcalar = soru.split()
        govde = " ".join(parcalar[2:]) if len(parcalar) > 3 else soru
        return f"{rng.choice(('peki', 'bir de', 'ya', 'e', 'hadi'))} {govde}"
    # KAYIT_KONUSMA — soru kalıbını konuşma diline çevirir.
    return soru.replace(" bazında", "lere göre").replace("toplam ", "ne kadar ")


# ═══════════════════════════════════════════════════════════════════════════════
# EKSEN 3 · DÖNEM İFADESİ
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ Boş dönem (`""`) BİLEREK var: dönemsiz soru ürünün *dönem kapısına* düşer ve
# *"hangi dönem?"* diye sorar. Bu bir kusur değil davranıştır — ve ölçülmesi gerekir.

_DONEM_YALIN = (
    "", "bu ay", "geçen ay", "bu yıl", "geçen yıl", "son 3 ay", "son 6 ay",
    "son 12 ay", "2. çeyrek", "3. çeyrek", "yılbaşından bugüne", "2025'te",
    "geçen hafta", "dün", "bu hafta",
    # 🔴 YALIN AY — kapsam kapısı yakaladı: çekimli hâlleri eklerken yalın hâli
    # **düşürmüşüm**. *Bir eksiği kapatırken komşusunu açmak, düzeltmenin en sık
    # görülen yan etkisidir* — ve ancak kapsam ölçülürse görülür.
    "ocak ayında", "mart ayı", "haziran", "aralık ayında",
    # Dönem ARALIĞI — iki ucu olan ifade
    "ocaktan marta", "nisan-haziran arası", "mayıstan bugüne",
)

#: 🔴 AY ADININ ÇEKİMLİ HÂLLERİ — canlı turda ölçülmüş kusur sınıfı.
#:
#: Kullanıcı *"mart cirosunu **şubata** göre kıyasla"* yazdı; sistem *"«subata»
#: kısmını anlayamadım"* dedi. Ay **biliniyordu**, **eki** tanınmadı.
#:
#: > ⚠ Ve bu kombinatoryal olarak büyük bir delik: 12 ay × 5 durum eki = **60 form**,
#: > ve korpus bunların **hiçbirini** sormuyordu — çünkü katalogdan üretilen sorular
#: > ayı hep yalın yazıyor. *Bir ekseni yalın hâlleriyle örneklemek, o eksenin
#: > çekimli yarısını ölçülmemiş bırakır.*
_AYLAR = ("ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
          "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık")

#: Türkçe durum ekleri — ünlü uyumuna göre iki biçim. ⚠ Ek listesi **elle küratörlü
#: bir sözlük değil**, dilin düzenli çekimi: her ay adına aynı kural uygulanır.
_EK_KALIPLARI = (
    ("a", "e"),        # yönelme:   şubata / eylüle      → "şubata göre"
    ("ta", "te"),      # bulunma:   martta / eylülde     → "martta ne oldu"
    ("tan", "ten"),    # ayrılma:   marttan / eylülden   → "marttan beri"
    ("la", "le"),      # birliktelik: ocakla / eylülle   → "ocakla kıyasla"
    ("ın", "in"),      # tamlayan:  martın / eylülün     → "martın cirosu"
)
_KALIN = set("aıou")


def _ay_cekimle(ay: str, kalip: tuple[str, str]) -> str:
    """Ay adına durum eki ekler — **büyük ünlü uyumuna** göre.

    ⚠ Yumuşama/ünsüz benzeşmesi tam modellenmiyor (*şubatta* vs *şubata*): amaç
    dilbilgisel mükemmellik değil, **kullanıcının yazdığı biçimleri üretmek**.
    Kullanıcı da her zaman doğru yazmıyor — ve tam da bu yüzden ölçülüyor.
    """
    son_unlu = next((h for h in reversed(ay) if h in "aeıioöuü"), "a")
    return ay + (kalip[0] if son_unlu in _KALIN else kalip[1])


_DONEM_CEKIMLI = tuple(_ay_cekimle(ay, kalip)
                       for ay in _AYLAR for kalip in _EK_KALIPLARI)

DONEMLER = _DONEM_YALIN + _DONEM_CEKIMLI

# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 DÖNEM **SINIFI** — eksen patlamasının çözümü
# ═══════════════════════════════════════════════════════════════════════════════
#
# ## Ölçülen problem
#
# `donem` ekseni 82 değer taşıyordu (15 yalın + 60 çekimli + 7 aralık). Pairwise'ın
# boyu **en büyük iki eksenin çarpımı** kadardır: 135 ölçü × 82 dönem = **11 070**
# ikili → korpus 10 589 vakaya şişti ve koşumu **~70 sn** sürdü.
#
# ## Ama o çarpım gereksiz — ve nedeni yapısal
#
# *"`şubata` çekimi tanınıyor mu"* sorusu **hangi ölçüyle sorulduğuna bağlı değildir**:
# dönem çözümlemesi ölçü eşleştirmesinden **ayrı bir mekanizma** (`_period_hit_words`
# vs `_match_measure`). Yani 135 ölçünün her biriyle 60 ay çekimini denemek, aynı
# mekanizmayı 8 100 kez sınamaktır.
#
# > ⚠ *Bir kombinasyon, iki eksen gerçekten etkileşiyorsa gereklidir.* Etkileşmeyen
# > iki ekseni çaprazlamak kapsam üretmez — yalnız süre üretir. Ve **uzun bir kapı,
# > atlanan bir kapıya dönüşür**.
#
# ## Çözüm: dönem **sınıfı** eksene girer, somut biçim içinden döner
#
# Pairwise `donem_sinifi` (7 değer) üzerinden kurulur; her vakada o sınıftan somut bir
# biçim **sırayla** seçilir. Böylece 60 ay çekiminin **hepsi** yine üretilir (kapsam
# korunur, `dil_ozellikleri` kapısı bunu sınıyor) ama pairwise 135 × 7 = **945** ikiliye
# iner. *Kapsam kaybolmuyor — kombinasyon kayboluyor, ki zaten anlamsızdı.*

DS_YOK = "yok"
DS_GORELI = "goreli"        # bu ay · geçen yıl · son 3 ay
DS_AY_YALIN = "ay_yalin"    # ocak ayında · haziran
DS_AY_CEKIMLI = "ay_cekimli"  # 🔴 şubata · ocakla · martta — CANLI KUSUR
DS_CEYREK = "ceyrek"        # 2. çeyrek · yılbaşından bugüne
DS_YIL = "yil"              # 2025'te
DS_ARALIK = "aralik"        # ocaktan marta

DONEM_SINIFLARI = (DS_YOK, DS_GORELI, DS_AY_YALIN, DS_AY_CEKIMLI,
                   DS_CEYREK, DS_YIL, DS_ARALIK)

_SINIF_BICIMLERI: dict[str, tuple[str, ...]] = {
    DS_YOK: ("",),
    DS_GORELI: ("bu ay", "geçen ay", "bu yıl", "geçen yıl", "son 3 ay", "son 6 ay",
                "son 12 ay", "geçen hafta", "dün", "bu hafta"),
    DS_AY_YALIN: ("ocak ayında", "mart ayı", "haziran", "aralık ayında"),
    DS_AY_CEKIMLI: _DONEM_CEKIMLI,          # 🔴 altmışının HEPSİ sırayla dönüyor
    DS_CEYREK: ("2. çeyrek", "3. çeyrek", "yılbaşından bugüne"),
    DS_YIL: ("2025'te",),
    DS_ARALIK: ("ocaktan marta", "nisan-haziran arası", "mayıstan bugüne"),
}


class _SinifSayaci:
    """Her dönem sınıfı için somut biçimleri **sırayla** dolaştırır.

    ⚠ Rastgele seçim yerine **döngüsel**: rastgelelikte 60 ay çekiminin bazıları hiç
    seçilmeyebilir ve `dil_ozellikleri` kapısı sessizce zayıflar. Döngüsel seçim,
    yeterli vaka üretildiğinde **hepsinin** görünmesini garanti eder.
    """

    def __init__(self) -> None:
        self._i: dict[str, int] = {k: 0 for k in _SINIF_BICIMLERI}

    def al(self, sinif: str) -> str:
        bicimler = _SINIF_BICIMLERI[sinif]
        d = bicimler[self._i[sinif] % len(bicimler)]
        self._i[sinif] += 1
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# NİYET ŞABLONLARI — soru gövdesini kurar
# ═══════════════════════════════════════════════════════════════════════════════

def _sablon(niyet: str, olcu: str, boyut: str | None, donem: str,
            rng: random.Random, olcu2: str | None = None) -> str:
    d = f"{donem} " if donem else ""
    b = boyut or "makine"
    o2 = olcu2 or "ciro"
    if niyet == NIYET_ETKI:
        # 🔴 CANLI VAKA: "…verimliliğini ciro üzerindeki etkisini ölç yani kıyasla"
        # Üç şey aynı anda: iki ölçü · emir kipi fiil · söylem dolgusu.
        return rng.choice((
            f"{d}{olcu} {o2} üzerindeki etkisini ölç",
            f"{olcu} ile {o2} arasında ilişki var mı {d}",
            f"{d}{olcu} {o2}yi nasıl etkiliyor",
            f"{olcu} {o2} korelasyonu {d}",
            f"{d}{olcu} artınca {o2} ne oluyor",
        ))
    if niyet == NIYET_OLUMSUZ:
        # 🔴 Kapsam kapısı: olumsuzluk (-ma/-me) **hiç üretilmiyordu**. Oysa
        # *"neden düşmedi"* ile *"neden düştü"* birbirinin zıddıdır ve aynı cevabı
        # veren bir sistem, ikisinden birinde mutlaka yanılıyordur.
        return rng.choice((
            f"{d}{olcu} neden düşmedi", f"{d}{olcu} artmadı mı",
            f"{b} hariç {d}{olcu}", f"{d}{olcu} {b} dışında ne durumda",
            f"{d}{olcu} hedefi tutturamadık mı",
        ))
    if niyet == NIYET_COKLU_SORU:
        return rng.choice((
            f"{d}{olcu} ne kadar, {o2} nasıl", f"{d}{olcu}? bir de {o2}?",
            f"{d}{olcu} ve ayrıca {b} bazında {o2} lazım",
        ))
    if niyet == NIYET_COK_KIRILIM:
        b2 = "vardiya" if b != "vardiya" else "makine"
        return rng.choice((
            f"{d}{b} ve {b2} bazında {olcu}", f"{d}{olcu} {b} {b2} kırılımında",
            f"{b} bazında {d}{olcu}, {b2} ayrımıyla",
        ))
    if niyet == NIYET_KOMPOZISYON:
        return rng.choice((
            f"{d}{olcu} ve {o2} birlikte",
            f"{d}{olcu} yanına {o2} ekle",
            f"{b} bazında {d}{olcu} ile {o2}",
            f"{d}{olcu} {o2} birlikte göster",
        ))
    if niyet == NIYET_DEGER:
        return rng.choice((f"{d}{olcu}", f"{d}toplam {olcu}", f"{d}{olcu} ne kadar"))
    if niyet == NIYET_KIRILIM:
        return rng.choice((f"{d}{b} bazında {olcu}", f"{b} bazında {d}{olcu}",
                           f"{d}{olcu} {b} kırılımında"))
    if niyet == NIYET_USTUNLUK:
        return rng.choice((f"{d}en çok {olcu} olan {b}", f"{d}en yüksek {olcu} hangi {b}",
                           f"{d}{olcu} en düşük {b}"))
    if niyet == NIYET_KIYAS:
        return rng.choice((f"{olcu} {donem or 'geçen ay'}a göre nasıl",
                           f"{donem or 'bu ay'} {olcu} geçen yılla kıyasla",
                           f"{olcu} {donem or 'geçen yıl'} ile karşılaştır"))
    if niyet == NIYET_TREND:
        return rng.choice((f"{d}{olcu} nasıl gidiyor", f"{olcu} trendi {d}",
                           f"{d}{olcu} artıyor mu azalıyor mu"))
    if niyet == NIYET_KATKI:
        return rng.choice((f"{d}{olcu} düşüşünde hangi {b} etkili",
                           f"{d}{olcu} değişiminde kimin payı var",
                           f"{d}{olcu} bizi hangi {b} aşağı çekiyor"))
    if niyet == NIYET_NEDEN:
        return rng.choice((f"{d}{olcu} neden arttı", f"{olcu} niye düştü {d}",
                           f"{d}{olcu} neden böyle"))
    if niyet == NIYET_ESIK:
        return rng.choice((f"{d}{olcu} hedefin neresinde", f"{d}{olcu} bütçeye uyuyor mu",
                           f"{d}{olcu} iyi mi kötü mü"))
    if niyet == NIYET_KARAR:
        return rng.choice((f"{olcu} için ne yapmalıyız", f"{d}{olcu} nasıl iyileştirilir",
                           f"{olcu} konusunda ne önerirsin"))
    if niyet == NIYET_TAHMIN:
        return rng.choice((f"{olcu} yılı nerede kapatır", f"bu gidişle {olcu} ne olur",
                           f"{olcu} önümüzdeki ay ne olur"))
    if niyet == NIYET_YETENEK:
        return rng.choice(("neler yapabilirsin", "hangi ölçüler var",
                           "başka ne sorabilirim", "hangi kırılımlar var"))
    return rng.choice(("asdf qwerty zxcv", "bana bir fıkra anlat", "merhaba",
                       "hava nasıl", "drop table faturalar", "1234567"))


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 PAIRWISE COVERING ARRAY — kapsamı kanıtlı, boyu küçük
# ═══════════════════════════════════════════════════════════════════════════════

def pairwise(eksenler: dict[str, list], rng: random.Random,
             azami: int | None = None) -> list[dict]:
    """Her **ikili** değer kombinasyonunu en az bir kez içeren vaka listesi.

    ## Algoritma — açgözlü IPO benzeri, ve neden bu

    Tam çarpım hesaplanmaz (bellekte tutulamaz). Bunun yerine: kapsanmamış ikililer
    kümesi tutulur; her turda **en çok yeni ikili kapatan** aday seçilir. Aday havuzu
    rastgele örneklenir ki algoritma `O(çarpım)` olmasın.

    ⚠ Rastgelelik **sabit tohumludur** — aksi hâlde korpus her koşumda değişir ve
    *"dün geçen test bugün kaldı"* teşhis edilemez hâle gelir.

    > *Bir test kümesinin tekrar üretilebilirliği, büyüklüğünden daha değerlidir.*
    """
    adlar = list(eksenler)
    # Kapatılması gereken tüm ikililer: ((eksen_i, değer_i), (eksen_j, değer_j))
    hedef: set[tuple] = set()
    for i, j in itertools.combinations(range(len(adlar)), 2):
        for vi in eksenler[adlar[i]]:
            for vj in eksenler[adlar[j]]:
                hedef.add(((adlar[i], vi), (adlar[j], vj)))
    toplam_ikili = len(hedef)

    # ⚡ HIZ: eksen ikilileri **bir kez** hesaplanır. Eskiden her aday için
    # `itertools.combinations` yeniden koşuyordu — 10 589 tur × 60 aday × 15 ikili
    # = ~9,5 milyon gereksiz üretim. Kapsam **birebir aynı**, yalnız aynı sonucu
    # daha az işle üretiyoruz. *Hız kapsamdan değil, tekrardan kısılır.*
    ikili_indeks = tuple(itertools.combinations(range(len(adlar)), 2))

    def _kapatilan(aday: dict) -> set:
        return {((adlar[i], aday[adlar[i]]), (adlar[j], aday[adlar[j]]))
                for i, j in ikili_indeks} & hedef

    secilen: list[dict] = []
    HAVUZ = 60                       # tur başına aday sayısı — kalite/hız dengesi
    while hedef:
        en_iyi, en_iyi_kazanc, en_iyi_kapanan = None, -1, None
        for _ in range(HAVUZ):
            aday = {ad: rng.choice(eksenler[ad]) for ad in adlar}
            kapanan = _kapatilan(aday)
            if len(kapanan) > en_iyi_kazanc:
                en_iyi, en_iyi_kazanc, en_iyi_kapanan = aday, len(kapanan), kapanan
                # ⚡ Erken çıkış: bir aday **tüm** ikililerini kapatıyorsa daha
                # iyisi yok — kalan 59 adayı denemek boşa iş.
                if en_iyi_kazanc == len(ikili_indeks):
                    break
        if not en_iyi_kazanc:        # havuz hiç yeni ikili bulamadı → kalanları tara
            eksik = next(iter(hedef))
            en_iyi = {ad: rng.choice(eksenler[ad]) for ad in adlar}
            for (eksen, deger) in eksik:
                en_iyi[eksen] = deger
            en_iyi_kapanan = _kapatilan(en_iyi)
        hedef -= en_iyi_kapanan or set()
        secilen.append(en_iyi)
        # 🔴 ERKEN KESME — ve neden **baştan** kesmek doğru.
        #
        # Açgözlü algoritma her turda **en çok yeni ikili kapatan** adayı seçer;
        # yani dizinin **başı en çeşitli** kısmıdır ve çeşitlilik sona doğru azalır.
        # Bu yüzden ilk N vaka, rastgele N vakadan **ölçülebilir biçimde** daha
        # geniş kapsar.
        #
        # ⚠ İkili kapsam kısmi kalır (ve `kapsam` raporu bunu **söyler**); ama
        # kapının sorduğu soru *"üreteç 71 dilsel özelliği üretebiliyor mu"*dur,
        # *"her ikili kapsandı mı"* değil. İkincisi lab koşumunun işi.
        if azami and len(secilen) >= azami:
            break
    # 🔴 Erken kesildiyse `hedef` boşalmamıştır. Kapsananı **saymadan** yalnız hedefi
    # raporlamak, kısmi bir kümeyi tam gibi gösterirdi.
    # *Bir kapsam raporunun ilk görevi, kapsamadığını söylemektir.*
    return secilen, toplam_ikili, toplam_ikili - len(hedef)


# ═══════════════════════════════════════════════════════════════════════════════
# NORMALİZASYON — 🔴 ürünle AYNI yol
# ═══════════════════════════════════════════════════════════════════════════════

def urun_gibi_normalize(q: str) -> str:
    """`/ask`in `q_norm = _norm(body.question)` adımının aynısı.

    ⚠ Bu fonksiyon `cube_router._norm`'u **çağırır**, kopyalamaz: bir normalizasyon
    kuralının iki sahibi olursa biri güncellenir öteki kalır, ve ölçüm ürünle
    ayrışır — *bu deponun defterindeki "aynı kuralın iki sahibi" sınıfı.*
    """
    from app import cube_router
    fn = getattr(cube_router, "_norm", None)
    if fn is None:                                       # sürüm sapması → sessizce yanlış
        raise RuntimeError("cube_router._norm yok — ölçüm ürünle AYRIŞIR, koşum durdu")
    return fn(q)


def _anlamli_kelimeler(soru: str) -> frozenset:
    """Kopya ölçüsü için anlamlı kelime kümesi (durak kelimeler atılır)."""
    durak = {"ne", "mi", "mı", "mu", "mü", "bu", "şu", "bir", "var", "yok", "ve",
             "ile", "için", "gibi", "kadar", "daha", "çok", "az", "en", "göre",
             "peki", "ya", "nasıl", "kaç", "hangi", "nerede", "neden", "niye",
             "kim", "biz", "bize", "bizi", "olan", "oldu", "de", "da"}
    return frozenset(k for k in unicodedata.normalize("NFC", soru.lower()).split()
                     if k not in durak and len(k) > 1)


# ═══════════════════════════════════════════════════════════════════════════════
# KATALOĞA BAĞLANMA — vakalar kataloğun KENDİSİNDEN doğar
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 Bu, üretecin elle yazımdan asıl farkı: yeni bir cube eklendiğinde korpus
# **kendiliğinden** büyür. Elle yazımda her cube için 20 satır daha yazmak gerekirdi
# ve pratikte yazılmazdı — *bir korpusun bakımı, yazılması kadar önemlidir.*

#: Cube → persona eşlemesi. ⚠ Elle bir liste DEĞİL, cube adından ve ölçülerinden
#: türetilir; tanınmayan cube `analist`e düşer — **sessizce atlanmaz**.
_PERSONA_IPUCU = {
    "ceo": ("kpi", "ozet"),
    "cfo": ("cari", "mizan", "ticaret", "butce", "kur", "kredi", "maliyet"),
    "uretim": ("oee", "parti", "makine_duruslari", "kapasite", "is_emri"),
    "kalite": ("kalite", "sikayet", "uygunsuz", "denetim"),
    "satis": ("siparis", "firsat", "musteri"),
    "ik": ("ik", "egitim", "isg", "performans", "bordro"),
    "bakim": ("bakim",),
    "lojistik": ("sevkiyat", "nakliye", "arac"),
    "surdurulebilirlik": ("enerji", "surdurulebilirlik", "su"),
}


def persona_of(cube_adi: str) -> str:
    for persona, ipuclari in _PERSONA_IPUCU.items():
        if any(i in cube_adi for i in ipuclari):
            return persona
    return "analist"


def _olcu_sahipleri(schema: dict) -> dict[str, list[str]]:
    """Bir ölçü **görünen adının** kaç cube'da geçtiği.

    🔴 Beklenen davranışın en önemli kuralı buradan çıkar: bir ad ≥2 cube'a aitse
    (`bakiye` → cari ∧ mizan, `fire` → parti ∧ oee) doğru davranış **netleştirmedir**,
    bir sayı üretmek değil. *Belirsizlik deterministik olarak BİLİNİYORken bir tarafı
    seçmek, sessiz-yanlışın tanımıdır.*
    """
    sahip: dict[str, list[str]] = defaultdict(list)
    for c in schema.get("cubes") or []:
        cad = c.get("name")
        syn = c.get("measure_synonyms") or {}
        gorunen = c.get("measure_synonyms_display") or {}
        for m in c.get("measures") or []:
            m = str(m)
            for ad in [m, gorunen.get(m), *(syn.get(m) or [])]:
                if ad:
                    sahip[str(ad).lower()].append(cad)
    return {k: sorted(set(v)) for k, v in sahip.items()}


# Beklenen davranış sınıfları — `gercek_dunya` ile AYNI adlar (tek sözlük).
DOGRU, NETLESTIRME, DURUST_RET, SESSIZ_YANLIS = (
    "dogru", "netlestirme", "durust_ret", "sessiz_yanlis")


def _beklenti(niyet: str, olcu_ifade: str, sahipler: dict[str, list[str]],
              donem: str, kayit: str) -> tuple[list[str], str]:
    """(kabul edilen sınıflar, yasak davranış) — **kuraldan** türetilir.

    ⚠ Kabul listesi bilerek **birden fazla** sınıf içerebilir: bir soruya hem doğru
    cevap vermek hem de netleştirme sormak makul olabilir. *Tek bir doğru dayatmak,
    ürünü kendi tasarım tercihleri için cezalandırırdı.*
    """
    if niyet == NIYET_GURULTU:
        return [DURUST_RET], "🔴 anlamsız/kapsam dışı girdiye bir cube seçip sayı üretmek"
    if niyet == NIYET_YETENEK:
        return [DURUST_RET, NETLESTIRME], "yetenek sorusuna bir veri sorgusu koşmak"
    if niyet in V1_DISI_NIYETLER:
        return ([DURUST_RET, NETLESTIRME],
                "v1'de olmayan bir yeteneği (tahmin/öneri) varmış gibi cevaplamak")

    coksahipli = len(sahipler.get(olcu_ifade.lower(), [])) >= 2
    if coksahipli:
        return ([NETLESTIRME],
                f"«{olcu_ifade}» {len(sahipler[olcu_ifade.lower()])} cube'un ölçüsüyken "
                "birini SESSİZCE seçmek")
    if kayit in (KAYIT_YAZIM, KAYIT_ELIPTIK):
        # Bozuk/eksik girdide **dürüst ret de kabul**: tahmin etmektense sormak.
        return ([DOGRU, NETLESTIRME, DURUST_RET],
                "🔴 bozuk ya da eksik girdiyi düzeltmeden RASTGELE bir cube'a gitmek")
    if not donem:
        return ([DOGRU, NETLESTIRME],
                "dönemsiz soruda sessizce bir dönem varsayıp sayı vermek")
    return [DOGRU, NETLESTIRME], "yanlış cube ya da yanlış ölçü seçmek"


def _katalog_parmak_izi(schema: dict, tohum: int, azami: int | None = None) -> str:
    """Kataloğun **anlam taşıyan** özeti — önbellek anahtarı.

    ⚠ Tüm şemayı hash'lemek yanlış olurdu: içinde koşumdan koşuma değişen alanlar
    (yol, zaman damgası) olabilir ve önbellek **hiç tutmazdı**. Yalnız üretimi
    etkileyen alanlar alınır: cube adı · ölçüler · boyutlar · sinonimler.
    """
    import hashlib
    import json as _json

    ozet = []
    for c in sorted(schema.get("cubes") or [], key=lambda x: str(x.get("name"))):
        ozet.append([
            c.get("name"),
            sorted(str(m) for m in (c.get("measures") or [])),
            sorted(str(d) for d in (c.get("dimensions") or [])),
            {k: sorted(v or []) for k, v in sorted((c.get("measure_synonyms") or {}).items())},
            {k: sorted(v or []) for k, v in sorted((c.get("dimension_synonyms") or {}).items())},
        ])
    # ⚠ `azami` anahtara **girer**: 2 500'lük kapı korpusu ile 10 700'lük lab korpusu
    # farklı kümelerdir; aynı anahtarı paylaşırlarsa biri ötekinin yerine geçer ve
    # kapı, lab'ın sonucunu kendi sonucu sanar.
    ham = _json.dumps([ozet, tohum, SURUM, azami], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:16]


#: ⚠ Üreteç değiştiğinde önbellek **bayatlar**. Bu sayı elle artırılır; artırılmazsa
#: eski korpus sessizce yeniden kullanılır ve *"değişikliğim neden bir şey yapmadı"*
#: diye saatler harcanır. *Bir önbelleğin en tehlikeli hâli, doğru görünen bayat hâlidir.*
SURUM = 4        # dönem ekseni sınıfa çevrildi → önbellek bayat


def uret(schema: dict, *, tohum: int = 20260805,
         azami: int | None = None, onbellek: bool = True) -> tuple[list[dict], dict]:
    """Kataloğa bağlı, pairwise-kapsamlı senaryo korpusu üretir.

    Dönen: (vakalar, kapsam_raporu)

    ## ⚡ ÖNBELLEK — üretim deterministik olduğu için güvenli

    Aynı katalog + aynı tohum → **birebir aynı** korpus. Dolayısıyla her testte
    yeniden üretmek saf tekrardır. Anahtar kataloğun parmak izidir: katalog
    değişirse önbellek **kendiliğinden** geçersizleşir.

    🔴 Kapsamdan ödün YOK: önbellek aynı vakaları döndürür, azını değil.
    `onbellek=False` ile kapatılır (üretecin kendisini sınayan testler için).
    """
    import json as _json
    import pathlib as _pl

    _anahtar = _katalog_parmak_izi(schema, tohum, azami) if onbellek else None
    # 🔴 ÖNBELLEK `reports/` ALTINDA DEĞİL — orası `.gitignore`'da ve o yüzden
    # **her yeni makinede, her CI koşumunda soğuk** başlıyordu. Bir önbelleğin
    # değeri kalıcılığındadır; her koşumda silinen bir önbellek, önbellek değildir.
    #
    # ⚠ `lab/.onbellek/` de commit'lenmez (türetilmiş veri repoya girmez) ama
    # **koşumlar arasında yaşar** — asıl kazanç zaten oradaydı.
    _yol = (_pl.Path(__file__).resolve().parent / ".onbellek" /
            f"senaryo_{_anahtar}.json") if _anahtar else None
    if _yol and _yol.exists():
        try:
            _v = _json.loads(_yol.read_text(encoding="utf-8"))
            return _v["vakalar"], _v["kapsam"]
        except Exception:                                  # noqa: BLE001
            _yol.unlink(missing_ok=True)                   # bozuk önbellek → yeniden üret
    rng = random.Random(tohum)
    cubes = [c for c in (schema.get("cubes") or []) if c.get("measures")]
    sahipler = _olcu_sahipleri(schema)

    # --- Eksenler. `olcu_ref` = (cube_adi, görünen ölçü ifadesi, boyut ifadesi)
    # ⚠ ŞEMA BİÇİMİ ÖLÇÜLDÜ, VARSAYILMADI: `measures` bir **ad listesidir** (dict
    # değil); kullanıcı dili ayrı sözlüklerde yaşar — `measure_synonyms` (ASCII
    # katlanmış) ve `measure_synonyms_display` (Türkçe aksanlı). İlk yazımımda
    # `isinstance(m, dict)` filtresi koydum ve **her ölçüyü eledim**; üreteç boş
    # eksenle patladı. *Bir yapının biçimini varsaymak, onu okumamaktır.*
    olcu_refleri: list[tuple[str, str, str | None]] = []
    for c in cubes:
        cad = c.get("name")
        m_syn = c.get("measure_synonyms") or {}
        m_gor = c.get("measure_synonyms_display") or {}
        d_syn = c.get("dimension_synonyms") or {}
        d_lbl = c.get("dimension_labels") or {}
        boyutlar = [str(d) for d in (c.get("dimensions") or [])]
        for m in c.get("measures") or []:
            m = str(m)
            # 🔴 KULLANICI DİLİ tercih edilir, teknik ad **son çare**: katalog adıyla
            # sorulan bir soru kullanıcının sorduğu soru değildir — ve mevcut korpusun
            # neden %93 çıktığını da bu açıklıyor.
            adaylar = [*(m_syn.get(m) or []), m_gor.get(m)]
            adaylar = [a for a in adaylar if a]
            ifade = str(rng.choice(adaylar)) if adaylar else m
            boyut = None
            if boyutlar:
                b = rng.choice(boyutlar)
                b_adaylar = [*(d_syn.get(b) or []), d_lbl.get(b)]
                b_adaylar = [a for a in b_adaylar if a]
                boyut = str(rng.choice(b_adaylar)) if b_adaylar else b
            olcu_refleri.append((cad, ifade, boyut))

    eksenler = {
        "olcu": olcu_refleri,
        "niyet": list(NIYET_KADEME),
        "kayit": list(KAYITLAR),
        # 🔴 Eksende **sınıf** var, somut biçim değil — gerekçe yukarıda ölçülü.
        "donem_sinifi": list(DONEM_SINIFLARI),
        "dolgu": list(DOLGULAR),
        "bicim": list(BICIMLER),
    }
    kombinasyonlar, toplam_ikili, kapsanan_ikili = pairwise(eksenler, rng, azami)
    sayac_donem = _SinifSayaci()

    vakalar: list[dict] = []
    gorulen: set[frozenset] = set()
    kopya_atlanan = 0
    for k in kombinasyonlar:
        cad, ifade, boyut = k["olcu"]
        niyet, kayit = k["niyet"], k["kayit"]
        donem_sinifi = k["donem_sinifi"]
        donem = sayac_donem.al(donem_sinifi)
        dolgu, bicim = k["dolgu"], k["bicim"]
        # ⚠ İKİ-ÖLÇÜ niyetlerinde ikinci ölçü **başka bir cube'dan** seçilir: aynı
        # cube'un iki ölçüsü zaten kompozisyon değil, çoklu-ölçü sorgusudur. Canlı
        # vakadaki zorluk (`verimlilik` oee'de, `ciro` parti'de) çapraz-cube olmasıydı.
        olcu2 = None
        if niyet in (NIYET_ETKI, NIYET_KOMPOZISYON, NIYET_COKLU_SORU):
            baska = [r for r in olcu_refleri if r[0] != cad]
            olcu2 = rng.choice(baska)[1] if baska else None
        govde = _sablon(niyet, ifade, boyut, donem, rng, olcu2)
        # ⚠ Sıra önemli: kayıt → dolgu → **biçim en son**. Biçim yüzeysel bir
        # dönüşümdür (büyük harf, noktalama); ondan sonra kelime değiştirmek onu bozar.
        soru = _bicim_uygula(_dolgu_uygula(_kayit_uygula(govde, kayit, rng), dolgu, rng),
                             bicim, rng)
        anahtar = _anlamli_kelimeler(soru)
        # ⚠ Kopya kapısı **üretim anında**: sonradan elemek, pairwise kapsamını
        # sessizce delerdi (kapsam raporu doğru, korpus eksik olurdu).
        if not anahtar or anahtar in gorulen:
            kopya_atlanan += 1
            continue
        gorulen.add(anahtar)
        kabul, yasak = _beklenti(niyet, ifade, sahipler, donem, kayit)
        vakalar.append({
            "soru": soru, "cube": cad, "olcu_ifade": ifade, "boyut": boyut,
            "niyet": niyet, "kayit": kayit, "donem": donem,
            "donem_sinifi": donem_sinifi, "dolgu": dolgu,
            "bicim": bicim, "olcu2": olcu2,
            "kademe": NIYET_KADEME[niyet], "persona": persona_of(cad),
            "kabul": kabul, "yasak": yasak,
            "kaynak": f"üreteç · pairwise · {cad}.{ifade}",
        })
        if azami and len(vakalar) >= azami:
            break

    kapsam = {
        "vaka": len(vakalar),
        "kopya_atlanan": kopya_atlanan,
        "ikili_hedef": toplam_ikili,
        "ikili_kapsanan": kapsanan_ikili,
        "ikili_yuzde": round(100 * kapsanan_ikili / max(toplam_ikili, 1), 1),
        # ⚠ `azami` verildiyse bu **kısmi** bir korpustur ve rapor bunu SÖYLER —
        # okuyucu 2 500'lük kapı örneğini 10 700'lük lab korpusu sanmasın.
        "kismi": bool(azami),
        "eksen_boyutlari": {k: len(v) for k, v in eksenler.items()},
        "cube": len(cubes),
        "persona": dict(Counter(v["persona"] for v in vakalar)),
        "kademe": dict(Counter(v["kademe"] for v in vakalar)),
        "kayit": dict(Counter(v["kayit"] for v in vakalar)),
        "niyet": dict(Counter(v["niyet"] for v in vakalar)),
        "dolgu": dict(Counter(v["dolgu"] or "yok" for v in vakalar)),
        "bicim": dict(Counter(v["bicim"] or "düz" for v in vakalar)),
        "donem_sinifi": dict(Counter(v["donem_sinifi"] for v in vakalar)),
        "donem_bicimi_sayisi": len({v["donem"] for v in vakalar}),
    }
    if _yol:
        try:
            _yol.parent.mkdir(parents=True, exist_ok=True)
            _yol.write_text(_json.dumps({"vakalar": vakalar, "kapsam": kapsam},
                                        ensure_ascii=False), encoding="utf-8")
        except Exception:                                  # noqa: BLE001
            pass                                           # önbellek yazılamazsa ölçüm yine doğru
    return vakalar, kapsam
