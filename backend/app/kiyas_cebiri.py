"""🔴 `G6` — **KIYAS CEBİRİ**: mutlak kıyası göreli kıyasa İNDİRGER.

## Motor zaten vardı — eksik olan CEBİRDİ

`app/yoy.py` bir dönemi geri kaydırıp iki seriyi birleştiriyor (`shift_period_back`:
`yoy` = −1 yıl, `mom` = −1 ay) ve `compare` alanı **uçtan uca** akıyor: `viz.py:395` ·
`report.py:56` · `dashboards.py:189,326` · `contribution.py:445` · chip yolu
(`cube_router.py:3631`). Yani *"mart'ı şubat ile kıyasla"* sorusunun cevabı için
**yeni bir motor gerekmiyor**: o soru zaten *"mart cirosu, `mom`"*tur.

Eksik olan tek şey, **iki uçlu** bir ifadeyi **göreli** bir ifadeye çevirecek cebirdi.

## Ölçülen kusur

`route()` iki dönem adını **tek aralığa çöküyor**: *"mart cirosunu şubat ile kıyasla"*
→ `gte 2026-02-01` + `lte 2026-03-31` → **1 Şubat–31 Mart TOPLAMI**. Kullanıcı kıyas
istedi, toplam aldı. (408 kıyas sorusunda **305**'i bu yoldan cevaplanıyordu.)

🔴 Ama o çöküş **geri döndürülebilir**: aralık tam olarak iki bitişik ayı kapsıyorsa,
uçları o iki ayın kendisidir. *Bir toplamın içinden parçaları çıkarmak, parçaların
toplamdan önce var olduğunu bilmeyi gerektirir — ve tarih aralığı bunu bilir.*

## FAIL-CLOSED: yalnız TAM temsil edilebileni indirger

| aralık | indirgeme | neden |
|---|---|---|
| Şubat + Mart | ✅ `mom` | bitişik ay — kaydırma **tam** |
| 2025 + 2026 | ✅ `yoy` | aynı dönem, bir yıl arayla |
| Ocak + Haziran | ❌ yok | 5 ay arayla; `mom` **yanlış** cevap verirdi |
| Mart + Mart'25 | ✅ `yoy` | aynı ay, bir yıl arayla |

İndirgenemeyen, **etiketli** kalır (`uyum` BEYAN-AÇIK). *Yaklaşık bir kıyas, kıyas
olmamaktan kötüdür: kullanıcı sayıya bakar, hangi iki dönemin kıyaslandığına bakmaz.*

## Neden AYRI MODÜL

`cube_router`'ın satır bütçesi muafiyet metninin kendi cümlesi: *"Yeni eşleştirme
kuralı bir **modüle** çıkar."* Bu bir eşleştirme kuralı bile değil — filtre listesi
üstünde bir **cebir**dir; sözlüğe, şemaya, katalog bilgisine hiç dokunmaz. Saf
fonksiyon olması testini de ucuzlatır: girdi bir liste, çıktı bir liste.
"""

from __future__ import annotations

import calendar
from datetime import date

from app.logging_setup import get_logger

_log = get_logger("kiyas_cebiri")


def _ay_sonu(y: int, a: int) -> date:
    return date(y, a, calendar.monthrange(y, a)[1])


def _uclar(filtreler: list[dict] | None, time_dim: str) -> tuple[date, date] | None:
    """Filtre listesindeki zaman aralığının iki ucu — yoksa `None`."""
    gte = lte = None
    for f in filtreler or []:
        if not isinstance(f, dict) or f.get("dimension") != time_dim:
            continue
        try:
            d = date.fromisoformat(str(f.get("value"))[:10])
        except (ValueError, TypeError):
            return None
        if f.get("operator") == "gte":
            gte = d
        elif f.get("operator") == "lte":
            lte = d
        else:
            return None      # eq/in gibi bir operatör: aralık değil, indirgeme tanımsız
    return (gte, lte) if gte and lte else None


def indirge(filtreler: list[dict] | None, time_dim: str = "tarih") -> tuple[list[dict], str] | None:
    """Çökmüş iki-dönem aralığını `(baz_filtreler, mode)` olarak geri açar.

    Döner `None` — indirgeme **tam** değilse. Bu bir başarısızlık değil bir **sınır**:
    indirgenemeyen soru `uyum` tarafından etiketlenir ve kullanıcı ne kaybettiğini görür.

    🔴 **Baz DAİMA geç olan dönemdir.** *"Mart'ı şubat ile kıyasla"* sorusunda merak
    edilen mart'tır; şubat referanstır. `yoy.compute` de bazı alıp **geriye** kaydırır —
    yani cebir motorun yönüyle aynı yöne bakmalıdır, yoksa değişim yüzdesinin **işareti**
    ters çıkar ve bu, en sessiz yanlış türüdür.
    """
    uc = _uclar(filtreler, time_dim)
    if not uc:
        return None
    gte, lte = uc
    if lte <= gte:
        return None
    digerleri = [f for f in (filtreler or [])
                 if not (isinstance(f, dict) and f.get("dimension") == time_dim)]

    # 1 · İKİ BİTİŞİK AY — "şubat ile mart"
    if gte.day == 1 and lte == _ay_sonu(lte.year, lte.month):
        ay_farki = (lte.year - gte.year) * 12 + (lte.month - gte.month)
        if ay_farki == 1:
            baz = date(lte.year, lte.month, 1)
            return digerleri + [
                {"dimension": time_dim, "operator": "gte", "value": baz.isoformat()},
                {"dimension": time_dim, "operator": "lte", "value": lte.isoformat()},
            ], "mom"
        # 2 · AYNI AY, BİR YIL ARAYLA — "mart 2025 ile mart 2026"
        if ay_farki == 12:
            baz = date(lte.year, lte.month, 1)
            return digerleri + [
                {"dimension": time_dim, "operator": "gte", "value": baz.isoformat()},
                {"dimension": time_dim, "operator": "lte", "value": lte.isoformat()},
            ], "yoy"

    # 3 · İKİ ARDIŞIK YIL — "2025 ile 2026"
    if (gte == date(gte.year, 1, 1) and lte == date(lte.year, 12, 31)
            and lte.year - gte.year == 1):
        return digerleri + [
            {"dimension": time_dim, "operator": "gte", "value": date(lte.year, 1, 1).isoformat()},
            {"dimension": time_dim, "operator": "lte", "value": lte.isoformat()},
        ], "yoy"

    # ⚠ Geriye kalan her şey — "ocak ve haziran", "2024 ile 2026", çeyrek karışımları —
    # indirgenmez. `mom` ya da `yoy` burada **yanlış** bir dönem kıyaslardı.
    return None


def ayikla(route_hit: dict | None) -> tuple[dict, str] | None:
    """`route_hit`'ten `(compare'sız cube_query, mode)` — kıyas yoksa `None`.

    🔴 **Neden `ask()` içinde değil:** `indirge` bir `compare` üretir ve o alanın ana
    cevap dalında **tüketicisi yoktu**. Buraya kadar gelip düz cube cevabına düşseydi
    sonuç *"Mart toplamı"* olur, `compare` sessizce yutulur ve üstelik `uyum` kapısı
    `compare` dolu diye ihlali **bastırırdı** — kapattığımız sessiz-yanlış sınıfının
    yeni bir örneği. *Bir alan üretmek, onu okuyan biri olmadan bir yetenek değil bir
    yalandır.*

    ⚠ Karar burada, **çağrı** `ask()`'te: `_kiyas_cevabi` bir kapanış (closure) ve
    gövdesi kopyalanamaz — kopyalansa iki dal zamanla ayrışırdı (bu deponun bir
    numaralı kusur sınıfı). Modüle çıkan şey *"kıyas var mı, bazı ne"* sorusudur;
    `ask()`'te kalan yalnız ÇAĞRI ve DÖNÜŞ (`app/typo_onerisi.py` deseni).
    """
    cq = (route_hit or {}).get("cube_query")
    if not isinstance(cq, dict) or not cq.get("compare"):
        return None
    baz = dict(cq)
    return baz, str(baz.pop("compare"))
