"""Deterministik görselleştirme önerisi — grafik/tablo/pivot KARARI sonuç ŞEKLİNDEN.

Karar backend semantik katmanda (ADR-0024): kolonları veri-tipine sınıflar (N/O/Q/T —
Stevens ölçekleri), kanal atar (Bertin/expressiveness), Mackinlay "Show Me" tablosuyla mark
seçer, Cleveland–McGill algısal sıralamasına uyar. LLM yok — saf kural, tekrarlanabilir.
Gerekçe + kaynaklar: docs/research/viz-oneri-standartlari-2026-07.md.

SUNUM (echarts option, renk, soluk sütun, responsive, kullanıcı override/toggle) FE'de KALIR;
burası yalnız TİP + ROL üretir (`VizSpec`). FE `data.viz` gelince yerel `analyze()` yerine bunu
kullanır; `view_hint` (açık NL niyeti) + kullanıcı toggle bu otomatik kararın ÜSTÜNE biner.

İki katman:
  • analyze()   — sonuç ŞEKLİNDEN taban karar (kpi/bar/line/heatmap/facet/table). FE chart.ts
                  analyze()'in birebir portu; mevcut davranışı KORUR (regresyonsuz geçiş).
  • recommend() — analyze üstüne STANDART katmanı: veri-tipi + BİRİM farkındalığı ile yeni mark'lar
                  (facet_measure / scatter / stacked / pivot) ve çok-birim politikası (§3).

KOPYA-MANTIK DURUMU (31 Temmuz 2026 — bağımsız araştırmayla denetlendi, `docs/research/
viz-chart-drift-2026-07-31.md` YERİNE burada özetlendi): chart.ts'in yerel `analyze()`'i BU
dosyanın `analyze()`'iyle hâlâ birebir eşdeğer (drift YOK) ama `recommend()`'in zenginleştirme
katmanını (scatter/facet_measure/stacked/pivot/partition) HİÇ taşımıyor — yani FE yereline
her düştüğünde kullanıcı GERÇEKTEN daha zayıf bir karar görüyor (varsayımsal değil, ölçüldü).
Kapatılan iki canlı tetikleyici: (1) `/ask`'in `_attach_viz`'i artık gerçek units/lower_set
kullanıyor + `recommend()` patlarsa None yerine çıplak `analyze()`'e düşüyor (ask.py), (2)
sohbet resume'i (`/conversations/{id}`) artık `viz`'i HER seferinde TAZE hesaplıyor (`result`
sabit kalır, yalnız sunum kararı yenilenir) — önceden donmuş/eski bir `viz` kalıcı olarak FE
yereline zorluyordu. KASITLI OLARAK AÇIK bırakılan TEK durum: `ResultView.tsx`'in facet
tek-panel drill-down'ı (kullanıcı bir facet panelini açtığında o ALT-KÜME satır için yerel
`analyze()` çağrılır) — backend bu ad-hoc alt-kümeyi hiç görmediğinden (yalnız tam sonuç
kümesi için `viz` hesaplanır) burada yerel bir yeniden-sınıflandırma mimari olarak gerekli;
bilinçli, dar kapsamlı bir istisna (genel bir "yedek" değil) — bkz. chart.ts'teki eşlenik not.
"""

from __future__ import annotations

from app.logging_setup import get_logger

import re
from typing import Any

# --- veri-tipi sinyalleri (Stevens ölçekleri) -------------------------------
# SÜREKLİ zaman (trend → çizgi). "gün/vardiya" gibi DÖNGÜSEL kategorikler kasıtlı YOK.
_TIME_NAMES = {
    "donem", "dönem", "tarih", "ay", "hafta", "period",
    "yil", "yıl", "year", "ceyrek", "çeyrek",
}
_log = get_logger("viz")

_DATEISH = re.compile(r"^\d{4}-\d{2}")
# Sıralı (ordinal) kategori kümeleri — çizgi/sıralama bunlarda anlamlı (N'de değil).
_WEEKDAY = {"pzt", "sal", "çar", "car", "per", "cum", "cmt", "paz"}
_SIZES = {"xs", "s", "m", "l", "xl", "xxl"}

# İNTENSİF (yoğunluk/oran) ölçüler additive DEĞİLDİR → yığma/pay grafiği YANLIŞ olur
# (ortalama %'leri toplamak anlamsız). Birim "%" ya da ad deseni oran/ortalama ise intensif.
_INTENSIVE_NAME = re.compile(r"(_yuzde|_orani?|_ort|_oran|oee|verimlilik|haslik|_de|yogunluk)$", re.I)
# Birim yedeği (schema()'nın "units" dict'i yoksa) — kaba eşleme; gerçek birim MDL'den gelir.
_UNIT_RX: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(_yuzde$|_orani?$|oee|haslik|verimlilik)", re.I), "%"),
    (re.compile(r"(tl$|_tl_|_tl$|ciro|maliyet|tutar|fiyat|gelir|gider|bakiye|kar$|karlilik)", re.I), "₺"),
    (re.compile(r"(_kg$|agirlik|tonaj|fire_kg)", re.I), "kg"),
    (re.compile(r"(kwh|elektrik)", re.I), "kWh"),
    (re.compile(r"(_l$|litre|_su_|water)", re.I), "L"),
    (re.compile(r"(_dk$|dakika|sure|durus)", re.I), "dk"),
    (re.compile(r"tep$", re.I), "tep"),
]


def _is_num(v: Any) -> bool:
    """Gövdesi `app/result_shape.py`'de (Faz C2). Eskiden Türkçe ondalık virgülünü
    (`"1,5"`) REDDEDİYORDU; `interpret` kabul ediyordu — yüklenen Türkçe CSV'de aynı kolon
    bir motorda ölçü, diğerinde kategoriydi."""
    from app.result_shape import is_num

    return is_num(v)


def _looks_date(v: Any) -> bool:
    return isinstance(v, str) and bool(_DATEISH.match(v))


def _card(rows: list[dict], c: str) -> int:
    """Bir kolonun ayrık (distinct) değer sayısı."""
    seen: set = set()
    for r in rows:
        try:
            seen.add(r.get(c))
        except TypeError:
            seen.add(str(r.get(c)))
    return len(seen)


def _unit_of(col: str, units: dict[str, str] | None) -> str:
    """Ölçünün birimi: MDL metadata (schema()'nın "units" dict'i) öncelik, yoksa regex yedeği,
    yoksa boş (birimsiz/sayım). Boş birim de AYRI birim sayılır (çok-birim kuralı için)."""
    if units and col in units and units[col]:
        return str(units[col])
    for rx, u in _UNIT_RX:
        if rx.search(col):
            return u
    return ""


def _additive(col: str, unit: str, beyan_edilmeyen: set[str] | None = None) -> bool:
    """Ölçü toplanabilir (extensive) mi? Yığma/pay grafiği YALNIZ additive'de geçerlidir.

    **BEYAN, SEZGİYİ EZER** (Faz I1). Cube metadata'sı `additive: full|semi|non` bildirir ve
    `schema()` bunu `semi_additive`/`non_additive` listeleri olarak ZATEN taşıyordu — ama
    `recommend()` onları hiç ALMIYOR, yerine bir ad/birim regex'i kullanıyordu.

    Ölçülen sessiz-yanlış (2 Ağustos 2026): `bakiye` iki cube'da (`cari`, `mizan`)
    `additive: semi` beyan edilmiş; birimi `₺` olduğu için regex ona `additive=True` diyor
    ve **yığılmış grafik öneriliyordu**. Bakiye bir STOK büyüklüğüdür: dönemler arasında
    toplanamaz (Ocak bakiyesi + Şubat bakiyesi bir şey ifade etmez). Yığma, matematiksel
    olarak yanlış bir grafiği "deterministik" rozetiyle sunardı.

    Regex YEDEK olarak kalır: beyan edilmemiş ölçüler (henüz `additive:` yazılmamış
    cube'lar) için bugünkü davranış korunur — beyanı olmayanı yasaklamak, ölçmeden
    kısıtlama getirmek olurdu.
    """
    if beyan_edilmeyen and col in beyan_edilmeyen:
        return False          # BEYAN: semi/non-additive → yığma/pay YASAK
    if unit == "%":
        return False
    return not bool(_INTENSIVE_NAME.search(col))


# FE ChartKind ile hizalı. "table" = FE'nin "none"u (grafik değil → tablo).
VizKind = str


def analyze(
    columns: list[str],
    rows: list[dict],
    dim_cols: set[str] | None = None,
    time_col_hint: str | None = None,
    measure_cols: set[str] | None = None,
) -> dict[str, Any]:
    """chart.ts analyze()'in portu — sonuç şeklinden TABAN viz kararı.

    Döndürür: {kind, measures, dims, time_col, primary_dim, heat, heat_any, facet}.
    recommend() bunun üstüne standart katmanını uygular.

    Rol OTORİTESİ (opsiyonel): `dim_cols`/`time_col_hint` cube_query'den geldiğinde BOYUT
    kolonları kesindir → (a) sayısal-değerli boyutlar (vardiya no, yıl) yanlışlıkla ölçü sanılmaz,
    (b) türetilmiş ölçüler (YoY `_gecen`/`_degisim_yuzde` gibi cube_query.measures'ta OLMAYAN ama
    sayısal kolonlar) doğru şekilde ÖLÇÜ sayılır, (c) zaman kovaları (tarih__month) kaçmaz. Boyut
    olmayan sayısal kolon = ölçü; boyut olmayan sayısal-olmayan kolon = boyut (güvenli). Verilmezse
    (yüklenen serbest veri) değer biçiminden çıkarıma düşülür (FE analyze() paritesi)."""
    # ROL ATAMASI TEK KAYNAKTAN (Faz C1): `app/result_shape.py`. Eskiden burada ve
    # `interpret._classify`'de İKİ BAĞIMSIZ uygulama vardı ve ölçülen iki vakada
    # ayrışıyorlardı (`ay`=1..12 → burada boyut, orada ÖLÇÜ; `gun`="Pzt" → orada zaman
    # ekseni, burada değil). Aynı cevapta grafik ile altındaki cümle farklı şey anlatıyordu
    # ve ikisi de "deterministik" rozetliydi.
    from app.result_shape import classify as _rol

    measures, dims, time_col = _rol(columns, rows, dim_cols=dim_cols,
                                    measure_cols=measure_cols,
                                    time_col_hint=time_col_hint)

    heat: dict[str, str] | None = None
    if len(dims) >= 2 and len(measures) >= 1 and len(rows) >= 4:
        for i in range(len(dims)):
            if heat:
                break
            for j in range(i + 1, len(dims)):
                if heat:
                    break
                ca = _card(rows, dims[i])
                cb = _card(rows, dims[j])
                prod = ca * cb
                if (
                    ca > 1 and cb > 1 and min(ca, cb) >= 3
                    and prod <= len(rows) * 1.6 and prod >= len(rows) * 0.5
                ):
                    heat = (
                        {"row": dims[i], "col": dims[j]} if ca <= cb
                        else {"row": dims[j], "col": dims[i]}
                    )

    heat_any: dict[str, str] | None = heat
    if not heat_any and len(dims) >= 2 and len(measures) >= 1:
        multi = sorted(
            [d for d in dims if _card(rows, d) > 1], key=lambda d: _card(rows, d)
        )
        if len(multi) >= 2:
            heat_any = {"row": multi[0], "col": multi[-1]}

    if time_col is not None:
        primary_dim: str | None = time_col
    elif dims:
        primary_dim = sorted(dims, key=lambda d: _card(rows, d), reverse=True)[0]
    else:
        primary_dim = None

    facet: dict[str, str] | None = None
    if len(dims) == 3 and len(measures) >= 1:
        if time_col:
            rest = sorted(
                [d for d in dims if d != time_col], key=lambda d: _card(rows, d)
            )
            a, b = rest[0], rest[1]
            if _card(rows, a) <= 6:
                facet = {"dim": a, "x": time_col, "series": b}
        else:
            srt = sorted(dims, key=lambda d: _card(rows, d))
            fd, sd, xd = srt[0], srt[1], srt[2]
            if _card(rows, fd) <= 6:
                facet = {"dim": fd, "x": xd, "series": sd}

    kind: VizKind = "table"
    if len(rows) == 1 and len(measures) >= 1 and len(dims) <= 1:
        kind = "kpi"
    elif len(measures) == 0:
        kind = "table"
    elif len(dims) == 3 and facet:
        kind = "facet"
    elif len(dims) > 2:
        kind = "table"
    elif time_col and len(measures) >= 1:
        kind = "line"
    elif heat:
        kind = "heatmap"
    elif primary_dim and len(measures) >= 1:
        kind = "bar"

    return {
        "kind": kind,
        "measures": measures,
        "dims": dims,
        "time_col": time_col,
        "primary_dim": primary_dim,
        "heat": heat,
        "heat_any": heat_any,
        "facet": facet,
    }


# --- STANDART KATMAN: veri-tipi + birim farkındalığı ------------------------

def _roles_from_cube_query(
    cube_query: dict | None, columns: list[str]
) -> tuple[set[str] | None, str | None]:
    """cube_query'den OTORİTER BOYUT kolonları + zaman kolonu. Boyutları (measures'ı DEĞİL)
    otoriter alırız: boyut olmayan sayısal kolon = ölçü. Böylece (a) sayısal boyutlar (vardiya no)
    boyut kalır, (b) türetilmiş ölçüler (YoY `_gecen`/`_degisim_yuzde` — cube_query.measures'ta
    YOK ama sayısal) doğru şekilde ölçü sayılır → YoY grafiği yanlışlıkla panel/facet'e düşmez.
    timeDimensions kovası `{dimension}__{granularity}` kolon adına çözülür (boyut + zaman ipucu)."""
    if not cube_query:
        return None, None
    colset = set(columns)
    dim_cols = {d for d in (cube_query.get("dimensions") or []) if d in colset}
    time_hint: str | None = None
    for td in (cube_query.get("timeDimensions") or []):
        dim = td.get("dimension")
        gran = td.get("granularity")
        for cand in (f"{dim}__{gran}" if gran else None, dim):
            if cand and cand in colset:
                time_hint = cand
                dim_cols.add(cand)
                break
        if time_hint:
            break
    return dim_cols, time_hint


# Şelale toplam denetiminin GÖRECELİ toleransı. Kayan nokta aritmetiği birebir eşitlik
# vermez (0.1+0.2 != 0.3); mutlak eşik ise ölçek değişince anlamını yitirir
# (₺15.576.000 ile %2,3 aynı eşiği paylaşamaz).
WATERFALL_TOLERANS = 1e-6


def waterfall_spec(*, baslangic: float, bilesenler: list[tuple[str, float]],
                   bitis: float, birim: str = "",
                   tolerans: float = WATERFALL_TOLERANS) -> dict[str, Any] | None:
    """ŞELALE grafiği — **yalnız ARTIKSIZ bir ayrışmada doğrudur** (Faz I2).

    ## Seçim kuralı (her yeni tür bir kuralla gelir)

    Şelale, bir başlangıç değerinden bir bitiş değerine giden yolu **bileşenlere** böler.
    Görselin tüm anlamı şudur: *"bu çubukları üst üste koyarsan sondaki değere varırsın."*
    Bileşenler toplamı bitişe varmıyorsa **grafik yalan söyler** — çubuklar bir yere
    çıkar, eksen başka bir yeri gösterir ve okuyan farkı göremez.

    Bu yüzden kural bir tercih değil bir **KAPIDIR**: toplam tutmuyorsa `None` döner ve
    çağıran tabloya düşer. `viz.py`'nin varlık sebebi (ADR-0024) *"grafik kararı
    deterministik ve doğrulanabilir olsun"*dur; toplamı denetlemeyen bir şelale o sebebi
    çürütürdü.

    **PVM tam olarak bu koşulu sağlar** ve `test_pvm_ARTIKSIZ` ile kilitlidir:
    `fiyat + miktar + birleşik = net_degisim` (birebir). Şelalenin ilk gerçek tüketicisi
    bu yüzden PVM'dir — matematiği Faz 5.1'de yazılmış ama **görseli olmayan** bir özellik.
    """
    if not bilesenler:
        return None
    toplam = sum(v for _, v in bilesenler)
    beklenen = bitis - baslangic
    olcek = max(abs(beklenen), abs(bitis), abs(baslangic), 1.0)
    if abs(toplam - beklenen) / olcek > tolerans:
        _log.info("şelale REDDEDİLDİ: bileşen toplamı %.6g, beklenen %.6g — artık var, "
                  "grafik yalan söylerdi", toplam, beklenen)
        return None
    return {
        "kind": "waterfall",
        "start": {"label": "önceki", "value": baslangic},
        "steps": [{"label": ad, "value": v} for ad, v in bilesenler],
        "end": {"label": "şimdi", "value": bitis},
        "unit": birim,
        # Okuyan toplayabilsin diye net değişim AYRICA yazılır — grafiğin iddiası budur.
        "net": beklenen,
    }


def meta_args(cube_meta: dict | None) -> dict[str, Any]:
    """Cube metadata'sından `recommend()`'in beslendiği argümanlar — **TEK KAYNAK** (Faz I1).

    Altı çağrı yeri var (`/ask` iki kez, `/report`, `dashboards`, `schedules`,
    `conversations`) ve her biri argümanları ELLE topluyordu. Sonuç ölçüldü: `units`
    anahtarı bir yerde `measure_units` diye yanlış yazılmış ve birim-farkındalığı o yolda
    HİÇ devreye girmemişti (kod yorumunda kayıtlı). Aynı sınıfın ikinci örneği
    `semi_additive`/`non_additive` oldu — `schema()` üretiyordu, hiçbir çağıran
    geçirmiyordu.

    Yeni bir metadata alanı görselleştirmeye bağlandığında **tek bir yer** değişir;
    beşinci çağıranı unutmak imkânsız hale gelir.
    """
    c = cube_meta or {}
    return {
        "units": c.get("units") or {},
        "lower_set": c.get("lower_is_better") or [],
        # Toplanamaz ölçüler: yığma/pay grafiği matematiksel olarak yanlış olur.
        "non_additive": (c.get("semi_additive") or []) + (c.get("non_additive") or []),
        # FAZ 2.5 — hedef beyanları. Buraya eklemek, ALTI çağrı yerinin hiçbirine
        # dokunmadan hepsinin hedefi görmesini sağlar; bu fonksiyonun var olma sebebi
        # tam olarak budur (bir alanın beşinci çağıranını unutmak imkânsız olsun diye).
        "hedefler": c.get("hedefler") or {},
    }


def recommend(
    result: dict | None,
    units: dict[str, str] | None = None,
    lower_set: list[str] | set[str] | None = None,
    cube_query: dict | None = None,
    non_additive: list[str] | set[str] | None = None,
    # FAZ 2.5 — `{ölçü: hedef}`. `units`/`lower_set` ile **aynı** parametre deseni:
    # şema burada okunmaz, çağıran verir (viz saf kalır, test edilebilirliği bozulmaz).
    hedefler: dict[str, float] | None = None,
    # 🔴 FAZ 5.12 — İÇGÖRÜ PAKETİ. Dönüş sözleşmesi artık **`VizSpec | list[VizSpec]`**:
    # `paket=False` (varsayılan) → **bugünkü sözlük, bayt bayt**; `paket=True` →
    # `list[VizSpec]`. *Tekil dönüş her zaman geçerlidir* — geriye uyumluluk bir vaat
    # değil, imzanın kendisidir.
    # ⚠ Bayrak burada çözülmez: `viz` saf kalır ve `lab/` araçları iki hâli de koşabilir.
    paket: bool = False,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    """QueryResult ({columns, rows}) → VizSpec. Sonuç yok/boşsa None.

    analyze() taban kararını alır, üstüne Show Me + çok-birim politikasını (§3) uygular:
      • ≥3 farklı birim ölçü + ortak eksen → facet_measure (ölçüye-göre small multiples)
      • 2 birim → dual_axis (FE combo zaten böler)
      • 2 ölçü + kimlik-boyutu (kard=satır, ≥8) + zamansız → scatter (korelasyon)
      • zaman/kategori + orta-kard additive seri → stacked
      • 2+ kategorik boyut grafiklenemiyor → pivot
      • tek boyut + additive ölçü → partition (pie≤6 / treemap) FE toggle olarak sunulur
      • tek boyut (kard≥4) + tek ölçü → reference_line (ortalama, aynı bar grafiğinde)
    """
    if not result:
        return None
    columns = result.get("columns") or []
    rows = result.get("rows") or []
    if not columns:
        return None

    dim_cols, time_hint = _roles_from_cube_query(cube_query, columns)
    # `§VZ` — ölçü otoritesi TEK SAHİPTEN (`result_shape`); ikinci bir türetme `KAT-1` olurdu.
    from app.result_shape import measure_authority as _olcu_otoritesi

    spec = analyze(columns, rows, dim_cols=dim_cols, time_col_hint=time_hint,
                   measure_cols=_olcu_otoritesi(cube_query))
    measures: list[str] = spec["measures"]
    dims: list[str] = spec["dims"]
    time_col: str | None = spec["time_col"]
    primary_dim: str | None = spec["primary_dim"]

    umap = {m: _unit_of(m, units) for m in measures}
    # BEYAN EDİLMİŞ toplanamaz ölçüler (semi/non-additive) — yığma ve pay grafiği YASAK.
    # Türetilmiş kıyas kolonları da (`bakiye_gecen`) aynı kısıtı miras alır: bir stok
    # büyüklüğünün geçen dönemi de stok büyüklüğüdür.
    _yasak = {str(m) for m in (non_additive or [])}
    _yasak |= {f"{m}_gecen" for m in _yasak}
    unit_count = len({u for u in umap.values()})
    cat_dims = [d for d in dims if d != time_col]
    # bar/line'da renk-serisi: ikinci (zaman-dışı) boyut
    shared_x = time_col or (primary_dim if len(dims) == 1 else None)
    series_dim = next((d for d in dims if d != shared_x), None) if shared_x else None
    # DÖNEMSEL KIYAS (YoY/MoM): türetilmiş ölçüler (baz + `_gecen` + `_degisim_yuzde`) bir
    # KIYAS AİLESİDİR — birbirinden bağımsız ölçü değil. Enhancement katmanı (scatter/facet_measure/
    # pivot/partition) bunları YANLIŞ yorumlar (ciro vs ciro_gecen serpme, YoY bar'a pie önerisi).
    # Kıyas varsa taban kararı (bar/line combo) KORUNUR; FE combo `_gecen` soluk sütun +
    # `_degisim_yuzde` ikincil çizgi olarak render eder.
    has_compare = bool(cube_query and cube_query.get("compare")) or any(
        m.endswith(("_gecen", "_degisim_yuzde")) for m in measures
    )

    spec.update({
        "units": umap,
        "unit_count": unit_count,
        "series_dim": series_dim,
        "facet_measure": None,
        "scatter": None,
        "pivot": None,
        "stackable": False,
        "partition": False,
        "dual_axis": False,
        "reference_line": None,
        "alternatives": [],
        "table_mode": "table",
    })

    kind = spec["kind"]

    # (A) SCATTER (korelasyon): 2+ ölçü, zaman yok, TEK kimlik-boyutu (kard=satır) yüksek kard.
    #     Az kategoride (≤~12) gruplu bar daha okunur; çok varlıkta (≥8) 2-ölçü serpme daha iyi.
    #     Çok-birim (B) küçük-multiple'dan ÖNCE bakılır: kimlik-boyutu paylaşılan-eksen DEĞİL,
    #     nokta kimliğidir → korelasyon serpmesi doğru mark (small multiples değil).
    if (
        kind in ("bar", "table")
        and not has_compare
        and time_col is None
        and len(measures) >= 2
        and len(cat_dims) == 1
        and _card(rows, cat_dims[0]) == len(rows)
        and len(rows) >= 8
    ):
        spec["kind"] = kind = "scatter"
        sc = {"x": measures[0], "y": measures[1], "color": cat_dims[0]}
        if len(measures) >= 3:
            sc["size"] = measures[2]
        spec["scatter"] = sc

    # (B) ÇOK-BİRİM (§3): tek/çift eksende yalnız 1-2 birim; ≥3 → ölçüye-göre small multiples.
    #     Yalnız TEK kategorik/zaman eksende çok-ölçü senaryosunda (seri boyutu YOKKEN) geçerli —
    #     seri boyutu varsa ölçü zaten teke düşer (iki seri kaynağı bir arada olmaz).
    multi_measure_x = kind in ("bar", "line") and shared_x is not None and series_dim is None
    if multi_measure_x and len(measures) >= 2:
        if unit_count >= 3 and not has_compare:
            spec["kind"] = kind = "facet_measure"
            spec["facet_measure"] = {"measures": measures, "x": shared_x, "series": None}
        elif unit_count == 2:
            # BİLİNÇLİ KARAR (Madde 10 değerlendirmesi, 1 Ağustos 2026): bu bayrak FE'de
            # OKUNMUYOR (chart.ts yalnız parse eder, hiçbir yerde tüketmez) — FE kendi
            # `comboSeriesDim` sezgisiyle (series_dim YOKKEN) AYNI durumu BAĞIMSIZ tespit
            # edip birincil-bar+ikincil-çizgi kombosunu ZATEN doğru üretiyor (chart.ts'teki
            # "KOMBO" bloğu). Bilgi doğru/zararsız — kaldırmak public viz sözleşmesini
            # (AskResponse.viz) gereksiz kırar; entegre etmek FE'de zaten çalışan combo
            # mantığını YENİDEN İCAT etmek olurdu. Bilerek dokunulmuyor.
            spec["dual_axis"] = True
    elif (
        kind in ("bar", "line") and shared_x is not None and series_dim is not None
        and len(measures) >= 2 and unit_count >= 2 and not has_compare
    ):
        # Madde 10 (1 Ağustos 2026): kırılım boyutu (series_dim) VARKEN çok-birim ölçüler
        # ÖNCEDEN HİÇBİR ayırma mekanizmasından geçmiyordu — combo (chart.ts) VE dual_axis
        # (yukarıdaki dal) İKİSİ de `series_dim is None` şartıyla sınırlıydı; kırılımlı
        # 2+-birim durumu (ör. "ay VE makine bazında oee ve duruş dakikası") iki farklı
        # birimi TEK eksende eziyordu. Var olan facet_measure (ölçüye-göre panel) diline
        # `series` alanını doldurarak GENİŞLETİLİYOR — yeni bir görsel dil İCAT edilmiyor.
        spec["kind"] = kind = "facet_measure"
        spec["facet_measure"] = {"measures": measures, "x": shared_x, "series": series_dim}

    # (C) STACKED (kompozisyon): x (zaman/kategori) + renk-serisi + TEK additive ölçü.
    #     Az seri (≤4) → gruplu (doğrudan kıyas okunur); orta seri (5..8) additive → yığılı.
    if kind in ("bar", "line") and series_dim is not None and len(measures) == 1:
        m0 = measures[0]
        if _additive(m0, umap.get(m0, ""), _yasak):
            spec["stackable"] = True
            sc_card = _card(rows, series_dim)
            if 4 < sc_card <= 8:
                spec["kind"] = kind = "stacked"

    # (D) PIVOT: 2+ kategorik boyut grafiklenemiyor (heatmap değil / çok-ölçü), ya da 3+ boyut
    #     facet'lenemedi. Eski "table"yı okunur satır×sütun×hücre yapısına yükseltir.
    if not has_compare and (
        (kind == "table" and len(cat_dims) >= 2 and len(measures) >= 1)
        or (kind == "heatmap" and len(measures) >= 2)
    ):
        srt = sorted(cat_dims, key=lambda d: _card(rows, d))
        rows_dim = [srt[0]] if len(srt) >= 1 else []
        cols_dim = [srt[1]] if len(srt) >= 2 else []
        spec["kind"] = kind = "pivot"
        spec["table_mode"] = "pivot"
        spec["pivot"] = {"rows": rows_dim, "cols": cols_dim, "measures": measures}

    # (E) PARTITION (pay): TEK kategorik boyut + TEK additive ölçü → pie(≤6)/treemap FE toggle olarak.
    #     Cleveland–McGill: pay grafiği bar'dan zayıf → OTOMATİK bar KALIR, pay yalnız öneri/hint.
    #     Tek ölçü şartı: çok-ölçü/YoY bar'da pay grafiği anlamsız (birden çok ölçünün payı olmaz).
    if kind == "bar" and len(cat_dims) == 1 and len(measures) == 1 and series_dim is None:
        m0 = measures[0]
        if _additive(m0, umap.get(m0, ""), _yasak):
            card = _card(rows, cat_dims[0])
            spec["partition"] = True
            spec["alternatives"] = ["pie"] if card <= 6 else ["treemap"]

    # (F) REFERANS ÇİZGİSİ (Madde 11 kalan kısım, §E, 1 Ağustos 2026): TEK kategorik boyut +
    #     TEK ölçü + orta-yüksek kardinalite (kişi/varlık bazlı karşılaştırma — "personelin
    #     OEE üzerindeki etkisi" gibi) → ölçünün ORTALAMASI yatay referans çizgisi olarak AYNI
    #     bar grafiğinde. Kim ortalamanın üstünde/altında ANINDA görülür — Cleveland-McGill'i
    #     bozmaz (bar KALIR), yalnız bir ANNOTASYON ekler. `_additive` şartı YOK (yüzde/oran
    #     ölçülerin de ortalaması anlamlıdır — additive yalnız TOPLAMA/yığma için gerekli, sade
    #     ORTALAMA için değil). 2+ ölçü durumu (İKİNCİL ölçü referans) mevcut combo (chart.ts)
    #     mekanizmasınca ZATEN karşılanıyor — bu yalnız TEK-ölçü boşluğunu kapatır.
    if kind == "bar" and len(cat_dims) == 1 and len(measures) == 1 and series_dim is None:
        m0 = measures[0]
        card = _card(rows, cat_dims[0])
        if card >= 4:
            vals = [r.get(m0) for r in rows if _is_num(r.get(m0))]
            if vals:
                # 🔴 FAZ 2.5 — HEDEF UYDURULMAZ. Beyan varsa çizgi **hedeftir**; yoksa
                # bugünkü davranış BİREBİR korunur (ortalama, `Ort.` etiketiyle).
                # *"Hedef yok" ile "hedef 0" asla karıştırılmaz.*
                _h = (hedefler or {}).get(m0)
                spec["reference_line"] = {
                    "kind": "target" if _h is not None else "average", "measure": m0,
                    "value": _h if _h is not None
                    else round(sum(float(v) for v in vals) / len(vals), 4),
                }

    # 🔴 FAZ 5.11 — **NE ZAMAN GRAFİK ÇİZİLMEZ** (§15.6). Dört kural, **en sonda**.
    _cizme_kurallari(spec, rows, cat_dims, measures, time_col, cube_query)

    # normalize: lower_set'i (FE ısı paleti yönü) taşı
    if lower_set:
        spec["lower_set"] = sorted(lower_set)
    # 🔴 FAZ 5.12 — **`VizSpec | list[VizSpec]`**. Tekil dönüş **her zaman geçerli**:
    # `paket=False` (varsayılan) bugünkü sözlüğü **bayt bayt** döndürür.
    return paket_ac(spec, rows, cat_dims, time_col, measures) if paket else spec


#: FAZ 5.12 — paketteki azami görsel. ⚠ Üçten fazlası bir **paket** değil bir **yığın**dır:
#: kullanıcı hangisine bakacağını bilemez ve paket, tek kartın yaptığı işi de bozar.
_MAX_PAKET = 3


def paket_ac(spec: dict[str, Any], rows: list[dict], cat_dims: list[str],
             time_col: str | None, measures: list[str]) -> list[dict[str, Any]]:
    """FAZ 5.12 — **İÇGÖRÜ PAKETİ**: aynı sonucun **birden çok ekseni**. [bayrak: `ui_icgoru_paketi`]

    ## 🔴 YENİ MOTOR YAZILMAZ

    Paketin her üyesi `recommend()`'in **zaten hesapladığı** bir karardan doğar
    (`partition` · `pivot` · `facet_measure` · `reference_line`). Bu fonksiyon bir
    **seçim** yapar, bir analiz değil — *ikinci bir görsel dilbilgisi yazmak, birincinin
    kararlarını sessizce ezerdi.*

    ## "Neden bu eksende" — her üye kendi gerekçesini taşır

    `neden` alanı bir **süs değil bir sözleşmedir**: bir paket üyesi neden orada
    olduğunu söyleyemiyorsa, o üye **gürültüdür**. Kapı her üyenin `neden` taşımasını
    zorlar.

    ## ⚠ Paket ASLA daraltılmış kararı ezmez

    §15.6 (FAZ 5.11) *"grafik çizilmez"* dediyse (`cizilmedi` dolu), paket **tek üyeli**
    kalır: aksi hâlde *"bu veri grafiğe uygun değil"* diyen bir karar, üç grafik
    önererek kendi kendini çürütürdü.
    """
    ilk = {**spec, "neden": _neden(spec, cat_dims, time_col, measures)}
    if spec.get("cizilmedi"):
        return [ilk]
    paket: list[dict[str, Any]] = [ilk]

    # (1) PAY GRAFİĞİ — `partition` zaten hesaplandı; paket onu ayrı bir üye yapar.
    if spec.get("partition") and spec.get("alternatives"):
        alt = str(spec["alternatives"][0])
        paket.append({**spec, "kind": alt, "partition": False, "alternatives": [],
                      "neden": f"Payları görmek için: tek boyut, toplanabilir ölçü "
                               f"({len(rows)} kalem)."})

    # (2) ZAMAN EKSENİ — kategori kararı verilmişse ve zaman da varsa, ikinci eksen
    # gerçekten **başka bir soruyu** cevaplar ("kim" ↔ "ne zaman").
    if time_col and cat_dims and spec.get("kind") in ("bar", "stacked"):
        paket.append({**spec, "kind": "line", "primary_dim": time_col,
                      "partition": False, "alternatives": [],
                      "neden": "Zaman ekseni ayrı bir soruyu cevaplar: *kim* değil "
                               "*ne zaman*."})

    # (3) PİVOT — iki kategorik boyut varken tablo, grafiğin göremediğini gösterir.
    if len(cat_dims) >= 2 and spec.get("pivot"):
        paket.append({**spec, "kind": "pivot", "table_mode": "pivot",
                      "partition": False, "alternatives": [],
                      "neden": "İki kırılım birlikte: grafik ikisini aynı anda "
                               "okunur kılamaz, çapraz tablo kılar."})
    return paket[:_MAX_PAKET]


def _neden(spec: dict[str, Any], cat_dims: list[str], time_col: str | None,
           measures: list[str]) -> str:
    """*"Neden bu eksende"* — **karardan türetilir, uydurulmaz**.

    ⚠ Metin `recommend()`'in kendi dallarının gerekçesidir; yeni bir açıklama motoru
    yazmak, gerekçeyi kararın kendisinden **ayırırdı** ve ikisi zamanla ayrışırdı.
    """
    kind = spec.get("kind")
    if spec.get("cizilmedi"):
        return str(spec["cizilmedi"])
    if kind == "line" or (time_col and kind in ("bar", "stacked")):
        return "Zaman serisi: eğilim, tek tek değerlerden daha çok şey söyler."
    if kind == "scatter":
        return "İki ölçü, tek varlık ekseni: ilişki ancak serpme ile görülür."
    if kind in ("facet_measure", "facet"):
        return "Farklı birimler: aynı eksende üst üste koymak ölçekleri yalan söyletir."
    if kind == "pivot":
        return "İki kırılım birlikte: çapraz tablo, grafiğin göremediğini gösterir."
    if kind == "heatmap":
        return "İki kategorik eksen + tek ölçü: yoğunluk en hızlı ısı haritasında okunur."
    if kind == "kpi":
        return "Tek sayı: bir grafik ondan daha az şey anlatır."
    if kind == "table":
        return "Okunabilirlik: bu şekil grafikte kaybolur, tabloda kalır."
    if cat_dims and len(measures) == 1:
        return "Tek ölçü, kategori kırılımı: uzunluk karşılaştırması en doğru okunandır."
    return "Varsayılan: başka bir kural bu veriye daha uygun bir eksen önermedi."


#: 🔴 FAZ 5.11 — finans/muhasebe kapsamı. Karar-vericiler ve finans profesyonelleri
#: **tablo tercih ediyor** (~50.000 yanıtlık çalışma, arXiv:2411.07451: genel kullanıcı
#: grafiği %41,7 vs tablo %36,3 tercih ederken bu iki grup **tersini** yapıyor).
#: `[DOĞRULANMADI — birincil kaynak okunmadı; oran bir gerekçedir, bir hedef değil]`
_FINANS_CUBELARI = ("mizan", "cari", "cari_finans", "kpi", "gelir_tablosu", "bilanco")

#: Sıralanmamış bir boyutta kaç kategoriden sonra grafik **okunamaz** hâle gelir.
#: ⚠ Sıralanmışsa kural **uygulanmaz**: 50 kategorili bir Top-N çubuğu okunabilir,
#: 21 kategorili alfabetik bir çubuk okunamaz. *Sorun sayı değil, SIRA.*
_KATEGORI_TAVANI = 20


def _daralt(spec: dict[str, Any], yeni_kind: str, gerekce: str) -> None:
    """Kararı daraltır **ve teklifleri kapatır**.

    🔴 Çizmemeye karar verip yine de bir pasta grafiği **teklif etmek**, kararı kendi
    içinde çelişkili yapardı: kullanıcı *"grafik uygun değil"* yazısının yanında bir
    grafik düğmesi görürdü. *Bir karar, kendi alternatifini önermez.*
    """
    spec["kind"] = yeni_kind
    if yeni_kind == "table":
        spec["table_mode"] = "table"
    spec["partition"] = False
    spec["stackable"] = False
    spec["alternatives"] = []
    spec["cizilmedi"] = gerekce


def _cizme_kurallari(spec: dict[str, Any], rows: list[dict], cat_dims: list[str],
                     measures: list[str], time_col: str | None,
                     cube_query: dict | None) -> None:
    """§15.6 — **grafik ÇİZİLMEZ** dalları. `spec`i yerinde günceller.

    ## 🔴 Mevcut kararları BOZMAZ

    Dört kuralın hepsi **daraltıcıdır**: bir grafiği tabloya/cümleye çevirirler, tersi
    asla olmaz. Bir kural ateşlemezse bugünkü karar **birebir** kalır.

    ## Dört kural

    | # | koşul | sonuç | neden |
    |---|---|---|---|
    | 1 | tek skaler, boyut yok | *(zaten `kpi`)* | Bir sayı zaten grafik değil |
    | 2 | ≤2 satır **veya** ≤3 kategori | `cumle` | Üç çubuk, üç kelimeden daha az anlatır |
    | 3 | >20 kategori **ve sıralanmamış** | `table` | Okunamayan bir grafik, tablodan kötüdür |
    | 4 | finans/muhasebe kapsamı | `table` | Karar-verici **tabloyu** tercih ediyor |

    ⚠ **Kural 3'ün şartı SIRA, sayı değil.** 50 kategorili bir Top-N çubuğu okunabilir;
    21 kategorili alfabetik bir çubuk okunamaz. Yalnız sayıya bakmak, kullanıcının
    kendi sıraladığı bir raporu **cezalandırırdı**.

    ⚠ **Zaman serisi hiçbir kuralda tabloya çevrilmez** (kural 3/4): bir trend,
    tablo hâlinde **görülemez** — grafiğin tek gerçek üstünlüğü tam olarak orada.
    """
    kind = spec.get("kind")
    # 🔴 **KURALLAR YALNIZ VARSAYILAN `bar`'A UYGULANIR — ve bu bir düzeltmedir.**
    #
    # İlk yazımda kural her karara uygulanıyordu ve `test_viz.py`'nin **yedi testi**
    # kırmızı verdi: `kpi` · `heatmap` · `table` · `partition`'lı `bar` — dördü de
    # **bilinçli** kararlardı ve daraltmak onların gerekçesini siliyordu. Yani maddenin
    # kendi şartını (*"mevcut kararları BOZMAZ"*) **ben çiğnedim** ve kapı yakaladı.
    #
    # Doğru kapsam: yalnız **varsayılan bar** — yani "başka bir kural konuşmadı, o hâlde
    # çubuk çizelim" kararı. §15.6'nın anlattığı boşluk tam olarak orada: *bir grafiğin
    # varsayılan olması, doğru olduğu anlamına gelmez.*
    #
    # ⚠ `kpi` zaten bir grafik **değildir** — kural 1 orada **zaten sağlanmış**tır ve
    # onu `cumle`ye çevirmek bir kazanç değil, bir yeniden adlandırmadır.
    # ⚠ **`partition`/`stackable` bir KARAR DEĞİL, bir TEKLİFTİR** (FE'de pie/treemap
    # toggle'ı). İlk yazımda onları muhafıza koydum ve kural **tam hedefinde** bloke
    # oldu: tek boyut + tek additive ölçü neredeyse her zaman `partition=True` alır,
    # yani *"3 kategori"* vakasının kendisi hiç ateşlemiyordu. *Bir teklifi bir karar
    # sanmak, kuralı sessizce ölü bırakır.*
    if kind != "bar" or not measures:
        return
    kategori_sayisi = 0
    if cat_dims:
        d = cat_dims[0]
        kategori_sayisi = len({str(r.get(d)) for r in rows if r.get(d) is not None})

    # (2) ≤2 satır VEYA ≤3 kategori → CÜMLE / KPI kartı
    #
    # ⚠ **TEK ÖLÇÜ şartı — ve bu da kapıdan geldi.** İlk yazımda şart yoktu ve iki
    # regresyon testi kırmızı verdi: 3 vardiya × 3 YoY ölçüsü **dokuz çubuktur**, üç
    # değil. *"Üç çubuk üç kelimeden az anlatır"* gerekçesi orada **geçersizdir** —
    # kıyaslanacak birden fazla seri varsa grafik gerçekten iş görür.
    if (not time_col and cat_dims and len(measures) == 1
            and (len(rows) <= 2 or kategori_sayisi <= 3)):
        _daralt(spec, "cumle",
                f"{max(len(rows), kategori_sayisi)} kalem — üç çubuk, üç kelimeden "
                f"daha az anlatır")
        return

    # (3) >20 kategori VE SIRALANMAMIŞ → TABLO
    sirali = bool((cube_query or {}).get("order"))
    if not time_col and kategori_sayisi > _KATEGORI_TAVANI and not sirali:
        _daralt(spec, "table",
                f"{kategori_sayisi} sıralanmamış kategori — okunamayan bir grafik, "
                f"tablodan kötüdür")
        return

    # (4) FİNANS/MUHASEBE kapsamı → varsayılan TABLO + metin
    cube = str((cube_query or {}).get("cube") or "")
    if not time_col and cube in _FINANS_CUBELARI:
        _daralt(spec, "table",
                "finans/muhasebe kapsamı — karar-vericiler ve finans profesyonelleri "
                "tabloyu tercih ediyor")
