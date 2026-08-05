"""KONUŞMA ÜRETECİ — *tek soru değil, akan sohbet.*

## 🔴 Neden bu dosya var

Bugüne kadar kurduğumuz her şey **tek soruyu** ölçüyordu. Ama ürün bir sohbet
motoru: kullanıcı bir soru sorar, cevabı görür, **üstüne** bir şey daha söyler,
sonra bir şey daha. Kullanıcının kendi cümlesiyle:

> *"chatte 1 sordun cevap geldi üstüne bi şey daha bi şey daha gibi akan mantık"*

Ve buradaki kusurlar **tek soruda görünmez**: bağlamın kayması, konu değişince eski
bağlamın yapışıp kalması, geri dönüşte bağlamın geri gelmemesi, *"teşekkürler"*
denince raporun kaybolması. Hepsi **turlar arasında** yaşar.

> ⚠ *Tek soruyu ölçen bir korpus, bir sohbet ürününün yarısını ölçer — ve ölçmediği
> yarı, kullanıcının zamanının çoğunu geçirdiği yarıdır.*

## 🔵 SONSUZ UZAY — ve akıllıca örnekleme

17 tur türü ve 8 turluk bir sohbet → **17⁸ ≈ 7 milyar** dizi. Hepsini üretmek
imkânsız, rastgele örneklemek ise ölçülemez.

Tekli soruda çözüm **pairwise** idi (her ikili kombinasyon). Dizide karşılığı
**GEÇİŞ KAPSAMI**dır: *her ardışık tur çiftinin* en az bir sohbette görünmesi.

| yaklaşım | sohbet sayısı | kapsam |
|---|---|---|
| tüm diziler | ~7×10⁹ | %100, imkânsız |
| rastgele N | N | ölçülemez |
| **geçiş kapsamı (bu dosya)** | **yüzler** | **17×17 geçişin %100'ü, kanıtlı** |

Gerekçe tekli soruyla aynı: bir bağlam kusuru tipik olarak **iki ardışık turun
etkileşiminden** doğar (*"kırılım ekledikten sonra konu değişirse"*), sekiz turun
aynı anda kesişmesinden değil.

⚠ Ve **derinlik ayrı bir eksen**: 2 · 3 · 5 · 8 turluk sohbetler ayrı ayrı üretilir,
çünkü *"beşinci turda bağlam hâlâ duruyor mu"* sorusu iki turlu bir sohbette
sorulamaz.

## Metamorfik BAĞINTILAR — sohbete özgü, altın cevap gerektirmez

`lab/metamorfik.py` tek soru için kurmuştu; sohbetin kendi bağıntıları var:

| bağıntı | beklenen | neyi yakalar |
|---|---|---|
| **bağlam sürer** | eksiltili tur, konuyu tekrarlamadan çözülmeli | bağlam kaybı |
| 🔴 **konu değişince bağlam DEĞİŞİR** | yeni konu eskisini ezmeli | bağlamın yapışması |
| **geri dönüşte geri gelir** | eski karta dönüş eski bağlamı verir | dallanma kaybı |
| **sosyal tur bağlamı BOZMAZ** | *"teşekkürler"* raporu düşürmemeli | ölçülmüş kusur |
| 🔴 **sıra önemlidir** | A→B ile B→A **farklı** sonuç vermeli | sıra körlüğü |
| **idempotens** | aynı takip iki kez → aynı sonuç | kararsızlık |

🔴 *"Sıra önemlidir"* bağıntısı, `metamorfik.py`'deki **negatif bağıntıların**
sohbetteki karşılığıdır: onsuz, her turu yok sayan bir ürün tüm testleri geçer.
"""

from __future__ import annotations

import random
from collections import Counter

# ═══════════════════════════════════════════════════════════════════════════════
# TUR TÜRLERİ — ürünün KENDİ tanıdıklarından + canlı senaryolardan
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ Bu liste hayalden değil: `app/followup.py` dört tür tanıyor (`NEDEN` · `NORMAL` ·
# `NE_YAPMALI` · `ISARET`), `lab/deneyim.py` 15 senaryo taşıyor, ve *"analiz et"*
# beşinci tür olarak plana yazılmış. Geri kalanı canlı turlarda görülen davranışlar.

T_ACILIS = "acilis"                 # sohbeti başlatan tam soru
T_DARALTMA = "daraltma"             # "sadece siyah renkte"
T_GENISLETME = "genisletme"         # "tüm yıl için"
T_KIRILIM = "kirilim_ekle"          # "makine bazında böl"
T_OLCU_EKLE = "olcu_ekle"           # "bir de fire ekle"          → KOMPOZİSYON
T_DONEM = "donem_degis"             # "peki geçen ay"
T_ATIF = "atif"                     # "bunu grafiğe dök"          → ANAFORA
T_NEDEN = "neden"                   # "neden?"                    → followup.NEDEN
T_NORMAL = "normal_mi"              # "normal mi?"                → followup.NORMAL
T_NE_YAPMALI = "ne_yapmali"         # "ne yapmalıyız?"            → followup.NE_YAPMALI
T_ANLAT = "anlat"                   # "bunu yorumla"              → beşinci tür
T_KONU_DEGIS = "konu_degis"         # bambaşka bir konu
T_GERI_DONUS = "geri_donus"         # "az önceki rapora dön"
T_SOSYAL = "sosyal"                 # "teşekkürler"
T_OZ_DUZELTME = "oz_duzeltme"       # "yok yok onu değil şunu"
T_BELIRSIZ = "belirsiz"             # "peki ya diğeri"
T_IC_ICE = "ic_ice"                 # 🔴 tek turda İKİ-ÜÇ istek birden

TUR_TURLERI = (
    T_ACILIS, T_DARALTMA, T_GENISLETME, T_KIRILIM, T_OLCU_EKLE, T_DONEM, T_ATIF,
    T_NEDEN, T_NORMAL, T_NE_YAPMALI, T_ANLAT, T_KONU_DEGIS, T_GERI_DONUS,
    T_SOSYAL, T_OZ_DUZELTME, T_BELIRSIZ, T_IC_ICE,
)

#: 🔴 Bağlamı **değiştirmesi gereken** turlar. Bu ayrım metamorfik bağıntının
#: belkemiği: konu değiştiği hâlde bağlam aynı kalıyorsa **yapışma** var demektir.
BAGLAM_DEGISTIREN = frozenset({T_ACILIS, T_KONU_DEGIS, T_OZ_DUZELTME, T_GERI_DONUS})

#: ⚠ Bağlamı **korumas** gereken turlar — *"teşekkürler"* dedikten sonra rapor
#: kaybolmamalı. Bu, canlı turda ölçülmüş bir kusur sınıfıdır (sosyal edim dolgudur).
BAGLAM_KORUYAN = frozenset({T_SOSYAL})

#: Bir **açılış** olamayacak turlar: bağlam yokken *"neden?"* demek anlamsızdır ve
#: doğru davranış **dürüst rettir**. ⚠ Yine de üretilir — çünkü kullanıcı gerçekten
#: böyle başlıyor, ve *"bağlamsız takip"* ölçülmesi gereken bir sınıftır.
ACILIS_OLAMAZ = frozenset(TUR_TURLERI) - {T_ACILIS, T_KONU_DEGIS, T_IC_ICE}


# ═══════════════════════════════════════════════════════════════════════════════
# TUR METİNLERİ — her tür için gerçek kullanıcı ağzından birkaç kalıp
# ═══════════════════════════════════════════════════════════════════════════════

_KALIPLAR: dict[str, tuple[str, ...]] = {
    T_DARALTMA: ("sadece {deger} olanlar", "yalnız {deger}", "{deger} için",
                 "bir de {deger} filtresi koy", "{deger} hariç"),
    T_GENISLETME: ("tüm yıl için", "filtreyi kaldır", "hepsini göster",
                   "geneli nasıl", "kısıtı kaldır"),
    T_KIRILIM: ("{boyut} bazında böl", "{boyut} kırılımı ekle", "{boyut}e göre dağıt",
                "bunu {boyut} bazında göster", "peki {boyut} bazında"),
    T_OLCU_EKLE: ("bir de {olcu2} ekle", "{olcu2} de gelsin", "yanına {olcu2} koy",
                  "{olcu2} ile birlikte", "ikisini birlikte göster"),
    T_DONEM: ("peki geçen ay", "geçen yıl neydi", "bu yıla bak",
              "son 3 ayı göster", "ya şubata göre", "martla kıyasla"),
    T_ATIF: ("bunu grafiğe dök", "şunu tabloya çevir", "onu indir",
             "bunu panoya ekle", "az önceki raporu paylaş"),
    T_NEDEN: ("neden", "neden böyle", "sebebi ne", "niye böyle çıktı", "neden arttı"),
    T_NORMAL: ("normal mi", "bu iyi mi", "beklenen bu mu", "sektörde de böyle mi"),
    T_NE_YAPMALI: ("ne yapmalıyız", "ne önerirsin", "nasıl düzeltiriz", "aksiyon ne"),
    T_ANLAT: ("bunu yorumla", "analiz et", "özetle", "bana bunu açıkla",
              "kısaca ne diyor bu"),
    T_GERI_DONUS: ("az önceki rapora dön", "ilk sorduğuma geri dön",
                   "en baştaki tabloya bak", "önceki karta dön"),
    T_SOSYAL: ("teşekkürler", "sağol", "harika", "eyvallah", "süper, teşekkür ederim"),
    T_OZ_DUZELTME: ("yok yok onu değil", "pardon, şunu demek istedim",
                    "dur, yanlış oldu", "hayır onu değil {olcu2}yi"),
    T_BELIRSIZ: ("peki ya diğeri", "ya öteki", "bir de şuna bak", "diğerleri nasıl"),
}


def _tur_metni(tur: str, baglam: dict, rng: random.Random) -> str:
    """Bir turun metnini üretir. Açılış/konu değişimi/iç içe **dışarıdan** gelir."""
    kalip = rng.choice(_KALIPLAR[tur])
    return kalip.format(
        boyut=baglam.get("boyut") or "makine",
        olcu2=baglam.get("olcu2") or "fire",
        deger=baglam.get("deger") or "siyah",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 GEÇİŞ KAPSAMI — dizideki pairwise
# ═══════════════════════════════════════════════════════════════════════════════

def gecis_kapsami(uzunluklar: tuple[int, ...], rng: random.Random) -> list[list[str]]:
    """Her **ardışık tur çiftini** en az bir sohbette içeren dizi kümesi.

    ## Algoritma ve neden bu

    Hedef küme: tüm `(tur_i, tur_j)` çiftleri. Her turda **kapanmamış çiftlerden**
    biri seçilir ve zincire eklenir; kapanan çift hedeften düşer. Bir sohbet
    uzunluğu dolunca yenisi başlar.

    ⚠ Sohbet **her zaman bir açılışla başlamaz** — bilerek. Kullanıcı gerçekten
    *"neden?"* diye başlıyor (yeni sekmede eski konuyu sanıyor) ve doğru davranış
    **dürüst rettir**. Bu sınıfı üretmemek, onu ölçmemek olurdu.

    🔴 Ama **çoğunluk** açılışla başlar (%70): aksi hâlde korpus gerçek kullanımı
    değil, kenar durumu ölçerdi. *Bir kenar durumu ölçmek onu merkeze taşımak
    değildir.*
    """
    hedef = {(a, b) for a in TUR_TURLERI for b in TUR_TURLERI}
    sohbetler: list[list[str]] = []
    # 🔴 SONSUZ DÖNGÜ — ölçüldü, ve tam da bu satırlarda yaşıyordu.
    #
    # İlk yazımım her turu **rastgele bir turla** başlatıp zinciri uzatıyordu:
    #
    #     zincir = [T_ACILIS if rng.random() < 0.70 else rng.choice(TUR_TURLERI)]
    #     ...  adaylar = [b for (a, b) in hedef if a == son]
    #
    # Kalan kapanmamış çiftlerin hepsi `X` ile başlıyorsa ve zincir hiçbir turda
    # `X`'e uğramıyorsa, o çiftler **hiçbir zaman** kapanmaz — döngü döner durur.
    # %70 `T_ACILIS` başlangıcı bunu ağırlaştırıyordu: uzun kuyruk fiilen sonsuz.
    # (Bir kapı testi 6+ dakika tek çekirdekte asılı kaldı; ilk teşhisim "regex
    # geri-izlemesi" idi ve **yanlıştı** — sebep buradaki ilerleme garantisizliğiydi.)
    #
    # > ⚠ *Rastgele arama, aradığı şeye ulaşacağını garanti etmez; yalnız
    # > ulaşabileceğini gösterir. Bir kapsam algoritması ihtimalle değil,
    # > **inşayla** ilerlemelidir.*
    #
    # Düzeltme: her tur **kapanmamış bir çiftle başlar** → o çift o turda kesin
    # kapanır → en çok `len(hedef)` tur, yani **289**. Terminasyon artık bir umut
    # değil, bir üst sınır.
    GUVENLIK_TAVANI = len(TUR_TURLERI) ** 2 + 50
    while hedef:
        if len(sohbetler) > GUVENLIK_TAVANI:             # asla ulaşılmamalı
            raise RuntimeError(
                f"geçiş kapsamı yakınsamadı: {len(hedef)} çift kaldı — "
                "ilerleme garantisi bozulmuş, algoritmayı gözden geçir")
        boy = rng.choice(uzunluklar)
        # ⚠ Deterministik seçim (`sorted`) — rastgele seçim aynı tohumda farklı
        # korpus üretip *"dün geçen test bugün kaldı"* teşhisini imkânsızlaştırırdı.
        a0, b0 = sorted(hedef)[0]
        zincir = [a0, b0]
        # Gerçekçilik korunuyor: sohbetlerin çoğu bir açılışla başlar. Önek eklemek
        # (a0, b0) çiftini **düşürmez** — yalnız başına bir geçiş daha katar.
        if a0 != T_ACILIS and rng.random() < 0.70:
            zincir.insert(0, T_ACILIS)
        while len(zincir) < boy:
            son = zincir[-1]
            adaylar = sorted(b for (a, b) in hedef if a == son)
            zincir.append(adaylar[0] if adaylar else rng.choice(TUR_TURLERI))
        for a, b in zip(zincir, zincir[1:]):
            hedef.discard((a, b))
        sohbetler.append(zincir)
    return sohbetler


# ═══════════════════════════════════════════════════════════════════════════════
# SOHBET ÜRETİMİ — kataloğa bağlı
# ═══════════════════════════════════════════════════════════════════════════════

#: Sohbet derinlikleri. ⚠ Uzunluk **ayrı bir eksendir**: *"beşinci turda bağlam hâlâ
#: duruyor mu"* sorusu iki turlu bir sohbette sorulamaz.
UZUNLUKLAR = (2, 3, 5, 8)

#: Açılış/konu-değişimi havuzunun büyüklüğü. ⚠ Sohbet çeşitliliği **tur dizisinden**
#: gelir, açılış sorusunun kendisinden değil — havuzu büyütmek geçiş kapsamını
#: artırmaz, yalnız üretim maliyetini artırır.
ACILIS_HAVUZU = 1200


def uret(schema: dict, *, tohum: int = 20260805) -> tuple[list[dict], dict]:
    """Kataloğa bağlı, geçiş-kapsamlı sohbet korpusu üretir.

    Dönen: `(sohbetler, kapsam_raporu)` — her sohbet `{turlar: [...], ...}`.
    """
    from lab import senaryo_uretec as SU

    rng = random.Random(tohum)
    # ⚠ Sohbet üreteci tekil korpusu **yalnız açılış/konu-değişimi havuzu** için
    # kullanıyor; her sohbet ondan birkaç soru çekiyor. Tam korpusu (10 700 vaka)
    # üretmek bu iş için saf israftı — havuz zaten birkaç yüz sorudan sonra
    # doyuyor. *Bir kaynağın tamamını üretmek, ondan azını kullanacaksan maliyettir.*
    tekil, _ = SU.uret(schema, azami=ACILIS_HAVUZU)
    if not tekil:
        raise RuntimeError("tekil korpus boş — sohbet üretilemez")

    # Açılış ve konu değişimi için **gerçek** tekil sorular kullanılır: sohbet
    # üreteci kendi cümlesini kurmaz. ⚠ İki ayrı cümle kurucu olsaydı, biri
    # güncellenir öteki kalırdı — *aynı kuralın iki sahibi.*
    acilislar = [v for v in tekil if v["niyet"] in (SU.NIYET_DEGER, SU.NIYET_KIRILIM,
                                                    SU.NIYET_USTUNLUK, SU.NIYET_TREND)]
    acilislar = acilislar or tekil

    zincirler = gecis_kapsami(UZUNLUKLAR, rng)
    sohbetler: list[dict] = []
    for i, zincir in enumerate(zincirler):
        acilis = rng.choice(acilislar)
        baglam = {
            "cube": acilis["cube"], "olcu": acilis["olcu_ifade"],
            "boyut": acilis.get("boyut"), "olcu2": None, "deger": None,
        }
        # İkinci ölçü **başka bir cube'dan**: `olcu_ekle` turunun asıl zorluğu
        # çapraz-cube kompozisyonudur (canlı vakada `verimlilik` oee'de, `ciro` parti'de).
        baska = [v for v in tekil if v["cube"] != acilis["cube"]]
        baglam["olcu2"] = rng.choice(baska)["olcu_ifade"] if baska else "fire"

        turlar: list[dict] = []
        for j, tur in enumerate(zincir):
            if tur == T_ACILIS:
                metin, kaynak_vaka = acilis["soru"], acilis
            elif tur == T_KONU_DEGIS:
                yeni = rng.choice(baska or tekil)
                metin, kaynak_vaka = yeni["soru"], yeni
            elif tur == T_IC_ICE:
                metin, kaynak_vaka = _ic_ice(tekil, rng), None
            else:
                metin, kaynak_vaka = _tur_metni(tur, baglam, rng), None
            turlar.append({
                "sira": j, "tur": tur, "soru": metin,
                "beklenen_baglam": _beklenen_baglam(tur, baglam, kaynak_vaka),
                "kabul": _kabul(tur, j),
                "yasak": _yasak(tur),
            })
            if tur == T_KONU_DEGIS and kaynak_vaka:
                baglam = {**baglam, "cube": kaynak_vaka["cube"],
                          "olcu": kaynak_vaka["olcu_ifade"]}
        sohbetler.append({
            "no": i, "uzunluk": len(zincir), "turlar": turlar,
            "acilis_cube": acilis["cube"], "persona": acilis["persona"],
        })

    gecisler = {(a["tur"], b["tur"]) for s in sohbetler
                for a, b in zip(s["turlar"], s["turlar"][1:])}
    kapsam = {
        "sohbet": len(sohbetler),
        "tur": sum(len(s["turlar"]) for s in sohbetler),
        "gecis_kapsanan": len(gecisler),
        "gecis_hedef": len(TUR_TURLERI) ** 2,
        "gecis_yuzde": round(100 * len(gecisler) / len(TUR_TURLERI) ** 2, 1),
        "uzunluk": dict(Counter(s["uzunluk"] for s in sohbetler)),
        "tur_dagilimi": dict(Counter(t["tur"] for s in sohbetler for t in s["turlar"])),
    }
    return sohbetler, kapsam


def _ic_ice(tekil: list[dict], rng: random.Random) -> str:
    """🔴 **İç içe istek** — tek turda iki-üç şey birden.

    Kullanıcının kendi ifadesiyle: *"iç içe birden fazla şey isteyen sorular"*.
    Gerçek hayatta en sık şu biçimlerde gelir:

    - **ve/bir de** ile bağlanmış iki istek
    - bir istek + **koşullu** ikinci istek (*"eğer düştüyse nedenini de söyle"*)
    - bir istek + **biçim** isteği (*"…, grafikle"*)

    ⚠ Bu turun doğru cevabı **tek bir şey değildir**: ürün ya ikisini de yapmalı ya
    da *"önce hangisi"* diye sormalı. Sessizce **birini seçip ötekini düşürmek**
    yasaktır — ve tam olarak ölçmek istediğimiz şey budur.
    """
    a, b = rng.sample(tekil, 2) if len(tekil) > 1 else (tekil[0], tekil[0])
    return rng.choice((
        f"{a['soru']} ve {b['soru']}",
        f"{a['soru']}, bir de {b['soru']}",
        f"{a['soru']} — eğer düştüyse nedenini de söyle",
        f"{a['soru']} ayrıca {b['soru']} lazım, ikisini de grafikle",
        f"önce {a['soru']} sonra {b['soru']}",
    ))


def _beklenen_baglam(tur: str, baglam: dict, vaka: dict | None) -> dict:
    """Bu turdan **sonra** bağlamın ne olması gerektiği — metamorfik kıyas için."""
    if tur in BAGLAM_DEGISTIREN and vaka:
        return {"cube": vaka["cube"], "olcu": vaka["olcu_ifade"], "degisti": True}
    if tur in BAGLAM_KORUYAN:
        return {**{k: baglam[k] for k in ("cube", "olcu")}, "degisti": False,
                "not": "🔴 sosyal edim DOLGUDUR — raporu düşürmemeli"}
    return {**{k: baglam[k] for k in ("cube", "olcu")}, "degisti": False}


def _kabul(tur: str, sira: int) -> list[str]:
    """Beklenen davranış sınıfı — **kuraldan** türetilir.

    ⚠ `sira == 0` özel: bağlamsız bir takip turu (*"neden?"* diye başlamak) **dürüst
    ret** bekler. Aynı tur beşinci sırada geldiğinde ise cevap beklenir.
    *Aynı cümle, bulunduğu yere göre farklı doğru cevaba sahiptir — ve bu ayrımı
    yapmayan bir korpus, ürünü haksız yere ya cömert ya cimri gösterir.*
    """
    from lab.senaryo_uretec import DOGRU, DURUST_RET, NETLESTIRME

    if sira == 0 and tur in ACILIS_OLAMAZ:
        return [DURUST_RET, NETLESTIRME]
    if tur == T_SOSYAL:
        return [DURUST_RET, DOGRU]      # ya nazikçe cevapla ya bağlamı koru — ikisi de doğru
    if tur in (T_NE_YAPMALI,):
        return [DURUST_RET, NETLESTIRME]   # v1'de öneri YOK
    if tur in (T_BELIRSIZ, T_OZ_DUZELTME):
        return [NETLESTIRME, DURUST_RET]   # belirsiz atıf → sor, tahmin etme
    return [DOGRU, NETLESTIRME]


def _yasak(tur: str) -> str:
    return {
        T_SOSYAL: "🔴 sosyal edimi veri sorusu sanıp bağlamı DÜŞÜRMEK",
        T_KONU_DEGIS: "🔴 eski bağlamı yeni konuya YAPIŞTIRMAK",
        T_GERI_DONUS: "eski karta dönüşte eski bağlamı geri getirmemek",
        T_IC_ICE: "🔴 iki istekten birini SESSİZCE düşürmek",
        T_ATIF: "atfın neyi işaret ettiği belirsizken bir rapor üretmek",
        T_OLCU_EKLE: "ikinci ölçüyü yok sayıp ilk raporu tekrar vermek",
        T_BELIRSIZ: "belirsiz atıfta tahmin etmek",
        T_NE_YAPMALI: "v1'de olmayan öneri yeteneğini varmış gibi cevaplamak",
    }.get(tur, "bağlamı kaybetmek ya da yanlış cube'a kaymak")


# ═══════════════════════════════════════════════════════════════════════════════
# SOHBETE ÖZGÜ METAMORFİK BAĞINTILAR — altın cevap gerektirmez
# ═══════════════════════════════════════════════════════════════════════════════
#
# `lab/metamorfik.py` tek soru için kurmuştu. Sohbetin kendi bağıntıları var ve
# hiçbiri *"doğru cevap şu"* bilgisini gerektirmiyor — yalnız **turlar arası
# tutarlılık** ölçüyor.

#: `(kod, açıklama, beklenti)` — `beklenti`: `"ayni"` | `"farkli"`
SOHBET_BAGINTILARI = (
    ("s.baglam_surer",
     "Eksiltili tur, konuyu tekrarlamadan çözülmeli: T1 tam soru → T2 «makine "
     "bazında böl» → aynı cube kalmalı",
     "ayni"),
    ("s.sosyal_bozmaz",
     "🔴 «teşekkürler» bir veri sorusu DEĞİLDİR: araya girmesi bağlamı düşürmemeli. "
     "Ölçülmüş kusur sınıfı — sosyal edim dolgudur (Faz D1).",
     "ayni"),
    ("s.konu_degisir",
     "🔴 Konu değişince eski bağlam EZİLMELİ. Aynı kalması «yapışma»dır ve "
     "kullanıcı bambaşka bir şey sorarken eski raporun cevabını alır.",
     "farkli"),
    ("s.geri_donus",
     "Eski karta dönüş eski bağlamı GERİ GETİRMELİ — yoksa dallanma bir yanılsamadır.",
     "ayni"),
    ("s.sira_onemli",
     "🔴 A→B ile B→A FARKLI sonuç vermeli. «kırılım ekle sonra dönem değiştir» ile "
     "tersi aynı çıkıyorsa ürün turları yok sayıyordur. "
     "*Bu, tek-soru korpusundaki negatif bağıntıların sohbetteki karşılığıdır: "
     "onsuz, her turu görmezden gelen bir ürün tüm testleri geçer.*",
     "farkli"),
    ("s.idempotens",
     "Aynı takip iki kez üst üste → aynı sonuç. Farklıysa ürün kararsızdır.",
     "ayni"),
)


def bagintı_vakalari(sohbetler: list[dict]) -> list[dict]:
    """Sohbetlerden **metamorfik kıyas çiftleri** çıkarır.

    ⚠ Her sohbet her bağıntıyı taşımaz (sosyal turu olmayan bir sohbette
    `s.sosyal_bozmaz` ölçülemez). Taşımayan sohbet **atlanır**, zorlanmaz —
    *uygulanamayan bir bağıntıyı zorlamak, anlamı koruduğunu kanıtlayamadığımız
    bir kıyas üretir.*
    """
    out: list[dict] = []
    for s in sohbetler:
        turlar = s["turlar"]
        for i, t in enumerate(turlar[:-1]):
            sonraki = turlar[i + 1]
            # bağlam sürer: veri turundan sonra eksiltili tur
            if t["tur"] in (T_ACILIS, T_KONU_DEGIS) and sonraki["tur"] in (
                    T_KIRILIM, T_DARALTMA, T_DONEM, T_ATIF, T_ANLAT):
                out.append({"kod": "s.baglam_surer", "sohbet": s["no"],
                            "oncesi": t["soru"], "sonrasi": sonraki["soru"],
                            "beklenti": "ayni"})
            # sosyal araya girdi
            if sonraki["tur"] == T_SOSYAL and i + 2 < len(turlar):
                out.append({"kod": "s.sosyal_bozmaz", "sohbet": s["no"],
                            "oncesi": t["soru"], "sonrasi": turlar[i + 2]["soru"],
                            "araya_giren": sonraki["soru"], "beklenti": "ayni"})
            # konu değişimi
            if sonraki["tur"] == T_KONU_DEGIS:
                out.append({"kod": "s.konu_degisir", "sohbet": s["no"],
                            "oncesi": t["soru"], "sonrasi": sonraki["soru"],
                            "beklenti": "farkli"})
            # geri dönüş
            if sonraki["tur"] == T_GERI_DONUS:
                out.append({"kod": "s.geri_donus", "sohbet": s["no"],
                            "oncesi": turlar[0]["soru"], "sonrasi": sonraki["soru"],
                            "beklenti": "ayni"})
        # sıra önemli — aynı iki turu ters sırayla kur
        if len(turlar) >= 3:
            a, b = turlar[1], turlar[2]
            if a["tur"] != b["tur"] and T_SOSYAL not in (a["tur"], b["tur"]):
                out.append({"kod": "s.sira_onemli", "sohbet": s["no"],
                            "dizi_a": [turlar[0]["soru"], a["soru"], b["soru"]],
                            "dizi_b": [turlar[0]["soru"], b["soru"], a["soru"]],
                            "beklenti": "farkli"})
        # idempotens — bir takibi iki kez
        for t in turlar[1:]:
            if t["tur"] in (T_KIRILIM, T_DONEM, T_DARALTMA):
                out.append({"kod": "s.idempotens", "sohbet": s["no"],
                            "dizi_a": [turlar[0]["soru"], t["soru"]],
                            "dizi_b": [turlar[0]["soru"], t["soru"], t["soru"]],
                            "beklenti": "ayni"})
                break
    return out


def rapor(kapsam: dict, bagintılar: list[dict]) -> str:
    """Kapsam raporu — **kapsanmayanı** ve **ölçülemeyeni** öne alır."""
    s = ["# KONUŞMA KORPUSU — *tek soru değil, akan sohbet*", "",
         f"Sohbet: **{kapsam['sohbet']}** · tur: **{kapsam['tur']}** · "
         f"geçiş kapsamı: **{kapsam['gecis_kapsanan']}/{kapsam['gecis_hedef']}** "
         f"(%{kapsam['gecis_yuzde']})", "",
         "> 🔵 **Neden geçiş kapsamı:** 17 tur türü × 8 tur = ~7 milyar dizi. Hepsini "
         "üretmek imkânsız, rastgele örneklemek ölçülemez. Bir bağlam kusuru tipik "
         "olarak **iki ardışık turun etkileşiminden** doğar — bu yüzden ölçü, tüm "
         "ardışık çiftlerin kapsanmasıdır.", "",
         "| uzunluk | sohbet |", "|---|---|"]
    for u, n in sorted(kapsam["uzunluk"].items()):
        s.append(f"| {u} tur | {n} |")
    s += ["", "| tur türü | adet |", "|---|---|"]
    for t, n in sorted(kapsam["tur_dagilimi"].items(), key=lambda x: -x[1]):
        s.append(f"| `{t}` | {n} |")
    say = Counter(b["kod"] for b in bagintılar)
    s += ["", "## Metamorfik bağıntı vakaları", "",
          "| bağıntı | vaka | beklenti | ne yakalar |", "|---|---|---|---|"]
    for kod, aciklama, beklenti in SOHBET_BAGINTILARI:
        s.append(f"| `{kod}` | {say.get(kod, 0)} | **{beklenti}** | "
                 f"{aciklama.splitlines()[0][:90]} |")
    return "\n".join(s)


def main() -> int:                                          # pragma: no cover
    import argparse
    import pathlib

    from app.config import get_settings
    from app.wren_service import WrenService

    ap = argparse.ArgumentParser(description="Konuşma korpusu (çok turlu sohbet)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    sohbetler, kapsam = uret(svc.schema())
    bag = bagintı_vakalari(sohbetler)
    if a.json:
        import json
        print(json.dumps({"sohbetler": sohbetler, "kapsam": kapsam,
                          "bagintilar": bag}, ensure_ascii=False, indent=1))
        return 0
    metin = rapor(kapsam, bag)
    print(metin)
    hedef = pathlib.Path(__file__).resolve().parent / "reports" / "konusma_korpusu.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(f"\nRapor: {hedef}")
    return 0


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(main())
