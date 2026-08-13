"""🔴🔴 `§5.2` · `§5.3` — **PILL KATMANI** kapısı.

## Planın iki cümlesi, iki ölçüt

> `§5.2` — *«`Niyet` alanları ↔ pill'ler **birebir** … ikinci bir temsil doğmaz.»*
> `§5.3` — *«geçersiz kombinasyonda pill **kırmızıya döner ve nedenini söyler** —
> koşmadan … **imkânsız soru sorulamaz hâle gelir**.»*

Bu dosya üç şeyi ölçer ve üçü de planın kendi cümlesinden gelir:

1. **`+` DÖRT AYRI TİPTE** — tek bir `+` yasak (planın bir numaralı tuzağı: *«göre /
   bazında»* üç anlamlıydı ve bu depoyu **üç kez** ısırdı).
2. **Geçersiz kırılım NEDENİYLE kırmızı** — kırmızılık yetmez; *«çünkü …»* olmadan bir
   uyarı bir şikâyettir.
3. **Pill sayısı `Niyet` alanlarıyla BİREBİR** — pill katmanı bir **çizim**dir, ikinci
   bir model değil.

## ⚠ Kapı neden çoğunlukla SENTETİK şema kullanıyor

`§5.3`'ün tamamı *«koşmadan»*dır: doğrulama şemayı **dışarıdan** alır, hiçbir şey
derlemez. Sentetik bir katalog bu sözleşmeyi **kanıtlar** (üç küp: biri toplanır, biri
yarı-toplanır, biri **zaman eksensiz**) ve kapının kendi maliyeti milisaniyedir.

🔴 Ama sentetik bir katalog **bayat bir katalog** riskini taşır — bu depo o bedeli
ölçtü (`test_olcum_semasi_taze.py`). Bu yüzden son iki yüklem **gerçek MDL** ile koşar
ve gerçek `Niyet.coz` çıktısını doğrular: *bir okumanın doğruluğu, okuduğu kataloğun
gerçekliğinden büyük olamaz.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app.niyet import (
    TUR_KIRILIM,
    TUR_KIYAS,
    TUR_TOPLAM,
    TUR_TREND,
    TUR_USTUNLUK,
    Niyet,
)
from app.pill import (
    ALAN_DONEM,
    ALAN_KIRILIM,
    ALAN_KAYNAGI,
    ALAN_OLCU,
    ALAN_TUR,
    ALANLAR,
    ARTI_ADIM,
    ARTI_DONEM,
    ARTI_KIRILIM,
    ARTI_OLCU,
    ARTI_TIPLERI,
    SONUC_PLAN,
    SONUC_TEK_SORGU,
    artilar,
    dogrula,
    pillerden,
)

# ═══════════════════════════════════════════════════════════════════════════════
# SENTETİK KATALOG — üç küp, üçü de bir DOĞRULAMA SINIFI için var
# ═══════════════════════════════════════════════════════════════════════════════
#
#   uretim  → normal (toplanır) · zaman ekseni VAR · iki boyut
#   stok    → 🔴 YARI-TOPLANIR (`semi_additive`) → grain ihlali sınıfı
#   kadro   → 🔴 ZAMAN EKSENİ YOK              → dönem uygulanamaz sınıfı

SEMA: dict = {"cubes": [
    {
        "name": "uretim",
        "display": "Üretim",
        "measures": ["toplam_fire_kg", "fire_orani_yuzde", "toplam_uretim_kg"],
        # ⚠ `toplam_uretim_kg` bilerek `measure_synonyms` DIŞINDA: `nl: false` ölçünün
        # (bir oranın PAYDASI) menüde de görünmediğini ölçmek için.
        "measure_synonyms": {"toplam_fire_kg": ["fire"],
                             "fire_orani_yuzde": ["fire orani"]},
        "measure_synonyms_display": {"toplam_fire_kg": "Toplam fire (kg)",
                                     "fire_orani_yuzde": "Fire oranı (%)"},
        "dimensions": ["makine", "vardiya"],
        "dimension_labels": {"makine": "Makine", "vardiya": "Vardiya"},
        "time_dimensions": ["tarih"],
        "semi_additive": [],
    },
    {
        "name": "stok",
        "display": "Stok",
        "measures": ["bakiye"],
        "measure_synonyms": {"bakiye": ["bakiye"]},
        "measure_synonyms_display": {"bakiye": "Bakiye"},
        "dimensions": ["depo"],
        "dimension_labels": {"depo": "Depo"},
        "time_dimensions": ["tarih"],
        "semi_additive": ["bakiye"],
    },
    {
        "name": "kadro",
        "display": "Kadro",
        "measures": ["personel_sayisi"],
        "measure_synonyms": {"personel_sayisi": ["personel"]},
        "measure_synonyms_display": {"personel_sayisi": "Personel sayısı"},
        "dimensions": ["birim"],
        "dimension_labels": {"birim": "Birim"},
        "time_dimensions": [],
        "semi_additive": [],
    },
]}

FIRE = ("uretim", "toplam_fire_kg")
BAKIYE = ("stok", "bakiye")
PERSONEL = ("kadro", "personel_sayisi")

BU_AY: list[dict] = [
    {"dimension": "tarih", "operator": "gte", "value": "2026-08-01"},
    {"dimension": "tarih", "operator": "lte", "value": "2026-08-31"},
]


def n(**kw) -> Niyet:
    """Sentetik `Niyet` — alanlar **elle** kurulur, çünkü ölçülen şey çözümleme değil
    **çizim**dir. (Gerçek `coz()` çıktısı son iki yüklemde ölçülür.)"""
    kw.setdefault("soru", "sentetik")
    kw.setdefault("turler", {TUR_TOPLAM})
    return Niyet(**kw)


def beklenen_sayi(niyet: Niyet) -> int:
    """`§5.2`'nin *«birebir»*inin **sayısal** hâli.

    ⚠ `donemler` bir dönemin **sınırlarıdır** (`gte`+`lte`), bir dönem listesi değil —
    `donem_capasi.not_metni` de onu zaten tek aralık olarak okuyor. Bu yüzden katkısı
    `len()` değil `0|1`."""
    return (len(niyet.olcu_adaylari) + (1 if niyet.donemler else 0)
            + len(niyet.kirilimlar) + len(niyet.turler))


ORNEKLER = [
    n(olcu_adaylari=[FIRE]),
    n(olcu_adaylari=[FIRE], donemler=list(BU_AY)),
    n(olcu_adaylari=[FIRE], donemler=list(BU_AY), kirilimlar=["makine"],
      turler={TUR_KIRILIM}),
    n(olcu_adaylari=[FIRE], donemler=list(BU_AY), kirilimlar=["makine", "vardiya"],
      turler={TUR_KIRILIM, TUR_TREND, TUR_USTUNLUK}, granulerlik="month", ustunluk=5),
    n(olcu_adaylari=[FIRE, BAKIYE], turler={TUR_TOPLAM}),
    n(),                                            # boş niyet — hiç ölçü yok
]


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · `§5.2` — PILL SATIRI, `Niyet`İN GÖRÜNÜR HÂLİ (ikinci temsil yok)
# ═══════════════════════════════════════════════════════════════════════════════

def test_PILL_ALANLARI_GERCEK_NIYET_ALANLARIDIR():
    """🔴🔴 *«Yeni model kurulmuyor, mevcut model çiziliyor.»*

    Kapalı `alan` kümesinin **her** üyesinin arkasında gerçek bir `Niyet` alanı var mı?
    Bir gün `Niyet` alanı yeniden adlandırılırsa pill katmanı burada, **adıyla** düşer —
    sessizce bayat bir kopya taşımaz."""
    import dataclasses

    alanlar = {f.name for f in dataclasses.fields(Niyet)}
    assert set(ALAN_KAYNAGI) == set(ALANLAR), "🔴 kapalı küme ile kaynak haritası ayrıştı"
    for pill_alani, niyet_alani in ALAN_KAYNAGI.items():
        assert niyet_alani in alanlar, (
            f"🔴 `{pill_alani}` pill'i `Niyet.{niyet_alani}` alanından türediğini "
            f"iddia ediyor ama böyle bir alan YOK — ikinci bir temsil doğmuş demektir")


@pytest.mark.parametrize("niyet", ORNEKLER)
def test_PILL_SAYISI_NIYET_ALANLARIYLA_BIREBIR(niyet):
    """🔴 **(c)** Pill sayısı nesnenin alanlarından **hesaplanabilir** olmalı: fazlası
    uydurma, eksiği gizleme demektir."""
    pills = pillerden(niyet, SEMA)
    assert len(pills) == beklenen_sayi(niyet), [p.metin for p in pills]


@pytest.mark.parametrize("niyet", ORNEKLER)
def test_IKINCI_TEMSIL_YOK(niyet):
    """🔴🔴 **(c)'nin asıl yüklemi:** pill'lerin `deger`leri `Niyet`i **yeniden kurar**.

    Sayı tutup içerik kaymasaydı bu kapı bir şey ölçmezdi. *Bir çizimin doğruluğu,
    çizdiğinden geri okunabilmesidir.*"""
    pills = pillerden(niyet, SEMA)
    assert [p.deger for p in pills if p.alan == ALAN_OLCU] == list(niyet.olcu_adaylari)
    assert ([p.deger for p in pills if p.alan == ALAN_DONEM]
            == ([list(niyet.donemler)] if niyet.donemler else []))
    assert [p.deger for p in pills if p.alan == ALAN_KIRILIM] == list(niyet.kirilimlar)
    assert {p.deger for p in pills if p.alan == ALAN_TUR} == set(niyet.turler)


@pytest.mark.parametrize("niyet", ORNEKLER)
def test_ALAN_KAPALI_KUME_VE_METIN_TURKCE(niyet):
    """Her pill kapalı kümeden bir alan taşır ve metni **kullanıcıya** yazılabilir:
    boş değil, teknik alt çizgi sızdırmıyor."""
    for p in pillerden(niyet, SEMA):
        assert p.alan in ALANLAR, p
        assert p.metin.strip(), f"🔴 metinsiz pill: {p}"
        assert "_" not in p.metin, f"🔴 teknik ad sızdı: {p.metin}"


def test_TUREV_PILLER_SILINEMEZ():
    """🔴 İki pill **silinemez** ve ikisi de bir türevdir:

    * tek **ölçü** — ölçüsüz bir fiş bir sorgu değildir (`§KV` ile aynı gerekçe);
    * **tür** — `kirilim`/`trend` pill'lerinden **doğar**; onu ayrıca silmek ekranda
      iki farklı niyet bırakırdı.

    ⚠ Ve **çok** ölçü adayında silme bir kayıp değil bir **cevaptır** (belirsizliği
    daraltır) — kapı bunu da ölçer, yoksa kural *«hiç silinemez»*e kayardı."""
    tek = pillerden(n(olcu_adaylari=[FIRE], turler={TUR_KIRILIM}), SEMA)
    assert [p.silinebilir for p in tek if p.alan == ALAN_OLCU] == [False]
    assert [p.silinebilir for p in tek if p.alan == ALAN_TUR] == [False]

    coklu = pillerden(n(olcu_adaylari=[FIRE, BAKIYE]), SEMA)
    assert [p.silinebilir for p in coklu if p.alan == ALAN_OLCU] == [True, True]


def test_BELIRLENIMLI_SIRA():
    """`turler` bir **kümedir** → sıra kümeden gelemez. Aynı niyet, aynı satır."""
    a = n(olcu_adaylari=[FIRE], kirilimlar=["makine"],
          turler={TUR_TREND, TUR_KIRILIM, TUR_TOPLAM}, granulerlik="month")
    b = n(olcu_adaylari=[FIRE], kirilimlar=["makine"],
          turler={TUR_TOPLAM, TUR_KIRILIM, TUR_TREND}, granulerlik="month")
    assert [(p.alan, p.metin) for p in pillerden(a, SEMA)] == \
           [(p.alan, p.metin) for p in pillerden(b, SEMA)]


def test_GRANULERLIK_VE_USTUNLUK_AYRI_PILL_DEGIL_METINDE():
    """🔴 `granulerlik`/`ustunluk` ayrı pill olsaydı aynı niyet **iki kutuda** görünürdü
    (`KAT-1`'in görsel hâli). Onlar ait oldukları `tur` pill'inin **metnidir**."""
    pills = pillerden(n(olcu_adaylari=[FIRE], turler={TUR_TREND, TUR_USTUNLUK},
                        granulerlik="month", ustunluk=5), SEMA)
    metinler = {p.metin for p in pills if p.alan == ALAN_TUR}
    assert metinler == {"aylık seyir", "en yüksek 5"}, metinler


def test_DONEM_TEK_PILL_VE_TARIH_INSANCA():
    """`gte`+`lte` **bir** dönemdir → tek pill, ve metni gün biçiminde."""
    pills = [p for p in pillerden(n(olcu_adaylari=[FIRE], donemler=list(BU_AY)), SEMA)
             if p.alan == ALAN_DONEM]
    assert len(pills) == 1
    assert pills[0].metin == "01.08.2026 – 31.08.2026", pills[0].metin


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · `§5.2`'nin BİR NUMARALI TUZAĞI — `+` TİPLİ OLMAK ZORUNDA
# ═══════════════════════════════════════════════════════════════════════════════

def test_ARTI_DORT_AYRI_TIPTE():
    """🔴🔴 **(a)** *«Tek bir `+` üç ayrı anlama gelir ve bu deponun bir numaralı
    tuzağıdır.»* Dört `+`, dört ayrı tip, dört ayrı metin — ve her biri **kendi
    alanını** beyan eder."""
    a = artilar(n(olcu_adaylari=[FIRE]), SEMA)
    assert tuple(x.tip for x in a) == ARTI_TIPLERI, "🔴 `+` sırası/tipi sözleşmedir"
    assert len({x.tip for x in a}) == 4, "🔴 tipsiz ya da yinelenen `+`"
    assert len({x.metin for x in a}) == 4, "🔴 iki `+` aynı metni taşıyor → tek `+` etkisi"
    for x in a:
        assert x.metin.startswith("+ "), x.metin
    beyan = {x.tip: x.alan for x in a}
    assert beyan[ARTI_OLCU] == ALAN_KAYNAGI[ALAN_OLCU]
    assert beyan[ARTI_KIRILIM] == ALAN_KAYNAGI[ALAN_KIRILIM]
    assert beyan[ARTI_DONEM] == ALAN_KAYNAGI[ALAN_DONEM]
    # `+ adım` hiçbir `Niyet` alanını büyütmez — bir PLAN doğurur.
    assert beyan[ARTI_ADIM] is None


def test_ARTININ_SONUCU_TEK_ANLAMLI():
    """🔴 **(a)'nın çekirdeği:** planın tablosu üç anlam sayıyor (*aynı sorguya ölçü* ·
    *adım* · *ayrı rapor*). Tipli `+` her birinin sonucunu **önceden** söyler; iki
    farklı sonuç kümede ayrışmazsa tuzak geri gelmiş demektir."""
    sonuc = {x.tip: x.sonuc for x in artilar(n(olcu_adaylari=[FIRE]), SEMA)}
    assert sonuc[ARTI_ADIM] == SONUC_PLAN
    assert {sonuc[t] for t in (ARTI_OLCU, ARTI_KIRILIM, ARTI_DONEM)} == {SONUC_TEK_SORGU}
    assert len(set(sonuc.values())) == 2, "🔴 tüm `+`'lar aynı sonucu veriyorsa tip yok"


def test_ARTI_SECENEKLERI_KAPALI_GRAMERDEN():
    """🔴 Her `+` **kapalı gramerdeki** seçeneklerini beyan eder — ve dördünün de sahibi
    başka bir modüldür. Burada hiçbir liste yazılmaz; kopyalansaydı ayrışırdı."""
    from app.donem_capasi import DONEM_SECENEKLERI
    from app.plan_semasi import FIILLER

    a = {x.tip: x for x in artilar(n(olcu_adaylari=[FIRE], kirilimlar=["makine"]), SEMA)}

    assert (tuple(s.deger for s in a[ARTI_DONEM].secenekler)
            == tuple(str(d["query"]) for d in DONEM_SECENEKLERI))
    assert tuple(s.deger for s in a[ARTI_ADIM].secenekler) == tuple(FIILLER)

    olculer = {s.deger for s in a[ARTI_OLCU].secenekler}
    assert "uretim.fire_orani_yuzde" in olculer
    assert "uretim.toplam_fire_kg" not in olculer, "🔴 zaten seçili ölçü menüde"
    assert "uretim.toplam_uretim_kg" not in olculer, (
        "🔴 `nl: false` ölçü (bir oranın PAYDASI) menüye sızdı")

    kirilimlar = {s.deger for s in a[ARTI_KIRILIM].secenekler}
    assert kirilimlar == {"vardiya"}, kirilimlar   # `makine` seçili, `depo` başka küpte


def test_ARTI_HER_ZAMAN_DORT_SECENEKLER_DARALIR():
    """`+`'ın kendisi bağlamla **kaybolmaz** (arayüz her turda yeniden öğrenilmez);
    daralan şey **seçeneklerdir**. Ölçüsüz fişte kırılım menüsü boştur: küp bilinmeden
    boyut bilinmez."""
    bos = {x.tip: x for x in artilar(n(), SEMA)}
    assert len(bos) == 4
    assert bos[ARTI_KIRILIM].secenekler == ()
    assert bos[ARTI_OLCU].secenekler, "🔴 giriş noktası: ölçü menüsü tüm katalogtur"
    assert bos[ARTI_DONEM].secenekler and bos[ARTI_ADIM].secenekler


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · `§5.3` — CANLI DOĞRULAMA: *«imkânsız soru sorulamaz hâle gelir»*
# ═══════════════════════════════════════════════════════════════════════════════

def test_GECERSIZ_KIRILIM_NEDENIYLE_KIRMIZIYA_DONER():
    """🔴🔴 **(b)** Kırmızı yetmez — **neden** de gelmeli. *«Bir uyarı, yapılacak şeyi
    göstermiyorsa bir şikâyettir»* (`§RK-2`)."""
    hatalar = dogrula(n(olcu_adaylari=[FIRE], kirilimlar=["depo"],
                        turler={TUR_KIRILIM}), SEMA)
    assert len(hatalar) == 1, hatalar
    h = hatalar[0]
    assert h.alan == ALAN_KIRILIM and h.deger == "depo"
    assert "Depo" in h.neden, h.neden          # kullanıcının gördüğü etiket
    assert "Üretim" in h.neden, h.neden        # hangi katalogta yok
    assert h.neden.strip().endswith("."), "🔴 neden bir CÜMLE olmalı"


def test_GECERLI_KOMBINASYON_KIRMIZI_DEGIL():
    """🔴 *Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*"""
    assert dogrula(n(olcu_adaylari=[FIRE], donemler=list(BU_AY),
                     kirilimlar=["makine", "vardiya"],
                     turler={TUR_KIRILIM}), SEMA) == []


def test_BELIRSIZLIK_IMKANSIZLIK_DEGIL():
    """🔴 Çok sahipli terimde (`§A.2`'nin 73 terimi) kırılım **bir** adayda geçiyorsa
    soru imkânsız değil **belirsizdir** — ve belirsizliğin sahibi başka bir mekanizma
    (`app/belirsizlik_chipi.py`). Her adayda düşerse kırmızıdır."""
    ikili = [FIRE, BAKIYE]
    assert dogrula(n(olcu_adaylari=ikili, kirilimlar=["makine"]), SEMA) == [], \
        "🔴 bir adayda geçen kırılım kırmızıya dönmemeli"
    hatalar = dogrula(n(olcu_adaylari=ikili, kirilimlar=["yok_boyle_bir_boyut"]), SEMA)
    assert [h.alan for h in hatalar] == [ALAN_KIRILIM]
    assert "Üretim" in hatalar[0].neden and "Stok" in hatalar[0].neden, hatalar[0].neden


def test_GRAIN_IHLALI_KIRMIZI():
    """🔴🔴 `R8`'in pill karşılığı: yarı-toplanır ölçü (bakiye/stok) dönem-**SONU**
    değeridir; zaman kovasına bölünürse *«dönemin net hareketi»* çıkar ve bu
    `source=cube` rozetiyle sunulur — sessiz-yanlış. Bugün bu red **koşum anında**
    düşüyor; pill onu **yazım anına** taşır."""
    hatalar = dogrula(n(olcu_adaylari=[BAKIYE], donemler=list(BU_AY),
                        turler={TUR_TREND}, granulerlik="month"), SEMA)
    assert [h.alan for h in hatalar] == [ALAN_TUR], hatalar
    assert "grain" in hatalar[0].neden.lower(), hatalar[0].neden
    assert "aylık" in hatalar[0].neden, hatalar[0].neden


def test_GRAIN_IHLALI_TOPLANIR_OLCUDE_YOK():
    """Aynı kova, **toplanır** bir ölçüde meşrudur — kural ölçüye bağlıdır, kovaya değil."""
    assert dogrula(n(olcu_adaylari=[FIRE], donemler=list(BU_AY),
                     turler={TUR_TREND}, granulerlik="month"), SEMA) == []


def test_KOVA_KAPALI_KUMENIN_DISINDA_KIRMIZI():
    """Zaman kovasının sahibi `cube_operatorleri.GRANULERLIKLER`; `hour` **yok** ve
    yokluğu bir karardır (veri o çözünürlüğü taşımıyor)."""
    hatalar = dogrula(n(olcu_adaylari=[FIRE], turler={TUR_TREND},
                        granulerlik="hour"), SEMA)
    assert [h.alan for h in hatalar] == [ALAN_TUR]
    assert "month" in hatalar[0].neden, hatalar[0].neden   # geçerli kümeyi SAYAR


def test_ZAMAN_EKSENI_OLMAYAN_KUPTE_DONEM_KIRMIZI():
    """Zaman ekseni olmayan bir küpte dönem süzgeci **uygulanamaz** — ve bunu beyaz
    listenin kendisi söyler (`allowed_filter_dims` boş kalır)."""
    hatalar = dogrula(n(olcu_adaylari=[PERSONEL], donemler=list(BU_AY)), SEMA)
    assert [h.alan for h in hatalar] == [ALAN_DONEM], hatalar
    assert "zaman ekseni yok" in hatalar[0].neden, hatalar[0].neden


def test_TEMSIL_BOSLUKLARI_KIRMIZI():
    """🔴 İki *«imkânsız soru»* sınıfı ve ikisinin de sahibi `Niyet.temsil_edilemeyen`:
    ayrık iki dönem (`CubeQuery` bir aralık taşır) ve tek uçlu kıyas."""
    cok = dogrula(n(olcu_adaylari=[FIRE], donem_sayisi=2, turler={TUR_TOPLAM}), SEMA)
    assert [h.alan for h in cok] == [ALAN_DONEM]
    assert "2 ayrı dönem" in cok[0].neden, cok[0].neden

    kiyas = dogrula(n(olcu_adaylari=[FIRE], turler={TUR_KIYAS}), SEMA)
    assert [h.alan for h in kiyas] == [ALAN_TUR]
    assert "ikinci uç" in kiyas[0].neden, kiyas[0].neden


def test_OLCUSUZ_NIYET_KIRMIZI_DEGIL():
    """🔴 Kullanıcı hâlâ yazıyor olabilir: ölçüsüz bir fişte **doğrulanacak kombinasyon
    yoktur**. Boş satırı ilk tuşta kırmızıya boyamak, arayüzü suçlayıcı yapardı — ve
    ölçünün bulunamaması ayrı bir sınıftır (`Niyet.SEBEP_OLCU_YOK`, sahibi garson)."""
    assert dogrula(n(kirilimlar=["yok_boyle_bir_boyut"]), SEMA) == []


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · KAT-1 · SAFLIK — bu katman KOŞMAZ ve HİÇBİR KURALI YENİDEN YAZMAZ
# ═══════════════════════════════════════════════════════════════════════════════

KAYNAK = pathlib.Path(__file__).resolve().parents[1] / "app" / "pill.py"

#: Bu adlardan biri `pill.py`'de geçmiyorsa, o kuralın **ikinci sahibi** doğmuş demektir.
SAHIPLER = ("parse_cube_query", "is_period_optional", "GRANULERLIKLER",
            "DONEM_SECENEKLERI", "FIILLER", "_GRAN_ADI", "temsil_edilemeyen")

#: Pill katmanı **koşmaz**: ne LLM, ne motor, ne ağ, ne sürücü.
YASAK = ("llm", "httpx", "requests", "openai", "anthropic",
         "wren_service", "wren", "duckdb", "sqlalchemy", "subprocess")


def test_KATMAN_SAF_KOSMAZ():
    """🔴 *«SAF: LLM yok, sorgu koşma yok. Şema dışarıdan verilir.»* — içe aktarma
    listesi bunu **yapısal** olarak kanıtlar; bir yorum satırı değil."""
    agac = ast.parse(KAYNAK.read_text(encoding="utf-8"))
    moduller: list[str] = []
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            moduller += [a.name for a in dugum.names]
        elif isinstance(dugum, ast.ImportFrom):
            moduller.append(dugum.module or "")
    for m in moduller:
        parcalar = set(m.split("."))
        assert not (parcalar & set(YASAK)), f"🔴 saf katman koşan bir modül çekti: {m}"


def test_KURALLARIN_IKINCI_SAHIBI_YOK():
    """🔴🔴 `KAT-1`: her doğrulama kuralı **çağrılır**, kopyalanmaz. Bir sahip adı
    kaynaktan düşerse, kural burada yeniden yazılmış demektir.

    *Bir kümenin üç kopyası, üç farklı küme demektir.*"""
    kaynak = KAYNAK.read_text(encoding="utf-8")
    eksik = [s for s in SAHIPLER if s not in kaynak]
    assert not eksik, f"🔴 şu sahiplere artık sorulmuyor (kural kopyalanmış?): {eksik}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5 · GERÇEK KATALOG — sentetik şemanın bayatlamadığının kanıtı
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("soru", ["bu ay makine bazinda fire",
                                  "son 6 ay ciro trendi",
                                  "en yuksek fire hangi makine"])
def test_GERCEK_NIYETTEN_TURETILEN_PILL_BIREBIR(soru, schema):
    """🔴 Gerçek MDL + gerçek `Niyet.coz` — çizim sözleşmesi orada da tutuyor mu?"""
    from app import niyet as _n

    niyet = _n.coz(soru, schema)
    pills = pillerden(niyet, schema)
    assert len(pills) == beklenen_sayi(niyet), [p.metin for p in pills]
    assert {p.alan for p in pills} <= set(ALANLAR)
    assert all(p.metin.strip() for p in pills)


@pytest.mark.parametrize("soru", ["bu ay makine bazinda fire",
                                  "vardiya bazinda oee",
                                  "son 3 ay makine bazinda fire orani"])
def test_KATALOGDAN_GELEN_KIRILIM_ASLA_KIRMIZI_DEGIL(soru, schema):
    """🔴🔴 Doğrulamanın en sert yüklemi: `Niyet` kırılımlarını **kataloğu okuyarak**
    buluyor (`cube_router._match_dims`). O hâlde onların hiçbiri beyaz listeden
    düşemez — düşerse pill katmanı ile eşleştirici **ayrışmış** demektir ve arayüz
    kullanıcıya kendi kataloğunu yalanlar.

    *Bir arayüzün en pahalı hatası, mümkün olanı imkânsız ilan etmesidir.*"""
    from app import niyet as _n

    niyet = _n.coz(soru, schema)
    kirmizi = [h for h in dogrula(niyet, schema) if h.alan == ALAN_KIRILIM]
    assert not kirmizi, f"🔴 katalogtan gelen kırılım kırmızıya döndü: {kirmizi}"
