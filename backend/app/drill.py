"""Dallı kök-neden analizi (Faz 4.10, 1 Ağustos 2026 — dış yol haritası 2.5+2.15).

GENİŞLETİLMİŞ TASARIM (kullanıcı düzeltmesi, 1 Ağustos 2026): ilk taslak yalnız "açıkla +
aykırı-işaretle" idi (gerçek veri çekmiyordu) — YETERSİZ bulundu. Kullanıcının talebi:
dallanma ile "her şeyi görebilmeli, tüm veri ağacına ulaşabilmeli" — yani tıklaya tıklaya
GERÇEK verilerle (her seviyede GERÇEK bir sorgu çalıştırarak) EN ALTTAKİ ham satırlara kadar
inebilmeli. Bu modül artık İKİ katman sağlar:

1. SAF yorumlama fonksiyonları (formula_explanation/flag_outliers/available_dimensions/
   kpi_components) — GİRDİ olarak ZATEN ÇALIŞTIRILMIŞ bir sonucu alır, SQL üretmez.
2. Durum-geçiş + ham-satır SQL fonksiyonları (expand_cube_query/select_cube_query/
   build_raw_row_sql) — bir cube_query'yi bir sonraki dallanma ADIMINA göre dönüştürür
   (app/routers/ask.py::ask_drill BUNLARI ÇALIŞTIRIR — dry_plan+query, /cube'un YAPTIĞI
   AYNI şey, gerçek veri döner). `build_raw_row_sql`, YAPRAK seviyesinde (daha fazla
   anlamlı kırılım kalmadığında) cube'un base_object'inden HAM SATIRLARI çeker — "veri
   ağacının en altı" budur; kullanıcı gerçek kök nedeni (ör. "15 Temmuz sabah Makine 3'te
   40 dakikalık duruş kaydı var") burada GÖRÜR.

İleride bir agent'ın AYNI mekanizmayı otomatik gezebilmesi hedeflenir — bu yüzden HİÇBİR
fonksiyon yeni bir LLM çağrısı yapmaz, hepsi deterministiktir ve saf girdi/çıktı sözleşmesi
taşır (bir agent'ın da çağırabileceği temiz bir arayüz)."""

from __future__ import annotations

import re

# Güvenlik: dimension/base_object adları HER ZAMAN bizim ŞEMA metadata'mızdan gelir
# (kullanıcı serbest metninden DEĞİL) — ama ham SQL inşa ederken savunma-derinliği ilkesiyle
# yine de KATI bir tanımlayıcı deseniyle doğrulanır (yalnız harf/rakam/alt çizgi).
_SAFE_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class UnsafeDrillError(Exception):
    """Güvenli olmayan bir tanımlayıcı (dimension/base_object adı) tespit edildi — asla
    kullanıcı serbest metninden gelmemeli; bir şema/veri tutarsızlığına işaret eder."""


def formula_explanation(cube_query: dict, cube_meta: dict | None) -> str:
    """`cube_query`'den DETERMİNİSTİK, insan-okur bir açıklama üretir (ör. "Bu değer,
    sabah vardiyası kayıtlarının OEE ortalamasıdır"). Yeni bir LLM çağrısı GEREKMEZ —
    app/routers/ask.py::_build_explain'in deseniyle AYNI ruhta, salt-kural-tabanlı."""
    measures = cube_query.get("measures") or []
    dimensions = cube_query.get("dimensions") or []
    filters = cube_query.get("filters") or []
    time_dims = cube_query.get("timeDimensions") or []

    m_disp = (cube_meta or {}).get("measure_synonyms_display") or {}
    d_labels = (cube_meta or {}).get("dimension_labels") or {}

    measure_txt = ", ".join(m_disp.get(m) or m for m in measures) or "değer"

    scope_bits: list[str] = []
    for f in filters:
        dim = f.get("dimension")
        label = d_labels.get(dim) or dim
        op = f.get("operator", "eq")
        val = f.get("value")
        if dim in ("tarih", "donem", "dönem"):
            if op == "gte":
                scope_bits.append(f"{val} tarihinden itibaren")
            elif op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                scope_bits.append(f"{val[0]} – {val[1]} aralığında")
            else:
                scope_bits.append(f"{val} tarihli")
        elif op == "in" and isinstance(val, list):
            scope_bits.append(f"{label} değeri {', '.join(str(v) for v in val)} olan")
        else:
            scope_bits.append(f"{label} = {val} olan")
    for td in time_dims:
        gran = td.get("granularity")
        if gran:
            scope_bits.append(f"{gran} bazında zaman kırılımlı")

    parts = [f"Bu değer {measure_txt} ölçüsünün"]
    if scope_bits:
        parts.append(" " + " ve ".join(scope_bits))
    if dimensions:
        dim_labels = ", ".join(d_labels.get(d) or d for d in dimensions)
        parts.append(f" {dim_labels} bazında kırılımıdır (toplam/ortalama).")
    else:
        parts.append(" kayıtlar üzerinden toplam/ortalamasıdır.")
    return "".join(parts)


def flag_outliers(rows: list[dict], dim: str, measure: str, *, k: float = 2.0) -> list[dict]:
    """`dim`'e göre kırılmış satırlarda Z-SKORU (ortalama ± k·std) ile aykırı kategorileri
    işaretler — `app/schedules.py::detect_anomalies` İLE AYNI istatistiksel yöntem (kullanıcı
    talimatı, 1 Ağustos 2026: "mevcut interpret.py/schedules.py sinyal-outlier tespiti
    BURADA yeniden kullanılır, yeni bir istatistik motoru İCAT EDİLMEZ"). Kategori-bazlı
    kırılımda satır SIRASI önemsiz — z-skor yöntemi zaten sıra-bağımsız (yalnız ortalama/
    std'ye bakar), bu yüzden zaman-serisi DIŞINDA da doğrudan uygulanabilir.

    [{value, amount, direction, z_score}] döner, |z| büyüklüğüne göre azalan sırada.
    Kategori sayısı < 4 ise (detect_anomalies İLE AYNI eşik — istatistik anlamsız) boş döner."""
    agg: dict[str, float] = {}
    for r in rows:
        v = r.get(dim)
        m = r.get(measure)
        if v is None or m is None:
            continue
        try:
            agg[str(v)] = agg.get(str(v), 0.0) + float(m)
        except (TypeError, ValueError):
            continue
    if len(agg) < 4:
        return []
    values = list(agg.values())
    mean = sum(values) / len(values)
    std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
    if std == 0:
        return []
    out = []
    for value, amount in agg.items():
        z = (amount - mean) / std
        if abs(z) >= k:
            out.append({
                "value": value, "amount": round(amount, 2),
                "direction": "above" if z > 0 else "below",
                "z_score": round(z, 2),
            })
    return sorted(out, key=lambda o: abs(o["z_score"]), reverse=True)


def available_dimensions(cube_meta: dict, cube_query: dict) -> list[dict]:
    """Cube'un HENÜZ kullanılmayan boyutları (dimensions'ta ya da filters'ta olmayan) —
    dallanma çipi adayları. Zaman boyutu (time_dimensions) burada AYRI ele alınmaz (zaman
    granülerliği değişimi farklı, mevcut bir işlemdir — cube_router zaten bunu yönetir)."""
    used = set(cube_query.get("dimensions") or [])
    used |= {f.get("dimension") for f in (cube_query.get("filters") or [])}
    d_labels = cube_meta.get("dimension_labels") or {}
    return [
        {"name": d, "label": d_labels.get(d) or d}
        for d in (cube_meta.get("dimensions") or []) if d not in used
    ]


def related_cubes(current_cube: str, active_dims: set[str], all_cubes: list[dict]) -> list[dict]:
    """Kök-neden için İLİŞKİLİ cube'ları bulur — mevcut dallanma yolunda (dimensions +
    filters) kullanılan boyutları PAYLAŞAN başka cube'lar. Somut senaryo (kullanıcı örneği,
    1 Ağustos 2026): "makine bazında OEE" sabah vardiyasında düşük çıkmış — `oee` cube'unun
    KENDİ boyutları tükendiğinde, "makine"+"vardiya" boyutunu PAYLAŞAN `makine_duruslari`
    cube'una (duruş NEDENİ boyutu taşır) geçilerek "bu vardiyada/makinede DURUŞ var mıydı,
    hangi sebepten?" sorusu GERÇEK veriyle cevaplanabilir. `cube_router.py`'nin cross_cube_
    add/cross_cube_dim_switch'iyle AYNI "paylaşılan boyut adı" ilkesi — yeni bir eşleştirme
    mantığı İCAT EDİLMEDİ, var olan ilke başka bir amaçla (blend değil, kök-neden keşfi
    için) yeniden kullanıldı."""
    out = []
    for c in all_cubes:
        name = c.get("name")
        if not name or name == current_cube:
            continue
        cube_dims = set(c.get("dimensions") or [])
        shared = active_dims & cube_dims
        if shared:
            out.append({
                "cube": name,
                "label": c.get("display") or name,
                "shared_dimensions": sorted(shared),
            })
    return out


def expand_cube_query(cube_query: dict, dimension: str) -> dict:
    """Mevcut cube_query'ye YENİ bir dallanma boyutu EKLER (dimensions listesine ekler) —
    saf, yan-etkisiz: girdiyi DEĞİŞTİRMEZ, yeni bir sözlük döner (breadcrumb geçmişinin her
    adımı KENDİ kopyasını saklayabilsin diye)."""
    new_cq = dict(cube_query)
    dims = list(cube_query.get("dimensions") or [])
    if dimension not in dims:
        dims.append(dimension)
    new_cq["dimensions"] = dims
    return new_cq


def select_cube_query(cube_query: dict, dimension: str, value: str) -> dict:
    """Kullanıcı bir kırılımdaki BELİRLİ bir kategoriye (ör. "sabah") tıkladığında: o boyutu
    `dimensions`'tan ÇIKARIR, YERİNE bir FİLTRE ekler ({dimension, operator:'eq', value}) —
    "Sabah Vardiyası → Makine 3 → …" breadcrumb'ının HER adımı bu şekilde inşa edilir."""
    new_cq = dict(cube_query)
    dims = [d for d in (cube_query.get("dimensions") or []) if d != dimension]
    new_cq["dimensions"] = dims
    filters = [f for f in (cube_query.get("filters") or []) if f.get("dimension") != dimension]
    filters.append({"dimension": dimension, "operator": "eq", "value": value})
    new_cq["filters"] = filters
    return new_cq


def jump_to_related_cube(cube_query: dict, target_cube: str, target_meta: dict) -> dict:
    """`related_cubes`ile bulunan bir cube'a GEÇİŞ — kaynak cube_query'nin dimensions/
    filters/timeDimensions'ından yalnız HEDEF cube'da da GERÇEKTEN var olan boyutlar
    taşınır (ör. "makine"+"vardiya" ikisinde de varsa taşınır; "renk" yalnız kaynakta
    varsa DÜŞÜRÜLÜR — hedef cube'da anlamsız bir filtre kalmaz). Zaman boyutu (tarih) AYRI
    ele alınır (dimensions/filters listesinde değil, time_dimensions'ta yaşar)."""
    target_dims = set(target_meta.get("dimensions") or [])
    target_time_dims = set(target_meta.get("time_dimensions") or [])
    target_measures = target_meta.get("measures") or []

    kept_dims = [d for d in (cube_query.get("dimensions") or []) if d in target_dims]
    kept_filters = [
        f for f in (cube_query.get("filters") or [])
        if f.get("dimension") in target_dims or f.get("dimension") in target_time_dims
    ]
    kept_time = [
        td for td in (cube_query.get("timeDimensions") or [])
        if td.get("dimension") in target_time_dims
    ]
    return {
        "cube": target_cube,
        "measures": list(target_measures),
        "dimensions": kept_dims,
        "filters": kept_filters,
        "timeDimensions": kept_time,
    }


def sql_literal(value) -> str:
    """SQL metin/sayı literali — GÜVENLİ tırnaklama (tek tırnak katlanarak escape edilir).
    `build_raw_row_sql`'in TEK savunma katmanı DEĞİL (dimension adları da ayrıca
    `_SAFE_IDENT_RE` ile doğrulanır) — ikisi BİRLİKTE ham SQL enjeksiyonuna karşı korur."""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def build_raw_row_sql(base_object: str, filters: list[dict], *, limit: int = 50) -> str:
    """YAPRAK seviyesi (Faz 4.10'un "tüm veri ağacına ulaşabilmeli" gereksinimi, kullanıcı
    talebi 1 Ağustos 2026): daha fazla anlamlı kırılım kalmadığında, mevcut filtre setiyle
    cube'un `base_object`'inden HAM (agregasyonsuz) satırları çeker — kullanıcı GERÇEK kök
    nedeni (ör. "15 Temmuz sabah Makine 3'te 40 dakikalık duruş kaydı var") burada görür.

    GÜVENLİK: `base_object` VE her `filters[].dimension` KATI bir tanımlayıcı deseniyle
    doğrulanır (yalnız harf/rakam/alt çizgi) — ikisi de bizim ŞEMA metadata'mızdan gelir,
    kullanıcı serbest metninden ASLA, ama savunma-derinliği ilkesiyle yine de kontrol edilir.
    Değerler `sql_literal` ile escape edilir (tek tırnak enjeksiyonuna karşı)."""
    if not _SAFE_IDENT_RE.match(base_object):
        raise UnsafeDrillError(f"Güvensiz base_object adı: {base_object!r}")
    where_parts: list[str] = []
    for f in filters:
        dim = f.get("dimension")
        if not dim or not _SAFE_IDENT_RE.match(dim):
            raise UnsafeDrillError(f"Güvensiz dimension adı: {dim!r}")
        op = f.get("operator", "eq")
        val = f.get("value")
        if dim in ("tarih", "donem", "dönem"):
            continue  # zaman filtresi bu ilk sürümde ATLANIR (ayrı, dialect'e özel ele alınmalı)
        if op == "in" and isinstance(val, list):
            vals = ", ".join(sql_literal(v) for v in val)
            where_parts.append(f"{dim} IN ({vals})")
        elif op == "gte":
            where_parts.append(f"{dim} >= {sql_literal(val)}")
        elif op == "lte":
            where_parts.append(f"{dim} <= {sql_literal(val)}")
        else:
            where_parts.append(f"{dim} = {sql_literal(val)}")
    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
    safe_limit = max(1, min(int(limit), 500))
    return f"SELECT * FROM {base_object}{where_sql} LIMIT {safe_limit}"


def kpi_components(kpi: dict | None) -> list[dict] | None:
    """Türetilmiş/KPI metrikler için ara bileşen değerleri (ör. CCC = DSO+DIO-DPO).
    `app/kpi.py::resolve_kpi` bunu ZATEN `components` olarak hesaplıyor — burada yalnız
    dışa-aktarılabilir bir şekle normalize edilir.

    NOT (canlı bulgu, 1 Ağustos 2026): `AskResponse.kpi` şu an HİÇBİR yerde set edilmiyor
    (resolve_kpi/resolve_kpi_series bu sistemde çağrılmıyor — muhtemelen daha önceki bir
    aşamadan kalan, henüz bağlanmamış bir yetenek). Bu fonksiyon YİNE DE yazıldı çünkü
    şema (AskResponse.kpi) zaten bu sözleşmeyi taşıyor — KPI yolu ileride bağlanınca drill
    paneli sıfırdan değişiklik gerektirmeden bileşen dökümünü gösterebilecek."""
    if not kpi:
        return None
    comps = kpi.get("components") or []
    out = [
        {"name": c.get("key"), "label": c.get("label") or c.get("key"),
         "value": c.get("value"), "unit": c.get("unit")}
        for c in comps if c.get("value") is not None
    ]
    return out or None
