"""🔴🔴 KÖK-2 + KÖK-3 — **UYUM KAPISI** ve **BEYANLI KISMİ CEVAP**.

## Ölçülen kusur (devralınan raporun KN-4 · bu raporun 42 sessiz-yanlışı)

`route()` bir `CubeQuery` üretiyor ve dönüyor. Ama sorudaki **her niyet işaretinin**
sorguda karşılığı olduğu **hiçbir yerde denetlenmiyor**. Ölçülen üç sınıf:

| soru | üretilen | kaybolan |
|---|---|---|
| `mart cirosunu şubat ile kıyasla` | tek toplam | **kıyas** |
| `ocak ve haziran ciro karşılaştır` | Ocak–Haziran **toplamı** | altı ay yutuluyor |
| `ciro değişimi son 6 ay` | toplam | **değişim** ≠ trend |

🔴 Ve hepsi `source=cube` rozetiyle dönüyor — yani **kanıtlanmış yol** damgasıyla.
*Yanlış cevap veren bir sistem, sustuğunu bilen bir sistemden tehlikelidir.*

## Neden bu bir "vaka listesi" değil, bir **değişmez listesi**

Kusuru tek tek düzeltmek (her ifade için bir yama) bu deponun on dört kez avladığı
desendir. Burada tersi yapılır: **niyet türü başına bir değişmez** yazılır. Yeni bir
niyet türü eklendiğinde denetimi de eklenir — mekanizma **kendini genişletir**.

## 🔴 Sıfırdan yazılmıyor — ZATEN VAR, dörtten yediye genişletiliyor

`cube_router.py:866` ve `:1191`'de bu koruma **iki yerde elle** duruyor ve kodun kendi
yorumu adını koymuş: *"SESSİZ-YANLIŞ koruması"*. Ama yalnız **kırılım** işaretine
bakıyor ve yalnız iki dalda çalışıyor. Bu modül aynı ilkeyi **yedi işarete** ve **tek
çıkışa** taşır. Dedektörlerin **hepsi** `cube_router`'ın kendi fonksiyonlarıdır —
`compare_mode` · `_kiyas_spanlari` · `_time_gran` · `_BREAKDOWN_HINTS` ·
`_TOPN_CUE` · `_measure_threshold` · `_EXCLUDE_MARKERS`. Yeni dilbilim **yazılmıyor**.

## KÖK-3 — ve neden ikisi BİRLİKTE inmeli

KÖK-2 tek başına inseydi **kapsam daralırdı**: bugün cevaplanan sorular netleştirmeye
düşerdi. Üçüncü seçenek bunu alır:

> Bugün iki seçenek var: **cevapla** ya da **reddet**. Üçüncüsü:
> *"şu kısmını verdim, şu kısmını **veremedim**, nedeni bu."*

⚠ **ADR-0008 uyumu:** kural *"yanlış cevaba güven rozeti takma"* der. Beyanlı kısmi
cevap **rozetsizdir** — yasağı çiğnemez, **karşılar**.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Bir niyet işaretinin sorguda karşılığı yoksa üretilen kayıt.
@dataclass(frozen=True)
class Ihlal:
    """`isaret` telemetri için SABİT; `aciklama` kullanıcıya gider."""

    isaret: str
    aciklama: str
    oneri: str


#: *"Değişim/trend"* — zaman EKSENİ ister, tek bir toplam değil.
#: ⚠ `_time_gran` granülerliği (`aylara göre`) yakalar; bu ise **niyeti** yakalar.
_TREND = re.compile(
    r"\b(trend|trendi|degisim|degisimi|degisti|seyri|seyir|gidisat|"
    r"nasil gidiyor|nasil gitti|artti|azaldi|dustu|yukseldi)\b")

#: Çok-dönem: iki AYRI dönem adı geçiyor ve ikisi de istenmiş.
_AY = ("ocak", "subat", "mart", "nisan", "mayis", "haziran",
       "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik")


def _norm(s: str) -> str:
    return s.translate(str.maketrans("çÇğĞıİöÖşŞüÜ", "cCgGiIoOsSuU")).lower()


#: 🔴 ARALIK İŞARETLERİ — iki dönem adı **tek bir aralığın iki UCU** olabilir.
#:
#: Ölçülen yanlış-pozitif: `1 ocak 31 mart arası toplam üretim` (eval `tarih-acik-aralik`)
#: iki ay adı taşıyor ve *"çok dönem"* sanılıyordu — oysa orada **tek bir aralık** var ve
#: `route()` onu zaten `gte`+`lte` ile doğru kurmuş.
#:
#: *İki tarih, aralarında bir "arası" varsa iki istek değil bir aralıktır.*
_ARALIK = (" arasi", " arasinda", " ila ", " kadar", "dan ", "den ",
           "tan ", "ten ", " itibaren")

#: 🔴 **AŞIRI-YÜKLÜ BAĞLAÇ** — `" ile "` iki ayrı işi görür ve `G6`'da ölçüldü:
#:
#: | okuma | örnek |
#: |---|---|
#: | **aralık** | *"ocak **ile** mart arası"* → tek dönem |
#: | **birliktelik** | *"mart cirosunu şubat **ile** kıyasla"* → **iki** dönem |
#:
#: Bağlaç `_ARALIK` içindeyken ikinci okuma birinciye yutuluyordu: `cok_donem` ihlali
#: bastırılıyor, `kiyas` ihlali de (o zaman) hiç doğmuyordu → soru **1 Şubat–31 Mart
#: toplamıyla** cevaplanıp **etiketsiz** gidiyordu.
#:
#: ⚠ Bu, bu deponun defterindeki **`göre`/`bazında` aşırı-yüklenmesinin** aynı sınıfı.
#: Çözüm bir kelime eklemek değil, iki sahip arasında bir **öncelik** kurmaktır:
#: kıyas fiili varsa `" ile "` **birliktelik** okunur. Gerçek aralık ifadesi zaten
#: `" arasi"`/`" ila "` taşır — yani bu kısıt meşru aralığı **daraltmaz**.
_ARALIK_BAGLAC = (" ile ",)

#: Göreli dönem aralığı — *"son 3 ay"*, *"son 6 ay"*. İkisi AYRI birer dönemdir.
_GORELI_DONEM = re.compile(
    r"son\s+(\d+)\s*(ay|gun|hafta|yil|ceyrek)")


def _cok_donem(q: str) -> int:
    """Soruda kaç **AYRI** dönem geçiyor.

    Dört biçim sayılır ve dördü de **ölçülerek** eklendi:
      · ay adı  — `ocak ve haziran`
      · yıl     — `2025 ve 2026`
      · göreli  — `son 3 ay ve son 6 ay`        ← 🔴 ilk yazımda EKSİKTİ
      · çeyrek  — `ilk çeyrek ve ikinci çeyrek` ← 🔴 KÖK-7c açınca EKSİK ÇIKTI

    ⚠ Üçüncüsü kapıyı ölçerken yakalandı: `son 3 ay ve son 6 ay ciro` hiçbir ihlal
    vermiyordu, oysa `route()` ikisini **tek bir filtreye** (`gte 2026-05-05`) çöküyor
    ve altı ayın üçü sessizce yutuluyordu. *Bir sayacın saymadığı biçim, o sayaç için
    var olmayan bir dünyadır.*

    🔴 **Dördüncüsü, KÖK-7c'nin kendi açtığı kapıydı.** `_period_hit_words` çok-geçişe
    geçince `ilk ceyrek ve ikinci ceyrek ciro` **R10'dan kurtuldu** — ama `route()` yine
    yalnız **ilk** çeyreği çözüyor (`_quarter_period_filters` tek `.search`). Sayaç
    çeyreği saymasaydı, bu soru **R10 reddinden SESSİZ-YANLIŞA terfi** ederdi.

    *Bir kapsamı açan değişiklik, açtığı kapsamın beyan sayacını da beslemek zorundadır;
    yoksa dürüst bir "anlamadım"ı sessiz bir yanlışa çevirir.*

    ⚠ Çeyrek sözlüğü **yazılmadı, ödünç alındı**: `cube_router._QUARTER_RE` çeyreğin tek
    sahibidir. Buraya ikinci bir sıra-sayı listesi yazmak, deponun ölçülmüş *"aynı kuralın
    iki sahibi"* sınıfını yeniden doğururdu.
    """
    from app.cube_router import _PREV_RE, _QUARTER_ORD, _QUARTER_RE

    qn = _norm(q)
    aylar = {a for a in _AY if re.search(rf"(?<![a-z0-9]){a}", qn)}
    yillar = set(re.findall(r"(?<!\d)(20\d{2})(?!\d)", qn))
    goreli = {f"{n}{b}" for n, b in _GORELI_DONEM.findall(qn)}
    # Çeyreğin KİMLİĞİ numarasıdır: `ilk çeyrek` ile `1. çeyrek` **aynı** dönemdir ve iki
    # kez sayılmamalıdır (*"1. çeyrek yani ilk çeyrek"* tek istektir).
    ceyrek = {str(m.group(1) or _QUARTER_ORD[m.group(2)])
              for m in _QUARTER_RE.finditer(qn)}
    # 🔴 Beşinci biçim, KAPININ KENDİSİ yakaladı: `gecen ay ve gecen yil ciro` →
    # `route()` yalnız **Temmuz 2026**'yı çözüyor, "geçen yıl" sessizce yutuluyor.
    # Kimlik BİRİMDİR (`ay` ≠ `yil`); *"geçen ay"* iki kez geçse tek dönemdir.
    onceki = {b for b, _ek in _PREV_RE.findall(qn)}
    return len(aylar) + len(yillar) + len(goreli) + len(ceyrek) + len(onceki)


def trend_istendi(qn: str) -> bool:
    """Soru bir **değişim/trend** istiyor mu — *"değişimi"* · *"artışı"* · *"seyri"*.

    ## 🔴 Neden bir FONKSİYON (KÖK-1 Faz 2'de doğdu)

    `_TREND` bu modülün **özel** kalıbıdır. `app/niyet.py` onu doğrudan çağırdı ve kendi
    kapısı (`test_YENI_DILBILIM_YAZILMADI`) haklı olarak kırmızı verdi: bir çatının başka
    modülün **kalıbına** uzanması, o kalıbı ikinci bir sahibe açar.

    ⚠ Ödünç alınacak şey bir kalıp değil bir **karardır**. Kalıp burada kalır, karar
    adıyla dışarı çıkar. *Bir kuralı paylaşmanın doğru biçimi, kuralı değil cevabını
    paylaşmaktır.*

    ⚠ `_time_gran` ile AYNI ŞEY DEĞİLDİR: o *"aylara göre"* der (eksen istendi), bu
    *"değişimi"* der (değişim istendi). İkisini bir alanda toplamak Faz 2'nin ilk
    ölçümünde yakalandı.
    """
    return bool(_TREND.search(qn))


def ustunluk_istendi(qn: str) -> bool:
    """Soru bir **üstünlük** istiyor mu — *"en yüksek"* · *"en çok"* (SAYI gerekmez).

    ⚠ `cube_router._top_n` ile aynı şey değildir: o **sayı** ister (`en yüksek 5`), bu
    istemez. `uyum`un beşinci değişmezi bunu sorar; `route`un sıralaması ötekini.
    """
    from app.cube_router import _TOPN_CUE

    return bool(_ustunluk_mu(qn, _TOPN_CUE, None, None))


def denetle(q: str, cq: dict, cube_meta: dict | None = None) -> list[Ihlal]:
    """Sorudaki niyet işaretlerinin **sorguda karşılığı var mı?**

    🔴 Boş liste = uyumlu. Dolu liste = **sessiz-yanlış adayı**: cevap üretildi ama
    kullanıcının istediği bir şey sorguya **taşınmadı**.

    ⚠ Kapı **fail-closed değil, BEYAN-AÇIK**: cevabı öldürmez, **etiketler** (KÖK-3).
    Öldürmek kapsamı daraltırdı; etiketlemek daraltmaz ama sessizliği bitirir.
    """
    from app.cube_router import _PERIOD_RANGE_REF, _TOPN_CUE, _time_gran
    from app.niyet import TUR_KIYAS, coz_soru

    out: list[Ihlal] = []
    qn = _norm(q or "")

    # 🔴 KÖK-1 FAZ 2 — SORU TARAFI ARTIK **NİYET NESNESİNDEN** OKUNUYOR.
    #
    # Bu modül soruyu yedi kez ayrı ayrı tarıyordu (`compare_mode` · `_cok_donem` ·
    # `_TREND` · `_BREAKDOWN_HINTS` · `_ustunluk_mu` · `_measure_threshold` ·
    # `_EXCLUDE_MARKERS`). Raporun KÖK-1'i *"çözümleme ile eşleştirme ayrılsın"* der ve
    # bu modül **ilk müşteridir** (*"KÇ-1, KÇ-0'ın ilk müşterisidir"*).
    #
    # ⊙ Göç ÖLÇÜLDÜ, tahmin edilmedi: **2 270** korpus sorusunda yedi sinyalin
    # **YEDİSİ DE** birebir aynı çıktı (`test_kok1_niyet.py::test_FAZ2_ESDEGERLIK`).
    # *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini kanıtlamaktır.*
    #
    # ⚠ ÜSTÜNLÜK **taşınMADI** ve bu bir eksik değil bir SINIR: `_ustunluk_mu` burada
    # `ic`+`cube_meta` ile çağrılır çünkü ipucu bir **ölçü adının içindeyse** ipucu
    # değildir (`kur` cube'unun ölçüsü literal olarak *"en yüksek kur"*; 525 meşru
    # soruda 10 yanlış-pozitif buradan geliyordu). O denetim **eşleştirme** tarafıdır ve
    # şemasız bir çözümlemede yapılamaz. *Ayrımın doğru yeri, ayrımın kendisi kadar
    # önemlidir: yanlış yerden bölünen bir sorumluluk iki yerde de eksik kalır.*
    niyet = coz_soru(q or "")

    # 🔴 `route()` bir SARMALAYICI döndürür: `{cube_query: {...}, measure, order, limit,
    # period_optional}`. İlk yazımda doğrudan `cq.get("dimensions")` okundu ve **her
    # kırılımlı soru** ihlal verdi (`bu yıl makine bazında oee` → «kırılım yok»).
    #
    # ⚠ Bu, bu deponun kendi defterindeki **"bir alan adını okumadan yazmak"** sınıfı —
    # ve bir kapı içinde en tehlikeli hâli: kapı, koruduğu şeyi bozuk ölçer ve kimse
    # fark etmez, çünkü kapı **kırmızı** verir ve kırmızı "çalışıyor" gibi görünür.
    # *Bir sözleşmeyi okumadan denetleyen kapı, denetlediğini sanır.*
    disi = cq or {}
    ic = disi.get("cube_query") if isinstance(disi.get("cube_query"), dict) else disi
    filtreler = ic.get("filters") or []
    boyutlar = ic.get("dimensions") or []
    siralama = (disi.get("order") or disi.get("limit") or ic.get("order")
                or ic.get("limit") or ic.get("entity_limit"))

    # 1 · KIYAS — "şubata göre", "geçen yılla kıyasla"
    #
    # 🔴 **`§67` — «KIYASLA» HER ZAMAN İKİ DÖNEM DEMEK DEĞİLDİR (8 kanıt).**
    #
    # Ölçüldü: `ciro ile kar marjını makine bazında **kıyasla**` → *«iki dönemi
    # kıyaslamanı istedin ama tek bir toplam üretebildim»*. Kullanıcı **iki ölçüyü**
    # kıyaslamak istedi; ortada dönem yok. Aynı desen `i7`·`d9`·`f2`·`g10`… sekiz kez.
    #
    # 🔴 Ve `Ö10`'un kuralı burada da geçerli: **yanlış bir beyan sessizlikten kötüdür** —
    # sistem kullanıcıya **onun söylemediği bir şeyi söylediğini** söylüyor.
    #
    # ⊙ Ayrım **yapısal**: kıyasın **nesnesi** ne? Sorguda **iki ya da daha çok ölçü**
    # varsa ve soru birden çok dönem saymıyorsa (`cok_donem` yok), o kıyas **ölçüler
    # arasıdır** ve sorguda **zaten karşılanmıştır** — iki ölçü yan yana duruyor.
    #
    # ⚠ Dar tutuldu: yalnız `cok_donem` **yokken** ve `cq` **çok ölçülüyken** susar.
    # `geçen yıla göre kıyasla` (tek ölçü, iki dönem) aynen ihlal sayılır.
    #
    # *Bir kıyasın eksik olduğunu söylemeden önce, neyin kıyaslandığına bakmak gerekir.*
    _olcu_kiyasi = (len([m for m in (ic.get("measures") or []) if m]) >= 2
                    and not niyet.cok_donem)
    if (TUR_KIYAS in niyet.turler and not _olcu_kiyasi
            and not (ic.get("compare") or ic.get("compare_mode"))):
        out.append(Ihlal(
            "kiyas",
            "iki dönemi **kıyaslamanı** istedin ama tek bir toplam üretebildim",
            "İki dönemi ayrı ayrı sorabilirsin; ya da *«geçen yıla göre»* diyerek "
            "dönemsel kıyası açıkça isteyebilirsin."))

    # 2 · ÇOK-DÖNEM — "ocak ve haziran", "2025 ve 2026"
    #    ⚠ Kıyas ihlali zaten yazıldıysa tekrar etme: aynı kaybı iki kez anlatmak,
    #    kullanıcıya iki ayrı sorun varmış gibi görünür.
    # ⚠ Aralık işareti varsa iki dönem adı tek bir aralığın UÇLARIDIR — ihlal yok.
    #
    # 🔴 İlk yazımda buna bir de *"route zaten gte+lte kurduysa niyet taşınmıştır"*
    # şartı eklenmişti ve **hedefi kaçırdı**: `ocak ve haziran ciro karşılaştır`
    # sorusunda route iki dönemi TEK aralığa (1 Ocak – 30 Haziran) çöküyor ve o da
    # gte+lte üretiyor. Yani "iki uçlu filtre" hem doğru aralığın hem YANLIŞ çöküşün
    # imzası — ayırt edici değil.
    # *Bir imza, iki farklı olayda da görünüyorsa kanıt değildir.*
    _pad = f" {qn} "
    _aralik_ifadesi = any(w in _pad for w in _ARALIK) or (
        any(w in _pad for w in _ARALIK_BAGLAC) and TUR_KIYAS not in niyet.turler)
    if (niyet.cok_donem and not _aralik_ifadesi
            and not any(i.isaret == "kiyas" for i in out)
            and not (ic.get("compare") or ic.get("compare_mode"))):
        out.append(Ihlal(
            "cok_donem",
            "birden çok dönem saydın ama tek bir **aralık** olarak topladım",
            "Dönemleri ayrı ayrı sorarsan her birini tek tek veririm."))

    # 3 · TREND — zaman ekseni ister
    if niyet.trend_istendi and not (_time_gran(qn) or _zaman_ekseni_var(ic, cube_meta)):
        out.append(Ihlal(
            "trend",
            "**değişimi/trendi** istedin ama tek bir toplam ürettim — zaman ekseni yok",
            "*«aylara göre»* ya da *«çeyreklere göre»* eklersen zaman ekseninde çizerim."))

    # 4 · KIRILIM — mevcut korumanın genelleştirilmiş hâli
    if (niyet.kirilim_istendi and not boyutlar
            and _time_gran(qn) is None and not _PERIOD_RANGE_REF.search(qn)):
        out.append(Ihlal(
            "kirilim",
            "bir **kırılım** istedin ama sorguya bir boyut taşıyamadım",
            "Kırılım adını açıkça yazarsan (*«makine bazında»*) uygularım."))

    # 5 · ÜSTÜNLÜK — "en yüksek 5", "en çok"
    if _ustunluk_mu(qn, _TOPN_CUE, ic, cube_meta) and not siralama:
        out.append(Ihlal(
            "ustunluk",
            "**en yüksek/en çok** dedin ama sıralama uygulayamadım",
            "*«en yüksek 5 makine»* gibi sayı verirsen sıralayıp keserim."))

    # 6 · EŞİK — "1.000 üstü"
    if any(f.get("operator") not in ("gte", "lte") for f in niyet.filtreler) \
            and not _esik_filtresi_var(filtreler) and not ic.get("measure_having"):
        out.append(Ihlal(
            "esik",
            "bir **eşik** verdin (ör. *«1.000 üstü»*) ama filtreye çeviremedim",
            "Eşiği ölçü adıyla birlikte yazarsan (*«cirosu 1.000 üstü»*) uygularım."))

    # 8 · 🔴 **ÖLÇÜ İKAMESİ — beş kez ölçüldü, hiç beyan edilmedi.**
    #
    # | soru | istenen | verilen |
    # |---|---|---|
    # | `bu yıl **bakım maliyetleri**ni makine bazında` | bakım maliyeti | **`ort_birim_maliyet`** |
    # | `bu yılki fire **maliyetimiz**` | ₺ | **`toplam_fire_kg`** (kg) |
    # | `kumaş türüne göre **ortalama** parti ağırlığı` | ortalama | **`toplam_agirlik_kg`** |
    # | `**kalite red oranı** nedir` | red oranı | `fire_orani_yuzde` |
    #
    # ⊙ Beşinde de cevap **sessizce** başka bir ölçüyle geldi. Bu, `KÖK-3`'ün tanımladığı
    # **sessiz-yanlış adayının** ta kendisidir: sayı doğru hesaplanmıştır ama **başka bir
    # şeyin** sayısıdır.
    #
    # ⚠ Yüklem **dar ve yapısal**: soruda bir **birim/toplulaştırma sözcüğü** geçiyor
    # (`maliyet`·`₺`·`tl`·`ortalama`·`oran`·`yüzde`) ama seçilen ölçünün **birimi ya da
    # toplulaştırması** onunla uyuşmuyorsa beyan edilir. Katalogdan okunur — ikinci bir
    # sözlük yazılmaz.
    #
    # ⚠ **Yalnız BEYAN eder, cevabı öldürmez** (`KÖK-3`'ün beyan-açık sözleşmesi):
    # kullanıcı sayıyı görür ve **neyin** sayısı olduğunu da görür.
    #
    # *Bir sayıyı doğru hesaplayıp yanlış şeyin adıyla sunmak, yanlış hesaplamaktan daha
    # zor fark edilir.*
    _birim_bekleniyor = None
    if re.search(r"\b(maliyet\w*|tl\b|₺|tutar\w*|para\w*)", qn):
        _birim_bekleniyor = "₺"
    _toplulastirma_bekleniyor = ("ort" if re.search(r"\b(ortalama|ort\b|vasati)", qn)
                                 else None)
    # ⚠ **BİRİM TEK SAHİPTEN OKUNUR.** İlk yazımda `cube_meta["measure_meta"][m]["unit"]`
    # diye bir yol uydurdum ve kapı sessizce hiç ateşlemedi — o anahtar **yok**. Birimin
    # sahibi `viz._unit_of`'tur (MDL `units` sözlüğü, yoksa regex yedeği) ve ikinci bir
    # çözücü yazmak `KAT-1` olurdu.
    # *Var olmayan bir alanı okuyan kod sessizce hiçbir şey yapar — ve testi geçer.*
    from app.viz import _unit_of as _vbirim
    _units = (cube_meta or {}).get("units") or {}
    for _m in (ic.get("measures") or []):
        _birim = _vbirim(_m, _units) or ""
        # 🔴 **VE İLK YAZIMIM YANLIŞ-POZİTİF ÜRETTİ — kapı yakaladı.** Test
        # `_birim != "₺"` idi; `birim maliyet` ölçüsünün birimi **`₺/kg`** olduğu için
        # meşru bir soru *"ikame"* diye damgalandı (**beş** korpus vakası).
        # ⊙ Doğru test **eşitlik değil TÜR**: birim bir **para** işareti taşıyor mu?
        # `₺/kg` de bir tutardır. *Bir türü eşitlikle sınamak, o türün bütün
        # biçimlerini reddetmektir.*
        _para_mi = bool(re.search(r"(₺|tl|\$|€|lira)", _birim, re.I))
        if _birim_bekleniyor and _birim and not _para_mi:
            out.append(Ihlal(
                "olcu_ikamesi",
                f"bir **{_birim_bekleniyor} tutarı** sordun ama elimdeki ölçü "
                f"**{_birim}** cinsinden (`{_m}`)",
                "O birimde bir ölçü katalogda yoksa hesabı ben uyduramam — "
                "başka bir ölçü adıyla sorabilirsin."))
            break
        if _toplulastirma_bekleniyor and _m.startswith("toplam_"):
            out.append(Ihlal(
                "olcu_ikamesi",
                f"**ortalama** sordun ama `{_m}` bir **toplam**",
                "Ortalaması katalogda varsa adıyla sorabilirsin "
                "(*«ortalama …»* biçiminde tanımlı bir ölçü)."))
            break

    # 9 · 🔴 **KISITLAMA — «sadece …» dedi, hiçbir şey kısıtlanmadı (2 kanıt).**
    #
    # Ölçüldü: `aylık üretim` → `**sadece** hafta içi günleri al` → **satırlar aynen**
    # döndü, filtre uygulanmadı ve **hiçbir şey beyan edilmedi** (`e16`T2 · `j4`T2).
    #
    # ⊙ Sebebi bir **mutfak** eksiği: `hafta içi` katalogda bir **değer değil** (boyut
    # `hafta_gunu`'nun değerleri tek tek günlerdir), yani garson da onu ifade edemiyor.
    # Ama bu, susmayı **haklı çıkarmaz**: kullanıcı bir kısıtlama istedi ve kısıtlanmamış
    # bir sayı gördü — sessiz-yanlışın tanımı.
    #
    # ⚠ Yüklem dar ve **kapalı bir dilbilgisi sınıfına** dayanır: kısıtlayıcı zarflar
    # (`sadece`·`yalnız`·`yalnızca`·`only`·`just`). Ölçüt yapısal: `cq`'da **tarih dışı**
    # hiçbir filtre yoksa kısıtlama gerçekleşmemiştir.
    #
    # ⚠ Yalnız **beyan eder**, cevabı öldürmez (`KÖK-3`).
    #
    # *Bir kısıtlamayı uygulayamamak bir sınırdır; uygulamadığını söylememek bir hatadır.*
    if re.search(r"\b(sadece|yalniz|yalnizca|only|just)\b", qn) and not any(
            f.get("dimension") and f.get("dimension") != "tarih"
            and f.get("operator") not in ("gte", "lte")
            for f in filtreler):
        out.append(Ihlal(
            "kisitlama",
            "**sadece …** dedin ama sorguya bir kısıtlama taşıyamadım — sayı **tüm**"
            " kayıtları kapsıyor",
            "Kısıtlamayı katalogdaki bir değerle yazarsan (*«sadece Siyah renk»*) "
            "uygularım."))

    # 7 · DIŞLAMA — "X hariç"
    if (niyet.dislama_istendi
            and not any(str(f.get("operator")) in ("neq", "not_in", "!=")
                        for f in filtreler)):
        out.append(Ihlal(
            "dislama",
            "bir şeyi **hariç tutmanı** istedin ama dışlama filtresi kuramadım",
            "Hariç tutulacak değeri açıkça yazarsan (*«RAM-2 hariç»*) uygularım."))

    return out


#: Zaman birimleri — `_TOPN_CUE`nun ("son") yanlış-pozitifini kapatır.
#: 🔴 **`§42` — SINIFIN EKSİK ÜYESİ BİR YANLIŞ BEYAN ÜRETTİ.**
#:
#: Ölçüldü: `2025 ile 2026 **ilk yarısını** kıyasla` → `eksik_niyet:['ustunluk']` ve
#: cevapta *«**en yüksek/en çok** dedin ama sıralama uygulayamadım»*. Kullanıcı öyle bir
#: şey **demedi**; `ilk` orada bir sıra sayısıdır ve `yarı` bir **zaman birimidir**.
#:
#: ⊙ `_ustunluk_mu`'nun kuralı zaten doğruydu (*"ipucundan sonra bir zaman birimi
#: geliyorsa üstünlük değildir"*) — eksik olan **sınıfın bir üyesiydi**: `yarı`/`yarıyıl`.
#:
#: 🔴 Ve `Ö10`'un kuralı burada da geçerli: *yanlış bir beyan sessizlikten kötüdür* —
#: sistem kullanıcıya **onun söylemediği bir şeyi söylediğini** söylüyor.
#:
#: *Bir kuralın yanlış çalışması her zaman kuralın yanlışlığından gelmez; bazen kuralın
#: baktığı kümenin eksikliğindendir.*
#:
#: ⚠ **KAYITLI BORÇ:** `ilk yarı`/`ikinci yarı` bir **dönem olarak da çözülmüyor**
#: (`date_filters("ilk yari")` → boş; oysa `ilk ceyrek` → dolu). Bu ayrı bir iştir; bu
#: madde yalnız **yanlış beyanı** kapatır, dönemi çözmez. İkisini karıştırmak, kapatılan
#: kusurun ölçüsünü kaybettirirdi.
#: ⚠ `§45` — **ÜNSÜZ YUMUŞAMASI da bir yüzey biçimidir.** Kapı `son çeyreğin karlılığı`
#: ile kırmızı verdi: `çeyrek` + ek → `çeyreğ`, ve `k` biten kök `\w{0,4}` ile
#: yakalanamaz çünkü **kökün kendisi değişmiştir**. Türkçede `k→ğ`·`p→b`·`t→d`·`ç→c`
#: kural gereğidir; kökü tanıyıp yumuşamışını tanımamak, aynı kelimenin yarısını bilmektir.
_ZAMAN_BIRIMI = (r"(ay|gun|gün|hafta|yil|yıl|ceyre[kg]|çeyre[kğ]|donem|dönem|saat|dakika"
                 r"|yari|yarı|yariyil|yarıyıl)")


def _olcu_sinonim_araliklari(qn: str, ic: dict, cube_meta: dict | None) -> list[tuple[int, int]]:
    """Sorudaki **ölçü adının** kapladığı aralıklar.

    🔴 Ölçülen yanlış-pozitif (525 meşru soruda 10 tanesi): `kur` cube'unun ölçüsü
    **`en yuksek kur`** diye adlandırılmış. Yani *"bu yıl en yüksek kur"* sorusunda
    `en yüksek` bir **sıralama isteği değil, ölçünün ADIDIR**.

    *Bir ipucu, başka bir şeyin adının içindeyse, ipucu değildir.*
    """
    if not cube_meta:
        return []
    araliklar: list[tuple[int, int]] = []
    secili = set(ic.get("measures") or [])
    for m, syns in (cube_meta.get("measure_synonyms") or {}).items():
        if secili and m not in secili:
            continue
        for syn in (syns or []):
            t = _norm(str(syn).removesuffix("!"))
            if len(t) < 3:
                continue
            for mt in re.finditer(re.escape(t), qn):
                araliklar.append(mt.span())
    return araliklar


def _ustunluk_mu(qn: str, topn_cue, ic: dict | None = None,
                 cube_meta: dict | None = None) -> bool:
    """Gerçekten bir **üstünlük** isteği mi, yoksa bir dönem mi?

    🔴 Ölçülen yanlış-pozitif: `_TOPN_CUE` kalıbı `son`u da içeriyor (çünkü *"son 5
    makine"* meşrudur) ve bu yüzden **`son 3 ay ve son 6 ay ciro`** sorusu *"sıralama
    uygulayamadım"* ihlali veriyordu — oysa orada `son` bir **dönem edatıdır**.

    ⚠ `route()` bu ayrımı zaten yapıyor ama **bağlamla** (`_TOPN_CUE.search(before)`),
    yani ipucunun neyin ÖNÜNDE olduğuna bakarak. Burada aynı ayrım tersten kurulur:
    ipucundan sonra bir **zaman birimi** geliyorsa üstünlük değildir.

    *Bir kalıbı ödünç almak, onun bağlamını da ödünç almayı gerektirir.*
    """
    olcu_araliklari = _olcu_sinonim_araliklari(qn, ic or {}, cube_meta)
    for m in re.finditer(topn_cue.pattern, qn):
        kuyruk = qn[m.end():m.end() + 24]
        # 🔴 **`§45` — `\b` TÜRKÇE EKİ GÖREMİYOR ve kural yarısında ölüydü.**
        #
        # Ölçüldü: `son 3 **ay** ciro` ✅ geçiyor ama `son 3 **ayın** ortalama günlük
        # üretimi` 🔴 geçmiyordu → *«en yüksek/en çok dedin ama sıralama uygulayamadım»*.
        # Kullanıcı öyle bir şey **demedi**.
        #
        # ⊙ Sebep tek karakter: `ay\b` deseni `ayin`de **`y` ile `i` arasında** bir sözcük
        # sınırı arar ve orada sınır **yoktur**. Yani kural, zaman biriminin **çekimsiz**
        # hâlinde çalışıyor, çekimli hâlinde susuyordu — ve Türkçede dönem ifadeleri
        # neredeyse **her zaman** çekimlidir (`ayın`·`ayda`·`aylık`·`yılın`·`çeyreğin`).
        #
        # ⚠ `\w{0,4}` bilerek **sınırlı**: eksiz de olabilir (`ay`), en fazla dört harflik
        # bir ek alabilir (`aylık`). Sınırsız bırakmak `ay` ile başlayan her kelimeyi
        # (`ayrıntı`) zaman birimi sayardı — `§32`'nin dersi: *kısa bir dizge her yere
        # sığar*, o yüzden sağı **açık değil dar** bırakılır.
        #
        # *Bir sınır kontrolü, sınırladığı dilin biçimbilgisini tanımıyorsa yalnız o dilin
        # en yalın hâlinde çalışır — ve gerçek cümleler yalın değildir.*
        if re.match(rf"\s*\d*\s*{_ZAMAN_BIRIMI}\w{{0,4}}\b", kuyruk):
            continue                       # "son 3 ay" / "son 3 ayın" → dönem
        if any(a <= m.start() and m.end() <= b for a, b in olcu_araliklari):
            continue                       # "en yüksek kur" → ölçünün ADI
        return True
    return False


def _zaman_ekseni_var(cq: dict, cube_meta: dict | None) -> bool:
    """Kırılımda bir ZAMAN boyutu var mı — trend gerçekten çizilebiliyor mu?"""
    zaman = set((cube_meta or {}).get("time_dimensions") or ["tarih"])
    return any(d in zaman or str(d).startswith("tarih") for d in (cq.get("dimensions") or []))


#: 🔴 **EŞİK İKİ YERDE YAŞAR — ve kapı yalnız birine bakıyordu.** Curl'de ölçüldü
#: (`§AJ4` sonrası): *"bu yıl 5 milyon üzeri ciro yapan müşteriler"* → `cq` artık
#: `measure_having={"measure":"toplam_ciro","op":">","value":5000000}` **taşıyor**, ama
#: `uyum` yine *"eşiği filtreye çeviremedim"* diyordu.
#:
#: ⊙ Sebep yapısal: **boyut** eşiği `filters`'a (WHERE), **ölçü** eşiği
#: `measure_having`'e (HAVING) gider — ikisi farklı SQL kademesidir ve farklı alanlarda
#: yaşar. Kapı yalnız `filters`'ı sayıyordu.
#:
#: ⚠ Ve bu, kapının en pahalı hata biçimiydi: sistem **doğru olanı yapmıştı** ve
#: kullanıcıya *"yapamadım"* diyordu — yanlış bir özür, yanlış bir cevaptan daha çok
#: güven tüketir çünkü kullanıcı çalışan bir yolu terk eder.
#:
#: *Bir niyetin karşılandığını sormak, onun nereye yazıldığını bilmeyi gerektirir.*


def _esik_filtresi_var(filtreler: list[dict]) -> bool:
    return any(str(f.get("operator")) in ("gt", "lt", "gte", "lte", ">", "<", ">=", "<=")
               and not _tarih_gibi(f.get("value")) for f in filtreler)


def _tarih_gibi(v) -> bool:
    """Dönem filtresini eşik sanma. ⚠ Bu ayrım olmadan **her dönemli soru** eşik
    ihlali verirdi — kapının en olası yanlış-pozitifi."""
    return isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}", v) is not None


# ═══════════════════════════════════════════════════════════════════════════════
# KÖK-3 · BEYANLI KISMİ CEVAP
# ═══════════════════════════════════════════════════════════════════════════════

def kismi_cevap_notu(ihlaller: list[Ihlal]) -> str:
    """*"Şu kısmını verdim, şu kısmını veremedim, nedeni bu."*

    ⚠ **Rozetsizdir**: ADR-0008 *"yanlış cevaba güven rozeti takma"* der; beyanlı kısmi
    cevap o yasağı **çiğnemez, karşılar**. Sayı doğrudur (küpten gelir) — eksik olan
    **sorunun bir parçasıdır** ve bu **yazılır**.
    """
    if not ihlaller:
        return ""
    if len(ihlaller) == 1:
        i = ihlaller[0]
        return f"⚠ Sayı doğru ama **eksik**: {i.aciklama}.\n\n{i.oneri}"
    satirlar = "\n".join(f"· {i.aciklama}" for i in ihlaller)
    return ("⚠ Sayı doğru ama **eksik** — sorunun şu kısımlarını yerine getiremedim:\n"
            f"{satirlar}\n\n{ihlaller[0].oneri}")
