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


# ═══ REFERANS EKSENLERİ — kapalı sözlük, ve HER EKSENİN SAHİBİ YAZILI ═══════════
#
# 🔴 `G6.3`. Sözlük **doğumda kapanır**: bir ekseni sonradan eklemek, kaydedilmiş her
# `referans`'ın anlamını geriye dönük değiştirir — yani bir şema göçüdür. Beşini birden
# adlandırmak bedava; altıncıyı sonradan eklemek değil.
#
# ⚠ Ama **adlandırmak, derlemek değildir.** Bugün yalnız `donem`'in bir derleyicisi var;
# ötekilerin sahibi başka modüller ve onlar bir `referans` alanı beklemiyor. Bu tablo
# olmasaydı, ikinci bir sahip **fark edilmeden** doğardı:
#
# | eksen | bugünkü sahibi | derleyici |
# |---|---|---|
# | `donem` | **bu modül** (`indirge` + `referans_uret`) | ✅ |
# | `hedef` | `app/hedef.py` — beyan yolu, `ADR-0028` (*hedef UYDURULMAZ*) | ⊘ beyan |
# | `sabit` | eşik kıyası (`cube_router._measure_threshold`) | ⊘ filtre |
# | `butce` | `butce` **cube'u** — bir veri kaynağı, bir alan değil | ⊘ katalog |
# | `kohort` | yok (v2) | ⊘ |
#
# *Bir sözlüğü kapatmak ucuzdur; kapalı sanılan bir sözlüğü açmak pahalıdır.*
EKSEN_DONEM = "donem"
EKSEN_KOHORT = "kohort"
EKSEN_HEDEF = "hedef"
EKSEN_BUTCE = "butce"
EKSEN_SABIT = "sabit"

#: Tanınan eksenlerin tamamı — `referans.eksen` bunun dışına çıkamaz.
EKSENLER = (EKSEN_DONEM, EKSEN_KOHORT, EKSEN_HEDEF, EKSEN_BUTCE, EKSEN_SABIT)

#: 🔴 Bugün **derleyicisi olan** eksenler. `parse_cube_query` yalnız bunları geçirir:
#: derleyicisi olmayan bir ekseni kabul etmek, sorguyu kıyassız çalıştırıp cevabı
#: kıyasmış gibi sunmak olurdu — §6.1'in sessiz-yanlışı.
DERLENEN_EKSENLER = (EKSEN_DONEM,)


def _pencere(filtreler: list[dict] | None, time_dim: str) -> dict | None:
    """Zaman filtrelerinin `{gte, lte}` penceresi — iki uç da yoksa `None`."""
    p: dict = {}
    for f in filtreler or []:
        if isinstance(f, dict) and f.get("dimension") == time_dim and f.get("operator") in ("gte", "lte"):
            p[f["operator"]] = str(f.get("value"))[:10]
    return p if p.get("gte") and p.get("lte") else None


def referans_uret(filtreler: list[dict] | None, time_dim: str = "tarih") -> dict | None:
    """🔴 `G6.3` — kıyasın **İKİ UCUNU ADLANDIRIR**: `{eksen, kaynak, hedef}`.

    `indirge` bir **mod** döndürür (`yoy`/`mom`); mod, motorun ihtiyacı olan şeydir ama
    kullanıcının sorduğu şey değildir. *"Mart'ı şubatla kıyasla"* diyen biri `mom`
    duymaz — **iki dönem adı** duyar. Makbuz, `uyum` ve netleştirme o iki adı ister.

    ⚠ **`hedef` ucu ELLE HESAPLANMAZ, motorun kendi kaydırıcısından alınır**
    (`shift_period_back`). Alternatifi *"aralığın ön kısmı"* idi ve **ölçülüp elendi**:
    *"mart 2025 ile mart 2026"* çöküşünde ön kısım **12 aylık** bir penceredir, oysa
    SQL'in kıyasladığı şey mart 2025'tir. İkinci bir hesap, ilkiyle **ayrışan** bir
    etiket üretirdi — ve etiketle sayının ayrışması, sayının yanlış olmasından beterdir.

    Döner `None` — indirgenemeyen kıyasta. O soru `uyum` tarafından **etiketli** kalır.
    """
    ind = indirge(filtreler, time_dim)
    if not ind:
        return None
    baz, mod = ind
    kaynak = _pencere(baz, time_dim)
    if not kaynak:
        return None
    # ⚠ Modül-içi değil **fonksiyon-içi** import: `cube_router` bu modülü çağırıyor
    # (`parse_cube_query`), tersi modül düzeyinde olsaydı döngü olurdu. `app/yoy.py`
    # `mali_takvim`'i aynı sebeple böyle çağırıyor — desen kopyalanmadı, **izlendi**.
    from app import cube_router as cr

    hedef = _pencere(cr.shift_period_back(baz, mod, time_dim), time_dim)
    if not hedef:
        return None
    return {"eksen": EKSEN_DONEM, "kaynak": kaynak, "hedef": hedef}


def referans_dogrula(referans: object, time_dim: str = "tarih") -> dict | None:
    """Dışarıdan gelen (LLM / pano / istemci) bir `referans`'ı **derlenebiliyorsa** geçirir.

    🔴 **Derlenemeyen geçmez — ve bu, gevşeklik değil KATILIK.** Bir `referans`'ı taşıyıp
    `compare`'ını kuramamak, sorguyu **kıyassız** çalıştırıp cevabı kıyasmış gibi
    sunmaktır: kullanıcı iki dönem ister, tek sayı alır, üstelik makbuzda iki dönem adı
    görür. §6.1'in sessiz-yanlışının en ikna edici biçimi bu olurdu.

    ⚠ Bu yüzden `referans` ile `compare` **birlikte doğar ya da hiç doğmaz**. İkisi bir
    şeyin iki izdüşümüdür: biri insanın okuduğu (*"mart ↔ şubat"*), öteki motorun
    okuduğu (`mom`). *Bir çeviriden yalnız birini saklamak, çeviriyi kaybetmektir.*
    """
    if not isinstance(referans, dict) or referans.get("eksen") not in DERLENEN_EKSENLER:
        return None
    ref = {"eksen": referans["eksen"],
           "kaynak": referans.get("kaynak"), "hedef": referans.get("hedef")}
    return ref if referans_modu(ref, time_dim) else None


def referans_modu(referans: dict | None, time_dim: str = "tarih") -> str | None:
    """`{eksen, kaynak, hedef}` → `yoy`/`mom`; indirgenemezse `None`.

    🔴 `referans_uret`'in **tersidir** ve bilerek aynı kaydırıcıyı kullanır: bir çevirici
    çiftinin iki yönü farklı hesaplara dayanırsa, gidiş-dönüş bir gün **başka bir yere**
    varır. Burada varamaz — iki yön de `shift_period_back`'e soruyor.
    """
    if not isinstance(referans, dict) or referans.get("eksen") != EKSEN_DONEM:
        return None
    kaynak, hedef = referans.get("kaynak"), referans.get("hedef")
    if not isinstance(kaynak, dict) or not isinstance(hedef, dict):
        return None
    from app import cube_router as cr

    baz = [{"dimension": time_dim, "operator": op, "value": kaynak.get(op)}
           for op in ("gte", "lte") if kaynak.get(op)]
    if len(baz) != 2:
        return None
    for mod in ("mom", "yoy"):
        if _pencere(cr.shift_period_back(baz, mod, time_dim), time_dim) == {
                "gte": str(hedef.get("gte"))[:10], "lte": str(hedef.get("lte"))[:10]}:
            return mod
    return None


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
