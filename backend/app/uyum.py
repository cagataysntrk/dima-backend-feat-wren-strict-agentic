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


#: Göreli dönem aralığı — *"son 3 ay"*, *"son 6 ay"*. İkisi AYRI birer dönemdir.
_GORELI_DONEM = re.compile(
    r"son\s+(\d+)\s*(ay|gun|hafta|yil|ceyrek)")


def _cok_donem(q: str) -> int:
    """Soruda kaç **AYRI** dönem geçiyor.

    Üç biçim sayılır ve üçü de ölçülerek eklendi:
      · ay adı  — `ocak ve haziran`
      · yıl     — `2025 ve 2026`
      · göreli  — `son 3 ay ve son 6 ay`   ← 🔴 ilk yazımda EKSİKTİ

    ⚠ Üçüncüsü kapıyı ölçerken yakalandı: `son 3 ay ve son 6 ay ciro` hiçbir ihlal
    vermiyordu, oysa `route()` ikisini **tek bir filtreye** (`gte 2026-05-05`) çöküyor
    ve altı ayın üçü sessizce yutuluyordu. *Bir sayacın saymadığı biçim, o sayaç için
    var olmayan bir dünyadır.*
    """
    qn = _norm(q)
    aylar = {a for a in _AY if re.search(rf"(?<![a-z0-9]){a}", qn)}
    yillar = set(re.findall(r"(?<!\d)(20\d{2})(?!\d)", qn))
    goreli = {f"{n}{b}" for n, b in _GORELI_DONEM.findall(qn)}
    return len(aylar) + len(yillar) + len(goreli)


def denetle(q: str, cq: dict, cube_meta: dict | None = None) -> list[Ihlal]:
    """Sorudaki niyet işaretlerinin **sorguda karşılığı var mı?**

    🔴 Boş liste = uyumlu. Dolu liste = **sessiz-yanlış adayı**: cevap üretildi ama
    kullanıcının istediği bir şey sorguya **taşınmadı**.

    ⚠ Kapı **fail-closed değil, BEYAN-AÇIK**: cevabı öldürmez, **etiketler** (KÖK-3).
    Öldürmek kapsamı daraltırdı; etiketlemek daraltmaz ama sessizliği bitirir.
    """
    from app.cube_router import (
        _BREAKDOWN_HINTS,
        _EXCLUDE_MARKERS,
        _PERIOD_RANGE_REF,
        _TOPN_CUE,
        _measure_threshold,
        _time_gran,
        compare_mode,
    )

    out: list[Ihlal] = []
    qn = _norm(q or "")

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
    if compare_mode(qn) and not (ic.get("compare") or ic.get("compare_mode")):
        out.append(Ihlal(
            "kiyas",
            "iki dönemi **kıyaslamanı** istedin ama tek bir toplam üretebildim",
            "İki dönemi ayrı ayrı sorabilirsin; ya da *«geçen yıla göre»* diyerek "
            "dönemsel kıyası açıkça isteyebilirsin."))

    # 2 · ÇOK-DÖNEM — "ocak ve haziran", "2025 ve 2026"
    #    ⚠ Kıyas ihlali zaten yazıldıysa tekrar etme: aynı kaybı iki kez anlatmak,
    #    kullanıcıya iki ayrı sorun varmış gibi görünür.
    if (_cok_donem(qn) >= 2 and not any(i.isaret == "kiyas" for i in out)
            and not (ic.get("compare") or ic.get("compare_mode"))):
        out.append(Ihlal(
            "cok_donem",
            "birden çok dönem saydın ama tek bir **aralık** olarak topladım",
            "Dönemleri ayrı ayrı sorarsan her birini tek tek veririm."))

    # 3 · TREND — zaman ekseni ister
    if _TREND.search(qn) and not (_time_gran(qn) or _zaman_ekseni_var(ic, cube_meta)):
        out.append(Ihlal(
            "trend",
            "**değişimi/trendi** istedin ama tek bir toplam ürettim — zaman ekseni yok",
            "*«aylara göre»* ya da *«çeyreklere göre»* eklersen zaman ekseninde çizerim."))

    # 4 · KIRILIM — mevcut korumanın genelleştirilmiş hâli
    if (any(w in qn for w in _BREAKDOWN_HINTS) and not boyutlar
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
    if _measure_threshold(qn) and not _esik_filtresi_var(filtreler):
        out.append(Ihlal(
            "esik",
            "bir **eşik** verdin (ör. *«1.000 üstü»*) ama filtreye çeviremedim",
            "Eşiği ölçü adıyla birlikte yazarsan (*«cirosu 1.000 üstü»*) uygularım."))

    # 7 · DIŞLAMA — "X hariç"
    if (any(w in qn for w in _EXCLUDE_MARKERS)
            and not any(str(f.get("operator")) in ("neq", "not_in", "!=")
                        for f in filtreler)):
        out.append(Ihlal(
            "dislama",
            "bir şeyi **hariç tutmanı** istedin ama dışlama filtresi kuramadım",
            "Hariç tutulacak değeri açıkça yazarsan (*«RAM-2 hariç»*) uygularım."))

    return out


#: Zaman birimleri — `_TOPN_CUE`nun ("son") yanlış-pozitifini kapatır.
_ZAMAN_BIRIMI = r"(ay|gun|gün|hafta|yil|yıl|ceyrek|çeyrek|donem|dönem|saat|dakika)"


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
        if re.match(rf"\s*\d*\s*{_ZAMAN_BIRIMI}\b", kuyruk):
            continue                       # "son 3 ay" → dönem
        if any(a <= m.start() and m.end() <= b for a, b in olcu_araliklari):
            continue                       # "en yüksek kur" → ölçünün ADI
        return True
    return False


def _zaman_ekseni_var(cq: dict, cube_meta: dict | None) -> bool:
    """Kırılımda bir ZAMAN boyutu var mı — trend gerçekten çizilebiliyor mu?"""
    zaman = set((cube_meta or {}).get("time_dimensions") or ["tarih"])
    return any(d in zaman or str(d).startswith("tarih") for d in (cq.get("dimensions") or []))


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
