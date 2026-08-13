"""🔴🔴 `§5.2` · `§5.3` — **PILL KATMANI**: `Niyet` nesnesinin GÖRÜNÜR HÂLİ.
[bayrak yok: tüketicisi olmayan **saf** bir okuma — ürün yüzeyinin bayrağı çağıranda]

## Planın iki cümlesi — ve bu dosyanın tamamı

> `§5.2` — *«`app/niyet.py::Niyet` alanları ↔ pill'ler **birebir**. 🔴 Yeni model
> kurulmuyor, mevcut model **çiziliyor**. `frozen` bir okumadır, pill'ler onu üretir —
> ikinci bir temsil doğmaz (`KAT-1`).»*
>
> `§5.3` — *«Doğrulama **zaten var** (`dogrula` koşmadan önce · `compose` grain ihlali).
> Eksik olan onu pill'e taşımak: geçersiz kombinasyonda pill **kırmızıya döner ve
> nedenini söyler** — koşmadan. **İmkânsız soru sorulamaz hâle gelir.**»*

⊡ Ölçüldü (`ONGORU-DURUM.md §26`): `§5.2` ve `§5.3` üründe **hiç yok** — *«oysa
`app/niyet.py` ve alanları **hazır**»*. Bu dosya o boşluğu kapatır ve **yalnız** onu:
tek bir yeni kural, tek bir yeni sözlük, tek bir yeni doğrulayıcı yazmaz.

## 🔴 KAT-1 — bu dosyanın SAHİP OLMADIĞI şeyler

Her satır bir **çağrıdır**, bir kopya değil. Sahipler:

| ne | sahibi | burada |
|---|---|---|
| pill'lerin **içeriği** | `app/niyet.py::Niyet` alanları | türetilir |
| küp **beyaz listesi** | `cube_router.parse_cube_query` | **artımlı** sorulur |
| **grain** ihlali (bakiye/stok ⊗ zaman kovası) | `cube_router.is_period_optional` (`R8`) | sorulur |
| zaman **kovası** kapalı kümesi | `cube_operatorleri.GRANULERLIKLER` | sorulur |
| **dönem** seçenekleri (tek tık) | `donem_capasi.DONEM_SECENEKLERI` | okunur |
| **adım** fiilleri | `plan_semasi.FIILLER` (⊂ yetenek kaydı) | okunur |
| **temsil boşluğu** (çok dönem · kıyas) | `Niyet.temsil_edilemeyen` | okunur |
| gün biçimi · granülerlik Türkçesi | `donem_capasi._gun` · `report._GRAN_ADI` | çağrılır |

*Bir kümenin üç kopyası, üç farklı küme demektir* — bu yüzden burada **sıfır** kopya var.

## 🔴 Beyaz liste neden ARTIMLI sorulur — ve neden yeniden yazılmaz

`parse_cube_query` bu deponun **tek doğrulama boğazıdır** ama `None` döner: *«geçmedi»*
der, *«hangi pill yüzünden»* demez. Kullanıcıya *«kırmızı, çünkü …»* diyebilmek için o
sebebe ihtiyaç var — ve iki yol vardı:

1. ⊘ Üyelik denetimlerini burada **tekrar yazmak** → beyaz listenin **ikinci sahibi**.
   Bu deponun bir numaralı kusur sınıfı; ve ayrıştığı gün pill *«yeşil»* derken motor
   reddederdi — yani arayüz **yalan söylerdi**.
2. ✅ Fişi **pill pill büyütmek** ve her adımda **aynı boğaza** sormak. Kabulden redde
   dönen ilk ekleme, suçlu pill'dir.

İkincisi seçildi: kural tek sahipte kalır, buradaki iş yalnız **yerelleştirmedir**.
*Bir kuralı kopyalamadan sebebini bulmanın yolu, kuralı birden çok kez sormaktır.*

## 🔴 «Bir adayda geçiyorsa KIRMIZI DEĞİLDİR» — belirsizlik ≠ imkânsızlık

`olcu_adaylari` **birden çok küpe** işaret edebilir (`§A.2`'nin 73 çok-sahipli terimi;
`Niyet.SEBEP_COK_SAHIP`). Bir kırılım adaylardan **birinde** varsa soru imkânsız değil,
**belirsizdir** — ve belirsizliğin sahibi başka bir mekanizmadır
(`app/belirsizlik_chipi.py`). Bu yüzden bir pill ancak **her adayda** düşerse kırmızıya
döner. *Bir soruyu imkânsız ilan etmek, onu cevaplayabilecek küpü görmemekle aynı şey
değildir.*

## ⚠ Kapsam — bilinçli olarak `§5.2` diyagramının kendisi

Diyagram dört sütun çiziyor (`olcu_adaylari · donemler · kirilimlar · turler`) ve
`alan` kapalı kümesi **tam olarak** o dört sütundur. Dışarıda kalanlar ve **neden**:

* `filtreler` — `donemler` + ölçü eşiği; eşiğin `alan`ı kapalı kümede **yok**. Kümeyi
  genişletmek bir **sözleşme değişikliğidir**, sessizce yapılmaz.
* `granulerlik` · `ustunluk` — birer pill **değil**, ait oldukları `tur` pill'inin
  **metnidir** (*«aylık seyir»* · *«en yüksek 5»*). Ayrı pill olsalardı aynı niyet iki
  kutuda görünürdü — yani `KAT-1`'in görsel hâli.
* `kirilim_istendi` **ama** `kirilimlar` boş — *«bir kırılım istedin, boyut
  taşıyamadım»* beyanı `app/uyum.py`'nindir. Buraya koymak onun **ikinci sahibi**
  olurdu; bu bir eşleştirme kusuru, bir kombinasyon geçersizliği değil.

## ⚠ Bu katman KOŞMAZ

LLM yok, sorgu yok, motor yok. Şema **dışarıdan** verilir. `§5.3`'ün tamamı buradadır:
kullanıcı imkânsız kombinasyonu **yazmadan önce** görür — ve gördüğü şey bir hata
kodu değil, **Türkçe bir cümledir**.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from app.niyet import (
    TUR_KIRILIM,
    TUR_KIYAS,
    TUR_LISTE,
    TUR_TOPLAM,
    TUR_TREND,
    TUR_USTUNLUK,
    Niyet,
)

# ═══════════════════════════════════════════════════════════════════════════════
# KAPALI KÜMELER — `§5.2` diyagramının dört sütunu
# ═══════════════════════════════════════════════════════════════════════════════

ALAN_OLCU = "olcu"
ALAN_DONEM = "donem"
ALAN_KIRILIM = "kirilim"
ALAN_TUR = "tur"
#: 🔴 `§51` — BEŞİNCİ ALAN: soruda geçen **katalog değeri** (`RAM-3`).
#: Plan `§5.2` dört sütun sayıyordu; beşincisi bir süs değil bir **eksikti**:
#: kullanıcının yazdığı varlık hiçbir yuvaya düşmüyordu. ⚠ Ön yüz pill'leri
#: alan adına **bakmadan** çiziyor (`PillSatiri`), yani bu ekleme FE
#: sözleşmesini bozmaz — ölçüldü.
ALAN_VARLIK = "varlik"

#: 🔴 Sıra bir **sözleşmedir**: `§5.2` diyagramının soldan sağa sırası.
ALANLAR: tuple[str, ...] = (ALAN_OLCU, ALAN_VARLIK, ALAN_DONEM, ALAN_KIRILIM,
                            ALAN_TUR)

#: 🔴🔴 **PILL ALANI → `Niyet` ALANI.** Bu sözlük, planın *«birebir»* iddiasının
#: **makinece okunabilir** hâlidir: her pill alanının arkasında **gerçek** bir `Niyet`
#: alanı vardır ve kapı bunu `dataclasses.fields(Niyet)` ile ölçer. Bir gün `Niyet`
#: alanı yeniden adlandırılırsa pill katmanı **içe aktarma anında değil kapıda**,
#: ama **adıyla** düşer — sessizce bayatlamaz.
ALAN_KAYNAGI: dict[str, str] = {
    ALAN_OLCU: "olcu_adaylari",
    #: `§51` — varlık pill'i `Niyet.filtreler`den doğar (dönem filtreleri hariç;
    #: onların kendi pill'i var). Kapı `set(ALAN_KAYNAGI) == set(ALANLAR)` ister:
    #: bir alanı ilan edip **kaydını** yazmamak, onu yarım ilan etmektir 🅧.
    ALAN_VARLIK: "filtreler",
    ALAN_DONEM: "donemler",
    ALAN_KIRILIM: "kirilimlar",
    ALAN_TUR: "turler",
}

#: `turler` bir **küme**dir → çizim sırası kümeden gelemez. Belirlenimli sıra bu
#: deponun yazılı kuralıdır (`test_belirlenimli_sira.py`): aynı niyet, aynı satır.
TUR_SIRASI: tuple[str, ...] = (
    TUR_TOPLAM, TUR_KIRILIM, TUR_TREND, TUR_KIYAS, TUR_USTUNLUK, TUR_LISTE)

#: Kapalı tür kümesinin **Türkçesi** — kullanıcıya `toplam`/`kirilim` yazılmaz.
TUR_METNI: dict[str, str] = {
    TUR_TOPLAM: "toplam",
    TUR_KIRILIM: "kırılım",
    TUR_TREND: "seyir",
    TUR_KIYAS: "kıyas",
    TUR_USTUNLUK: "üstünlük",
    TUR_LISTE: "liste",
}


# ═══════════════════════════════════════════════════════════════════════════════
# `+` — 🔴 TİPLİ, ÇÜNKÜ TEK BİR `+` BU DEPONUN BİR NUMARALI TUZAĞIDIR
# ═══════════════════════════════════════════════════════════════════════════════
#
# Planın tablosu (`§5.2`) birebir:
#
#     | `+` ne demek                | sonuç                        |
#     | aynı sorguya **ölçü** ekle  | **tek** `cube_query`, iki ölçü |
#     | **adım** ekle               | sıralı **plan**              |
#     | **ayrı rapor**              | **iki** kart                 |
#
# → `[+ ölçü] [+ kırılım] [+ dönem] [+ adım]` — dördü de **kapalı gramerin alanları**.
#
# 🔴 Neden bu tuzak ciddiye alınıyor: *«göre/bazında»* de üç anlamlıydı ve bu depoyu
# **üç kez** ısırdı (`_BREAKDOWN_HINTS` · `gore_donem_mi` · `§Ö10`). Aradaki fark
# şu: orada üç anlam **kullanıcının cümlesinden** geliyordu, burada **bizim
# arayüzümüzden**. Kendi ürettiğimiz bir belirsizliği taşımak için hiçbir mazeret yok.
#
# ⚠ Üçüncü anlam (**ayrı rapor → iki kart**) bilerek bir `+` **DEĞİL**: o bir *«yeni
# konu»*dur ve yeri `§5.1`'in çapasıdır (`YENİ KONU` grubu). Bir `+`'ın hiçbir zaman
# *«ekranı ikiye böl»* anlamına gelmemesi, tipli `+`'ın asıl kazancıdır.

ARTI_OLCU = "olcu"
ARTI_KIRILIM = "kirilim"
ARTI_DONEM = "donem"
ARTI_ADIM = "adim"

#: 🔴 Sıra planın yazdığı sıradır: `[+ ölçü] [+ kırılım] [+ dönem] [+ adım]`.
ARTI_TIPLERI: tuple[str, ...] = (ARTI_OLCU, ARTI_KIRILIM, ARTI_DONEM, ARTI_ADIM)

#: `+`'ın **sonucu** — kapalı küme. Tek bir `+`'ın üç anlama gelmesi bu iki değerin
#: ayrılmasıyla imkânsızlaşır: bir `+` ya aynı fişi büyütür ya bir plan doğurur.
SONUC_TEK_SORGU = "tek_sorgu"
SONUC_PLAN = "plan"

ARTI_METNI: dict[str, str] = {
    ARTI_OLCU: "+ ölçü",
    ARTI_KIRILIM: "+ kırılım",
    ARTI_DONEM: "+ dönem",
    ARTI_ADIM: "+ adım",
}

#: Her `+` **kendi alanını beyan eder** — `adim` hiçbir `Niyet` alanını büyütmez,
#: bir **plan** doğurur (`plan_semasi.tek_adimli`: tek adımlı plan = bugünkü fiş).
ARTI_ALANI: dict[str, str | None] = {
    ARTI_OLCU: ALAN_KAYNAGI[ALAN_OLCU],
    ARTI_KIRILIM: ALAN_KAYNAGI[ALAN_KIRILIM],
    ARTI_DONEM: ALAN_KAYNAGI[ALAN_DONEM],
    ARTI_ADIM: None,
}

ARTI_SONUCU: dict[str, str] = {
    ARTI_OLCU: SONUC_TEK_SORGU,
    ARTI_KIRILIM: SONUC_TEK_SORGU,
    ARTI_DONEM: SONUC_TEK_SORGU,
    ARTI_ADIM: SONUC_PLAN,
}


# ═══════════════════════════════════════════════════════════════════════════════
# NESNELER — hepsi `frozen`, çünkü hepsi bir OKUMA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Pill:
    """`Niyet`in bir alanının **tek bir görünür parçası**.

    ⚠ `frozen`: `Niyet`in gerekçesinin aynısı — bir pill bir okumadır, bir çalışma
    alanı değil. Kullanıcı bir pill'i *«düzenlemez»*; siler ya da yenisini ekler, ve
    her ikisi de **yeni bir niyet** doğurur.
    """

    #: `ALANLAR` kapalı kümesinden.
    alan: str
    #: Kullanıcıya görünen **Türkçe**. Teknik ad buraya yazılmaz.
    metin: str
    #: Pill'in `Niyet`teki **karşılığı** — üzerine bir şey eklenmez, çıkarılmaz.
    #: ⚠ `hash=False`: `donem` değeri bir **listedir**; eşitlik korunur, karma
    #: kimlikten (`alan`+`metin`) hesaplanır — bir pill kümeye konulabilsin diye.
    deger: Any = field(hash=False)
    #: Kullanıcı bu pill'i **kaldırabilir mi**. `False` olan ikisi de türevdir:
    #: tek ölçü (ölçüsüz fiş bir sorgu değildir) ve `tur` (ötekilerden **doğar**).
    silinebilir: bool = True


@dataclass(frozen=True)
class Secenek:
    """Bir `+`'ın **kapalı gramerdeki** tek bir seçeneği: kimlik + Türkçesi."""

    deger: str
    metin: str


@dataclass(frozen=True)
class Arti:
    """🔴 **TİPLİ `+`.** Kendi alanını, sonucunu ve seçeneklerini **beyan eder**."""

    #: `ARTI_TIPLERI` kapalı kümesinden.
    tip: str
    metin: str
    #: Büyüttüğü `Niyet` alanının adı — `adim`'da `None` (plan doğurur, alan değil).
    alan: str | None
    #: `SONUC_TEK_SORGU` | `SONUC_PLAN` — *«bu `+` ne üretir»* sorusunun **tek** cevabı.
    sonuc: str
    secenekler: tuple[Secenek, ...] = ()


@dataclass(frozen=True)
class PillHatasi:
    """Geçersiz kombinasyon — **hangi pill** ve **neden** (Türkçe, koşmadan)."""

    alan: str
    deger: Any = field(hash=False)
    #: 🔴 Bir hata kodu değil, kullanıcının okuyacağı **cümle**. `§5.3`'ün tamamı:
    #: *«pill kırmızıya döner **ve nedenini söyler**»* — ikincisi olmadan birincisi
    #: bir şikâyettir (`§RK-2`: *bir uyarı, yapılacak şeyi göstermiyorsa şikâyettir*).
    neden: str


# ═══════════════════════════════════════════════════════════════════════════════
# `§5.2` — PILL SATIRI
# ═══════════════════════════════════════════════════════════════════════════════

def pillerden(niyet: Niyet, schema: dict[str, Any] | None = None) -> list[Pill]:
    """🔴 `Niyet` → pill satırı. **Yeni model kurulmaz, mevcut model çizilir.**

    Sözleşme — her pill'in `deger`i bir `Niyet` alanından **birebir** gelir:

        olcu_adaylari  → her aday bir pill        (n adet)
        donemler       → TEK pill                 (0 ya da 1 adet)
        kirilimlar     → her boyut bir pill       (n adet)
        turler         → her tür bir pill         (n adet)

    ⚠ **`donemler` neden TEK pill:** liste bir *«dönem listesi»* değil, **bir**
    dönemin sınır süzgeçleridir (`gte` + `lte`). `donem_capasi.not_metni` o listeyi
    **zaten** tek bir aralık olarak okuyor; pill de öyle okur. İki pill çizmek
    (*«01.08 sonrası»* + *«31.08 öncesi»*) kullanıcıya **bir** niyeti **iki** kutuda
    gösterirdi — `KAT-1`'in görsel hâli.

    ⚠ `schema` **isteğe bağlıdır**: yoksa etiketler teknik addan türetilir. Katalog
    olmadan da pill satırı çizilebilmeli, çünkü `Niyet`in çözümleme yarısı (`coz_soru`)
    şemasız üretilebiliyor — *bir okumanın önkoşulu, okuduğu nesneninkinden ağır
    olamaz.*
    """
    pills: list[Pill] = []

    # ── olcu_adaylari ──────────────────────────────────────────────────────────
    # 🔴 Tek aday **silinemez**: ölçüsüz bir fiş bir sorgu değildir (`§KV`'nin
    # *«ölçüsüz bir fişte dönem sorulmaz»* kuralıyla aynı gerekçe). Birden çok aday
    # ise bir **belirsizliktir** ve silmek onu daraltır — yani orada silme bir
    # kayıp değil, bir **cevaptır**.
    coklu = len(niyet.olcu_adaylari) > 1
    # 🔴 `§69` — **KÜP ADI BİR AYIRT EDİCİDİR; AYIRT ETMİYORSA GÜRÜLTÜDÜR.**
    #
    # ⊙ Canlıda ölçüldü (`s33`, kararsız garson teklifi): dört aday da **aynı** küpten
    # geldi (`oee`) ve satır *«OEE · OEE»* · *«performans · OEE»* · *«kalite · OEE»*
    # yazdı. Küp adı orada hiçbir şeyi ayırmıyor — yalnız her pill'i uzatıyor.
    #
    # ⚠ Ölçüt `silinebilir`den **ayrıldı** ve bu bilinçli ⑯: silinebilirlik *«birden çok
    # ADAY var mı»* sorusunun cevabıdır (tek adayı silmek fişi ölçüsüz bırakır), etiket
    # ise *«hangi KATALOGDAN»* sorusunun. İkisini tek bayrakla sürmek, bir ekranı öteki
    # uğruna bozmaktı — `t13` (`elektrik` ↔ `tep`, **iki** küp) küp adını hâlâ görmeli.
    coklu_kup = len({c for c, _ in niyet.olcu_adaylari}) > 1
    for cube, olcu in niyet.olcu_adaylari:
        pills.append(Pill(alan=ALAN_OLCU,
                          metin=_olcu_metni(cube, olcu, schema, coklu_kup),
                          deger=(cube, olcu),
                          silinebilir=coklu))
    # ── varlık (soruda geçen katalog DEĞERİ) ───────────────────────────────────
    # 🔴 `§51` — Kullanıcı `«ram 3»` yazdığında pill satırı yalnız `['toplam']`
    # gösteriyordu: yazdığı **şey** hiçbir yuvada görünmüyordu. `Niyet.filtreler` artık
    # değer filtresini taşıyor (`niyet._varlik_filtreleri`) ve burada **çizilir**.
    # ⚠ Dönem filtreleri bu bandın dışında (`tarih` boyutu kendi pill'ini alıyor);
    # ikisini karıştırmak, bir dönemi bir varlık gibi göstermek olurdu 🆪.
    for f in niyet.filtreler:
        boyut, deger = str(f.get("dimension") or ""), f.get("value")
        if not boyut or boyut == "tarih" or deger in (None, ""):
            continue
        pills.append(Pill(alan=ALAN_VARLIK, metin=str(deger),
                          deger=(boyut, deger), silinebilir=True))

    # ── donemler ───────────────────────────────────────────────────────────────
    if niyet.donemler:
        pills.append(Pill(alan=ALAN_DONEM,
                          metin=_donem_metni(niyet.donemler),
                          deger=list(niyet.donemler),
                          silinebilir=True))

    # ── kirilimlar ─────────────────────────────────────────────────────────────
    for boyut in niyet.kirilimlar:
        pills.append(Pill(alan=ALAN_KIRILIM,
                          metin=_kirilim_metni(boyut, niyet, schema),
                          deger=boyut,
                          silinebilir=True))

    # ── turler ─────────────────────────────────────────────────────────────────
    # 🔴 **Silinemez, çünkü TÜREV.** `TUR_KIRILIM` bir kırılım pill'inden, `TUR_TREND`
    # granülerlikten doğar. Bir türü silmek, doğduğu pill dururken onu yok saymaktır —
    # ve o an ekranda **iki farklı niyet** olurdu. Kullanıcı türü değil, **sebebini**
    # siler. *Bir türevi bağımsızca düzenlenebilir yapmak, iki değeri garanti etmektir.*
    for tur in _tur_sirasi(niyet.turler):
        pills.append(Pill(alan=ALAN_TUR,
                          metin=_tur_metni(tur, niyet),
                          deger=tur,
                          silinebilir=False))

    return pills


def artilar(niyet: Niyet, schema: dict[str, Any] | None = None) -> list[Arti]:
    """🔴 **DÖRT TİPLİ `+`** — her biri kendi alanını, sonucunu ve seçeneklerini beyan eder.

    Dördü **her zaman** döner (sayı sabit): bir `+`'ın *«bu bağlamda yok»* diye
    kaybolması, kullanıcıya arayüzün kendisini öğrenmeyi yeniden başlatırdı. Bağlam
    `secenekler`i daraltır, `+`'ın kendisini değil.

    ⚠ Seçenekler **kapalı gramerden** gelir ve dördünün de sahibi başkasıdır:
    ölçü/kırılım → **katalog**, dönem → `donem_capasi.DONEM_SECENEKLERI`,
    adım → `plan_semasi.FIILLER` (o da yetenek kaydından türer). Burada hiçbir liste
    **yazılmaz**.
    """
    return [
        Arti(tip=t, metin=ARTI_METNI[t], alan=ARTI_ALANI[t], sonuc=ARTI_SONUCU[t],
             secenekler=_secenekler(t, niyet, schema))
        for t in ARTI_TIPLERI
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# `§5.3` — CANLI DOĞRULAMA · *«imkânsız soru sorulamaz hâle gelir»*
# ═══════════════════════════════════════════════════════════════════════════════

def dogrula(niyet: Niyet, schema: dict[str, Any]) -> list[PillHatasi]:
    """🔴🔴 Geçersiz kombinasyonu **koşmadan** bulur ve **Türkçe** nedenini söyler.

    Üç kaynak, üçünün de sahibi başka bir modül:

    1. **Temsil boşluğu** — `Niyet.temsil_edilemeyen` (şema gerekmez).
       *«İki ayrı dönem adlandı, `CubeQuery` bir aralık taşır.»*
    2. **Katalog** — `cube_router.parse_cube_query` beyaz listesi, **artımlı** sorulur.
       *«O kırılım bu küpte yok.»*
    3. **Grain** — `cube_router.is_period_optional` (`R8`) + `GRANULERLIKLER`.
       *«Bakiye dönem-SONU değeridir, zaman kovasına bölünemez.»*

    Boş liste = *«bu kombinasyon koşulabilir»*. ⚠ Bu bir **doğru cevap** vaadi
    değildir; yalnızca *«motor bunu reddetmeyecek»* demektir — doğruluğun sahibi
    hâlâ küptür (*«sayıyı küp koyar»*).
    """
    hatalar: list[PillHatasi] = []
    hatalar.extend(_temsil_hatalari(niyet))
    hatalar.extend(_katalog_hatalari(niyet, schema))
    hatalar.extend(_grain_hatalari(niyet, schema))
    return hatalar


# ── ① TEMSİL BOŞLUĞU — şema GEREKMEZ ───────────────────────────────────────────

#: `Niyet.temsil_edilemeyen`in kapalı kümesi → hangi pill kırmızıya döner.
#: ⚠ Metinler **yapılacak şeyi** söyler; *«temsil edilemiyor»* demek bir hata kodudur.
_TEMSIL_ALANI: dict[str, str] = {"cok_donem": ALAN_DONEM, "kiyas": ALAN_TUR}


def _temsil_hatalari(niyet: Niyet) -> list[PillHatasi]:
    out: list[PillHatasi] = []
    for eksik in niyet.temsil_edilemeyen:
        if eksik == "cok_donem":
            out.append(PillHatasi(
                alan=ALAN_DONEM, deger=list(niyet.donemler) or None,
                neden=(f"Soru {niyet.donem_sayisi} ayrı dönem adlandırıyor; tek sorgu "
                       "en fazla BİR aralık taşır — dönemleri ayrı sorulara böl ya da "
                       "bir kıyas kur.")))
        elif eksik == "kiyas":
            out.append(PillHatasi(
                alan=ALAN_TUR, deger=TUR_KIYAS,
                neden=("Kıyas istendi ama kıyaslanacak ikinci uç yok — "
                       "karşılaştırılacak dönemi de yaz.")))
    return out


# ── ② KATALOG — beyaz listeye ARTIMLI sorulur ──────────────────────────────────

def _katalog_hatalari(niyet: Niyet, schema: dict[str, Any]) -> list[PillHatasi]:
    """Her aday küpte fişi pill pill büyütür; **her adayda** düşen pill kırmızıdır."""
    index = _index(schema)
    adaylar = [(c, m) for c, m in niyet.olcu_adaylari if c in index]
    if not adaylar:
        # 🔴 Ölçüsüz bir fişte **doğrulanacak kombinasyon yoktur** — kullanıcı hâlâ
        # yazıyor olabilir ve boş bir satırı kırmızıya boyamak, arayüzü daha ilk
        # tuşta suçlayıcı yapardı. Ölçünün bulunamaması ayrı bir sınıftır ve adı
        # zaten konmuştur: `Niyet.SEBEP_OLCU_YOK` — sahibi de garson devridir.
        return []

    dusenler = [_kupte_dusenler(index, cube, olcu, niyet) for cube, olcu in adaylar]
    ortak = set(dusenler[0])
    for d in dusenler[1:]:
        ortak &= set(d)
    if not ortak:
        return []

    kupler = _kup_adlari([c for c, _m in adaylar], schema)
    out: list[PillHatasi] = []
    for anahtar in sorted(ortak, key=lambda a: (ALANLAR.index(a[0]), str(a[1]))):
        alan, _ = anahtar
        deger = dusenler[0][anahtar]
        out.append(PillHatasi(alan=alan, deger=deger,
                              neden=_katalog_nedeni(alan, deger, niyet, schema, kupler)))
    return out


def _kupte_dusenler(index: dict[str, dict], cube: str, olcu: str,
                    niyet: Niyet) -> dict[tuple[str, str], Any]:
    """Bu küpte hangi pill'ler beyaz listeden **geçmiyor** — sebep metni ÜRETİLMEZ.

    🔴 Fiş **kabul edilmiş hâliyle** büyür: geçmeyen bir ekleme fişe **girmez**.
    Girseydi ondan sonraki her ekleme de düşer ve tek bir geçersiz kırılım, satırın
    **tamamını** kırmızıya boyardı. *Bir suçluyu bulmak isteyen, onu delil zincirinden
    çıkarmalıdır.*
    """
    from app import cube_router as cr

    def gecer(fis: dict) -> bool:
        return cr.parse_cube_query(json.dumps(fis, ensure_ascii=False), index) is not None

    dusen: dict[tuple[str, str], Any] = {}
    kabul: dict[str, Any] = {"cube": cube, "measures": [olcu]}
    if not gecer(kabul):
        # Taban geçmiyorsa üstüne bir şey denenmez: ölçüsü olmayan bir küpte
        # kırılımı sormak, olmayan bir sorunun cevabını aramaktır.
        dusen[(ALAN_OLCU, olcu)] = (cube, olcu)
        return dusen

    for boyut in niyet.kirilimlar:
        aday = {**kabul, "dimensions": [*kabul.get("dimensions", []), boyut]}
        if gecer(aday):
            kabul = aday
        else:
            dusen[(ALAN_KIRILIM, boyut)] = boyut

    if niyet.donemler:
        zaman = (index[cube].get("time_dimensions") or [])
        if not zaman:
            # 🔴 Zaman ekseni olmayan bir küpte dönem süzgeci **uygulanamaz** — ve bu,
            # beyaz listenin de vereceği karardır (`allowed_filter_dims` boş kalır).
            # Eksen adı burada **seçilir, icat edilmez**: `Niyet.donemler` varsayılan
            # `tarih` adıyla üretilir (`niyet._coz_soru`), küpün ekseni başka ad
            # taşıyabilir; izdüşüm bir doğrulama değil, bir **projeksiyondur**.
            dusen[(ALAN_DONEM, "")] = list(niyet.donemler)
        else:
            aday = {**kabul, "filters": [{**f, "dimension": zaman[0]}
                                         for f in niyet.donemler]}
            if gecer(aday):
                kabul = aday
            else:
                dusen[(ALAN_DONEM, "")] = list(niyet.donemler)
    return dusen


def _katalog_nedeni(alan: str, deger: Any, niyet: Niyet, schema: dict[str, Any],
                    kupler: str) -> str:
    if alan == ALAN_OLCU:
        cube, olcu = deger
        return (f"«{_olcu_etiketi(cube, olcu, schema)}» ölçüsü {kupler} kataloğunda "
                "tanımlı değil — koşulamaz.")
    if alan == ALAN_KIRILIM:
        return (f"«{_kirilim_etiketi(deger, niyet, schema)}» boyutu {kupler} küpünde "
                "yok — bu ölçü o kırılımda dağıtılamaz.")
    return (f"{kupler} küpünde zaman ekseni yok — dönem süzgeci uygulanamaz, "
            "dönemi kaldır.")


# ── ③ GRAIN — `R8` kuralının pill karşılığı ────────────────────────────────────

def _grain_hatalari(niyet: Niyet, schema: dict[str, Any]) -> list[PillHatasi]:
    """🔴 *«Grain ihlali `compose`'da **zaten** yakalanıyor → pill kırmızıya döner»*
    (planın `§25` risk tablosu, 14. madde).

    Burada yakalanan iki şey var ve ikisi de **koşmadan** bilinebilir:

    * **Zaman kovası kapalı kümenin dışında** — sahibi `cube_operatorleri`.
    * **Yarı-toplanır ölçü ⊗ zaman kovası** — `cube_router`'ın `R8` reddi: bakiye/stok
      dönem-**SONU** değeridir; kovalı düz `SUM` *«dönemin net hareketi»*ni verir ve
      bunu `source=cube` rozetiyle sunar. Yani sessiz-yanlış. Bugün bu red **koşum
      anında** düşüyor; pill onu **yazım anına** taşır.
    """
    gran = niyet.granulerlik
    if not gran:
        return []

    from app import cube_operatorleri as ops
    from app import cube_router as cr

    if gran not in ops.GRANULERLIKLER:
        return [PillHatasi(
            alan=ALAN_TUR, deger=TUR_TREND,
            neden=(f"«{gran}» bir zaman kovası değil — geçerli kovalar: "
                   f"{', '.join(ops.GRANULERLIKLER)}."))]

    index = _index(schema)
    adaylar = [(c, m) for c, m in niyet.olcu_adaylari if c in index]
    if not adaylar:
        return []

    kupler = _kup_adlari([c for c, _m in adaylar], schema)
    if all(not (index[c].get("time_dimensions") or []) for c, _m in adaylar):
        return [PillHatasi(
            alan=ALAN_TUR, deger=TUR_TREND,
            neden=(f"{kupler} küpünde zaman ekseni yok — {_gran_metni(gran)} seyir "
                   "çizilemez."))]

    # ⚠ `is_period_optional` **çağrılır**, `semi_additive` listesi burada okunmaz:
    # *«hangi ölçüde dönem isteğe bağlıdır»* sorusunun tek gerçek kaynağı odur.
    if all(cr.is_period_optional(m, index[c]) for c, m in adaylar):
        ad = _olcu_etiketi(adaylar[0][0], adaylar[0][1], schema)
        return [PillHatasi(
            alan=ALAN_TUR, deger=TUR_TREND,
            neden=(f"«{ad}» dönem-SONU değeridir (bakiye/stok); {_gran_metni(gran)} "
                   "kovaya bölünürse dönemin net hareketi çıkar — grain ihlali. "
                   "Kovayı kaldır, güncel değeri sor."))]
    return []


# ═══════════════════════════════════════════════════════════════════════════════
# METİN — kullanıcıya görünen Türkçe. Hiçbiri bir DİL KURALI değil.
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 Burada **morfoloji yok**: *«makineye göre»* gibi ek gerektiren bir kalıp
# üretilmez (`CLAUDE.md`: *route'a dil kuralı EKLEME*). Kullanılan biçim
# `report.bolum_basligi`'nın **zaten** ürettiği biçimdir — *«makine kırılımı»*,
# *«aylık seyir»* — yani ikinci bir üslup doğmaz.

def _olcu_metni(cube: str, olcu: str, schema: dict[str, Any] | None, coklu: bool) -> str:
    ad = _olcu_etiketi(cube, olcu, schema)
    if not coklu:
        return ad
    # 🔴 Çok sahipli terim (`§A.2`): küp adı **ayırt edici**dir, yoksa iki pill aynı
    # metni taşır ve kullanıcı hangisini sildiğini bilemez.
    # ⚠ `§69` — ama küp etiketi **ölçü etiketinin aynısıysa** eklemek bir şeyi ayırmaz:
    # *«OEE · OEE»* iki kez aynı sözcüktür (canlı ölçüm). Bu ikinci kural birinciyi
    # zayıflatmaz — iki küpten biri böyleyse öteki hâlâ kendi adıyla ayrılır.
    kup = _kup_etiketi(cube, schema)
    return ad if kup.casefold() == ad.casefold() else f"{ad} · {kup}"


def _olcu_etiketi(cube: str, olcu: str, schema: dict[str, Any] | None) -> str:
    meta = _meta(schema, cube) or {}
    etiket = (meta.get("measure_synonyms_display") or {}).get(olcu)
    return str(etiket or olcu).replace("_", " ")


def _kup_etiketi(cube: str, schema: dict[str, Any] | None) -> str:
    meta = _meta(schema, cube) or {}
    return str(meta.get("display") or cube).replace("_", " ")


def _kup_adlari(cubeler: list[str], schema: dict[str, Any] | None) -> str:
    """Aday küplerin Türkçe adları — nedende **hangi katalog** olduğu görünsün diye."""
    adlar: list[str] = []
    for c in cubeler:
        ad = _kup_etiketi(c, schema)
        if ad not in adlar:
            adlar.append(ad)
    return "«" + "» / «".join(adlar) + "»"


def _kirilim_metni(boyut: str, niyet: Niyet, schema: dict[str, Any] | None) -> str:
    return f"{_kirilim_etiketi(boyut, niyet, schema)} kırılımı"


def _kirilim_etiketi(boyut: str, niyet: Niyet, schema: dict[str, Any] | None) -> str:
    """Boyutun Türkçesi — **önce aday küpler**, sonra katalogun geri kalanı.

    ⚠ İkinci tur bilerek var: kırmızıya dönen bir kırılım **tanım gereği** aday küpte
    yoktur, yani etiketi de orada bulunamaz. Etiketsiz bir kırmızı pill kullanıcıya
    teknik ad gösterirdi — *bir hata mesajı, hatanın kendisinden daha anlaşılır olmak
    zorundadır.*
    """
    for cube, _olcu in niyet.olcu_adaylari:
        etiket = ((_meta(schema, cube) or {}).get("dimension_labels") or {}).get(boyut)
        if etiket:
            return str(etiket).replace("_", " ")
    for meta in ((schema or {}).get("cubes") or []):
        etiket = (meta.get("dimension_labels") or {}).get(boyut)
        if etiket:
            return str(etiket).replace("_", " ")
    return str(boyut).replace("_", " ")


def _tur_metni(tur: str, niyet: Niyet) -> str:
    """Türün Türkçesi — `granulerlik` ve `ustunluk` **burada** görünür, ayrı pill olarak
    değil. *Bir niyeti iki kutuda göstermek, iki niyet göstermektir.*"""
    temel = TUR_METNI.get(tur, str(tur))
    if tur == TUR_TREND and niyet.granulerlik:
        return f"{_gran_metni(niyet.granulerlik)} {temel}"
    if tur == TUR_USTUNLUK and niyet.ustunluk:
        return f"en yüksek {niyet.ustunluk}"
    return temel


def _gran_metni(gran: str) -> str:
    """Granülerliğin Türkçesi — sahibi `report._GRAN_ADI`, ikinci sözlük yazılmaz."""
    from app.report import _GRAN_ADI

    return str(_GRAN_ADI.get(str(gran), gran))


#: `date_filters`ın ürettiği sınır operatörleri — `donem_capasi.not_metni` ile **aynı**
#: okuma. ⚠ Adlar `cube_operatorleri.MOTOR_OPERATORLERI`'nin üyeleridir; burada bir
#: operatör **tanımlanmaz**, yalnız hangisinin alt/üst sınır olduğu söylenir.
_ALT_SINIR = ("gte", ">=", ">", "gt")
_UST_SINIR = ("lte", "<=", "<", "lt")


def _donem_metni(filtreler: list[dict]) -> str:
    """Dönem süzgeçlerinin **tek** Türkçe karşılığı: *«01.08.2026 – 31.08.2026»*.

    ⚠ Gün biçimi `donem_capasi._gun`dan gelir — ikinci bir tarih biçimleyici yazmak,
    aynı tarihin iki farklı yazımını garanti etmekti.
    """
    from app.donem_capasi import _gun

    ilk = next((str(f.get("value"))[:10] for f in filtreler
                if str(f.get("operator")) in _ALT_SINIR), None)
    son = next((str(f.get("value"))[:10] for f in filtreler
                if str(f.get("operator")) in _UST_SINIR), None)
    if ilk and son:
        return f"{_gun(ilk)} – {_gun(son)}"
    if ilk:
        return f"{_gun(ilk)} sonrası"
    if son:
        return f"{_gun(son)} öncesi"
    return "dönem"


def _tur_sirasi(turler) -> list[str]:
    """Kümeyi **belirlenimli** sıraya koyar; tanınmayan tür sona, alfabetik."""
    bilinen = [t for t in TUR_SIRASI if t in turler]
    kalan = sorted(str(t) for t in turler if t not in TUR_SIRASI)
    return bilinen + kalan


# ═══════════════════════════════════════════════════════════════════════════════
# `+` SEÇENEKLERİ — dördü de KAPALI GRAMERDEN, hiçbiri burada yazılmaz
# ═══════════════════════════════════════════════════════════════════════════════

def _secenekler(tip: str, niyet: Niyet, schema: dict[str, Any] | None) -> tuple[Secenek, ...]:
    if tip == ARTI_OLCU:
        return _olcu_secenekleri(niyet, schema)
    if tip == ARTI_KIRILIM:
        return _kirilim_secenekleri(niyet, schema)
    if tip == ARTI_DONEM:
        return _donem_secenekleri()
    return _adim_secenekleri()


def _olcu_secenekleri(niyet: Niyet, schema: dict[str, Any] | None) -> tuple[Secenek, ...]:
    """Aday küplerin **NL yüzeyindeki** ölçüleri; ölçü henüz yoksa **tüm** katalog.

    ⚠ `nl: false` ölçüler menüde de **yok**: onlar bir oranın paydasıdır, kullanıcının
    soracağı bir sayı değil (`wren_service`'in kendi gerekçesi). Açıkça istenebilmeleri
    için `/cube` yolu duruyor — menüden çıkmak, kaldırılmak değildir.
    """
    secili = {(c, m) for c, m in niyet.olcu_adaylari}
    out: list[Secenek] = []
    for meta in _kupler(niyet, schema, hepsi_ise_bos=False):
        ad = str(meta.get("name") or "")
        for olcu in meta.get("measures") or []:
            if olcu not in (meta.get("measure_synonyms") or {}):
                continue                          # NL yüzeyi dışında (`nl: false`)
            if (ad, olcu) in secili:
                continue
            out.append(Secenek(deger=f"{ad}.{olcu}",
                               metin=_olcu_metni(ad, olcu, schema, coklu=True)))
    return tuple(out)


def _kirilim_secenekleri(niyet: Niyet, schema: dict[str, Any] | None) -> tuple[Secenek, ...]:
    """Aday küplerin boyutları. 🔴 **Ölçü yoksa seçenek de yok** — küp bilinmeden
    boyut bilinmez (`§KV`: *«ölçüsüz bir fişte dönem sorulmaz»* ile aynı gerekçe)."""
    secili = set(niyet.kirilimlar)
    out: list[Secenek] = []
    for meta in _kupler(niyet, schema, hepsi_ise_bos=True):
        for boyut in meta.get("dimensions") or []:
            if boyut in secili or any(s.deger == boyut for s in out):
                continue
            out.append(Secenek(deger=boyut,
                               metin=_kirilim_metni(boyut, niyet, schema)))
    return tuple(out)


def _donem_secenekleri() -> tuple[Secenek, ...]:
    """`donem_capasi.DONEM_SECENEKLERI` — *«hangi dönemleri tek tıkla seçebilirim»*
    sorusunun **tek** cevabı; o modül bu listeyi zaten iki çağırana veriyor."""
    from app.donem_capasi import DONEM_SECENEKLERI

    return tuple(Secenek(deger=str(d["query"]), metin=str(d["label"]))
                 for d in DONEM_SECENEKLERI)


def _adim_secenekleri() -> tuple[Secenek, ...]:
    """`plan_semasi.FIILLER` — kapalı fiil kümesi; o da **yetenek kaydından** türer
    (`_fiilleri_kayittan_dogrula`), yani buradaki liste kaydın izdüşümüdür."""
    from app.plan_semasi import FIIL_ANLAMI, FIILLER

    return tuple(Secenek(deger=f, metin=str(FIIL_ANLAMI.get(f, f))) for f in FIILLER)


# ═══════════════════════════════════════════════════════════════════════════════
# ŞEMA OKUMA — dışarıdan verilir, hiçbir yerde derlenmez
# ═══════════════════════════════════════════════════════════════════════════════

def _index(schema: dict[str, Any] | None) -> dict[str, dict]:
    """`parse_cube_query`nin beklediği `{ad: küp}` biçimi. Bir **yeniden şekillendirme**,
    bir doğrulama değil — beyaz liste hâlâ orada."""
    return {str(c.get("name")): c
            for c in ((schema or {}).get("cubes") or []) if c.get("name")}


def _meta(schema: dict[str, Any] | None, cube: str) -> dict | None:
    """Küp meta'sı — sahibi `cube_router._cube_meta`, ikinci bulucu yazılmaz."""
    if not schema:
        return None
    from app import cube_router as cr

    return cr._cube_meta(schema, cube)


def _kupler(niyet: Niyet, schema: dict[str, Any] | None,
            *, hepsi_ise_bos: bool) -> list[dict]:
    """Niyetin aday küpleri. Aday yoksa: ölçü menüsü **tüm** katalogdur (giriş noktası),
    kırılım menüsü **boştur** (önce ölçü, sonra kırılım)."""
    index = _index(schema)
    adlar: list[str] = []
    for cube, _olcu in niyet.olcu_adaylari:
        if cube in index and cube not in adlar:
            adlar.append(cube)
    if adlar:
        return [index[a] for a in adlar]
    return [] if hepsi_ise_bos else list(index.values())
