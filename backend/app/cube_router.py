"""Deterministik-önce yönlendirme (ADR-0004).

Bilinen metrik sorularını **Wren cube** golden-path'ine yönlendirir: soru bir cube
metriği/boyutu/filtresine güvenle eşlenirse yapısal bir CubeQuery döner; motor bunu
`cube_query_to_sql` ile LLM'siz, deterministik SQL'e derler (🥇). Emin değilse `None`
döner → istek LLM zincirine düşer (bkz. routers/ask.py).

Cube'lar sektör/konu-alanı paketlerinden gelir (ADR-0005); bu router onların üstünde çalışır.

DİSİPLİN (ADR-0008): Bu dosyaya YENİ dil kalıbı (keyword/regex) refleksle EKLENMEZ.
Yeni ifadeler önce LLM yolunda yaşar; buraya terfi ancak (1) log kanıtı, (2) tam-parse-
ya-da-ret garantisi, (3) golden test ve mümkünse metadata/synonyms ile olur.
"""

from __future__ import annotations

import calendar
import contextvars
import difflib
import re
from datetime import date, timedelta

from app.llm import _norm

# Göreli tarih aralığı: "son 3 ay / son 30 gun / son 2 hafta / son yil" → time dim `gte` filtresi.
# Cube'da granularity'siz saf WHERE üretir (ay kovası eklemez) → haftanın-günü vb. bozulmaz.
# Tek yerde tanımlı → her N-ay/gün/hafta/yıl sorgusu deterministik faydalanır (ADR-0004).
_REL_DATE = re.compile(r"son\s+(?:(\d+)\s+)?(ay|gun|hafta|yil)")

# DİL ÇAKIŞMASI (bkz. _time_gran'daki aynı isimli not): "son 4 aya göre" / "son 4 ay
# bazında" gibi ifadeler DÖNEM ifadesidir — buradaki "göre"/"bazında"/"bazlı" bir
# kırılım isteği DEĞİL, göreli tarih aralığının kendi edatıdır. deterministic_refine'ın
# sessiz-yanlış koruması (_BREAKDOWN_HINTS taraması) bu deseni ayrı tutmalı, yoksa
# "son 4 aya göre yap" gibi salt dönem-değişikliği istekleri (log regresyonu:
# test_son_n_aya_gore_kova_degil) yanlışlıkla "karşılanamayan kırılım" sanılır.
_PERIOD_RANGE_REF = re.compile(r"son\s+(?:\d+\s+)?(?:ay|gun|hafta|yil)\w*\s+(?:gore|bazinda|bazli)")


def _months_ago(d: date, n: int) -> date:
    m = d.month - 1 - n
    y = d.year + m // 12
    mm = m % 12 + 1
    return date(y, mm, min(d.day, calendar.monthrange(y, mm)[1]))


def _relative_date_filter(q: str, time_dim: str) -> dict | None:
    m = _REL_DATE.search(q)
    if not m:
        return None
    n = int(m.group(1)) if m.group(1) else 1
    unit = m.group(2)
    today = date.today()
    if unit == "ay":
        start = _months_ago(today, n)
    elif unit == "yil":
        start = _months_ago(today, 12 * n)
    elif unit == "hafta":
        start = today - timedelta(days=7 * n)
    else:  # gun
        start = today - timedelta(days=n)
    return {"dimension": time_dim, "operator": "gte", "value": start.isoformat()}


def _current_period_filter(q: str, time_dim: str) -> dict | None:
    """İçinde bulunulan dönem: "bugün / bu hafta / bu ay / bu yıl" → gte filtresi (Python hesaplar)."""
    today = date.today()
    if "bugun" in q:
        start = today
    elif "bu hafta" in q:
        start = today - timedelta(days=today.weekday())  # Pazartesi
    elif "bu ay" in q:
        start = today.replace(day=1)
    # "bu sene" = "bu yıl"; "tüm yıl" (log-kanıtlı terfi) = yıl başından beri
    elif "bu yil" in q or "bu sene" in q or "tum yil" in q:
        start = today.replace(month=1, day=1)
    else:
        return None
    return {"dimension": time_dim, "operator": "gte", "value": start.isoformat()}


_PREV_RE = re.compile(r"\b(?:bir\s+)?(?:gecen|onceki|evvelki)\s+(ay|hafta|yil|sene|gun)\b")


def _prev_period_filters(q: str, time_dim: str) -> list[dict]:
    """ÖNCEKİ takvim dönemi: "geçen ay / bir önceki ay / geçen hafta / geçen yıl / dün"
    → [gte başı, lte sonu]. (Log 2026-07-20: "geçen ay" gereksiz netleştirme soruyordu.)
    DİKKAT: "geçen aya GÖRE" dönemsel KARŞILAŞTIRMADIR (_COMPARE_HINTS) — burada değil."""
    today = date.today()
    m = _PREV_RE.search(q)
    unit = m.group(1) if m else ("gun" if re.search(r"\bdun\b", q) else None)
    if unit is None:
        return None  # type: ignore[return-value]
    if unit == "ay":
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
    elif unit in ("yil", "sene"):
        start = date(today.year - 1, 1, 1)
        end = date(today.year - 1, 12, 31)
    elif unit == "hafta":
        start = today - timedelta(days=today.weekday() + 7)  # önceki Pazartesi
        end = start + timedelta(days=6)
    else:  # gun → dün
        start = end = today - timedelta(days=1)
    return [
        {"dimension": time_dim, "operator": "gte", "value": start.isoformat()},
        {"dimension": time_dim, "operator": "lte", "value": end.isoformat()},
    ]


# "2. çeyrek / ikinci çeyrek" bir DÖNEMDİR (Nis-Haz aralığı) — kova ("çeyreklere göre")
# değil. _time_gran bu ifadeyi söker; date_filters aralığa çevirir (log 2026-07-21).
_QUARTER_RE = re.compile(
    r"\b(?:([1-4])\s*\.?\s*|(ilk|birinci|ikinci|ucuncu|dorduncu)\s+)ceyrek\w*"
)
_QUARTER_ORD = {"ilk": 1, "birinci": 1, "ikinci": 2, "ucuncu": 3, "dorduncu": 4}


def _quarter_period_filters(q: str, time_dim: str) -> list[dict] | None:
    m = _QUARTER_RE.search(q)
    if not m:
        return None
    n = int(m.group(1)) if m.group(1) else _QUARTER_ORD[m.group(2)]
    ym = re.search(r"\b(20\d{2})\b", q)
    year = int(ym.group(1)) if ym else date.today().year
    start = date(year, 3 * (n - 1) + 1, 1)
    end_mon = 3 * n
    end = date(year, end_mon, calendar.monthrange(year, end_mon)[1])
    return [
        {"dimension": time_dim, "operator": "gte", "value": start.isoformat()},
        {"dimension": time_dim, "operator": "lte", "value": end.isoformat()},
    ]


_MONTHS = {"ocak": 1, "subat": 2, "mart": 3, "nisan": 4, "mayis": 5, "haziran": 6,
           "temmuz": 7, "agustos": 8, "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12}


_AY_ADI_RE = re.compile(
    r"\b(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\b(\s+ayi\w*)?"
)


def _adlandirilan_aylar(q: str) -> list[tuple[int, int]]:
    """Soruda ADI GEÇEN tüm ayları (yıl, ay) olarak, tekrarsız ve sıralı döner.

    FAZ -0.5a — eskiden bu tarama `re.search`'tü ve YALNIZ İLK ayı görüyordu: "ocak şubat
    mart" sorusu sessizce **yalnız Ocak** filtresine çevriliyordu ve cevap `source="cube"`
    rozetiyle geliyordu. Kapsam kapısı da bunu göremiyordu, çünkü `_period_hit_words`
    (1 Ağustos'ta) zaten `finditer`'a geçirilmişti — yani KAPI çoklu ay görüyor,
    ÇÖZÜCÜ tek ay çözüyordu. Asimetri buradaydı.

    "aralık" tek başına belirsizdir ("tarih aralığı") — yalnız "aralık ayı" sayılır.
    Yıl yoksa: geçmişteki en yakın o ay (gelecek ay adı geçen yıla sarar).
    """
    ym = re.search(r"\b(20\d{2})\b", q)
    today = date.today()
    bulunan: list[tuple[int, int]] = []
    for m in _AY_ADI_RE.finditer(q):
        ad = m.group(1)
        if ad == "aralik" and not m.group(2):
            continue
        mon = _MONTHS[ad]
        year = int(ym.group(1)) if ym else (today.year if mon <= today.month
                                            else today.year - 1)
        if (year, mon) not in bulunan:
            bulunan.append((year, mon))
    return sorted(bulunan)


def _bitisik_mi(aylar: list[tuple[int, int]]) -> bool:
    """Aylar AYNI YILDA ve ARDIŞIK mı? ("ocak şubat mart" ✓ · "ocak mart" ✗)

    Bitişiklik şartı keyfi değil, **sözleşmenin sınırı**: `date_filters` düz bir
    `list[dict]` (AND zinciri) döner ve bu biçim ancak TEK bir aralık ifade edebilir.
    Ayrık aylar bir OR/küme gerektirir — o, sözleşme genişletmesidir (Faz 2a), burada
    çözülmez. Burada yapılan tek şey, ayrık durumu **sessizce yanlış çözmemek**.
    """
    if len(aylar) < 2:
        return True
    yillar = {y for y, _ in aylar}
    if len(yillar) > 1:
        return False
    aylar_no = [m for _, m in aylar]
    return aylar_no == list(range(aylar_no[0], aylar_no[0] + len(aylar_no)))


def cozulemeyen_ay_listesi(q: str) -> bool:
    """Soruda BİRDEN ÇOK ay adı geçiyor ve bunlar tek bir aralığa çevrilemiyor mu?

    `_period_gate`'in bunu bilmesi ZORUNLU: `_period_hit_words` ay adlarını görüp
    *"kullanıcı dönem belirtti"* diyor ve kapıyı susturuyor — oysa `date_filters` ayrık
    ayları çözemiyor. O durumda kapı **sormazsa** cevap dönemsiz (tüm zamanlar) gelir ve
    kullanıcı verdiği dönem detayının yok sayıldığını göremez.

    §1.6'nın çarpıcı asimetrisi tam buydu: *"kullanıcı NE KADAR çok dönem detayı verirse,
    kapı O KADAR az soru soruyor."*
    """
    aylar = _adlandirilan_aylar(q)
    return len(aylar) > 1 and not _bitisik_mi(aylar)


_AY_TR = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
          7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
_AY_SORGU = {1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
             7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım", 12: "aralık"}


def ay_netlestirme(q: str) -> list[dict] | None:
    """Ayrık ay listesi için NETLEŞTİRME seçenekleri — kullanıcının KENDİ saydığı aylar.

    Neden jenerik dönem chip'leri yetmiyor: `_PERIOD_SUGGESTIONS` ("Bugün · Bu hafta ·
    Bu ay · Bu yıl · Tümü") *"ocak ve mart"* diyen kullanıcıya **hiçbir şey söylemez** —
    o iki belirli ay istedi, "Bu ay" onun sorduğu şey değil. Belirsizlikte SORMAK
    (ADR-0008) yalnız soru sormak değil, **cevaplanabilir bir soru** sormaktır.

    Üretilen seçenekler: her ay ayrı ayrı + **kapsayan aralık**. Sonuncusu önemli, çünkü
    kapsayan aralık mevcut sözleşmede ifade EDİLEBİLİR — kullanıcı çoğu zaman zaten onu
    kastediyordur ve tek tıkla alır. Ayrık kümenin kendisi (yalnız Ocak + yalnız Mart, arası
    hariç) bir OR gerektirir; o Faz 2a'nın sözleşme genişletmesidir ve burada VAAT EDİLMEZ.
    """
    aylar = _adlandirilan_aylar(q)
    if len(aylar) < 2 or _bitisik_mi(aylar):
        return None
    tek_yil = len({y for y, _ in aylar}) == 1
    out = [{"label": _AY_TR[m] if tek_yil else f"{_AY_TR[m]} {y}",
            "query": f"{_AY_SORGU[m]} ayı {y}"} for y, m in aylar]
    (y0, m0), (y1, m1) = aylar[0], aylar[-1]
    out.append({
        "label": f"{_AY_TR[m0]}–{_AY_TR[m1]} arası (tümü)",
        "query": f"{_AY_SORGU[m0]} {y0} ile {_AY_SORGU[m1]} {y1} arası",
    })
    return out


def _month_range_filters(q: str, time_dim: str) -> list[dict] | None:
    """Ay adı/adları → [gte ilk ayın 1'i, lte son ayın sonu].

    Tek ay ("temmuz ayı", "2025 mart") bugünkü davranışını AYNEN korur.
    Bitişik çoklu ay ("ocak şubat mart") tek bir aralığa çevrilir — bu, mevcut AND-zinciri
    sözleşmesinde ifade EDİLEBİLİR.
    Ayrık aylar ("ocak ve mart") `None` döner: yarım bir filtre (sessizce yalnız Ocak)
    hiç filtreden **kötüdür** — `date_filters`'ın "yarım uygulama yok" disiplininin aynısı.
    O durumda `cozulemeyen_ay_listesi()` True olur ve dönem kapısı SORAR.
    """
    aylar = _adlandirilan_aylar(q)
    if not aylar:
        return None
    if not _bitisik_mi(aylar):
        return None  # ayrık → çözülemez; kapı soracak (cozulemeyen_ay_listesi)
    (y0, m0), (y1, m1) = aylar[0], aylar[-1]
    start = date(y0, m0, 1)
    end = date(y1, m1, calendar.monthrange(y1, m1)[1])
    return [
        {"dimension": time_dim, "operator": "gte", "value": start.isoformat()},
        {"dimension": time_dim, "operator": "lte", "value": end.isoformat()},
    ]


_MONTH_ALT = "ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik"
# "1 ocak 31 mart arası", "ocak - mart arası", "ocak ile haziran arasında"
_RANGE_RE = re.compile(
    rf"(?:(\d{{1,2}})\s+)?({_MONTH_ALT})(?:\s+(20\d{{2}}))?"
    rf"\s*(?:-|–|ile\s+)?\s*"
    rf"(?:(\d{{1,2}})\s+)?({_MONTH_ALT})(?:\s+(20\d{{2}}))?\s+aras"
)


def _explicit_range_filters(q: str, time_dim: str) -> list[dict] | None:
    """Açık tarih aralığı: "1 ocak 31 mart arası" → gte 01-01 + lte 03-31."""
    m = _RANGE_RE.search(q)
    if not m:
        return None
    d1, m1, y1, d2, m2, y2 = m.groups()
    today = date.today()
    year1 = int(y1) if y1 else today.year
    year2 = int(y2) if y2 else year1
    mon1, mon2 = _MONTHS[m1], _MONTHS[m2]
    start = date(year1, mon1, int(d1) if d1 else 1)
    end_day = int(d2) if d2 else calendar.monthrange(year2, mon2)[1]
    end = date(year2, mon2, min(end_day, calendar.monthrange(year2, mon2)[1]))
    if end < start:
        end = date(year2 + 1, mon2, min(end_day, calendar.monthrange(year2 + 1, mon2)[1]))
    return [
        {"dimension": time_dim, "operator": "gte", "value": start.isoformat()},
        {"dimension": time_dim, "operator": "lte", "value": end.isoformat()},
    ]


# "1 marttan itibaren / hazirandan beri" → açık başlangıç (gte); "15 nisana kadar" → lte.
# Ay adı ÇEKİMLİ olabilir (marttan/hazirana) → \w* toleransı.
_OPEN_START_RE = re.compile(
    rf"(?:(\d{{1,2}})\s+)?({_MONTH_ALT})\w*(?:\s+(20\d{{2}})\S*)?\s+(?:itibaren|beri|baslay\w*)"
)
_OPEN_END_RE = re.compile(
    rf"(?:(\d{{1,2}})\s+)?({_MONTH_ALT})\w*(?:\s+(20\d{{2}})\S*)?\s+(?:kadar|dek)"
)


def _month_date(day_s, mon_name, year_s, default_last: bool = False) -> date:
    mon = _MONTHS[mon_name]
    today = date.today()
    year = int(year_s) if year_s else (today.year if mon <= today.month else today.year - 1)
    last = calendar.monthrange(year, mon)[1]
    day = int(day_s) if day_s else (last if default_last else 1)
    return date(year, mon, min(day, last))


def _open_range_filters(q: str, time_dim: str) -> list[dict] | None:
    out: list[dict] = []
    m = _OPEN_START_RE.search(q)
    if m:
        d1, mn, y = m.group(1), m.group(2), m.group(3)
        out.append({"dimension": time_dim, "operator": "gte",
                    "value": _month_date(d1, mn, y).isoformat()})
    m = _OPEN_END_RE.search(q)
    if m:
        d1, mn, y = m.group(1), m.group(2), m.group(3)
        out.append({"dimension": time_dim, "operator": "lte",
                    "value": _month_date(d1, mn, y, default_last=True).isoformat()})
    return out or None


# TEK GÜN ("1 nisan", "15 mart 2026", "1 nisan günü") — canlı bulgu (31 Temmuz 2026):
# `_month_range_filters` ay adını AY BAŞINDAN AY SONUNA çeviriyordu, önündeki gün
# numarasını YOK SAYIYORDU ("1 nisan" → tüm Nisan). Bu, tek gün ile tüm-ay arasındaki
# farkı sessizce kaybediyordu (kullanıcı NET bir gün sordu, ay-toplamı aldı — sessiz-yanlış).
# Yalnız date_filters'ın DİĞER TÜM aralık/açık-uçlu/göreli denemeleri BAŞARISIZ olunca
# denenir (sıra: explicit range → open range → prev → quarter → relative/current →
# TEK GÜN → son çare ay-adı). "arası/itibaren/kadar" gibi işaretçiler zaten önce
# yakalandığından tek-gün burada YALNIZ gerçekten "gün + ay" ifadesiyle eşleşir.
_SINGLE_DAY_RE = re.compile(rf"\b(\d{{1,2}})\s+({_MONTH_ALT})\w*(?:\s+(20\d{{2}}))?\b")


def _single_day_filters(q: str, time_dim: str) -> list[dict] | None:
    m = _SINGLE_DAY_RE.search(q)
    if not m:
        return None
    day_s, mon_name, year_s = m.groups()
    d = _month_date(day_s, mon_name, year_s)
    return [
        {"dimension": time_dim, "operator": "gte", "value": d.isoformat()},
        {"dimension": time_dim, "operator": "lte", "value": d.isoformat()},
    ]


def date_filters(q: str, time_dim: str = "tarih") -> list[dict]:
    """Dönem ifadesini deterministik tarih filtrelerine çevirir: açık aralık
    ("1 ocak 31 mart arası"), göreli ("son 3 ay"), içinde bulunulan ("bu ay") ya da
    AY ADI ("temmuz ayı"). YARIM UYGULAMA YOK: "arası" deniyor ama aralık
    çözülemiyorsa tek-ay eşleşmesine DÜŞÜLMEZ (yanlış yarım filtre, hiç filtreden kötü)."""
    rng = _explicit_range_filters(q, time_dim)
    if rng:
        return rng
    opn = _open_range_filters(q, time_dim)  # "1 marttan itibaren" / "15 nisana kadar"
    if opn:
        return opn
    prev = _prev_period_filters(q, time_dim)  # "geçen ay" / "bir önceki yıl" / "dün"
    if prev:
        return prev
    qp = _quarter_period_filters(q, time_dim)  # "2. çeyrek" / "ikinci çeyrek"
    if qp:
        return qp
    single = _relative_date_filter(q, time_dim) or _current_period_filter(q, time_dim)
    if single:
        return [single]
    if re.search(r"\baras[ıi]", q):
        return []  # aralık istendi ama çözülemedi → yarım ay-adı uygulama YAPMA
    day = _single_day_filters(q, time_dim)  # "1 nisan" (belirli GÜN — ay değil)
    if day:
        return day
    return _month_range_filters(q, time_dim) or []



def is_all_time(q: str) -> bool:
    """"Tüm zamanlar" seçimi — bilinçli tüm-veri isteği (chip ya da yazılı)."""
    s = q.strip()
    return s in ("tumu", "hepsi", "tum veriler") or s.startswith("tum zaman")


def is_period_only(q: str) -> bool:
    """Mesaj sadece bir dönem ifadesi mi ("bu ay", "son 3 ay", "temmuz ayı", "tümü")?

    ⚠️ **ÜRETİMDE ÇAĞRILMIYOR** (2 Ağustos 2026 denetimi: 0 prod referansı, 13 test).
    Amaçlandığı akış — ADR-0007 K3'ün dönem netleştirme chip'i: kullanıcıya *"hangi dönem?"*
    sorulur, *"son 3 ay"* yanıtı gelir — **`deterministic_refine` tarafından ZATEN
    karşılanıyor.** Ölçüldü: `"son 3 ay"` → `gte 2026-05-02`, `"bu yıl"` → `gte 2026-01-01`,
    `"geçen ay"` → `gte/lte` çifti; üçü de doğru. Takip sınıflandırması da refine'ın
    başarısını sinyal olarak kullandığı için bu fonksiyona ihtiyaç duymuyor.

    **Neden silinmedi:** 13 testi Türkçe dönem ifadelerinin (çeyrek varyantları, "evvelki
    ay", "dün için", "tümü") bir **şartnamesidir** ve `deterministic_refine`'ın bunları
    karşılamaya devam etmesi gerekir. Fonksiyonu silmek o şartnameyi de silerdi. Doğru
    kapanış: testleri gerçek akışın (refine) şartnamesine çevirip fonksiyonu kaldırmak —
    ayrı bir tur. O güne kadar bu not, "ölü sanıp silme, önce testleri taşı" uyarısıdır.
    """
    s = q.strip()
    if s in ("bugun", "bu hafta", "bu ay", "bu yil", "bu sene"):
        return True
    if is_all_time(s):
        return True
    if re.fullmatch(r"son\s+(?:\d+\s+)?(ay|gun|hafta|yil)(\s+icin)?", s):
        return True
    if re.fullmatch(r"(?:bir\s+)?(?:gecen|onceki|evvelki)\s+(ay|hafta|yil|sene|gun)(\s+icin)?", s):
        return True
    if s in ("dun", "dun icin"):
        return True
    # "2. çeyrek" / "dönem 2. çeyrek" / "ikinci çeyrek 2026"
    if re.fullmatch(
        r"(?:donem\s+)?(?:20\d{2}\s+)?(?:[1-4]\s*\.?\s*|ilk\s+|birinci\s+|ikinci\s+|ucuncu\s+|dorduncu\s+)"
        r"ceyrek\w*(\s+20\d{2})?(\s+icin)?",
        s,
    ):
        return True
    return bool(re.fullmatch(
        r"(?:20\d{2}\s+)?(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)"
        r"(\s+ayi\w*)?(\s+20\d{2})?(\s+icin)?",
        s,
    ))


def is_capability_query(q: str) -> bool:
    """"Hangi kırılımlara göre detaylandırabilirim?" gibi META-sorular bir DÜZENLEME
    DEĞİL — mevcut cube'un HANGİ boyutları taşıdığının sorulmasıdır (log regresyonu:
    LLM bunu düzenleme sanıp TÜM boyutları rapora ekleyip 861 satır üretiyordu).
    "hangi" + "kırılım/boyut" birlikte geçiyorsa (sıra önemsiz) yakalanır — ayrı ayrı
    ikisi de yaygın kelimeler olduğundan BİRLİKTE geçme şartı yanlış-pozitifi düşürür."""
    return bool(re.search(r"\bhangi\b", q)) and bool(
        re.search(r"\bkirilim\w*\b|\bboyut\w*\b", q))


# --- Generic sinonim eşleştirme (ADR-0005: içerik cube metadata'sında, kod generic) --
# Sinonimler cube metadata.yml'den gelir (wren_service.schema() normalize eder).
# Eşleşme kuralı: sinonim KELİME BAŞINDA başlar ve arkasında yalnız geçerli bir Türkçe ek
# zinciri kalabilir ("ciro" → "cirosu" ✓, "kıyasla" içindeki "yas" ✗); sonu "!" olan
# sinonim hiç ek almadan TAM KELİME eşleşir ("kar!" → "karşılaştır"ı yakalamaz).


# KELİME BAŞI — `\b` DEĞİL. Python'da `_` bir KELİME KARAKTERİDİR, dolayısıyla `\b`
# `yas_grubu` içinde `grubu`'nun önünde sınır GÖRMEZ. Kullanıcılar makine adlarını olduğu
# gibi yapıştırır ("yas_grubu bazında işlenen kg" — canlı test vakası) ve `_uncovered` o
# metni `[a-z]+` ile ZATEN iki kelimeye ayırır. İki mekanizma aynı sınırı görmezse kapsam
# kapısı kendi eşleşmelerini tanımaz hale gelir. Türkçede sınır = harf/rakam OLMAYAN her şey.
_KELIME_BASI = r"(?<![a-z0-9])"


def _syn_hit(q: str, syn: str) -> bool:
    """Sinonim q'da geçiyor mu? — `_covers` ile AYNI biçimbirim disiplini (Faz D3).

    ÖNCEDEN `syn in q` idi: herhangi bir konumda altdizi. `_uncovered`'ın Faz 0.4'te
    düzeltilen kusurunun **kardeşi**; MIMARI §6.1'de *"henüz düzeltilmedi, daha geniş etki
    alanı var"* diye kayıtlıydı. Ölçülen sahte eşleşmeler (2 Ağustos 2026):

        yas ⊂ kıyasla · yas ⊂ kıyaslama · eden ⊂ neden · ay ⊂ detay · ay ⊂ ayrıca

    **`route()`'a bakarak görünmüyordu** çünkü orada kapsam kapısı (`_coverage_ok`) zaten
    çekiliyor. Zarar, kapsam kapısından GEÇMEYEN takip yollarındaydı — `deterministic_refine`,
    `cross_cube_add`, `cross_cube_dim_switch` (takip sorusu eksik cümledir, kapsam kapısı
    uygulanamaz). Ölçüldü: `deterministic_refine(ik raporu, "kıyaslama yap")` rapora
    **`yas_grubu` GROUP BY'ı** ekliyordu — kullanıcının hiç istemediği bir kırılım, her
    hücredeki sayıyı değiştiren, `source="cube"` rozetiyle gelen bir cevap.

    Faz 0.5'in `_match_dims` tahkimi bunu kurtaramaz: tahkim *hangi eşleşme kazanır*
    sorusunu çözer, *bu eşleşme gerçek mi* sorusunu değil.

    Kural `_covers`'ın aynısıdır (Türkçe EKLEMELİ dildir, ek SONA gelir) ve `_ek_gecerli`
    üzerinden **tek kaynaktan** gelir: kelime başı çapası + olumsuzluk eki reddi + geçerli
    ek zinciri. Çok kelimeli sinonimlerde çekim son kelimeye gelir ("fire oranını" ✓).
    """
    if syn.endswith("!"):
        return re.search(rf"{_KELIME_BASI}{re.escape(syn[:-1])}(?![a-z0-9])", q) is not None
    # `_ek_gecerli`/`_SUFFIX_CHAIN_RE` modülün ilerisinde tanımlı (biçimbirim bloğu bir arada
    # dursun diye); çağrı anında modül tam yüklü olduğundan ileri referans güvenlidir.
    return any(_ek_gecerli(m.group(1))
               for m in re.finditer(rf"{_KELIME_BASI}{re.escape(syn)}([a-z]*)", q))


def _any_hit(q: str, syns) -> bool:
    return any(_syn_hit(q, s) for s in syns or [])


_TOPN_CUE = re.compile(r"\b(ilk|son|top|en|ust|alt)\b")
# Sayının DEĞER değil MİKTAR/dönem olduğunu gösteren ardıl birimler.
_NUM_UNIT_AFTER = re.compile(r"\s*(adet|tane|kez|kalem|adetlik|ay|gun|hafta|yil|"
                            r"milyon|bin|tl|lira|kg|kilo|ton|adette)")


def _value_token_hit(q: str, nv: str) -> bool:
    """Kategorik DEĞER eşleşmesi: kelime başından, çekim ekine toleranslı
    ("antrasitte" ← Antrasit) — ama salt altdizi DEĞİL ve dönem ifadesinin parçası
    olan token'a bağlanmaz ("GEÇEN ay" ← Gece filtresi olmaz; log-kanıtlı tuzak).

    SAYISAL enum değeri (şube/depo/TRCODE "1".."8") ÖZEL: `\\b1\\w*` öneki "10/15/1990"ı
    yakalayıp hayalet WHERE üretiyordu (panel K1, sessiz-yanlış). Saf sayı için TAM-token
    eşleşme + top-N ("ilk 5") / miktar-birim ("3 adet") / dönem bağlamındaki sayıyı DEĞER
    sayma."""
    if nv.isdigit():
        for m in re.finditer(rf"\b{re.escape(nv)}\b", q):
            before = q[max(0, m.start() - 14):m.start()]
            if _TOPN_CUE.search(before):
                continue  # "ilk 5", "son 3", "en çok 10" → top-N sayısı, kategori değil
            if _NUM_UNIT_AFTER.match(q[m.end():m.end() + 10]):
                continue  # "3 adet / 5 milyon / 2 ay" → miktar/dönem, kategori değil
            return True
        return False
    m = re.search(rf"\b{re.escape(nv)}\w*", q)
    if not m:
        return False
    period = _period_hit_words(q)
    toks = re.findall(r"[a-z0-9]+", m.group(0))
    return not any(t in period for t in toks)


def _cube_meta(schema: dict, name: str) -> dict | None:
    return next((c for c in schema.get("cubes", []) if c.get("name") == name), None)


def is_period_optional(measure: str | None, cube_meta: dict | None) -> bool:
    """Dönem-kapısı (ask.py `_period_gate`) İÇİN tek gerçek kaynak: hangi ölçüde
    "hangi dönem?" SORULMAZ. Yalnız semi-additive (bakiye/stok — dönemsiz SUM = güncel
    bakiye, zaten as-of-now) bunun dışında tutulur. Diğer TÜM ölçülerde (avg/oran dahil)
    dönem sorulur — kırılımlı sorularda bile sessiz tüm-zaman varsayımı YOK, kullanıcı
    "Tümü" chip'iyle bilinçli tercih eder (ürün politikası, bkz. tests/test_ask_golden.py
    `_ask_all_time` — "dönem bilgisi yoksa KIRILIMLI sorularda da sorulur")."""
    if not measure or not cube_meta:
        return False
    return measure in (cube_meta.get("semi_additive") or [])


_ADD_RE = re.compile(r"\b(ekle\w*|ayrica|bir de|yanina|ilave|dahil et|hem de)\b")


def cross_cube_add(prev: dict, q: str, schema: dict) -> dict | None:
    """CROSS-CUBE BLEND ("kâr da ekle"): mevcut cube'da OLMAYAN ama BAŞKA cube'da olan bir
    ölçüyü mevcut rapora `blend` olarak katar (konu değiştirme değil). Uyum: mevcut kırılım
    boyutları hedef cube'da da bulunmalı (zaman ekseni tüm cube'larda var). q ekleme-niyeti
    içermeli ("ekle/ayrıca/bir de"). Aksi halde None → çağıran normal akışa döner."""
    if not _ADD_RE.search(q):
        return None
    prev_cube = prev.get("cube")
    if not prev_cube or not prev.get("measures"):
        return None
    prev_meta = _cube_meta(schema, prev_cube)
    if prev_meta is None or _match_measure(q, prev_meta)[0]:
        return None  # ölçü mevcut cube'da eşleşiyorsa aynı-cube ekleme → refine (blend değil)
    prev_dims = prev.get("dimensions") or []
    for cm in schema.get("cubes", []):
        if cm.get("name") == prev_cube:
            continue
        m = _match_measure(q, cm)[0]
        if not m:
            continue
        in_report = m in (prev.get("measures") or []) or any(
            m in (b.get("measures") or []) for b in prev.get("blend", []))
        if in_report:
            continue
        if any(d not in (cm.get("dimensions") or []) for d in prev_dims):
            continue  # hedef cube mevcut kırılımı taşımıyor → o grain'de blend olmaz
        import copy

        cq = copy.deepcopy(prev)
        cq.setdefault("blend", []).append({"cube": cm["name"], "measures": [m]})
        return cq
    return None


def cross_cube_dim_switch(prev: dict, q: str, schema: dict) -> dict | None:
    """Mevcut cube istenen KIRILIMI taşımıyorsa ("stok adı"/"ürün bazlı" ama rapor ticaret'te),
    o boyutu + mevcut ÖLÇÜLERİN HEPSİNİ birlikte taşıyan başka cube'a geçir. Kullanıcı cube'la
    ilgilenmez (canlı 2026-07-25: "ticaret'te stok_adi yok" diye REDdediyordu) — çağıran en
    fazla "cube değişti" bilgisi verir. Boyut zaten mevcut cube'daysa None (normal refine)."""
    import copy

    prev_cube = prev.get("cube")
    prev_measures = prev.get("measures") or []
    if not prev_cube or not prev_measures:
        return None
    prev_meta = _cube_meta(schema, prev_cube)
    if prev_meta is None or _match_dims(q, prev_meta):
        return None  # istenen boyut zaten burada → normal refine, geçiş yok
    for cm in schema.get("cubes", []):
        if cm.get("name") == prev_cube:
            continue
        dims = _match_dims(q, cm)
        if not dims or any(m not in (cm.get("measures") or []) for m in prev_measures):
            continue  # bu cube ya boyutu ya da mevcut ölçüleri taşımıyor
        cq = copy.deepcopy(prev)
        cq["cube"] = cm["name"]
        cq["dimensions"] = list(dict.fromkeys((cq.get("dimensions") or []) + dims))
        return cq
    return None


def match_kpi(q_norm: str, schema: dict) -> str | None:
    """Zaten NORMALİZE edilmiş soru metnini (`_norm(...)` — çağıranın sorumluluğu, `route()`'un
    kendi `q_norm`'uyla TUTARLI kalsın diye burada TEKRAR normalize EDİLMEZ) derlenmiş
    CROSS-CUBE KPI kataloğuna (`WrenService.schema()["kpis"]` — `app/kpi.py::load_kpis`,
    yalnız gerekli türev-view'ları ÜRETİLMİŞ şirketlerde dolu olur, ör. CCC/cari oran) karşı
    eşler, eşleşen KPI'nın ADINI (`kpis/<ad>.yml`'deki `name`) döner.

    Doğrulama turu düzeltmesi (1 Ağustos 2026): bu katalog metadata için (`app/wren_
    service.py`) ZATEN hazırlanmıştı ("yönlendirme için ad/etiket/sinonim") ve `tests/
    test_kpi.py` bu fonksiyonun VAR OLMASINI ZATEN BEKLİYORDU (`test_likidite_kpileri_
    mizan_uzerinde`, `test_match_kpi_en_uzun_sinonim_kazanir`).

    ⚠️ **DÜZELTME (Faz -0.5b, 2 Ağustos 2026):** yukarıdaki notun ilk hâli *"cube_router.py'de
    HİÇ TANIMLANMAMIŞTI"* diyordu — **yanlıştı**. 12 satır yukarıda ikinci bir `match_kpi`
    tanımı duruyordu; Python modül seviyesinde ikinciyi bağladığı için birincisi **sessizce
    gölgeleniyor ve ölü kalıyordu**. Yani testler bu tanımı çağırıyordu, öteki hiç
    çağrılmıyordu. İki tanımın semantiği de farklıydı: ölü olan `_syn_hit()` ile **Türkçe ek
    farkındaydı**, yaşayan bu tanım çıplak `in` kullanıyor. Ölü tanım silindi; **ek
    farkındalığının kaybı bilinçli bir kabul değil, ölçülmemiş bir borçtur** — KPI sinonimleri
    bugün tam-alt-dizi eşleşiyor ve `len >= 3` tabanıyla korunuyor (aşağıda). `schema()["kpis"]` boş olan şirketlerde (demo-boyahane dahil ÇOĞU
    demo/tenant) HER ZAMAN None döner — davranış DEĞİŞMEZ, KPI paketi derlenmiş
    şirketlerde (gulteks/gitas gibi) devreye girer.

    Birden fazla KPI eşleşirse EN UZUN eşleşen sinonim kazanır (cube-eşleştirmedeki
    "ölçü kanıtı" ilkesiyle AYNI ruh — daha spesifik ifade önceliklidir)."""
    kpis = schema.get("kpis") or []
    if not kpis:
        return None
    best_name: str | None = None
    best_len = 0
    for k in kpis:
        candidates = list(k.get("synonyms") or [])
        if k.get("label"):
            candidates.append(_norm(str(k["label"])))
        for syn in candidates:
            syn_n = str(syn).strip()
            if syn_n and len(syn_n) >= 3 and syn_n in q_norm and len(syn_n) > best_len:
                best_name = k.get("name")
                best_len = len(syn_n)
    return best_name


def _longest_syn_hit(q: str, cube: dict) -> int:
    """Bu cube'un q'da eşleşen EN UZUN sinonimin harf sayısı (eşleşme yoksa 0).

    `_match_cube`'un TB4 kırıcısının ölçüsüdür ve `cube_tie_candidates` de AYNI ölçüyü
    okur — beraberlik tanımı ile beraberliği kıran kural tek kaynaktan gelsin diye modül
    seviyesine çıkarıldı (ikisi ayrışırsa chip, route'un çözebildiği bir soruya sorulur)."""
    best = 0
    for s in cube.get("synonyms") or []:
        if _syn_hit(q, s):
            best = max(best, len(s.removesuffix("!")))
    return best


def _match_cube(q: str, schema: dict) -> dict | None:
    """Cube-düzeyi sinonimlerden aday cube. Birden fazla aday → ÖLÇÜ kanıtıyla kırılır:
    yalnız birinde ölçü sinonimi de geçiyorsa ("müşteri bazında SU tüketimi" → su cube'u;
    "müşteri" paylaşılan boyut kelimesidir) o kazanır; yoksa None (çapraz konu → LLM)."""
    hits = [c for c in schema.get("cubes", []) if _any_hit(q, c.get("synonyms"))]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # ÖLÇÜ-KANITI (en spesifik ölçü kazanır): eşleşen ÖLÇÜ sinonimi EN UZUN olan cube.
        # "satış miktarı" → mal.satis_miktari ("satış miktarı"=13) > ticaret.satis_tutari
        # ("satış"=5) → mal. Cube-düzeyi kelime uzunluğu (satış=5 vs miktar=6) yanıltıcıydı:
        # jenerik cube-sinonimi ("satış"/"miktar") spesifik ölçüyü gölgeliyordu (panel Y1/K1).
        m_scored = sorted(((c, _match_measure(q, c)[1] or "") for c in hits),
                          key=lambda x: len(x[1]), reverse=True)
        top_syn, snd_syn = m_scored[0][1], m_scored[1][1]
        # BOYUT-UYUMU ÖNCELİĞİ (canlı bulgu, 1 Ağustos 2026): rakip adayın (2. sırada) HİÇ
        # ölçü sinonimi eşleşmediği (`snd_syn` boş) durumda, aşağıdaki ölçü-kanıtı testi
        # (boş string HER string'in alt-dizisidir) DAİMA en-üstteki adayı kazandırır — o
        # adayın "ölçü kanıtı" yalnız CUBE-KİMLİĞİ kelimesinin PAYLAŞILMASINDAN geliyor
        # olsa bile. "satış" hem parti (toplam_ciro'nun ölçü sinonimi "satış") hem
        # ticaret'in (YALNIZ cube-kimliği, HİÇ ölçü sinonimi yok) kimliğiyken "türlere göre
        # satış trendi" bu yüzden HER ZAMAN parti'ye gidiyordu — ama "tür" boyutu YALNIZ
        # ticaret'te var, parti kırılımı SAĞLAYAMAZ. Soru AÇIKÇA bir kırılım istiyorsa
        # (`_BREAKDOWN_HINTS`) VE adaylardan YALNIZ biri o kırılımı karşılayabiliyorsa
        # (`_match_dims`, aşağıdaki BOYUT-KANITI bloğuyla AYNI mekanizma) ölçü-kanıtı bu
        # ÖZEL durumda güvenilmez sayılır. YALNIZ zaten-belirsiz dalda çalışır ve YALNIZ
        # "ölçü kanıtı bir tarafta sıfır" örüntüsünde devreye girer — `snd_syn` DOLUYSA
        # (iki taraf da ölçü sinonimi taşıyorsa, ör. test_boyut_kaniti_belirsiz_olcuyu_
        # ayirir) davranış HİÇ DEĞİŞMEZ.
        if top_syn and not snd_syn and any(w in q for w in _BREAKDOWN_HINTS):
            dim_owners = [c for c in hits if _match_dims(q, c, None)]
            if len(dim_owners) == 1 and dim_owners[0] is not m_scored[0][0]:
                return dim_owners[0]
        # YALNIZ aynı ifade için rekabette uygula: kısa eşleşme uzun eşleşmenin ALT-DİZİSİ
        # ise (ör. "satış" ⊂ "satış miktarı") en spesifik ölçü kazanır. İki AYRI ifade
        # ("verim VE fire oranı") çok-ölçü/çapraz-cube'dur → kırma, None (LLM).
        if top_syn and len(top_syn) > len(snd_syn) and snd_syn in top_syn:
            return m_scored[0][0]
        # BOYUT-KANITI: ölçü belirsizse (satis_tutari hem ticaret hem mal'da) ama soru
        # bir BOYUT kırılımı istiyorsa ("stok ref bazında") ve o boyut adaylardan
        # YALNIZ birinde varsa o kazanır. "stok ref bazında satış tutarı" → stok_ref
        # yalnız mal'da → mal; "cari ref bazında" → yalnız ticaret'te → ticaret.
        dim_owners = [c for c in hits if _match_dims(q, c, None)]
        if len(dim_owners) == 1:
            return dim_owners[0]
        # EN SPESİFİK TERİM kazanır: en uzun eşleşen sinonim ("cari yaşlandırma" →
        # "yaşlandırma" 11 > "cari" 4 → yaslandirma). Genel entity kelimesinin
        # (cari/stok) spesifik rapor kelimesini gölgelemesini önler.
        scored = sorted(hits, key=lambda c: _longest_syn_hit(q, c), reverse=True)
        # Fark BELİRGİN olmalı (≥4 harf): "yaşlandırma"(11) vs "cari"(4) → yaslandirma;
        # ama "fire"(4) vs "üretim"(6) → gerçek belirsizlik, kırma (çapraz konu → sor).
        if _longest_syn_hit(q, scored[0]) - _longest_syn_hit(q, scored[1]) >= 4:
            return scored[0]
        # cube-düzeyi çoklu aday, kırılamadı. Kanıt EŞİTSE bu bir tahmin sorusu değil bir
        # SORU sorma anıdır → `cube_tie_candidates` netleştirme chip'i üretir (Faz 3.1).
        return None
    # ÖLÇÜ-KELİMESİYLE CUBE SEÇİMİ (ADR-0018 §2-2 kaldıracı): cube-düzeyi sinonim
    # hiç geçmedi ama bir ÖLÇÜ sinonimi geçiyorsa ("hasılat", "bakiye", "kaç fatura")
    # o cube seçilir — kullanıcı çoğu zaman cube adını değil ÖLÇÜyü söyler. YALNIZ tek
    # aday varsa (belirsizse LLM); arketip/overlay bu yolla tam verimli olur.
    by_measure = [c for c in schema.get("cubes", []) if _match_measure(q, c)[0]]
    if len(by_measure) == 1:
        return by_measure[0]
    return None


def _match_measure(q: str, cube: dict) -> tuple[str | None, str | None]:
    """Mesajda AÇIKÇA geçen ölçü: (ölçü, eşleşen sinonim metni). En uzun sinonim kazanır
    ("fire oranı" > "fire"). Eşleşme yoksa (None, None) — varsayılanı çağıran uygular."""
    best: tuple[str | None, str] = (None, "")
    for m, syns in (cube.get("measure_synonyms") or {}).items():
        for s in syns:
            plain = s.removesuffix("!")
            if len(plain) > len(best[1]) and _syn_hit(q, s):
                best = (m, plain)
    return (best[0], best[1] or None)


# Entity'siz jenerik boyut token'ları (normalize/ascii): "stok adı" gibi bir sorguda
# stok_adi'yi NİTELİKLİ yapan "stok"/"stok adi"nin aksine, bunlar tek başına kardeş bir
# *_adi/*_kodu boyutunu (cari_adi) yanlışça çekebilir → 1b jenerik-entity dedup'ında kullanılır.
_GENERIC_DIM_TOKENS = frozenset({"ad", "adi", "isim", "ismi", "kod", "kodu", "no"})


def _match_dims(q: str, cube: dict, measure_syn: str | None = None) -> list[str]:
    """Sorudaki TÜM cube boyutları (metadata sırasıyla). Boyut kelimesi yalnız eşleşen
    ölçü sinoniminin içinde geçiyorsa sayılmaz (ör. "renk sapması" → renk boyut değil)."""
    dims: list[str] = []
    matched_via: dict[str, str] = {}  # d → eşleşen EN UZUN sinonim (nitelik ayrımı için)
    for d, syns in (cube.get("dimension_synonyms") or {}).items():
        best: str | None = None
        for s in syns:
            plain = s.removesuffix("!")
            if not _syn_hit(q, s):
                continue
            if (
                measure_syn
                and plain in measure_syn
                and q.count(plain) <= measure_syn.count(plain)
            ):
                continue  # yalnız ölçü ifadesinin parçası
            if best is None or len(plain) > len(best):
                best = plain
        if best is not None:
            dims.append(d)
            matched_via[d] = best
    # EN SPESİFİK EŞLEŞME KAZANIR (Faz 0.5, 2 Ağustos 2026) — `_match_measure`'ın ZATEN
    # uyguladığı disiplinin boyut tarafındaki karşılığı. Bir boyut YALNIZCA daha spesifik
    # bir ifadenin PAYLAŞILAN parçası sayesinde eşleştiyse, o eşleşme kullanıcının niyeti
    # DEĞİLDİR ve raporun grain'ini bozar.
    #
    # Canlı üretilen kanıt (demo-boyahane, `parti` cube'u):
    #   ham_grup  sinonimleri: [..., "ham grubu",  "grubu", ...]
    #   yas_grubu sinonimleri: [..., "yas grubu",  "grubu", ...]
    #   "yas grubu bazinda fire orani" → ['ham_grup', 'yas_grubu']       ← 2 boyut
    #   "ham grubu bazinda fire orani" → ['kumas_cinsi','ham_grup','yas_grubu'] ← 3 boyut
    # Her fazla kolon GROUP BY'ı böler: satır sayısı ve her hücredeki SAYI değişir.
    # Kullanıcı bir kırılım istedi, üçünü birden değil.
    #
    # Kural: A'nın eşleştiği sinonim, B'nin eşleştiği sinonimin ÖZ ALT-DİZİSİYSE A düşer
    # ("grubu" ⊂ "yas grubu" → ham_grup düşer; "ham" ⊂ "ham grubu" → kumas_cinsi düşer).
    # Eşit eşleşmeler (iki boyut AYNI sinonimle geldiyse) GERÇEK bir belirsizliktir ve
    # burada çözülmez — dokunulmaz. Bu durum esas olarak ilişki-türevi boyutlar
    # yayımlanınca (Faz 1) yaygınlaşacak; o zaman `route()`'un bir belirsizlik SİNYALİ
    # döndürüp chip sorması gerekecek (Faz 3.1), sessizce birini seçmesi değil.
    _drop = {
        d for d in dims
        if any(o != d
               and matched_via.get(d, "") != matched_via.get(o, "")
               and matched_via.get(d, "") in matched_via.get(o, "")
               for o in dims)
    }
    if _drop:
        dims = [d for d in dims if d not in _drop]
        for d in _drop:
            matched_via.pop(d, None)

    # AD/KOD ÇİFTİ dedup: jenerik entity kelimesi ("stok"/"cari") hem <base>_adi hem
    # <base>_kodu'yu eşliyor → ikisi birden eklenip satırları böler + kod gürültüsü
    # (canlı gitas log 2026-07-24: "stok türlerine göre" → stok_adi+stok_kodu, 271 satır).
    # Soru açıkça "kod" demiyorsa yalnız ADI kalır (kullanıcı "türleri/isimleri" ister).
    if "kod" not in q:
        for d in list(dims):
            if d.endswith("_kodu") and f"{d[:-5]}_adi" in dims:
                dims.remove(d)
                matched_via.pop(d, None)
    # JENERİK-ENTITY dedup (1b — canlı gitas log): "stok"/"cari" gibi FARKLI entity'lerin
    # _adi/_kodu boyutları çoğu şemada bare "adi"/"kod" sinonimini PAYLAŞIR. "stok adı" →
    # stok_adi NİTELİKLİ ("stok"/"stok adi") eşleşirken cari_adi bare "adi" ile de eşleşip
    # sızıyordu (yanlış kırılım). Kural: aynı sonek grubunda NİTELİKLİ (entity'li) eşleşme
    # varsa, YALNIZ jenerik token'la geleni düş. İki taraf da nitelikliyse ("cari ve stok
    # bazında") ikisi de kalır; ikisi de jenerikse ("adı bazında") ayrım yok → dokunma.
    for suffix in ("_adi", "_kodu"):
        grp = [d for d in dims if d.endswith(suffix)]
        if len(grp) < 2:
            continue
        if any(matched_via.get(d) not in _GENERIC_DIM_TOKENS for d in grp):
            for d in grp:
                if matched_via.get(d) in _GENERIC_DIM_TOKENS:
                    dims.remove(d)
    return dims


# Ölçü-çıkarma fiilleri (çok-ölçülü rapor düzenlemesi). "çıkar"→cikar, "sil" tam-kelime
# (silindir/silo'yu yakalamasın). "gösterme/gizle/olmasın/istemiyorum" olumsuz kalıplar.
_RM_VERB_RE = re.compile(
    r"\b(gosterme\w*|gizle\w*|kaldir\w*|cikar\w*|sil|silelim|silsin|istemiyorum|istemem|olmasin)\b")


def deterministic_refine(prev: dict, q: str, schema: dict) -> dict | None:
    """Yaygın konuşmasal düzenlemeleri LLM'SİZ uygular (deterministik-önce, ADR-0004):
    granularity ("aylara göre"), boyut ekle ("makine kırılımı"), sıralama ("en düşük"),
    dönem ("bu ay"). Ölçü değişiyorsa ya da hiçbir düzenleme yoksa None (LLM'e bırak)."""
    import copy

    cube_meta = _cube_meta(schema, prev.get("cube"))
    if cube_meta is None:
        return None
    em, msyn = _match_measure(q, cube_meta)
    # DÜZELTME KALIBI "X değil Y" / "X yerine Y": istenen ölçü işaretten SONRAKİ
    # parçadadır — en-uzun-sinonim tüm cümlede yanlış tarafı seçebilir ("fire oranı
    # değil kar oranı"). Aynı cube içinde açık ölçü takası kırılım/dönem/filtre
    # KORUNARAK deterministik uygulanır; kalıp yoksa ölçü değişimi LLM'e kalır.
    swap = None
    corr = re.search(r"\b(degil|yerine)\b", q)
    if corr:
        em2, msyn2 = _match_measure(q[corr.end():], cube_meta)
        if em2:
            em, msyn = em2, msyn2
            if em2 not in prev.get("measures", []):
                swap = em2
    # VARLIK TOP-N: mesajdaki ölçü ("en çok SATIŞ yapılan 3 müşteri") seçim ÖLÇÜTÜdür,
    # rapor ölçüsü değişimi değil — measure-change bail'ini tetiklememeli.
    topn = None
    if prev.get("timeDimensions") or _time_gran(q):
        topn = _top_n_entity(q, cube_meta)
    if em and em not in prev.get("measures", []) and swap is None and topn is None:
        return None  # farklı metrik açıkça isteniyor → yeni sorgu, LLM sınıflandırsın
    time_dims = cube_meta.get("time_dimensions") or ["tarih"]
    cq = copy.deepcopy(prev)
    changed = False
    already = False  # istek mevcut durumla zaten örtüşüyor (no-op) → LLM'e düşme

    if swap:
        cq["measures"] = [swap]
        if cq.get("order"):
            cq["order"] = {"measure": swap, "direction": cq["order"].get("direction", "desc")}
        changed = True

    # ÖLÇÜ ÇIKARMA: "X'i kaldır/çıkar/gösterme/gizle/sil/istemiyorum" — çok-ölçülü raporda
    # adı geçen ölçüyü düşürür (kalan ≥1). Türkçe SOV: ölçü fiilin ÖNÜNDE ("alım tutarını
    # çıkar"); orada yoksa ARDINDA da bakılır ("çıkar alım tutarını"). Fiil kelimeleri
    # kapsam kapısına takılmasın diye known'e eklenir (canlı 2026-07-25: "kaldır" uygulanıp
    # coverage'ta None'a düşüyordu; "çıkar" hiç tetiklenmiyordu — regex'te yoktu).
    rm_verb_words: set[str] = set()
    for nm in _RM_VERB_RE.finditer(q):
        rm_verb_words.update(re.findall(r"[a-z]+", nm.group(0)))
        dm, _s = _match_measure(q[: nm.start()].rsplit(",", 1)[-1][-40:], cube_meta)
        if not (dm and dm in (cq.get("measures") or [])):
            dm, _s = _match_measure(q[nm.end():][:40], cube_meta)
        if dm and dm in (cq.get("measures") or []) and len(cq["measures"]) > 1:
            cq["measures"] = [x for x in cq["measures"] if x != dm]
            if (cq.get("order") or {}).get("measure") == dm:
                cq.pop("order")
            changed = True

    gran = _time_gran(q)
    if gran:
        existing = (prev.get("timeDimensions") or [{}])[0].get("granularity")
        if gran == existing:
            already = True
        else:
            cq["timeDimensions"] = [{"dimension": time_dims[0], "granularity": gran}]
            changed = True
            # VARLIK top-N'e ÇEVİR (canlı gitas 2026-07-24): mevcut SATIR-limiti + sıralama
            # + boyut varken zaman kovası eklemek seriyi keser — "en çok 20 ürün" sonra
            # "aylık" = toplam 20 SATIR olurdu; oysa 20 ürünün TÜM aylık serisi istenir.
            # Row-limit → entity_limit (ilk N varlık seçilir, ask.py iki adımda çözer).
            if cq.get("limit") and cq.get("order") and cq.get("dimensions") and "entity_limit" not in cq:
                cq["entity_limit"] = {
                    "dimension": cq["dimensions"][0],
                    "measure": cq["order"]["measure"],
                    "direction": cq["order"].get("direction", "desc"),
                    "n": cq["limit"],
                }
                cq.pop("limit", None)
                cq.pop("order", None)

    dims = list(cq.get("dimensions", []))
    matched_dims_now = _match_dims(q, cube_meta, msyn)
    for d in matched_dims_now:
        if d in dims:
            already = True  # ör. "haftanın günleri bazında" — boyut zaten raporda
        else:
            dims.append(d)
            changed = True
    if dims:
        cq["dimensions"] = dims

    # SESSİZ-YANLIŞ koruması (route()'un AYNI ilkesi — bkz. _BREAKDOWN_HINTS kullanımı
    # orada — canlı bulgu, 1 Ağustos 2026): mesaj açıkça bir kırılım istiyor ("personel
    # bazlı verimlilik") ama BU cube'un HİÇBİR boyutu eşleşmediyse (ör. oee'de personel/
    # operatör boyutu yok — yalnız parti'de var, ama parti'nin "verimlilik" ölçüsü de yok,
    # gerçekten çapraz-cube bir istek), eski boyutu/filtreyi (ör. önceki "makine=RAM-2")
    # SESSİZCE KORUYUP yalnız dönemi değiştirip "başarılı" gibi göstermek YANLIŞTIR —
    # çağıran (ask.py) BUNUN İÇİN zaten bir düşme zinciri kuruyor (cross_cube_add →
    # cross_cube_dim_switch → fresh route()) ama bu fonksiyon "changed=True" (yalnız
    # dönem değişti) dönünce o zincire HİÇ ULAŞILMIYORDU. `_time_gran(q) is None` şartı
    # BİLEREK dar tutuldu: "aylara göre"/"çeyreklere göre" gibi AÇIK zaman-birimi
    # ifadeleri de "göre"/"bazında" içerir ama KENDİ BAŞINA meşru bir isteklerdir (route()
    # kırılım-koruması düzeltmesinde AYNI yanlış-pozitif yakalanmıştı) — yalnız hem zaman
    # HEM boyut sinyali YOKSA (ikisi de boş) gerçekten karşılanamayan bir istek olduğu
    # kesinleşir. `_PERIOD_RANGE_REF` deseni de aynı gerekçeyle hariç tutulur: "son 4
    # aya göre yap" gibi ifadelerde "göre" kırılım değil, dönem aralığının edatıdır.
    if (not matched_dims_now and _time_gran(q) is None
            and any(w in q for w in _BREAKDOWN_HINTS) and not _PERIOD_RANGE_REF.search(q)):
        return None

    if topn:
        el = dict(topn)
        el["measure"] = el["measure"] or (cq.get("measures") or [None])[0]
        if el["measure"]:
            cq["entity_limit"] = el
            cq.pop("limit", None)  # satır limiti değil varlık limiti
            changed = True

    direction = _direction(q)
    if direction and cq.get("measures") and not topn:
        cq["order"] = {"measure": cq["measures"][0], "direction": "asc" if direction == "ASC" else "desc"}
        changed = True

    # Satır limiti ("... 5 cari"): yalnız zaman kovasız raporda — kovalı seride satır
    # limiti seriyi keser (o durum entity_limit'in işi, yukarıda).
    n_lim = _top_n(q, cube_meta)
    if n_lim and not topn and not cq.get("timeDimensions") and cq.get("limit") != n_lim:
        cq["limit"] = n_lim
        changed = True

    # Kategorik DEĞER filtreleri ("kadın çalışanlar için" → cinsiyet=Kadın): route ile
    # aynı mantık — mevcut aynı-boyut filtresini değiştirir (Erkek→Kadın deterministik).
    cols = {c["name"]: c for mdl in schema.get("models", []) for c in mdl["columns"]}
    for dname in cube_meta.get("dimensions", []):
        col = cols.get(dname)
        if not col or not col.get("values"):
            continue
        matched = [str(v) for v in col["values"]
                   if (nv := _norm(str(v))) and _value_token_hit(q, nv)]
        if not matched:
            continue
        # ÇOK değer ("sadece beyaz ve siyah renk") → `in` filtresi; TEK değer → eq.
        flt = ({"dimension": dname, "operator": "eq", "value": matched[0]}
               if len(matched) == 1
               else {"dimension": dname, "operator": "in", "value": matched})
        if flt in cq.get("filters", []):
            already = True
        else:
            cq["filters"] = [
                f for f in cq.get("filters", []) if f.get("dimension") != dname
            ] + [flt]
            changed = True

    if is_all_time(q):
        # "Tümü" chip'i / "tüm zamanlar" yazımı: bilinçli tüm-veri seçimi (needs_period
        # de aynı sinyali okur). Var olan dönem filtresi varsa SİLİNİR (log regresyonu:
        # "bu yıl" → "Tümü" eski filtreyi taşımamalı); filtre zaten yoksa bu bir NO-OP'tur
        # ama yine de "already" sayılır — aksi halde deterministic_refine None döner ve
        # zincir LLM'e/dürüst-rete düşer, oysa istek zaten tam olarak mevcut durumu onaylıyor.
        had_period_filter = any(f.get("dimension") == time_dims[0] for f in cq.get("filters", []))
        if had_period_filter:
            cq["filters"] = [f for f in cq.get("filters", []) if f.get("dimension") != time_dims[0]]
            changed = True
        else:
            already = True
        # KALICI ONAY İMZASI: "Tümü" tek-tık bir seçimdir (needs_period docstring'i) —
        # sonraki HER düzenleme (ör. "vardiyalara göre de") teknik olarak YENİ bir cq
        # üretir ve dönem kapısı yeniden sorardı (kullanıcı ZATEN bilinçli seçim yaptı).
        # cube_query_to_sql BİLİNMEYEN üst-düzey alanları yutar (zararsız) — bu imza
        # sonraki turlarda ask.py'nin dönem-kapısını (period_confirmed) atlatır.
        cq["period_confirmed"] = True
    else:
        dfs = date_filters(q, time_dims[0])  # "son 3 ay" / "bu ay" / "temmuz ayı" (aralık)
        if dfs:
            cq["filters"] = [
                f for f in cq.get("filters", []) if f.get("dimension") != time_dims[0]
            ] + dfs
            changed = True

    # KAPSAM KAPISI (ADR-0008): mesajda tanınmayan içerik varsa kısa devre YOK — LLM
    # devralsın ("istanbul için haftanın günü" → istanbul'u anlamadık; no-op yutma yok).
    known: set[str] = set()
    known |= _syn_hit_words(q, cube_meta.get("synonyms"))
    if msyn:
        known.update(re.findall(r"[a-z]+", msyn))
    # TÜM ölçü sinonimleri tanınan sözlüktür (çok-ölçülü düzenlemeler: "fire miktarı
    # ve üretim miktarı" — yalnız seçilen em değil, geçen her ölçü kelimesi kapsanır)
    for syns in (cube_meta.get("measure_synonyms") or {}).values():
        known |= _syn_hit_words(q, syns)
    for syns in (cube_meta.get("dimension_synonyms") or {}).values():
        known |= _syn_hit_words(q, syns)
    for f in cq.get("filters", []):
        known.update(re.findall(r"[a-z]+", _norm(str(f.get("value", "")))))
    known |= _period_hit_words(q)
    known |= _misc_hit_words(q)
    known |= rm_verb_words  # ölçü-çıkarma fiilleri (kaldır/sil…) dolgu sayılır, kapsamı delmez
    if not _coverage_ok(q, known):
        return None

    if changed:
        return cq
    if already:
        return cq  # no-op: aynı raporu deterministik yeniden ver (LLM turu israf olurdu)
    return None


def needs_period(cube_query: dict, q: str) -> bool:
    """Dönem bilgisi yoksa SOR (ADR-0007 K3) — kırılımlı da olsa sessiz tüm-zaman
    toplama YOK (10 yıllık gerçek DB'de hem yanlış hem pahalı). Chip'te "Tümü" seçeneği
    bilinçli tüm-zamanı tek tıka indirir; takip mesajları (bağlam) yeniden sormaz."""
    if cube_query.get("timeDimensions"):
        return False  # trend zaten zaman ekseni taşıyor
    if any(f.get("dimension") == "tarih" for f in cube_query.get("filters", [])):
        return False
    if is_all_time(q):
        return False
    return not date_filters(q)


# Kırılım niyeti kelimeleri: soru bir kırılım/gruplama istiyor ama hiçbir boyut
# eşleşmediyse sessiz-yanlış cube dönmemek için kullanılır (haftanın-günü ifadeleri
# dahil — hafta_gunu boyutu olmayan cube'larda da doğru davranış: reddet → LLM).
_BREAKDOWN_HINTS = ("bazinda", "bazli", "gore", "kirilim",
                    "haftanin gun", "hafta gunu", "hangi gun", "gunlere", "gune gore")

# PANELLİ (facet) görünüm niyeti: "her X için ayrı ayrı [grafik]" — AÇIK kullanıcı
# isteği, viz.py'nin otomatik kararının ÜSTÜNE biner (ADR-0024, AskResponse.view_hint).
# X, cube'un dimension_synonyms'ından hangi boyuta denk geliyorsa ("kumaş türü" →
# kumas_cinsi) o boyut panel-eksenidir; fragment YALNIZ "her"–"ayrı ayrı" arası (soruda
# geçen DİĞER boyutlar — ör. "renklerine göre" — normal kırılım kalır, facet olmaz).
_FACET_RE = re.compile(r"\bher\s+(.+?)\s+(?:icin\s+)?ayri\s+ayri\b")


def detect_facet(q: str, cube_meta: dict) -> str | None:
    """"her kumaş türü için ayrı ayrı grafik" → "facet:kumas_cinsi". Fragmentte
    tanınan boyut yoksa None (görünüm kararı viz.py'nin varsayılanına kalır)."""
    m = _FACET_RE.search(q)
    if not m:
        return None
    dims = _match_dims(m.group(1), cube_meta)
    return f"facet:{dims[0]}" if dims else None

# DÖNEMSEL karşılaştırma niyeti (önceki dönem/LAG) — cube bunu ifade EDEMEZ; golden
# SQL'li LLM yolu (aggregate-then-LAG) devralmalı. DİKKAT: yalın "karşılaştır" burada
# DEĞİL — boyut karşılaştırması ("erkek ve kadını karşılaştır") cube'un ifade
# EDEBİLDİĞİ bir kırılımdır; yalnız dönem-referanslı ifadeler LLM'e gider.
_COMPARE_HINTS = ("onceki donem", "onceki aya", "onceki yila", "onceki haftaya",
                  "onceki ayla", "onceki yilla", "onceki ay ile", "onceki yil ile",
                  "gecen aya gore", "gecen yila gore", "gecen haftaya gore")
# NOT: YALIN "önceki ay / geçen ay" karşılaştırma DEĞİL, önceki takvim dönemidir
# (_prev_period_filters) — bu yüzden liste yalnız çekimli/edatlı biçimleri içerir.

# ── DÖNEMSEL KIYAS (YoY/MoM) — çok-yıl veriyle DETERMİNİSTİK (period-shift) ──────
# "geçen yıla göre" → cari dönem + geçen yıl aynı dönem iki seri + %değişim. Jenerik
# sorgu-modifier'ı (cube_query["compare"]); metrik DEĞİL — herhangi ölçüye uygulanır.
_YOY_HINTS = ("gecen yila gore", "onceki yila", "onceki yilla", "onceki yil ile",
              "gecen yil ile", "gecen seneye gore", "yil oncesine gore", "yoy")
_MOM_HINTS = ("gecen aya gore", "onceki aya", "onceki ayla", "onceki ay ile",
              "gecen ay ile", "mom")


def compare_mode(q: str) -> str | None:
    """Dönemsel kıyas niyeti: 'yoy' (geçen yıla göre) | 'mom' (geçen aya göre) | None."""
    if any(h in q for h in _YOY_HINTS):
        return "yoy"
    if any(h in q for h in _MOM_HINTS):
        return "mom"
    return None


def strip_compare(q: str) -> str:
    """Kıyas ifadesini söker (yıl/ay kelimesi granularity tetiklemesin) — route için."""
    for h in _YOY_HINTS + _MOM_HINTS:
        q = q.replace(h, " ")
    return re.sub(r"\s+", " ", q).strip()


def shift_period_back(filters: list[dict], mode: str, time_dim: str = "tarih") -> list[dict]:
    """tarih gte/lte değerlerini bir dönem geri kaydır (yoy=-1 yıl, mom=-1 ay). Kıyas serisi."""
    out = []
    for f in filters or []:
        if f.get("dimension") == time_dim and f.get("operator") in ("gte", "lte"):
            try:
                d = date.fromisoformat(str(f["value"])[:10])
            except ValueError:
                out.append(f); continue
            nd = date(d.year - 1, d.month, min(d.day, calendar.monthrange(d.year - 1, d.month)[1])) \
                if mode == "yoy" else _months_ago(d, 1)
            out.append({**f, "value": nd.isoformat()})
        else:
            out.append(f)
    return out


def _time_gran(q: str) -> str | None:
    # DİL ÇAKIŞMASI: "son 4 AYA göre" bir DÖNEM ifadesidir ("aya göre" kova değil);
    # göreli-dönem eşleşmesi sökülür ki içindeki ay/yıl kelimeleri kova tetikleyemesin.
    q = _REL_DATE.sub(" ", q)
    # "2. çeyrek / ikinci çeyrek" DÖNEMDİR — sökülür ki "çeyrek" kova tetiklemesin
    # ("çeyreklere göre / çeyreklik" gibi salt kova ifadeleri ordinal içermez, kalır).
    q = _QUARTER_RE.sub(" ", q)
    # "tüm zamanlar" = TÜM-ZAMAN toplamıdır, aylık kova DEĞİL — "zaman" ay-tetikleyicisine
    # yanlış takılıp istenmemiş aylık seri üretiyordu (panel K7; "tüm zamanlar bakiye" →
    # gran=month → semi bloğu None → sessiz kayıp). All-time sökülür; "zamana göre" (trend) kalır.
    q = re.sub(r"\btum\s+zaman\w*", " ", q)
    # Tam kova seti (motor destekli): day | week | month | quarter | year
    if "ceyrek" in q or "uc aylik" in q:
        return "quarter"
    if any(w in q for w in ["yillik", "yillara", "yila gore", "yil bazinda", "senelik"]):
        return "year"
    if any(w in q for w in ["haftalik", "haftalar", "haftaya"]):
        return "week"
    # DİL TUZAĞI: "haftanın günleri" hafta-günü BOYUTUdur (Pzt..Paz), günlük zaman
    # kovası değil — "günler" eşleşmesi yalnız hafta-günü ifadesi YOKKEN geçerli.
    if (not any(w in q for w in ("haftanin gun", "hafta gunu"))
            and any(w in q for w in ["gunluk", "gunler", "gunlere"])):
        return "day"
    if any(w in q for w in ["aylik", "aylar", "aya gore", "ay bazinda", "trend", "zaman"]):
        return "month"
    return None


def _direction(q: str):
    asc = any(w in q for w in ["en dusuk", "en az", "en kotu", "en verimsiz"])
    desc = any(w in q for w in ["en cok", "en yuksek", "en fazla", "en verimli", "en iyi", "en buyuk", "hangisi"])
    if asc:
        return "ASC"
    if desc:
        return "DESC"
    return None


def _top_n(q: str, cube_meta: dict | None = None) -> int | None:
    """"ilk 5" / "top 3" / "en çok ... 5 <varlık>" sayısını yakalar.

    Varlık kelimeleri HARD-CODED liste DEĞİL, cube metadata'sındaki boyut adları +
    sinonimlerinden türetilir (ADR-0005 generic ilkesi — "5 cari" boyahane listesinde
    olmadığı için kaçıyordu, Gitaş logu 2026-07-24). Meta verilmezse eski çekirdek
    liste yedek olarak kalır."""
    m = re.search(r"\b(?:ilk|top|en\s+\w+)\s+(\d+)", q)
    if m:
        return int(m.group(1))
    words: set[str] = {"makin", "musteri", "parti", "vardiya", "renk", "kumas", "personel"}
    for dname, syns in ((cube_meta or {}).get("dimension_synonyms") or {}).items():
        words.add(_norm(dname))
        words.update(_norm(s.removesuffix("!")) for s in syns or [])
    alt = "|".join(sorted((re.escape(w) for w in words if w), key=len, reverse=True))
    m = re.search(rf"\b(\d+)\s+(?:{alt})", q)
    return int(m.group(1)) if m else None


def _top_n_entity(q: str, cube_meta: dict) -> dict | None:
    """VARLIK top-N niyeti: "en çok satış yapılan 3 müşteri(ninkileri)" → önce ölçüte
    göre ilk N varlık seçilir, rapor onlara filtrelenir. Satır limiti (limit) zaman
    serili kırılımda seriyi ortadan keser — yanlış cevap sınıfı (log 2026-07-20).
    Sayı, dönem ifadesinden ("son 3 ay") izole aranır. measure None kalabilir —
    çağıran rapor ölçüsünü kullanır."""
    q2 = _REL_DATE.sub(" ", q)
    direction = _direction(q2)
    m = re.search(r"\b(\d+)\b", q2)
    if not direction or not m:
        return None
    dims = _match_dims(q2, cube_meta, None)
    if not dims:
        return None
    # SIRALAMA ÖLÇÜTÜ "en çok X" ifadesinden gelir (X=satılan→satis_miktari), TÜM sorgudan
    # DEĞİL — yoksa GÖSTERİLEN ölçü sıralamayı çalar (canlı 2026-07-25: "en çok SATILAN 10
    # ürünün ORTALAMA FİYATI" → fiyata göre sıralayıp yanlış ürünleri seçti). Yön ipucundan
    # (en çok/ilk…) sayıya kadarki pencerede ölçü ara; boşsa tüm sorgu (yedek).
    cue = _TOPN_CUE.search(q2)
    seg = q2[cue.end():m.start()] if (cue and cue.start() < m.start()) else q2
    crit = _match_measure(seg, cube_meta)[0] or _match_measure(q2, cube_meta)[0]
    return {
        "dimension": dims[0],
        "measure": crit,
        "direction": "asc" if direction == "ASC" else "desc",
        "n": int(m.group(1)),
    }


def cube_only_match(q: str, schema: dict) -> dict | None:
    """Cube-düzeyi sinonim TEK bir cube'a işaret ediyor ama hiçbir ÖLÇÜ sinonimi
    geçmiyor VE cube'un `default_measure`'ı yoksa o cube_meta'yı döner — route()'un
    NEDEN None döndüğünü ayırt eder (çapraz-konu/kısmi-anlama DEĞİL: "hangi ölçü?"
    chip'i gerekir). Çok-ölçülü, eşit-geçerli cube'larda (ör. sürdürülebilirlik: su/
    enerji/gaz/kimyasal yoğunluğu) sessizce bir ölçü varsaymak yanıltıcı olur
    (ADR-0008) — kullanıcı seçsin."""
    cube_meta = _match_cube(q, schema)
    if cube_meta is None or _match_measure(q, cube_meta)[0] or cube_meta.get("default_measure"):
        return None
    # ÇAPRAZ-KONU ÖNCELİĞİ (Faz D3, ölçülmüş vaka). Soruda bu cube'un tanımadığı ama BAŞKA
    # bir cube'un GERÇEK terimi olan bir kelime varsa *"hangi ölçüyü istiyorsun?"* YANLIŞ
    # sorudur: kullanıcı ölçüyü zaten SÖYLEDİ, yalnız o ölçü burada yok.
    #
    # Ölçüldü: *"personel bazlı verimlilikleri karşılaştır"* → cube `parti` (personel
    # kırılımını YALNIZ o taşıyor), ama `verimlilik` bir `oee` ölçüsüdür. Bu chip
    # kullanıcıya parti'nin ölçülerini sıralıyordu — hiçbiri verimlilik değil. Doğru cevap
    # aşağıdaki çapraz-konu netleştirmesidir ("verimlilik başka bir konu gibi görünüyor").
    unknown, _hits = partial_unknowns(q, schema)
    if unknown:
        for c in schema.get("cubes") or []:
            if c.get("name") == cube_meta.get("name"):
                continue
            vocab = _catalog_vocabulary(schema, only_cube=c)
            if any(any(_covers(t, w) for t in vocab) for w in unknown):
                return None
    return cube_meta


def olcu_netlestirme(adaylar: list[tuple[dict, str]],
                     schema: dict | None = None) -> list[dict]:
    """Ölçü belirsizliği için netleştirme seçenekleri — `[{label, query}]`.

    ## Ölçülen kusur (Faz 2a, 2 Ağustos 2026)

    `ask.py` chip'leri yalnız ölçünün GÖRÜNEN ADIYLA kuruyordu. İki cube aynı adı taşıdığında
    (`cari.bakiye` ve `mizan.bakiye` → ikisi de *"bakiye"*) liste tekilleşip **1'e düşüyor**,
    `len(...) >= 2` kapısı chip'i **sessizce atlıyor** ve soru **Discovery'ye** düşüyordu —
    ham SQL, `cube_query=None`, yani §1'in tarif ettiği uçurum, üstelik netleştirme yolundan.

    Ölçüldü: **54 belirsiz sinonimin 33'ü** (%61) bu tuzağa düşüyordu — `bakiye · borç ·
    alacak · fire · ilk seferde tamam · doğalgaz` aileleri. Üçü de sessizdi: belirsizlik
    tespit ediliyor, chip atlanıyor, kullanıcı ham bir SQL cevabı alıyor.

    ## Kural

    Ayırt edici bilgi **ölçü adı değil CUBE'un kendisi**. Etiket çakıştığında cube ile
    nitelenir: *"bakiye (cari)"* / *"bakiye (mizan)"*. Çakışmayan etiket **dokunulmadan**
    kalır — gereksiz gürültü üretilmez.

    `query` de nitelenir, yoksa chip tıklanınca AYNI belirsizliğe geri döner: kullanıcıyı
    aynı duvara ikinci kez çarptıran bir chip, chip olmamasından kötüdür (aynı disiplin
    `ay_netlestirme`'de de uygulandı, Faz -0.5a).
    """
    ham: list[tuple[dict, str, str]] = []
    for c, m in adaylar:
        etiket = (c.get("measure_synonyms_display") or {}).get(m) or m
        ham.append((c, m, str(etiket)))
    sayac: dict[str, int] = {}
    for _, _, e in ham:
        sayac[e] = sayac.get(e, 0) + 1

    out: list[dict] = []
    for c, _m, etiket in ham:
        cube_ad = str(c.get("display") or c.get("name") or "").strip()
        # ETİKET: yalnız çakışmada cube ile nitelenir — çakışmayan etikete cube adı
        # eklemek gereksiz gürültüdür.
        label = f"{etiket} ({cube_ad})" if (sayac[etiket] > 1 and cube_ad) else etiket
        # SORGU: HER İKİ dalda da doğrulanır. Çakışma olmasa bile ham etiket tek başına
        # çözülmeyebiliyor (ölçüldü: "dE", "sapma yüzdesi" → R1/R10) ve tıklanınca
        # çalışmayan bir chip, çakışmadan bağımsız olarak kötüdür.
        secenek = {"label": label, "query": _calisan_sorgu(c, etiket, schema)}
        if not any(o["label"] == secenek["label"] for o in out):
            out.append(secenek)
    return out


def _calisan_sorgu(cube: dict, etiket: str, schema: dict | None) -> str:
    """Chip'in `query`'si: `route()` ile DOĞRULANMIŞ bir "cube + ölçü" ifadesi.

    ## Neden `display` yetmiyor (ölçüldü)

    İlk sürüm `f"{cube_display} {etiket}"` üretiyordu ve **39 chip'in sorgusu
    çözülmüyordu**. İki sebep:
      * `display` bir İNSAN ETİKETİDİR, sorgu kelimesi değil — `mizan`'ınki
        *"mizan (hesap bakiyeleri)"*, üretilen sorgu *"mizan (hesap bakiyeleri) borç"*
        gibi anlamsız bir metin oluyordu;
      * temiz görünen etiketler bile (*"cari hesap"*) kapsam kapısına takılıyordu (R10).

    Cube'un **sinonimleri** ise tanım gereği `_match_cube`'un TANIDIĞI kelimelerdir.
    Sırayla denenir ve **`route()` ile doğrulanır** — tıklanınca çalışmayan bir chip,
    kullanıcıyı aynı duvara ikinci kez çarptırır ve chip olmamasından kötüdür (aynı kural
    `ay_netlestirme`'de de uygulandı, Faz -0.5a).

    Hiçbiri çalışmazsa ham birleşim döner: chip yine de bir İPUCU taşır ve `label`
    kullanıcıya hangi cube'u kastettiğini zaten söyler.
    """
    if schema is None:
        return etiket
    hedef = cube.get("name")

    def _cozuluyor(aday: str) -> bool:
        hit = route(aday, schema)
        return bool(hit) and hit.get("cube_query", {}).get("cube") == hedef

    # 1) ÇIPLAK etiket zaten çalışıyorsa ona dokunma — en kısa, en doğal ifade.
    if _cozuluyor(etiket):
        return etiket
    # 2) Cube SİNONİMLERİYLE nitele. Sinonimler tanım gereği `_match_cube`'un TANIDIĞI
    #    kelimelerdir; `display` ise bir insan etiketidir ve sorgu olarak çalışmaz
    #    (ölçüldü: "mizan (hesap bakiyeleri) borç" gibi anlamsız sorgular üretiyordu).
    #    Kısa ad önce: en az gürültülü, kapsam kapısına en az takılan.
    adlar = [str(s).removesuffix("!") for s in (cube.get("synonyms") or [])]
    adlar.append(str(hedef or ""))
    for ad in sorted({a.strip() for a in adlar if a.strip()}, key=len):
        aday = f"{ad} {etiket}"
        if _cozuluyor(aday):
            return aday
    # 3) Hiçbiri çalışmıyor → ham etiket. Chip yine bir İPUCU taşır ve `label` kullanıcıya
    #    hangi cube'u kastettiğini zaten söyler; uydurma bir sorgu üretmekten iyidir.
    return etiket


def measure_cube_candidates(q: str, schema: dict) -> list[tuple[dict, str]]:
    """Bir ÖLÇÜ sinonimi geçen ama cube-düzeyi sinonim geçMEyen cube'lar
    (ADR-0018 §2-2 + belirsizlikte-sor): "bu yıl satış" → hem ticaret (satış tutarı)
    hem mal (satış miktarı) → [(ticaret, satis_tutari), (mal, satis_miktari)].
    Tek aday → route zaten seçti; ≥2 → ask.py "hangisi?" chip'i sorar (LLM tahmin
    etmez). Cube-düzeyi sinonim geçen cube'lar hariç (onlar route'un işi)."""
    out: list[tuple[dict, str]] = []
    for c in schema.get("cubes", []):
        if _any_hit(q, c.get("synonyms")):
            continue  # cube-düzeyi eşleşme → route halleder
        m, _ = _match_measure(q, c)
        if m:
            out.append((c, m))
    return out


# Bir adayı ayırt etmek için denenecek EN FAZLA sinonim sayısı. Her deneme tam bir
# `route()` koşusudur (LLM'siz ama bedava değil); 8 denemede ayırt edilemeyen bir aday
# pratikte ayırt edilemez.
_TIE_MAX_DENEME = 8


def cube_tie_candidates(question: str, schema: dict) -> list[tuple[dict, str, dict]]:
    """CUBE-DÜZEYİ BERABERLİK (Faz 3.1): iki cube AYNI kelimeleri AYNI güçle sahiplendi.

    `(cube_meta, netleştirici_soru, cube_query)` listesi; beraberlik yoksa **boş liste**.

    Neden ayrı bir kırıcı değil de SORU: ölçülen vaka (demo-boyahane, 55 soru) *"makine
    bazında arıza duruşu"* — `bakim.toplam_durus_dakika` ile `oee.plansiz_durus_dakika`
    İKİSİ DE `"arıza duruşu"` sinonimini taşıyor ve ikisi de MEŞRU: biri bakım
    perspektifinden arıza süresi, öteki OEE perspektifinden plansız duruş. Metinde ayrım
    YOK. Burada bir tie-break kuralı icat etmek (alfabetik, manifest sırası, "bakım daha
    spesifik") denetlenemez bir tercih gömmek olurdu — MIMARI.md §5'in açıkça yasakladığı
    şey. Kullanıcı bilir; sormak ücretsiz.

    Neden LLM'e de bırakılmıyor: Intent-JSON bu soruda TAHMİN eder ve tahminini `cube+llm`
    rozetiyle sunar. Yanlış tahmin, makul görünen yanlış cevaptır — merdivenin en pahalı
    hata sınıfı (MIMARI.md §4 madde 6: *belirsizlikte SORAR, tahmin etmez*). Bu yüzden
    chip Intent-JSON'dan ÖNCE gelir.

    **YALNIZ kanıt EŞİTKEN** çalışır. Kanıt = (en uzun cube-sinonimi, en uzun ölçü-sinonimi)
    — `_match_cube`'un kendi kırıcılarının okuduğu iki ölçü. Fark varsa (ölçüldü: 33 soru,
    `parti` vs `surdurulebilirlik`, fark 1) bu bir beraberlik değil ZAYIF bir sinyaldir ve
    orta-güven bandına aittir: dokunulmaz, Intent-JSON devralır.

    Netleştirici soru **ÜRETİLİR VE DOĞRULANIR, VARSAYILMAZ.** Her aday için önce REFERANS
    hesaplanır: `route()`, kataloğu YALNIZ o cube'a daraltılmış bir şemayla koşulur (repo'da
    zaten kullanılan alt-şema deseni, bkz. `route`'un boyut-uyumu yeniden yönlendirmesi) —
    yani "bu cube tek aday olsaydı kullanıcı NE alırdı". Sonra aday metinler denenir ve
    yalnız **cube_query'si referansla BİREBİR AYNI** çıkan metin chip olur.

    Doğrulamanın bu kadar sıkı olması teorik değil: ilk sürüm yalnız `cube`'un doğru
    çözüldüğüne bakıyordu ve gerçek koşuda İKİ hata üretti — (1) `oee` için ayırt edici
    kelime `"kullanılabilirlik"` seçildi, ama o kelime AYNI ZAMANDA bir ölçü sinonimi ve
    eşleşen ifadeden UZUN olduğu için ölçüyü `plansiz_durus_dakika`dan
    `ort_kullanilabilirlik`e kaydırdı: chip *"OEE: plansız duruş"* yazıp BAŞKA bir sayı
    getirecekti. (2) `bakim` için `"makine arızası"` seçildi ve içindeki `"arıza"` kelimesi
    `ariza_tipi` BOYUTUNU tetikleyip kırılımı `makine × arıza_tipi`ye böldü. İkisi de
    sessiz-yanlıştır; ikisini de tam cube_query eşitliği yakalar.

    İki üretim stratejisi denenir (ikisi de mekanik, kelimeye özel kural YOK):
      1. **İkame** — eşleşen ölçü ifadesi, adayın KENDİ ölçüsünün başka bir sinonimiyle
         değiştirilir (`"arıza duruşu"` → `"plansız duruş"`). Sorunun geri kalanı korunur.
      2. **Önek** — rakiplerde bulunmayan bir cube sinonimi başa eklenir. `_longest_syn_hit`
         MAKSİMUM aldığı için bu ancak kelime rakibin en iyisinden ≥4 harf uzunsa işe yarar;
         yaramazsa doğrulama zaten eler.

    Adaylardan BİRİ bile ifade edilemiyorsa **hiçbiri yayımlanmaz**: eksik bir chip listesi
    bir yorumu sessizce eler — ADR-0008'in tam olarak yasakladığı davranış. O durumda
    merdiven olağan şekilde Intent-JSON'a düşer.
    """
    q = _norm(question)
    if _match_cube(q, schema) is not None:
        return []  # beraberlik kırıldı ya da hiç yok → route zaten cevaplıyor
    hits = [c for c in schema.get("cubes", []) if _any_hit(q, c.get("synonyms"))]
    if len(hits) < 2:
        return []

    def _kanit(c: dict) -> tuple[int, int]:
        return (_longest_syn_hit(q, c), len(_match_measure(q, c)[1] or ""))

    en_iyi = max(_kanit(c) for c in hits)
    esitler = [c for c in hits if _kanit(c) == en_iyi]
    if len(esitler) < 2:
        return []  # kanıt eşit değil → orta güven → Intent-JSON'ın işi

    modeller = schema.get("models", [])
    out: list[tuple[dict, str, dict]] = []
    for c in esitler:
        # REFERANS: bu cube tek aday olsaydı üretilecek cube_query.
        try:
            referans = route(question, {"models": modeller, "cubes": [c]})
        except Exception:  # noqa: BLE001 — netleştirme best-effort'tur, cevabı bozmaz
            referans = None
        if not referans:
            break  # aday tek başına bile cevaplanamıyor → chip listesi eksik kalır
        hedef_cq = referans.get("cube_query")

        adaylar: list[str] = []
        # 1) İKAME: eşleşen ölçü ifadesini adayın kendi ölçüsünün başka bir sinonimiyle değiştir.
        olcu, eslesen = _match_measure(q, c)
        if olcu and eslesen:
            digerleri = sorted(
                {s.removesuffix("!")
                 for s in (c.get("measure_synonyms") or {}).get(olcu, [])} - {eslesen},
                key=len, reverse=True)
            adaylar += [_norm(question).replace(eslesen, alt) for alt in digerleri]
        # 2) ÖNEK: rakiplerde bulunmayan cube sinonimi.
        rakip = {s.removesuffix("!")
                 for o in hits if o is not c
                 for s in (o.get("synonyms") or [])}
        adaylar += [f"{kelime} {question}" for kelime in sorted(
            {s.removesuffix("!") for s in (c.get("synonyms") or [])} - rakip,
            key=len, reverse=True)]

        for aday_soru in adaylar[:_TIE_MAX_DENEME]:
            try:
                r = route(aday_soru, schema)
            except Exception:  # noqa: BLE001
                continue
            if r and r.get("cube_query") == hedef_cq:
                out.append((c, aday_soru, r))
                break
    return out if len(out) == len(esitler) else []


def resolve_cube_name(name: str | None, schema: dict) -> str | None:
    """Eski cube adını katalog adına çözer (yeniden adlandırma göçü): istemcide
    kalan rapor "fire" derken katalog "parti" olabilir — ad TEK bir cube'un sinonimi
    ise ona bağlanır; böylece takip mesajı sahte "bağlam kopması" yaşamaz."""
    if not name or _cube_meta(schema, name) is not None:
        return name
    n = _norm(str(name))
    hits = [
        c
        for c in schema.get("cubes", [])
        if n in [s.removesuffix("!") for s in (c.get("synonyms") or [])]
    ]
    return hits[0]["name"] if len(hits) == 1 else name


# --- KAPSAM KAPISI (ADR-0008 K1): "anlamadığını bil" ---------------------------
# Deterministik yol yalnız mesajın TAMAMI tanınan parçalardan oluşuyorsa kısa devre
# yapar; tek bir tanınmayan kelime bile varsa → LLM. Sessiz yutma sınıfını kapatır.

# Dolgu/istek kelimeleri — anlam taşımaz, kapsam dışı sayılmaz.
_STOP_STEMS = (
    "icin", "gore", "bazinda", "bazli", "olarak", "rapor", "goster", "getir",
    "ver", "yap", "peki", "simdi", "lutfen", "acaba", "toplam", "ortalama",
    "sadece", "yalniz", "calisan", "ile", "daha", "nedir", "nasil", "kadar",
    "ayir", "ayri", "grafi", "tablo", "cizgi", "sutun", "panel", "chart",
    # "pasta" (pasta grafik = pie chart) Faz 4.4'e kadar eksikti (31 Temmuz 2026):
    # `_viz_hint()`/`_VIZ_MAP` (app/routers/ask.py) bu kelimeyi ZATEN tanıyordu ama
    # kelime burada STOP değildi → typo_correct katalogda bulamayınca fuzzy-eşleşme
    # denedi ("pasta"→"pass" gibi alakasız bir öneri) — grafik-tipi isteği bu yüzden
    # cevap yerine sahte bir "şunu mu demek istedin?" netleştirmesine düşüyordu.
    "pasta",
    "gorsel", "heatmap", "isi", "harita", "goruntule", "olsun", "istiyorum",
    "turl", "turu", "cesit", "cins", "kirilim", "kova", "ekle", "cikar",  # kökler tüm çekimleri kapsar
    "degil", "yerine", "yapilan", "yapan", "olan", "sahip",
    # TR fiil çekimleri + hedging (panel bulgusu Opus K8/Sonnet K5,K9): "sattık"
    # altdizi "satis"i eşlemez → bunlar dolgu sayılıp kapsam kapısını delmemeli.
    # Ölçü/boyut kelimeleri KALIR; yalnız içi-boş fiil/soru kalıpları eklenir.
    "yaptik", "yaptiniz", "ettik", "ederiz", "tuttu", "oldu", "geldi", "gecti",
    "galiba", "herhalde", "sanki", "niye", "neden", "getirip", "gosterip",
    "kadardi", "istiyoruz", "isterim", "gerceklestir", "bakalim",
    # gündelik hitap/dolgu ("birader bana ... getir" — log 2026-07-20)
    "birader", "kanka", "hocam", "dostum", "bana", "bakalim", "hadi",
    "iste", "senden", "sana", "sunu", "simdi",  # sohbet dolgusu ("şimdi şunu isteyeceğim senden")
    # liste/döküm niyeti: cube'a sığmaz ama TANINAN bir niyettir (serbest-SQL yolu)
    "listele", "liste", "dokum", "detay",
    # niyet/nicelik kelimeleri: typo adayı sanılmamalı (değer indeksi gürültüsü)
    "karsilastir", "kiyasla", "tum", "her", "miktar", "tek", "yan yana", "yanyana", "donem", "filtre", "kalsin",
    # jenerik KOMUT fiili (canlı bulgu, 31 Temmuz 2026): "hesapla" gerçek kullanımda
    # katalogdaki "hesap" (mizan/cari boyutu, muhasebe hesap kodu) ile 0.83 benzerlik
    # taşıyor — typo_correct bunu "hesap"a düzeltmeye ÇALIŞIYORDU (yanlış-pozitif: iki
    # kelime aynı TR kökten [hesap+la] ama TAMAMEN farklı anlam, typo DEĞİL). "hesapla"
    # (calculate) diğer jenerik fiiller (goster/getir/ver) gibi anlam taşımaz → dolgu.
    "hesapla",
)

# TAM-KELİME dolgu kökleri (`!` = sinonimlerdeki AYNI disiplin, bkz. `_syn_hit`).
# Bunlar ÖNEK olarak eşleşirse gerçek iş kelimelerini yutuyorlardı — hepsi doğrulandı:
#     ver   → veresiye (vadeli satış)      tek  → tekstil
#     turu  → turuncu (renk değeri)        sana → sanayi
#     getir → getiri (finansal getiri)     isi  → ısıtma/ısı
# Yutulan kelime "tanınmış dolgu" sayılınca kapsam kapısı deliniyor ve soru, o kelimeyi
# HİÇ dikkate almayan bir cube cevabına dönüşüyordu ("veresiye satışlar" → tüm satışlar).
#
# DİSİPLİN: buraya YALNIZ kanıtı olan kök girer. İlk denemede "cins" de eklenmişti ve
# `test_cins_cekimleri_tam_soru` onu anında düşürdü — testin kendi docstring'i
# *"kök ('cins') tüm çekimleri kapsar"* diyor ("kumaş cinsleri..."). Tahminle liste
# şişirmek, düzeltmeye çalıştığımız sessiz-yanlışın aynısını ters yönde üretir.
_STOP_EXACT = frozenset({"ver", "tek", "turu", "sana", "getir", "isi"})


def _is_stop_word(w: str) -> bool:
    """Kelime bir dolgu köküyle başlıyor mu? `_STOP_EXACT` kökleri ÖNEK eşleşmez.

    ÖNEK semantiği BİLEREK korundu. `_STOP_STEMS` girdileri sözcük KÖKÜ değil, ELLE
    KISALTILMIŞ eşleşme köküdür ("grafi" → grafik/grafiği/grafikte; "turl" → türler/
    türlerine). Bunlara `_covers()`'ın biçimbirim kuralını uygulamak YANLIŞTIR ve nitekim
    denendiğinde kırdı: "grafi"+"k" geçerli bir Türkçe ek zinciri değildir, dolayısıyla
    "grafik" kelimesi dolgu sayılmayı bıraktı ve grafik isteyen her soru kapsam kapısına
    takıldı (`test_grafik_tipi_ipucu_jenerik` ve 3 test daha).

    Kazayla yutulan gerçek iş kelimeleri (veresiye/tekstil/turuncu/sanayi/getiri) bu yüzden
    biçimbirimle değil, `_STOP_EXACT` TAM-KELİME listesiyle çözülür — kanıta dayalı ve
    denetlenebilir. İki mekanizma AYRI tutulur çünkü iki farklı sorunu çözerler.
    """
    if w in _STOP_EXACT:
        return True
    return any(w.startswith(s) for s in _STOP_STEMS if s not in _STOP_EXACT)


def _syn_hit_words(q: str, syns) -> set[str]:
    """Eşleşen sinonimlerin KELİMELERİNİ döndürür (kapsam hesabı için)."""
    words: set[str] = set()
    for s in syns or []:
        plain = s.removesuffix("!")
        if _syn_hit(q, s):
            words.update(re.findall(r"[a-z]+", plain))
    return words


def _period_hit_words(q: str) -> set[str]:
    """Tanınan dönem ifadelerinin kelimeleri (son 3 ay / bu ay / temmuz ayı / aralık…)."""
    words: set[str] = set()
    for rx in (_RANGE_RE, _REL_DATE, _OPEN_START_RE, _OPEN_END_RE, _PREV_RE, _QUARTER_RE):
        m = rx.search(q)
        if m:
            words.update(re.findall(r"[a-z]+", m.group(0)))
    if re.search(r"\bdun\b", q):
        words.add("dun")
    for phrase in ("bugun", "bu hafta", "bu ay", "bu yil", "bu sene",
                   "tum zamanlar", "tumu", "hepsi", "tum veriler"):
        # son kelime ÇEKİMLİ olabilir ("bu AYKİ satışlar", "bu seneki") → \w* toleransı
        m = re.search(r"\b" + phrase.replace(" ", r"\s+") + r"\w*", q)
        if m:
            words.update(re.findall(r"[a-z]+", m.group(0)))
    # re.search DEĞİL re.finditer: "mayıs ayı cirosunu NİSAN ayına göre karşılaştır" gibi
    # çok-aylı (kıyas) sorularda yalnız İLK ay yakalanırsa ikinci ay adı SESSİZCE "unknown"
    # kalır ve typo_correct() onu alakasız bir kategorik değere ("nisan"→"Lisans" gibi)
    # yanlışlıkla önerir (Madde 1, 1 Ağustos 2026 canlı bulgu).
    for m in re.finditer(rf"\b({_MONTH_ALT})\b(\s+ayi\w*)?", q):
        words.update(re.findall(r"[a-z]+", m.group(0)))
    return words


def _misc_hit_words(q: str) -> set[str]:
    """Gran/yön/limit ifadelerinin kelimeleri."""
    words: set[str] = set()
    for w in ("haftalik", "haftalar", "haftaya", "gunluk", "gunler", "gunlere",
              "aylik", "aylar", "aya gore", "ay bazinda", "trend", "zaman",
              "ceyrek", "uc aylik", "yillik", "yillara", "yila gore", "yil bazinda", "senelik",
              "en dusuk", "en az", "en kotu", "en verimsiz", "en cok", "en yuksek",
              "en fazla", "en verimli", "en iyi", "en buyuk", "hangisi", "her gun"):
        if w in q:
            words.update(w.split())
    m = re.search(r"\b(?:ilk|top|en\s+\w+)\s+(\d+)", q)
    if m:
        words.update(re.findall(r"[a-z]+", m.group(0)))
    return words


# OLUMSUZLUK / YOKSUNLUK EKLERİ — bunlar ÇEKİM DEĞİL, NİYET OPERATÖRÜDÜR.
# `_norm` Türkçe harfleri düzleştirir (ı→i, ü→u, ş→s...), bu yüzden ASCII biçimleri yeter.
# "firesiz" = fire YOK demektir; "fire" ile kapsanmış saymak, sorunun anlamını TERSİNE
# çevirir. Faz 3.3'te bu ekler `neq`/`not_in` üretimine bağlanacak; o zamana kadar
# kapsanmamış sayılmaları (→ dürüst ret / LLM) tek doğru davranıştır.
_NEGATION_SUFFIXES = ("siz", "suz", "sizl", "suzl",          # -sIz (yoksunluk)
                      "mayan", "meyen", "miyen", "muyan",     # -mAyAn (olumsuz sıfat-fiil)
                      "madan", "meden", "madi", "medi",       # -mAdAn / -mAdI
                      "mamis", "memis", "maz", "mez")         # -mAmIş / -mAz


# Türkçe çekim/türetme eki ATOMLARI (normalize/ASCII — `_norm` ı→i, ü→u, ş→s yapar).
# Sıra UZUNDAN KISAYA: regex alternasyonu soldan dener, geri-izleme zaten çalışır ama
# uzun atomların önce denenmesi hem hızlı hem okunaklı bir ayrıştırma verir.
# Tek-harfli atomlar YALNIZ ünlüler ve tampon ünsüzler (y/n/s/m) — rastgele ünsüz (t, g,
# l...) atom OLMADIĞI için "iyeti"/"go"/"stil" gibi ek-olmayan kuyruklar ayrışamaz.
_SUFFIX_ATOMS = (
    "leri", "lari", "imiz", "iniz", "umuz", "unuz", "deki", "daki", "ligi", "lugu",
    "nin", "nun", "den", "dan", "ten", "tan", "yle", "yla", "dir", "dur", "tir", "tur",
    "lik", "luk", "ler", "lar", "mis", "mus",
    "de", "da", "te", "ta", "le", "la", "ki", "ni", "nu", "ne", "na", "si", "su",
    "se", "sa", "in", "un", "im", "um", "ye", "ya", "yi", "yu", "li", "lu",
    "ce", "ca", "ci", "cu",
    "ir", "ur", "er", "ar",          # geniş zaman: "göster"+"ir"
    "i", "u", "e", "a", "y", "n", "s", "m",
)
# DİKKAT — buraya atom eklerken: "ti"/"tu"/"di"/"du" DENENDİ ve GERİ ALINDI. Onlarla
# "mal"+"iyeti" = i+ye+ti diye ayrışıp KAPSANIYORDU (maliyet ≠ mal). `-dir/-dur/-tir/-tur`
# zaten TAM atom olarak listede; parçalarını ayrıca atom yapmak deliği geri açar.
_SUFFIX_CHAIN_RE = re.compile(r"(?:" + "|".join(_SUFFIX_ATOMS) + r")+")


def _ek_gecerli(kalan: str) -> bool:
    """Bir kökün arkasında kalan `kalan` dizisi GEÇERLİ bir çekim mi? (Faz D3'te tekleştirildi.)

    İki tüketici vardı ve **aynı soruyu farklı cevaplıyorlardı**: `_covers` (kapsam kapısı)
    bu üç kuralı uyguluyordu, `_syn_hit` (boyut/ölçü/cube eşleşmesi) hiçbirini — düz altdizi
    bakıyordu. Kural artık tek yerde:

      1. Boş kalan = kökün kendisi.
      2. Olumsuzluk eki ÇEKİM SAYILMAZ — anlamı tersine çevirir (`fire` ≠ `firesiz`).
      3. Kalan, ek atomlarının bir zinciri olmalı; kazayla denk gelen devamlar elenir
         (`mal`+`iyeti`, `kar`+`go`).
    """
    if not kalan:
        return True
    if any(kalan.startswith(n) for n in _NEGATION_SUFFIXES):
        return False
    return bool(_SUFFIX_CHAIN_RE.fullmatch(kalan))


# --- DIŞLAMA (Faz 3.3): "beyaz HARİÇ", "iptaller DIŞINDA" -----------------------
# Türkçede dışlama bir SON-ÇEKİM EDATIYLA kurulur ve edat tümlecini İZLER. Kural bu yüzden
# konumsaldır, kelime listesi değil: edatın eşleşen DEĞERDEN SONRA gelmesi aranır. Böylece
# "beyaz hariç renk bazında rework" ile "hariç tutulmayan..." gibi ifadeler karışmaz.
#
# "disi" (dışı) BİLEREK YOK: `_norm` sonrası "dişi" ile ÇAKIŞIR ve cinsiyet/hayvan
# bağlamında yanlış dışlama üretirdi. "disinda"/"disindaki" tek başına yeterli.
_EXCLUDE_MARKERS = ("haric", "disinda", "disindaki", "disindakiler",
                    "olmayan", "olmayanlar", "degil", "disi birakarak")
# Değerler arası bağlaçlar: "beyaz VE siyah hariç" ikisini birden dışlar.
_CONJ = ("ve", "ile", "veya", "ya da", "yada", ",", "-")

# --- ÖNEK / İÇERME (Faz 3.3) ----------------------------------------------------
# "M10 İLE BAŞLAYAN müşteriler", "ram İÇEREN makineler".
#
# Motorun `starts_with`/`contains` operatörleri BÜYÜK/KÜÇÜK HARF DUYARLIDIR (ölçüldü:
# `starts_with('B')` → ['Beyaz'], `starts_with('b')` → []). Dima'nın NL katmanı ise
# `_norm` ile küçültüp aksanları düzleştirir. İkisini doğrudan bağlamak, kullanıcı
# "beyaz" yazdığında GÜVENLE BOŞ sonuç döndürmek demekti — `None`dan kötü.
#
# Bu yüzden önek/içerme DEĞER İNDEKSİNDE çözülür ve mevcut `in` operatörüne indirgenir:
# eşleşen gerçek değerler (özgün yazımlarıyla) bulunur, filtre onlarla kurulur. Hangi
# boyut olduğu da buradan gelir — boyut KELİMESİNE hiç bakılmaz, dolayısıyla "hangi
# boyutu kastetti" tahmini yapılmaz. Birden çok boyut eşleşirse belirsizdir → dürüst red.
_PREFIX_RE = re.compile(r"(\S+)\s+ile\s+baslayan\b")
_CONTAINS_RE = re.compile(r"(\S+)\s+iceren\b")


def _deger_dislaniyor(q: str, deger_norm: str, kardesler: list[str]) -> bool:
    """Bu değer bir DIŞLAMA edatının kapsamında mı? ("beyaz hariç", "iptaller dışında")

    Türkçe son-çekim edatı tümlecini İZLER, o yüzden kural konumsaldır: eşleşen değerden
    sonra sırayla (değerin kendi çekim eki | boşluk | bağlaç | AYNI boyutun başka eşleşen
    değeri) yutulur ve ardından bir dışlama edatı gelmelidir. Böylece "beyaz VE siyah
    hariç" ikisini birden dışlar, ama "beyaz bazında rework, siyah hariç" ifadesinde
    "beyaz" dışlanmaz — arada bağlaç olmayan içerik vardır.

    Ek zinciri için `_SUFFIX_CHAIN_RE` YENİDEN KULLANILIR: dışlamanın kendi ek listesini
    doğurması, aynı dilbilgisi kuralının iki yerde ayrışması demek olurdu (MIMARI.md §5).
    """
    def _ek_yut(s: str) -> str:
        """Baştaki çekim eki zincirini bir kez yutar (`beyazın` → `ın`)."""
        m = _SUFFIX_CHAIN_RE.match(s)
        return s[m.end():] if m else s

    for m in re.finditer(re.escape(deger_norm), q):
        kalan = _ek_yut(q[m.end():])
        if kalan[:1].isalpha():
            continue  # kelime ortasında eşleşmiş (ör. "beyaz" ⊂ "beyazlatma") → değer değil
        ilerledi = True
        while ilerledi:
            ilerledi = False
            kalan = kalan.lstrip(" ,-")
            for parca in (*_CONJ, *kardesler):
                if not parca or not kalan.startswith(parca):
                    continue
                aday = _ek_yut(kalan[len(parca):])
                if aday[:1].isalpha():
                    continue  # bağlaç/kardeş kelimenin ORTASINDA kesildi → geçersiz
                kalan, ilerledi = aday, True
                break
        if any(kalan.lstrip().startswith(w) for w in _EXCLUDE_MARKERS):
            return True
    return False


def _covers(known: str, word: str) -> bool:
    """`known` kelimesi `word`'ü kapsıyor mu? (Türkçe EKLEMELİ dil varsayımı.)

    ÖNCEDEN `known in word` idi — HERHANGİ BİR KONUMDA alt-dizi. Kanıtlanmış sessiz-yanlışlar
    (hepsi canlı `route()` üzerinde çalıştırılarak doğrulandı, 2 Ağustos 2026):

        kar ⊂ ankara · mal ⊂ imalat · mal ⊂ maliyeti · son ⊂ personel · gun ⊂ uygun
        fire ⊂ firesiz · sapma ⊂ sapmasiz · reddedil ⊂ reddedilmeyen

    Sonucu yalnız gürültü değildi: `"firesiz partilerin cirosu"` kapsam kapısından GEÇİP
    **fire toplamını** döndürüyordu — sorulanın TAM TERSİ metrik, üstelik `source="cube"`
    rozeti ve Query Contract'ıyla. Bu, sistemin üretebileceği en kötü hata sınıfıdır.

    Üç kurallı düzeltme:
      1. EK BAŞA DEĞİL SONA gelir → `word.startswith(known)`. (ankara/imalat/personel/uygun
         bu tek kuralla düşer.)
      2. Ek OLUMSUZLUK eki olamaz → `_NEGATION_SUFFIXES`. (firesiz/sapmasiz/reddedilmeyen.)
      3. Kalan kısım GEÇERLİ BİR EK ZİNCİRİ olmalı (`_SUFFIX_CHAIN_RE`). Kazayla denk
         gelen önekler burada elenir: "mal"+"iyeti" (→ i+yet+i, "yet" ek değil) ve
         "kar"+"go" ("go" ek değil) çekim değildir; buna karşılık "renk"+"lerine"
         (ler+i+ne), "oee"+"yi", "verim"+"liliği" ve "musteri"+"ninkileri" çekimdir.

    Neden uzunluk sezgisi DEĞİL: ilk iki deneme uzunluk oranıyla ayırmaya çalıştı ve ikisi
    de meşru çekimleri kesti — "verim"→"verimliliği" ve "renk"→"renklerine" testlerde
    anında düştü. Ayrım uzunlukta değil BİÇİMDE.

    Zincir kuralının bilinen sınırı: tek-harfli ek atomları yüzünden "esiye" de e+si+ye
    diye ayrışır, yani "ver"+"esiye" (veresiye) geçerdi — bu yüzden o sınıf kökler
    `_STOP_EXACT` ile TAM-KELİME olarak işaretlidir. İki mekanizma birbirini tamamlar.
    """
    if word == known:
        return True
    if not word.startswith(known):
        return False
    # Kural gövdesi `_ek_gecerli`'de — `_syn_hit` (Faz D3) ile TEK KAYNAK.
    return _ek_gecerli(word[len(known):])


def _uncovered(q: str, known_words: set[str]) -> list[str]:
    """q'daki tanınan HİÇBİR parçayla örtüşmeyen anlamlı kelimeler.
    Kelime kapsanır ⇔ kısa (<3) | tanınan bir parçanın ÇEKİMİ (`_covers`) | dolgu kökü."""
    known = {w for w in known_words if len(w) >= 3}
    out: list[str] = []
    for w in re.findall(r"[a-z]+", q):
        if len(w) < 3:
            continue
        if any(_covers(k, w) for k in known):
            continue
        if _is_stop_word(w):
            continue
        out.append(w)
    return out


def _coverage_ok(q: str, known_words: set[str]) -> bool:
    """q'daki HER anlamlı kelime tanınan bir parçayla örtüşüyor mu?
    Aksi tek kelime bile varsa deterministik yol ÇEKİLİR (LLM'e)."""
    return not _uncovered(q, known_words)


def ilgili_cubelar(q: str, schema: dict, haric: set[str] | None = None) -> list[dict]:
    """Soruda cube-düzeyi VEYA boyut-düzeyi sinonimi eşleşen cube'lar (ZAYIF sinyal).

    "Zayıf" çünkü bir (cube, ölçü) çifti kurmuyor — yalnız *"bu soru şu konularla ilgili
    görünüyor"* diyor. Ama netleştirmeyi **13 seçenekten 2-3'e** indirmeye yeter ve
    bunun için LLM gerekmez.

    ## Neden ayrı bir fonksiyon (Faz -1)

    Bu tarama `ask.py`'nin `if unknown and hits:` dalının **İÇİNDE** gömülüydü — yani
    `partial_unknowns` hiçbir (cube, ölçü) çifti bulamadığında (`hits == []`)
    **erişilemiyordu**. Tam da o durumda, yani sistemin en çaresiz olduğu anda, elindeki
    tek sinyali kullanamıyordu ve 13 cube'un 1'er örneğini döküyordu — kullanıcının
    *"bildiğini okuyor"* dediği davranış.

    Canlı örnek: *"son 6 ay personel bazlı çalışma süreleri kıyasla"* — "personel"
    `ik`/`parti` cube'larında **zaten bir sinonim**; bu sinyal 13'ü 2'ye indirir.

    Gövde kopyalanmadı, **taşındı**: iki çağıran da aynı fonksiyonu kullanır (bu depoda
    gövde kopyalamanın bedeli altı kez ölçüldü).
    """
    # DOLGU KELİMESİ KONU SİNYALİ OLAMAZ. Ölçüldü (2 Ağustos 2026 — bu değişikliğin KENDİ
    # testi yakaladı): `ik.donem` boyutunun sinonimleri ['donem','ay','periyot','period'] ve
    # *"bu yıl tüm AYLARINI karşılaştır"* — hiçbir konu taşımayan, testinin adı bile
    # `test_konusuz_soru_tahmin_etmez` olan soru — `"aylarini"` üzerinden `ik`e eşleşiyordu.
    # Sonuç *"İK / bordro ile ilgili görünüyor"*: 13 seçenekli dökümden **DAHA KÖTÜ**, çünkü
    # kendinden emin ve yanlış — bu deponun "en tehlikeli sınıf" dediği şeyin bir DÜZELTMENİN
    # içinden doğmuş hâli.
    #
    # `time_dimensions` beyanı bu ayrımı TAŞIMIYOR (ölçüldü: `ik`'in zaman boyutu
    # `donem_tarih`; `donem` kategorik bir etikettir). Doğru ayrım kelime listesinde de
    # değil — **soruyu açıklayan dolgu sözlüğünde**: `_period_hit_words | _misc_hit_words`
    # bu deponun "bu kelime dönem/granülerlik ifadesidir" TEK KAYNAĞIDIR ve `_uncovered`
    # zaten onu kullanıyor. Bir kelime dolguyla açıklanıyorsa konu hakkında hiçbir şey
    # söylemez. Yeni bir liste yazılmadı; var olan kapı yeniden kullanıldı (ADR-0008).
    dolgu = _period_hit_words(q) | _misc_hit_words(q)
    anlamli = _uncovered(q, dolgu)
    if not anlamli:
        return []   # soruda dolgu dışında hiçbir şey yok → daraltılacak konu da yok
    # Eşleşme YALNIZ dolgu-dışı kelimeler üzerinde aranır: "aylarini" elenir, "personel" kalır.
    konu_metni = " ".join(anlamli)

    haric = haric or set()
    out: list[dict] = []
    for c in schema.get("cubes") or []:
        if c.get("name") in haric:
            continue
        # Cube-düzeyi VEYA boyut-düzeyi sinonim — "tedarikçi" gibi bir kelime ölçü değil,
        # BAŞKA bir cube'un BOYUTU olabilir (cari/ticaret'in "tedarikçi" boyutu).
        # İkisi de "bu konu ilgili" sinyali sayılır.
        dim_hit = any(_syn_hit_words(konu_metni, syns)
                      for syns in (c.get("dimension_synonyms") or {}).values())
        if _syn_hit_words(konu_metni, c.get("synonyms")) or dim_hit:
            out.append(c)
    return out


def partial_unknowns(q: str, schema: dict) -> tuple[list[str], list[tuple[dict, str]]]:
    """KATALOG-GENELİ kısmi anlama denetimi (dürüstlük kapısı, ADR-0008):
    (hiçbir cube sözlüğünde karşılığı olmayan kelimeler, tanınan (cube, ölçü) çiftleri).

    "kar oranı sürdürülebilirlik" → (["surdurulebilirlik"], [(parti, kar_marji_yuzde)]).
    İkisi de doluysa serbest-SQL'e DÜŞÜLMEZ: LLM tanımadığı kavram için istenmemiş
    çok-metrikli rapor uydurabiliyor (log 2026-07-20) — tanınan kısım chip'lenir,
    tanınmayan açıkça söylenir."""
    known: set[str] = set()
    hits: list[tuple[dict, str]] = []
    # route()'un KENDİ kapsam-kapısıyla AYNI standart: bir cube adı yalnız KATALOGDA var
    # olması "anlaşıldı" saymaz — mesaj BAŞKA bir cube'a çözülüyorsa (ör. "kar oranı
    # sürdürülebilirlik" → ölçü kanıtıyla parti'ye çözülür) "sürdürülebilirlik" hâlâ
    # AÇIKLANMAMIŞTIR. Belirsizse (resolved=None, çapraz-konu adayı) TÜM cube-düzeyi
    # sinonimler sayılır — o durumda birden fazla konu GERÇEKTEN tanınmış olabilir.
    resolved = _match_cube(q, schema)
    for c in schema.get("cubes", []):
        # AYNI kısıt (cube-düzeyi/ölçü/boyut/değer — DÖRDÜ de) yalnız ÇÖZÜLEN cube'un
        # kendi sözlüğüne uygulanır; resolved=None ise (gerçek çapraz-konu adayı,
        # "verim ve fire oranı" gibi) TÜM katalog sayılır — o durumda birden fazla
        # konu GERÇEKTEN tanınmış olabilir. `hits` HER ZAMAN kısıtsız (hangi ölçü
        # NEREDE geçerse, "hangisini istedin?" chip'i için gerekli).
        in_scope = resolved is None or c is resolved
        if in_scope:
            known |= _syn_hit_words(q, c.get("synonyms"))
        m, msyn = _match_measure(q, c)
        if m:
            hits.append((c, m))
            if msyn and in_scope:
                known.update(re.findall(r"[a-z]+", msyn))
        if in_scope:
            for syns in (c.get("dimension_synonyms") or {}).values():
                known |= _syn_hit_words(q, syns)
            for vals in (c.get("dimension_values") or {}).values():
                for v in vals or []:
                    nv = _norm(str(v))
                    if nv and _value_token_hit(q, nv):
                        known.update(re.findall(r"[a-z]+", nv))
    known |= _period_hit_words(q)
    known |= _misc_hit_words(q)
    return _uncovered(q, known), hits


# --- Typo/bulanık-eşleştirme toleransı (Faz 2c/Faz 3, 31 Temmuz 2026) -------
# route()'un değer/sözlük eşleştirmesi (_value_token_hit, _syn_hit) TAM/ALT-DİZİ
# eşleşme yapar, yazım hatasına karşı kırılgandı ("Siyh"/"vardya"/"müterileri" hiç
# tanınmıyordu, dürüst-ret ya da serbest-SQL'e düşüyordu). Yanlış-pozitif riski (bir
# YANLIŞ "düzeltme" sessiz-yanlış veriden KÖTÜdür, ADR-0008 ilkesi) yüzünden İKİ katı
# güvence var: (1) YALNIZ `partial_unknowns`'ın zaten "hiçbir şeye karşılık gelmiyor"
# dediği kelimeler denenir (stopword/kısa-kelime riski sıfır — mevcut kapsam-kapısı
# aynen miras alınır), (2) OTOMATİK düzeltme yalnız YÜKSEK benzerlik + NET aday (ikinci
# en-iyi adayla belirgin fark) şartıyla olur; aksi hâlde metin DEĞİŞMEZ, yalnız "şunu mu
# demek istedin?" ÖNERİSİ üretilir (tahmin YOK).
_TYPO_MIN_WORD_LEN = 4    # 3 harf ve altı fuzzy'ye hiç girmez (gürültü/yanlış-pozitif riski)
_TYPO_HIGH = 0.82         # bu ve üstü + net aday → OTOMATİK düzelt
# 0.60 → 0.65 (canlı bulgu, 31 Temmuz 2026): cube'a-daraltma (aşağıdaki `only_cube`) doğru
# adayları güçlendirirken, KÜÇÜLEN havuzda alakasız bir kelime de "en iyi" olabiliyordu —
# "fizibilite"/"profitability" tam 0.6087 (uzunluk-oranı korumasını GEÇİYOR, 0.77) → 0.60
# eşiğinde YANLIŞ öneri üretti (test_alakasiz_kelime_oneriye_donusmez canlı yakaladı).
# Gerçek düzeltmelerin (müterileri/müşteri=0.706, vardya/vardiya=0.923, siyh/siyah=0.889)
# hepsi 0.65'in ÜSTÜNDE kalıyor — 0.60→0.65 net bir ayrım sağlıyor, regresyon YOK.
_TYPO_MID = 0.65          # bu ve üstü (HIGH altı) → yalnız "şunu mu demek istedin?" öner
_TYPO_GAP = 0.08          # en iyi/ikinci-iyi aday arası bu kadar fark olmalı (net aday şartı)
# GENİŞ HAVUZ (only_cube=None) İÇİN DAHA SIKI "ÖNERİ" BARAJI (canlı bulgu, 1 Ağustos 2026):
# cube çözülemeyince (`_match_cube` None) havuz TÜM kataloğa genişliyor — bu rejimde
# alakasız-ama-benzer bir kelime çifti ("kalem"(5)/"kalite"(6) → 0.7273, "nisan"/"lisans"
# ile MATEMATİKSEL AYNI desen: 5-6 harfli TR kelime çifti, ortak alt-dizi uzun) hâlâ MID
# barajını (0.65) geçip "şunu mu demek istedin?" öneriyordu — "kalem" hiçbir cube'un
# sözlüğünde YOKTUR, "kalite" TAMAMEN alakasız bir domain kelimesidir (oee.ort_kalite).
# Cube ÇÖZÜLMEDİĞİNDE (bağlam belirsiz) fuzzy önerinin güven barajı da YÜKSELMELİ.
# _TYPO_HIGH'a EŞİTLENDİ (keyfi yeni sayı icat etmek yerine): geniş havuzda bir öneri
# ancak OTOMATİK-düzelt kalitesindeyse (yalnız ikinci-aday GAP'i yetersiz kaldığı için
# auto'ya değil suggest'e düştüyse) gösterilir — tek-cube'a-daralmış (mevcut, test
# edilmiş) davranış bu sabitten ETKİLENMEZ.
_TYPO_MID_WIDE = _TYPO_HIGH
# UZUNLUK-ORANI KORUMASI: SequenceMatcher.ratio() ÇOK FARKLI uzunluktaki kelimeler için
# de yanıltıcı biçimde orta-yüksek çıkabiliyor (gerçek bulgu: "fizibilite"(10)/"fiili"(5)
# → 0.667, "müterileri"(10)/"musteri"(7) → 0.706 — aradaki fark ince, salt eşik yetmez).
# Gerçek bir yazım hatası kelimeyi genelde 1-2 harf değiştirir/ekler/eksiltir, İKİYE
# KATLAMAZ — kısa/uzun kelime oranı bu payı aşarsa (alakasız kelime, "fizibilite" gibi)
# aday tamamen ELENİR (öneri bile YOK — ADR-0008: yanlış öneri, önerisizlikten kötüdür).
_TYPO_LEN_RATIO = 0.65


def _catalog_vocabulary(schema: dict, only_cube: dict | None = None) -> set[str]:
    """Katalogdaki tanınan tek-kelimelik terimler (değer + sinonim) — typo-düzeltme
    adaylarının havuzu. `partial_unknowns`'ın kapsam evreniyle AYNI kaynaklardan
    beslenir (cube/ölçü/boyut sinonimleri + kategorik değerler). `only_cube` verilirse
    (soru zaten belirli bir cube'a çözüldüyse) YALNIZ o cube'un sözlüğü kullanılır —
    aksi halde jenerik bir kelime ("hesapla" gibi) alakasız bir cube'un (mizan'ın
    "hesap"ı gibi) teriminle rastgele yüksek benzerlik yakalayıp yanlış öneri üretebilir
    (canlı bulgu, 31 Temmuz 2026 — `partial_unknowns`'ın kendi `in_scope` ilkesiyle AYNI)."""
    cubes = [only_cube] if only_cube is not None else schema.get("cubes", [])
    terms: set[str] = set()
    for c in cubes:
        terms.update(s.removesuffix("!") for s in (c.get("synonyms") or []))
        for syns in (c.get("measure_synonyms") or {}).values():
            terms.update(s.removesuffix("!") for s in syns)
        for syns in (c.get("dimension_synonyms") or {}).values():
            terms.update(s.removesuffix("!") for s in syns)
        for vals in (c.get("dimension_values") or {}).values():
            terms.update(str(v) for v in vals or [])
    words: set[str] = set()
    for term in terms:
        words.update(re.findall(r"[a-z]+", _norm(term)))
    return {w for w in words if len(w) >= _TYPO_MIN_WORD_LEN}


def typo_correct(q: str, schema: dict) -> tuple[str, list[dict]]:
    """Sorudaki TANINMAYAN kelimeleri (`partial_unknowns` kapsamında) katalog kelime
    haznesine karşı bulanık eşler. Döner: (olası-düzeltilmiş soru metni, düzeltme
    kayıtları — `{"kind": "auto"|"suggest", "from": ..., "to": ...}`). `kind="auto"`
    metne YANSIR (ask.py trace'e "yazım düzeltme" ekler); `kind="suggest"` metni
    DEĞİŞTİRMEZ (ask.py "şunu mu demek istedin?" chip'i kurar, tahmin etmez)."""
    unknown, _hits = partial_unknowns(q, schema)
    if not unknown:
        return q, []
    # Soru zaten bir cube'a çözülüyorsa (route()'un KENDİ eşleştirmesiyle AYNI), sözlük
    # O CUBE'A daralır — `partial_unknowns`'ın "unknown" tanımıyla TUTARLI kapsam.
    resolved = _match_cube(q, schema)
    vocab = _catalog_vocabulary(schema, only_cube=resolved)
    if not vocab:
        return q, []
    # Cube çözülemediyse (resolved=None → vocab TÜM kataloğa genişledi) "öneri" barajı
    # da yükselir; tek-cube'a-daralmış durumda eski (test edilmiş) davranış korunur.
    min_suggest = _TYPO_MID if resolved is not None else _TYPO_MID_WIDE
    # ÇAPRAZ-KONU TERİMİ YAZIM HATASI DEĞİLDİR (Faz D3, ölçülmüş vaka). Soru bir cube'a
    # çözüldüğünde `unknown`, YALNIZ O CUBE'a göre bilinmeyenleri içerir; oysa kelime
    # başka bir cube'un GERÇEK terimi olabilir. Ölçüldü: "personel bazlı verimlilikleri
    # karşılaştır" → cube `parti`ye çözülüyor (personel kırılımını YALNIZ o taşıyor),
    # `verimlilikleri` orada bilinmiyor ve bulanık eşleşme onu `renk_derinlik`in
    # "derinliği"ne çeviriyordu — anlamsız bir "şunu mu demek istedin?".
    # `verim` tüm katalogda GERÇEK bir terimdir (oee) → düzeltilecek bir yazım hatası
    # değil, bir ÇAPRAZ-KONU sinyalidir; `partial_unknowns`'ın netleştirmesine bırakılır.
    tum_katalog = _catalog_vocabulary(schema) if resolved is not None else set()
    corrections: list[dict] = []
    q_out = q
    for w in unknown:
        if len(w) < _TYPO_MIN_WORD_LEN:
            continue
        if any(_covers(t, w) for t in tum_katalog):
            continue
        scored = sorted(
            ((difflib.SequenceMatcher(None, w, cand).ratio(), cand) for cand in vocab),
            key=lambda t: t[0], reverse=True,
        )
        best_score, best = scored[0]
        if best == w or best_score < min_suggest:
            continue
        len_ratio = min(len(w), len(best)) / max(len(w), len(best))
        if len_ratio < _TYPO_LEN_RATIO:
            continue  # uzunluk çok farklı → muhtemelen alakasız kelime, ELE
        second_score = scored[1][0] if len(scored) > 1 else 0.0
        fixed_q = re.sub(rf"\b{re.escape(w)}\b", best, q)
        if best_score >= _TYPO_HIGH and (best_score - second_score) >= _TYPO_GAP:
            q_out = re.sub(rf"\b{re.escape(w)}\b", best, q_out)
            corrections.append({"kind": "auto", "from": w, "to": best, "corrected_q": fixed_q})
        else:
            # "suggest": q_out (asıl dönen metin) DEĞİŞMEZ — yalnız kayıtta "eğer bu
            # kelime düzeltilseydi" metni taşınır, ask.py chip'in `query`'si için kullanır.
            corrections.append({"kind": "suggest", "from": w, "to": best, "corrected_q": fixed_q})

    # Doğrulama turu düzeltmesi (1 Ağustos 2026) — `app/value_index.py` (ADR-0008) TAM
    # yazılmıştı ama HİÇ bağlanmamıştı. Yukarıdaki difflib geçişi yalnız TEK KELİMELİK
    # düzeltme yapabilir (`_catalog_vocabulary` çok-kelimeli değerleri BİLE tek tek
    # kelimelere bölüyor) — `value_index.FuzzyIndex` KOMŞU KELİME İKİLEMELERİNİ de dener
    # (ör. "efe dokma" → çok-kelimeli bir müşteri/ürün adı "efe dokuma" ancak böyle
    # yakalanır). Bu YÜZDEN yukarıdaki geçişin YERİNE değil, YALNIZ onun ÇÖZEMEDİĞİ
    # (hâlâ tanınmayan) kelimeler için EK bir deneme olarak eklenir — mevcut, %100
    # hassasiyetli tek-kelime kararını asla EZMEZ/DEĞİŞTİRMEZ.
    corrected_words = {c["from"] for c in corrections}
    # DİKKAT — `leftover` çapraz-konu filtresinden GEÇİRİLMEZ. Denendi ve
    # `test_value_index_multi_word_value_typo_fallback` anında düştü: `FuzzyIndex` KOMŞU
    # KELİME İKİLEMESİ dener ("kontinu kasr" → "kontinu kasar") ve doğru yazılmış komşuyu
    # havuzdan çıkarmak ikilemenin kurulmasını imkânsız kılar. Filtre bu yüzden girdide
    # değil, ÇIKTIDA uygulanır (aşağıda).
    leftover = [w for w in unknown if w not in corrected_words and len(w) >= _TYPO_MIN_WORD_LEN]
    if leftover:
        from app.value_index import FuzzyIndex

        fi_schema = {"cubes": [resolved]} if resolved is not None else schema
        idx = FuzzyIndex(fi_schema)
        auto = idx.auto_fix(q, leftover)
        if auto is not None and auto.surface != auto.span:
            fixed_q = re.sub(rf"\b{re.escape(auto.span)}\b", auto.surface, q)
            q_out = re.sub(rf"\b{re.escape(auto.span)}\b", auto.surface, q_out)
            corrections.append({"kind": "auto", "from": auto.span, "to": auto.surface,
                                "corrected_q": fixed_q})
        else:
            for c in idx.suggest(q, leftover)[:1]:  # yalnız EN İYİ aday (chip gürültüsü olmasın)
                if c.surface == c.span:
                    continue
                if any(_covers(t, c.span) for t in tum_katalog):
                    continue  # çapraz-konu terimi — yazım hatası değil (bkz. yukarıdaki gerekçe)
                fixed_q = re.sub(rf"\b{re.escape(c.span)}\b", c.surface, q)
                corrections.append({"kind": "suggest", "from": c.span, "to": c.surface,
                                    "corrected_q": fixed_q})
    return q_out, corrections


# ÖLÇÜ EŞİĞİ (HAVING): "10 milyon üzeri / 100 bin altında / 5 milyon TL'den fazla".
# cube derleyici HAVING üretmez → cube_sql agregat ölçü alias'ına dış WHERE ile uygular.
_THRESHOLD_RE = re.compile(
    r"\b(\d+(?:[.,]\d+)?)\s*(milyar|milyon|bin|k|m)?\s*(?:tl\w*|lira\w*|₺)?\s*"
    r"(uzerindeki|uzerinde|uzeri|ustu|asan|gecen|dan fazla|den fazla|dan buyuk|den buyuk|"
    r"dan yuksek|den yuksek|altindaki|altinda|alti|dan az|den az|dan kucuk|den kucuk|"
    r"dan dusuk|den dusuk)")
_TH_MULT = {"milyar": 1e9, "milyon": 1e6, "m": 1e6, "bin": 1e3, "k": 1e3}
# TAM ifadeler (alt-dizi DEĞİL): "az" 'den f**az**la' içinde yanlış eşleşiyordu → '<' hatası.
_TH_LESS = {"alti", "altinda", "altindaki", "dan az", "den az", "dan kucuk", "den kucuk",
            "dan dusuk", "den dusuk"}
_TH_WORDS = {"milyon", "milyar", "bin", "tl", "lira", "uzeri", "ustu", "uzerinde",
             "uzerindeki", "asan", "gecen", "alti", "altinda", "altindaki", "fazla",
             "az", "buyuk", "kucuk", "yuksek", "dusuk"}


def _measure_threshold(q: str) -> dict | None:
    """"10 milyon üzeri" → {op:'>', value:10000000}; "100 bin altında" → {op:'<', value:100000}."""
    m = _THRESHOLD_RE.search(q)
    if not m:
        return None
    num = float(m.group(1).replace(",", "."))
    mult = _TH_MULT.get((m.group(2) or "").lower(), 1)
    op = "<" if m.group(3) in _TH_LESS else ">"
    return {"op": op, "value": num * mult}


# --- RED GEREKÇESİ TELEMETRİSİ (Faz 0) -------------------------------------------
#
# `route()` on ayrı yerde `None` döner ve bugün HANGİSİNDE pes ettiği yalnız `trace`
# metninde/`source=None`'da görünüyor — **sayısal olarak gruplanamıyor**. Plan §2.3'ün
# tezi tam bu: *"çoğu soru LLM'e gidiyor"* bir HİPOTEZ, ölçüm değil. Hangi kaldıraca
# yatırım yapılacağı (netleştirme chip'i mi, Intent-JSON mu, Discovery mi) 36'nın nasıl
# dağıldığı görülmeden karar verilemez.
#
# ## Neden ContextVar, neden imza değişmiyor
#
# `route()`'un beş çağıranı var (`ask.py`, iki iç sonda `cube_router`'da, `lab/nl_corpus`,
# `eval/`). Dönüş tipini `tuple`a çevirmek hepsini kırardı ve gerekçe zincirin her
# katmanından elle taşınırdı. Bu deponun **kanıtlanmış** çözümü var: `app/llm.py:43`
# (`_llm_usage_var` + `reset/record/get`) tam bu şekli çözüyor — derin bir fonksiyon
# kaydeder, sığ bir fonksiyon okur, aradaki imzalar sabit kalır. Yeni bir mekanizma
# İCAT EDİLMEDİ; var olan kalıp ikinci kez kullanıldı.
#
# FastAPI sync endpoint'i kendi kopya-context'inde koştuğu için istekler izoledir
# (`llm.py`'nin aynı gerekçesi).
_reddi_var: contextvars.ContextVar = contextvars.ContextVar("dima_route_reddi", default=None)

#: Dal kodu → insan-okur gerekçe. Kod SABİT kalır (telemetri gruplaması ona dayanır),
#: metin değişebilir. `route()`'un `return None` dallarıyla BİREBİR eşleşir.
RED_KODLARI: dict[str, str] = {
    "R1": "cube eşleşmedi",
    "R2": "liste/döküm niyeti (politika: küp üretebilir ama devredildi)",
    "R3": "kıyas dili (compare) — cube yolu kıyası kurmuyor",
    "R4": "ölçü eşleşmedi",
    "R5": "ortalama istendi ama ortalama ölçü tanımlı değil",
    "R6": "dışlama filtresi kısmen çözüldü (yarım uygulama yapılmaz)",
    "R7": "boyut adayı tek değil (belirsizlik)",
    "R8": "yarı-toplanabilir ölçü + zaman kovası (running balance = WINDOW)",
    "R9": "kırılım istendi ama boyut eşleşmedi",
    "R10": "kapsam kapısı — tanınmayan kelime (ADR-0008)",
}


def reddi_sifirla() -> None:
    """İstek başında: bu isteğin red gerekçesini taze bir kovaya al."""
    _reddi_var.set(None)


def _reddet(kod: str) -> None:
    """`route()`'un bir `return None` dalını etiketler. Kova kurulmadıysa sessizce atlar
    (eval/test/iç sonda çağrıları — `llm.py`'nin aynı davranışı)."""
    try:
        _reddi_var.set(kod)
    except LookupError:  # pragma: no cover — ContextVar her zaman set edilebilir
        pass


def red_gerekcesi() -> str | None:
    """`route()` en son hangi dalda pes etti? (`None` = pes etmedi ya da hiç çağrılmadı)"""
    return _reddi_var.get()


def route(question: str, schema: dict) -> dict | None:
    """Soru bir cube metriğine eşlenirse {cube_query, order, limit} döner; yoksa None.

    Tamamen GENERIC: cube/ölçü/boyut eşleşmeleri cube metadata'sındaki `synonyms`
    içeriğinden gelir (ADR-0005) — bu fonksiyon sektör/demo bilgisi içermez.

    **Red gerekçesi (Faz 0):** `None` dönen her dal `_reddet("R…")` ile etiketlenir ve
    `red_gerekcesi()` ile okunabilir. İmza DEĞİŞMEDİ — beş çağıranın hiçbiri kırılmadı
    (`app/llm.py`'nin `_llm_usage_var` kalıbı)."""
    reddi_sifirla()
    q = _norm(question)

    cube_meta = _match_cube(q, schema)
    if cube_meta is None:
        _reddet("R1")
        return None  # eşleşme yok ya da çapraz konu (birden çok cube) → LLM
    cube = cube_meta["name"]

    # Liste/döküm istekleri cube'a uymaz → LLM/kural. KELİME-SINIRLI: "dokum" altdizisi
    # "DOKUMa"yı (kumaş!) yakalıyordu; genel "göster" ise liste niyeti DEĞİL (dolgu).
    if re.search(r"\b(listele\w*|liste\b|hangileri|detay\w*|dokum(u|un|unu|ler\w*)?\b)", q):
        _reddet("R2")
        return None

    # Dönemsel karşılaştırma (önceki dönem/LAG) cube'a sığmaz → LLM (golden SQL deseni)
    if any(w in q for w in _COMPARE_HINTS):
        _reddet("R3")
        return None

    measure, msyn = _match_measure(q, cube_meta)
    if measure is None:
        measure = cube_meta.get("default_measure")
    if measure is None:
        _reddet("R4")
        return None  # ölçü kelimesi yok ve varsayılan tanımlı değil → LLM

    # "ORTALAMA" NİTELEYİCİSİ YUTULMASIN (canlı gitas 2026-07): "ortalama satış" bare
    # "satış" ile satis_tutari'ye (TOPLAM) düşüyordu → "ortalama" göz ardı. Soru ortalama
    # isterken eşleşen ölçü ortalama DEĞİLSE (adı ort_ değil ve sinonim "ortalama" içermiyor)
    # deterministik dönme — ölçü belirsiz (AOV mı, birim fiyat mı?) → chip/LLM devralsın.
    if ("ortalama" in q or "average" in q) and not (
            measure.startswith("ort_") or "ortalama" in (msyn or "")):
        _reddet("R5")
        return None

    cols = {c["name"]: c for m in schema.get("models", []) for c in m["columns"]}
    dims = _match_dims(q, cube_meta, msyn)

    # Kategorik değer filtreleri (müşteri/renk/kumaş/aşama adı → WHERE); değer eşleşen
    # kolon boyut olarak değil filtre olarak kullanılır.
    filters = []
    filtered = set()
    multi_val_dims: list[str] = []
    exclude_words: set[str] = set()
    # 1. GEÇİŞ — hangi boyutta hangi değerler eşleşti. Dışlama kararı İKİNCİ geçişte
    # verilir çünkü "beyaz ve siyah hariç" ifadesindeki bağlaç zinciri BOYUT SINIRINI
    # AŞAR: `renk_derinlik`te "Siyah" yoktur ama zinciri yutabilmek için o kelimeyi
    # tanıması gerekir. Tek geçişte bu bilgi henüz yoktu ve `renk_derinlik` sessizce
    # `eq Beyaz` alıyordu — yani kullanıcı "beyaz hariç" derken beyazın kendisi
    # filtreleniyordu (üstelik `renk`teki `not_in` ile ÇELİŞEREK).
    eslesen: dict[str, list[str]] = {}
    for dname in cube_meta.get("dimensions", []):
        c = cols.get(dname)
        if not c or not c.get("values"):
            continue
        matched = [str(v) for v in c["values"]
                   if (nv := _norm(str(v))) and _value_token_hit(q, nv)]
        if matched:
            eslesen[dname] = matched
    tum_norm = {_norm(v) for vs in eslesen.values() for v in vs}

    # 2. GEÇİŞ — DIŞLAMA (Faz 3.3): "beyaz hariç", "iptaller dışında" → neq/not_in.
    # Motor 12 operatör destekliyor (çalıştırılarak doğrulandı: eq neq in not_in gt gte
    # lt lte contains starts_with is_null is_not_null; geçersiz operatör Rust'ta gürültülü
    # reddediliyor), Python bugüne kadar yalnız 4 üretiyordu — eksik olan tek şey
    # NL→operatör köprüsüydü. Bu, "beyaz hariç rework" sorusuna BEYAZIN rework'ünü
    # döndüren sessiz-yanlışı kapatır.
    for dname, matched in eslesen.items():
        norm_matched = [_norm(v) for v in matched]
        dislanan = [v for v, nv in zip(matched, norm_matched)
                    if _deger_dislaniyor(
                        q, nv, sorted(tum_norm - {nv}, key=len, reverse=True))]
        if dislanan and len(dislanan) != len(matched):
            # KARMA ("beyaz hariç siyah dahil"): hangi değerin hangi tarafta olduğu
            # metinden güvenle çıkarılamaz. Sessizce bir yorum seçmek yerine dürüst red
            # (ADR-0008) — LLM devralsın.
            _reddet("R6")
            return None
        if dislanan:
            exclude_words |= {w for w in _EXCLUDE_MARKERS if w in q}
            op = "neq" if len(matched) == 1 else "not_in"
            filters.append({"dimension": dname, "operator": op,
                            "value": matched[0] if len(matched) == 1 else matched})
            # Dışlamada boyut KIRILIM olarak anlamlıdır (geriye birden çok değer kalır) —
            # `eq`in aksine burada boyutu düşürmek bilgiyi yok ederdi.
            multi_val_dims.append(dname)
        elif len(matched) == 1:
            filters.append({"dimension": dname, "operator": "eq", "value": matched[0]})
            filtered.add(dname)
        else:
            # "beyaz ve siyah" = KARŞILAŞTIRMA niyeti → in-filtre + boyut kırılım kalır
            filters.append({"dimension": dname, "operator": "in", "value": matched})
            multi_val_dims.append(dname)
    # ÖNEK / İÇERME (Faz 3.3) — değer indeksinde çözülüp `in`e indirgenir (bkz. _PREFIX_RE).
    for rx, onek_mi in ((_PREFIX_RE, True), (_CONTAINS_RE, False)):
        m = rx.search(q)
        if not m:
            continue
        lit = m.group(1)
        aday: dict[str, list[str]] = {}
        for dname in cube_meta.get("dimensions", []):
            c = cols.get(dname)
            if not c or not c.get("values") or dname in eslesen:
                continue
            vs = [str(v) for v in c["values"]
                  if (nv := _norm(str(v))) and (nv.startswith(lit) if onek_mi else lit in nv)]
            if vs:
                aday[dname] = vs
        if len(aday) != 1:
            # 0 → hiçbir gerçek değer bu ifadeye uymuyor; >1 → hangi boyut belirsiz.
            # İkisinde de sessizce bir yorum seçmek yerine dürüst red (ADR-0008).
            _reddet("R7")
            return None
        dname, vs = next(iter(aday.items()))
        filters.append({"dimension": dname, "operator": "in", "value": vs})
        multi_val_dims.append(dname)
        known_extra = re.findall(r"[a-z]+", m.group(0))
        exclude_words.add(" ".join(known_extra))

    dims = [d for d in dims if d not in filtered]
    for dname in multi_val_dims:
        if dname not in dims:
            dims.append(dname)

    # Göreli tarih aralığı ("son 3 ay") → time dim üzerinde gte filtresi (granularity'siz).
    cube_time = cube_meta.get("time_dimensions") or []
    time_dim = cube_time[0] if cube_time else "tarih"
    # göreli ("son 3 ay"), içinde bulunulan ("bu ay") veya ay adı ("temmuz ayı" → aralık)
    filters.extend(date_filters(q, time_dim))

    gran = _time_gran(q)

    # SEMI-ADDITIVE koruması (panel P0, 6 model oybirliği): bakiye/stok ölçüleri zamanda
    # dönem-SONU (snapshot) değeridir. Düz SUM zaman kovasında ("aylara göre bakiye") ya da
    # dönem-ARALIĞI filtresinde ("bu ay bakiye" → gte) "dönemin net hareketi"ni verir —
    # cube rozetli sessiz-yanlış. Deterministik cube derleyicisi window/period-end üretemez
    # → bu vakayı LLM devralsın (as-of `lte` / windowed SQL yazabilir). Dönemsiz "bakiye"
    # ise TÜM geçmişin SUM'ı = doğru güncel bakiye → deterministik KALIR (period_optional).
    is_semi = measure in (cube_meta.get("semi_additive") or [])
    if is_semi:
        if gran:
            _reddet("R8")
            return None  # zaman kovalı bakiye = running balance = WINDOW → cube üretemez → LLM
        # AS-OF DÖNÜŞÜMÜ: bakiye/stok dönem-SONU snapshot'ıdır, dönem-net-hareketi değil.
        # Dönem-aralığı (gte..lte) → tek `lte` (dönem sonu bakiyesi); açık/güncel dönem
        # ("bu ay", "son 3 ay") üst sınırsızdır → as-of bugün ≡ tüm-geçmiş SUM = doğru
        # güncel bakiye, o yüzden gte filtresini DÜŞÜR. Böylece "geçen ay bakiye" =
        # ayın-sonu bakiyesi (deterministik+doğru), "bu ay bakiye" = güncel bakiye.
        period_fs = [f for f in filters if f.get("dimension") == time_dim]
        if period_fs:
            end = next((f for f in period_fs if f.get("operator") in ("lte", "lt")), None)
            filters = [f for f in filters if f.get("dimension") != time_dim]
            if end:
                filters.append({"dimension": time_dim, "operator": "lte", "value": end["value"]})

    # SESSİZ-YANLIŞ koruması: soruda kırılım niyeti var ("bazında/göre/kırılım") ama hiçbir
    # boyut eşleşmediyse (ör. typo: "m<kina bazında") dejenere toplam DÖNDÜRME — cube
    # rozetiyle yanlış cevap, retten kötüdür. Değer filtresi (ör. cinsiyet=Erkek) bunu
    # KURTARMAZ: "erkekler için X bazında" sorusunda X kaçtıysa sonuç yine dejenere olur.
    # DÜZELTME (canlı bulgu, 1 Ağustos 2026): eskiden `not gran` da şart koşuluyordu — ama
    # "trend"/"zaman" gibi JENERİK (birim belirtmeyen) kelimeler `gran`'ı dolduruyor VE
    # sorudaki AYRI bir boyut-kırılımı isteğini ("tedarikçi bazında oee TRENDİNİ göster")
    # sessizce KARŞILANMIŞ SAYDIRIYORDU — X kırılımı sessizce düşüyor, "dimensions" alanı
    # hiç olmadan "başarılı" görünüyordu (uyarı YOK). AÇIK birim ifadeleri ("aylık/çeyrek/
    # yıllık/haftalık X'e göre") ise KENDİ BAŞINA meşru bir kırılımdır (bkz. _time_gran) —
    # bunlar `not gran` GİBİ davranmaya DEVAM ETMELİ (regresyon: `test_time_gran_ceyrek_
    # yil`, "çeyreklere göre üretim" yanlışlıkla reddediliyordu). Ayrım: yalnız `gran`
    # SIRF jenerik trend/zaman kelimesiyle dolduysa (hiçbir AÇIK birim ifadesi YOKSA)
    # koruma `not gran` KOŞULUNU YOK SAYAR.
    _gran_only_generic_trend = gran is not None and any(w in q for w in ("trend", "zaman")) and not any(
        w in q for w in ("ceyrek", "uc aylik", "yillik", "yillara", "yila gore", "yil bazinda",
                         "senelik", "haftalik", "haftalar", "haftaya", "gunluk", "gunler",
                         "gunlere", "aylik", "aylar", "aya gore", "ay bazinda"))
    if not dims and (not gran or _gran_only_generic_trend) and any(w in q for w in _BREAKDOWN_HINTS):
        # BOYUT-UYUMU İÇİN YENİDEN YÖNLENDİRME: seçilen cube bu kırılımı sağlayamıyor ama
        # AYNI ölçüye + istenen boyuta sahip başka bir cube olabilir. "stok bazında satış
        # tutarı" → ticaret (cube-sinonim "satış") seçildi ama stok yok; mal'da satis_tutari
        # VE stok_ref var → mal'a yönlendir. Tek aday varsa güvenli (belirsizse chip/LLM).
        alts = [c for c in schema.get("cubes", [])
                if c.get("name") != cube and measure in (c.get("measures") or [])
                and _match_dims(q, c, None)]
        if len(alts) == 1:
            sub = {"models": schema.get("models", []), "cubes": [alts[0]]}
            return route(question, sub)
        _reddet("R9")
        return None

    # KAPSAM KAPISI (ADR-0008): mesajda tanınmayan içerik varsa deterministik cevap
    # VERME — LLM devralsın. ("oee istanbul" → istanbul'u anlamadık; toplam dönme.)
    known: set[str] = set()
    known |= _syn_hit_words(q, cube_meta.get("synonyms"))
    if msyn:
        known.update(re.findall(r"[a-z]+", msyn))
    # Eşleşen ölçünün TÜM sinonimlerinin q'da geçen kelimeleri (msyn tek eşleşmedir):
    # "satış miktarları" → measure "miktar"la eşleşse de "satış" ("satış miktarı"
    # sinonimindeki) orphan kalıp kapsamı düşürüyordu (regresyon). Hepsini kapsa.
    for _s in (cube_meta.get("measure_synonyms") or {}).get(measure, []):
        if _syn_hit(q, _s):
            known.update(re.findall(r"[a-z]+", _s.removesuffix("!")))
    for syns in (cube_meta.get("dimension_synonyms") or {}).values():
        known |= _syn_hit_words(q, syns)
    for f in filters:
        known.update(re.findall(r"[a-z]+", _norm(str(f.get("value", "")))))
    # Dışlama edatı ("hariç"/"dışında") ANLAŞILDI — bir operatöre çevrildi, dolgu değil.
    # Kapsam kapısına takılırsa doğru üretilmiş `neq`/`not_in` filtresi çöpe giderdi.
    for w in exclude_words:
        known.update(re.findall(r"[a-z]+", w))
    known |= _period_hit_words(q)
    known |= _misc_hit_words(q)
    # Ölçü-eşiği ("10 milyon üzeri") kelimeleri: anlaşılıyor → kapsam düşürmesin.
    having = _measure_threshold(q)
    if having:
        known |= {w for w in _TH_WORDS if w in q}
    if not _coverage_ok(q, known):
        _reddet("R10")
        return None

    cq: dict = {"cube": cube, "measures": [measure]}
    if having:
        cq["measure_having"] = {"measure": measure, **having}  # HAVING → cube_sql uygular
    if dims:
        cq["dimensions"] = dims
    if gran:
        cq["timeDimensions"] = [{"dimension": time_dim, "granularity": gran}]
    if filters:
        cq["filters"] = filters

    # Sıralama/limit (cube SQL'i dışarıdan sarılır — bkz. ask.py)
    direction = _direction(q)
    n = _top_n(q, cube_meta)
    has_group = bool(dims or gran)
    # VARLIK top-N: zaman kovalı kırılımda satır limiti seriyi ortadan keser
    # ("ilk 3" = ilk ayın 3 satırı olurdu) — ilk N varlık entity_limit ile seçilir,
    # ask.py iki adımda (`in` filtresi) çözer.
    if gran and dims and n and direction:
        # SIRALAMA ÖLÇÜTÜ "en çok X"ten gelir (X=satılan→satis_miktari), GÖSTERİLEN ölçüden
        # DEĞİL (canlı 2026-07-25: "en çok SATILAN 10 ürünün ORTALAMA FİYATI" → fiyata göre
        # sıralayıp yanlış ürünler seçti). Yön ipucundan sayıya kadarki pencerede ölçü ara.
        q2 = _REL_DATE.sub(" ", q)
        cue = _TOPN_CUE.search(q2)
        nm = re.search(r"\b(\d+)\b", q2)
        crit = measure
        if cue and nm and cue.start() < nm.start():
            crit = _match_measure(q2[cue.end():nm.start()], cube_meta)[0] or measure
        cq["entity_limit"] = {
            "dimension": dims[0],
            "measure": crit,
            "direction": "asc" if direction == "ASC" else "desc",
            "n": n,
        }
        return {"cube_query": cq, "measure": measure, "order": None, "limit": None,
                "period_optional": is_period_optional(measure, cube_meta)}
    order = (measure, direction) if (direction and has_group) else None
    limit = n if (n and has_group) else (1 if (direction and dims and not gran) else None)

    # period_optional: semi-additive (bakiye/stok) VE non-additive (avg/count_distinct)
    # ölçülerde dönem SORULMAZ (bkz. is_period_optional) — güncel bakiye zaten as-of-now,
    # tüm-zamanların ortalaması da SUM'un aksine sessizce yanıltıcı değil. ask.py
    # period-kapısı bu bayrağı okur.
    return {"cube_query": cq, "measure": measure, "order": order, "limit": limit,
            "period_optional": is_period_optional(measure, cube_meta)}


# --- LLM'e cube seçtirme (kelime yönlendirici kaçırırsa) --------------------

def build_catalog(schema: dict) -> tuple[str, dict]:
    """LLM prompt'u için cube kataloğu metni + doğrulama indeksi döner."""
    from app.sensitivity import prompt_safe_values

    cubes = schema.get("cubes") or []
    cols = {c["name"]: c for m in schema.get("models", []) for c in m["columns"]}
    lines, enum_lines, index = [], [], {}
    for c in cubes:
        index[c["name"]] = c
        line = f'- {c["name"]}: measures[{", ".join(c.get("measures", []))}]'
        if c.get("dimensions"):
            line += f'; dimensions[{", ".join(c["dimensions"])}]'
        if c.get("time_dimensions"):
            line += f'; time[{", ".join(c["time_dimensions"])}]'
        lines.append(line)
        for dim in c.get("dimensions", []):
            col = cols.get(dim)
            # HASSAS KOLON DEĞERLERİ PROMPT'A GİRMEZ (Faz A1). Süzgeç `llm._schema_prompt`
            # ile AYNI kaynaktan (`app/sensitivity.py`) — eskiden iki prompt üreticisi
            # farklı politika uyguluyordu (burada ≤25 + cube whitelist, orada HER VARCHAR).
            vals = prompt_safe_values(col) if col else []
            if vals and len(vals) <= 25:
                enum_lines.append(f'  {c["name"]}.{dim} ∈ {{{", ".join(map(str, vals))}}}')
    catalog = "\n".join(lines)
    if enum_lines:
        catalog += "\n\nFiltre değerleri (birebir kullan):\n" + "\n".join(enum_lines)
    return catalog, index


# Zaman granülerliği merdiveni (kaba→ince); drill-down bir kademe iner (ay→hafta).
_GRAN_LADDER = ["year", "quarter", "month", "week", "day"]
_GRAN_LABEL = {"year": "Yıllık", "quarter": "Çeyreklik", "month": "Aylık",
               "week": "Haftalık", "day": "Günlük"}
_MAX_NEXT_STEPS = 6


def suggest_next_steps(cube_query: dict, index: dict) -> list[dict]:
    """K2 (rehberli analitik) — bir rapordan DETERMİNİSTİK 'sonraki adım' önerileri:
    kullanılmayan BOYUTLAR (kırılım), kullanılmayan ÖLÇÜLER (ölçek), zaman GRANÜLERLİĞİ.

    Her öneri TAM cube_query taşır → FE `/cube` ile LLM'siz koşar (mevcut chip yolu).
    Katalogdan türetilir (LLM yok, halüsinasyon yok). Boş liste = öneri yok."""
    cube = (cube_query or {}).get("cube")
    spec = index.get(cube) if cube else None
    if not spec:
        return []
    dims_used = list(cube_query.get("dimensions") or [])
    meas_used = list(cube_query.get("measures") or [])
    dim_labels = spec.get("dimension_labels") or {}
    meas_labels = spec.get("measure_synonyms_display") or {}
    all_dims = spec.get("dimensions") or []
    dims, meases, times = [], [], []

    # 1) KIRILIM — kullanılmayan boyutlar. İkiden fazla kırılım satırı patlatır → 2'de dur.
    uretilen = spec.get("dimension_origin") or {}
    if len(dims_used) < 2:
        for d in all_dims:
            if d in dims_used:
                continue
            # _kodu boyutunu, _adi kardeşi varken önerme (kod gürültüsü; ad kırılımı yeğ).
            if d.endswith("_kodu") and f"{d[:-5]}_adi" in all_dims:
                continue
            label = dim_labels.get(d) or d.replace("_", " ")
            dims.append({"label": f"{label} kırılımı", "kind": "dimension", "_ad": d,
                         "cube_query": {**cube_query, "dimensions": [*dims_used, d]}})

    # 2) ÖLÇEK — kullanılmayan ölçüler ("kâr da ekle", "adet de gör").
    for m in spec.get("measures") or []:
        if m in meas_used:
            continue
        label = meas_labels.get(m) or m.replace("_", " ")
        meases.append({"label": f"+ {label}", "kind": "measure",
                       "cube_query": {**cube_query, "measures": [*meas_used, m]}})

    # 3) ZAMAN — cube'un zaman boyutu varsa trend/granülerlik öner.
    time_dims = spec.get("time_dimensions") or []
    if time_dims:
        tds = cube_query.get("timeDimensions") or []
        cur = tds[0].get("granularity") if tds else None
        if cur is None:
            times.append({"label": "Aylık trend", "kind": "time",
                          "cube_query": {**cube_query, "timeDimensions": [
                              {"dimension": time_dims[0], "granularity": "month"}]}})
        elif cur in _GRAN_LADDER and _GRAN_LADDER.index(cur) + 1 < len(_GRAN_LADDER):
            finer = _GRAN_LADDER[_GRAN_LADDER.index(cur) + 1]
            times.append({"label": f"{_GRAN_LABEL[finer]} detay", "kind": "time",
                          "cube_query": {**cube_query, "timeDimensions": [
                              {**tds[0], "granularity": finer}]}})

    # 4) DÖNEMSEL KIYAS (YoY) — zaman boyutu varsa "geçen yıla göre" öner. compare modifier'ı
    #    taşıyan cube_query → FE /cube ile period-shift koşar (LLM'siz; çok-yıl veri gerekir).
    cmp_steps = []
    if time_dims and not cube_query.get("compare"):
        cmp_steps.append({"label": "Geçen yıla göre kıyasla", "kind": "time",
                          "cube_query": {**cube_query, "compare": "yoy"}})

    # KIRILIM SEÇİMİ (Faz 3.4) — iki slottan biri İLİŞKİ-TÜREVİ boyuta ayrılır.
    #
    # Ölçüldü (2 Ağustos 2026): katalogdaki 7 üretilen boyutun (bakim/kalite/
    # makine_duruslari/oee `bölüm`, parti/surdurulebilirlik `kısım`, kalite `operatör`)
    # SIFIRI chip'te görünüyordu. Sebep sıralama değil KESME: `dims[:2]` manifest sırasını
    # alıyor, üreteç ise boyutları metadata'nın SONUNA ekliyor — `parti`nin 15 boyutundan
    # yalnız `makine` + `hat` chip oluyordu. Planın önerdiği "hop-derinliğine göre sırala"
    # TEK BAŞINA ETKİSİZDİR: yerli boyutlar zaten manifest başında, sıralamak çıktıyı hiç
    # değiştirmez.
    #
    # Neden ikinci YERLİ chip feda ediliyor: yerli boyut kullanıcının zaten yazabileceği
    # bir kelimedir ("hat bazında" → çalışır). Çapraz-model boyut ise VAR OLDUĞU BİLİNMEYEN
    # bir yetenektir — Faz 1'de açıldı ama kullanıcı ondan haberdar değil. Chip bir KEŞİF
    # mekanizmasıdır; keşfedilmesi gerekeni göstermelidir.
    #
    # Sıçrama derinliği burada (ve pratikte yalnız burada) gerçekten iş görür: iki üretilen
    # boyut varsa (kalite: bölüm + operatör) yakın olan önce gelir. Bugün hepsi hops=1
    # olduğu için sıralama manifest sırasına düşer — kural, katalog derinleştiğinde anlam
    # kazanmak üzere yazıldı ve o güne kadar davranışı değiştirmez.
    yerli = [x for x in dims if x["_ad"] not in uretilen]
    turev = sorted((x for x in dims if x["_ad"] in uretilen),
                   key=lambda x: uretilen[x["_ad"]].get("hops", 1))
    secilen = (yerli[:1] + turev[:1]) if turev else yerli[:2]
    for x in secilen:
        x.pop("_ad", None)

    return (secilen + meases[:2] + times[:1] + cmp_steps[:1])[:_MAX_NEXT_STEPS]


def recommend_actions(signals: list[dict], cube_query: dict, spec: dict | None) -> list[dict]:
    """K4 (karar motoru) — K3 SİNYALLERİNDEN aksiyon önerileri: her öneri ``{text, action?}``.
    trend/anomali/eşik → 'sürükleyeni bul' drill'i (K2 ``suggest_next_steps`` şekli:
    kullanılmayan ilk boyuta kır); yoğunlaşma → salt-metin. Deterministik (LLM yok); ilk 3.

    **`threshold` neden trend/anomali ile AYNI muameleyi görür** (2 Ağustos 2026, bütünsel
    denetimde ölçüldü): eşik ihlali sinyallerin **en aksiyon alınabiliridir** — kullanıcının
    KENDİ koyduğu sınır aşılmıştır — ama aksiyon chip'i üretmeyen **tek** sinyal oydu.
    Sistemin kendi bulduğu bir aykırılığa *"hangi makine sürüklüyor?"* derken, kullanıcının
    kendi kurduğu alarma sessiz kalmak tutarsızdı. Sorulacak soru ikisinde de aynı.

    `driver` **Faz B'den beri anlamlı**: `available_dimensions` adayları maliyet+güvene göre
    sıralar (kendi tablosundaki boyut önce, sonra sıçrama, sonra fan-out sertifikası) —
    yani "ilk kullanılmayan boyut" artık keyfi değil, **en ucuz ve en güvenilir** olandır.
    """
    used = list((cube_query or {}).get("dimensions") or [])
    # Aday sırası `drill.available_dimensions`'tan gelir: maliyet+güven sıralı (Faz B).
    # Burada `spec["dimensions"]`i doğrudan taramak, o sıralamayı ATLARDI ve "ilk boyut"
    # yine YAML beyan sırası olurdu — düzeltilen kusurun aynısı, ikinci bir yerde.
    from app.drill import available_dimensions

    driver = next((d["name"] for d in available_dimensions(spec or {}, cube_query or {})), None)
    dim_labels = (spec or {}).get("dimension_labels") or {}
    out: list[dict] = []
    seen: set[str] = set()
    for s in signals or []:
        kind = s.get("kind")
        if kind in ("trend", "anomaly", "threshold") and driver:
            dlabel = dim_labels.get(driver) or driver
            text = f"{dlabel} kırılımına bak — hangi {dlabel} bunu sürüklüyor?"
            if text in seen:
                continue
            seen.add(text)
            out.append({"text": text, "action": {
                "label": f"{dlabel} kırılımı", "kind": "dimension",
                "cube_query": {**cube_query, "dimensions": [*used, driver]}}})
        elif kind == "concentration" and "yog" not in seen:
            seen.add("yog")
            out.append({"text": "En yüksek kalemi ayrı incele — bağımlılık/risk."})
    return out[:3]


def parse_cube_query(text: str, index: dict) -> dict | None:
    """LLM'in ürettiği CubeQuery JSON'ını cube tanımına karşı DOĞRULAR.

    Sadece tanımlı cube/ölçü/boyut/zaman geçerlidir → LLM SQL/kolon halüsine edemez.
    Geçersiz/`cube:null` ise None (serbest SQL'e düşülür)."""
    import json

    try:
        cq = json.loads(text)
    except Exception:
        return None
    if not isinstance(cq, dict):
        return None
    cube = cq.get("cube")
    if not cube or cube not in index:
        return None
    spec = index[cube]
    measures = cq.get("measures") or []
    if not measures or any(m not in spec.get("measures", []) for m in measures):
        return None
    dims = cq.get("dimensions") or []
    if any(d not in spec.get("dimensions", []) for d in dims):
        return None
    tds = cq.get("timeDimensions") or []
    if any(td.get("dimension") not in spec.get("time_dimensions", []) for td in tds):
        return None
    filters = cq.get("filters") or []
    allowed_filter_dims = set(spec.get("dimensions", [])) | set(spec.get("time_dimensions", []))
    if any(f.get("dimension") not in allowed_filter_dims for f in filters):
        return None
    out: dict = {"cube": cube, "measures": measures}
    if dims:
        out["dimensions"] = dims
    if tds:
        out["timeDimensions"] = tds
    if filters:
        out["filters"] = filters
    # İsteğe bağlı sıralama/limit (konuşmasal düzenleme: "en düşük", "ilk 5") — doğrula.
    order = cq.get("order")
    if isinstance(order, dict) and order.get("measure") in spec.get("measures", []):
        d = str(order.get("direction") or "desc").lower()
        out["order"] = {"measure": order["measure"], "direction": "asc" if d.startswith("a") else "desc"}
    lim = cq.get("limit")
    if isinstance(lim, int) and 0 < lim <= 1000:
        out["limit"] = lim
    # CROSS-CUBE BLEND: ek cube ölçüleri (paylaşılan kırılım prev'den taşınır). Her blend
    # cube'u + ölçüsü kataloğa karşı DOĞRULANIR (halüsinasyon yok); geçersiz entry atlanır.
    blend_out = []
    for b in cq.get("blend") or []:
        bspec = index.get(b.get("cube"))
        if not bspec:
            continue
        bms = [m for m in (b.get("measures") or []) if m in bspec.get("measures", [])]
        if bms:
            blend_out.append({"cube": b["cube"], "measures": bms})
    if blend_out:
        out["blend"] = blend_out
    return out
