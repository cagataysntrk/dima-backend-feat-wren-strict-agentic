"""Cross-cube KPI-kompozisyon katmanı (ADR-0017 evrimi).

Bir KPI, birden çok türev-view'dan skaler bileşenleri çeker ve bir formülle birleştirir
(CCC = DSO + DIO − DPO; DSO/DPO cari_finans_src'ten, DIO karlilik_src'ten). Bu, tek cube
ölçüsüyle ifade edilemeyen ilk *cross-cube* metrik ailesidir — "her sorguda tüm eksenler"
vizyonunun kompozisyon primitifi.

KPI tanımları DB-bağımsızdır (kanonik view kolonları); compose yalnız gerekli view'lar
üretilmişse `kpis/<ad>.yml` yazar. Bileşen SQL'i doğrudan view adına atıfla çalışır —
Wren motoru view'ı CTE olarak genişletir (cube_sql'le aynı yol)."""

from __future__ import annotations

import ast
import operator
from pathlib import Path

import yaml

# Formül değerlendirme: yalnız + − × ÷ ve bileşen adları (güvenli; eval YOK).
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node: ast.AST, env: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body, env)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left, env), _eval(node.right, env))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand, env))
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise KeyError(f"KPI formülünde bilinmeyen bileşen: {node.id}")
        return float(env[node.id])
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    raise ValueError(f"KPI formülünde izinsiz ifade: {ast.dump(node)}")


def eval_formula(formula: str, env: dict[str, float]) -> float:
    return _eval(ast.parse(formula, mode="eval"), env)


def load_kpis(project_dir: Path) -> dict[str, dict]:
    """Derlenmiş projeden KPI tanımlarını okur (kpis/*.yml). Boş dizin = {}."""
    kdir = Path(project_dir) / "kpis"
    out: dict[str, dict] = {}
    if not kdir.is_dir():
        return out
    for f in sorted(kdir.glob("*.yml")):
        spec = yaml.safe_load(f.read_text()) or {}
        if spec.get("name"):
            out[spec["name"]] = spec
    return out


def resolve_kpi(svc, spec: dict, where: str = "") -> dict:
    """KPI bileşenlerini çalıştırır (skaler), formülü değerlendirir, kartı döner.

    where: opsiyonel dönem yüklemi (ör. "WHERE tarih >= '2024-01-01'"); bileşen SQL'inin
    {where} placeholder'ına gömülür (dönemsiz view'lar için boş)."""
    comps: list[dict] = []
    env: dict[str, float] = {}
    for key, c in (spec.get("components") or {}).items():
        sql = c["sql"].format(where=where)
        rows = svc.query(sql, limit=1).get("rows", [])
        val = None
        if rows:
            raw = next(iter(rows[0].values()), None)
            val = round(float(raw), 1) if raw not in (None, "") else None
        env[key] = val if val is not None else 0.0
        comps.append({"key": key, "label": c.get("label", key),
                      "unit": c.get("unit"), "value": val})
    value = None
    try:
        # decimals: oran KPI'ları 2 ondalık (3.51) ister; gün/tutar 1 yeter (varsayılan).
        value = round(eval_formula(spec.get("formula", "0"), env), int(spec.get("decimals", 1)))
    except (KeyError, ValueError, ZeroDivisionError):
        value = None
    return {
        "kpi": spec["name"],
        "label": spec.get("label", spec["name"]),
        "unit": spec.get("unit"),
        "lower_is_better": spec.get("lower_is_better", False),
        "formula": spec.get("formula"),
        "explain": spec.get("explain"),
        "value": value,
        "components": comps,
    }


_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _as_date(x):
    import datetime as _dt

    if x is None:
        return None
    if isinstance(x, str):
        return _dt.date.fromisoformat(x[:10])
    return _dt.date(x.year, x.month, x.day)


def _time_buckets(mn, mx, gran: str) -> list[dict]:
    """[mn, mx] tarih aralığını granülariteye göre kovalara böler → {label, start, end}
    (end HARİÇ). GENERIC — herhangi bir KPI'nın dönem-serisi buradan gelir."""
    import datetime as _dt

    a, b = _as_date(mn), _as_date(mx)
    if a is None or b is None:
        return []
    out: list[dict] = []
    if gran == "day":
        cur = a
        while cur <= b:
            nxt = cur + _dt.timedelta(days=1)
            out.append({"label": f"{cur.day} {_MONTHS_TR[cur.month - 1]}",
                        "start": cur.isoformat(), "end": nxt.isoformat()})
            cur = nxt
    elif gran == "week":
        cur = a - _dt.timedelta(days=a.weekday())  # haftanın Pazartesi'si
        while cur <= b:
            nxt = cur + _dt.timedelta(days=7)
            out.append({"label": f"{cur.day} {_MONTHS_TR[cur.month - 1]}",
                        "start": cur.isoformat(), "end": nxt.isoformat()})
            cur = nxt
    elif gran == "year":
        for y in range(a.year, b.year + 1):
            out.append({"label": str(y), "start": f"{y}-01-01", "end": f"{y + 1}-01-01"})
    elif gran == "quarter":
        y, q = a.year, (a.month - 1) // 3
        while (y, q) <= (b.year, (b.month - 1) // 3):
            ey, eq = (y + 1, 0) if q == 3 else (y, q + 1)
            out.append({"label": f"{y} Ç{q + 1}", "start": f"{y}-{q * 3 + 1:02d}-01",
                        "end": f"{ey}-{eq * 3 + 1:02d}-01"})
            y, q = ey, eq
    else:  # month (varsayılan)
        y, m = a.year, a.month
        while (y, m) <= (b.year, b.month):
            ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
            out.append({"label": f"{_MONTHS_TR[m - 1]} {y}", "start": f"{y}-{m:02d}-01",
                        "end": f"{ny}-{nm:02d}-01"})
            y, m = ny, nm
    return out[-60:]  # emniyet: en SON 60 kova (yakın trend; gün/haftada patlamayı önler)


def resolve_kpi_series(svc, spec: dict, gran: str, period_where: str = "") -> dict:
    """KPI'yı DÖNEM-SERİSİ olarak çözer (CCC/likidite trendi). GENERIC: skaler resolver'ı
    her zaman-kovası için bir kez çalıştırır ({where} = o kovanın aralığı) — component SQL'i
    yeniden yazmaya GEREK YOK, tüm KPI'lar bedavaya trend olur.

    gran: month|quarter|year. period_where: dış dönem sınırı (aralığı daraltır, "bu yıl")."""
    views = spec.get("requires_views") or []
    view = views[0] if views else None
    # ZAMAN KOLONU SABİT KODLU DEĞİL (Faz C3). Eskiden üç yerde `tarih` yazıyordu; KPI'ın
    # dayandığı view farklı bir zaman kolonu taşıyorsa (`donem_tarih` gibi) sorgu ya patlar
    # ya da — kolon adı tesadüfen varsa — SESSİZCE YANLIŞ PENCERE kurardı. Artık KPI
    # spec'inde beyan edilebilir; beyan yoksa `tarih` (mevcut davranış, geriye uyumlu).
    tcol = str(spec.get("time_column") or "tarih")
    mn = mx = None
    if view:
        rows = svc.query(
            f"SELECT MIN({tcol}) AS mn, MAX({tcol}) AS mx FROM {view} {period_where}".strip(),
            limit=1).get("rows", [])
        if rows:
            mn, mx = rows[0].get("mn"), rows[0].get("mx")
    buckets = _time_buckets(mn, mx, gran)
    # series_mode: "asof" = kümülatif bakiye (dönem-SONUNA kadar; bilanço oranları — Cari
    # Oran/NWC/CCC balance-sheet), "flow" = yalnız o dönemin akışı (satış/SMM gibi). asof
    # şart: bilanço oranını tek ayın hareketinden hesaplamak negatif/saçma verir (canlı bulgu).
    mode = str(spec.get("series_mode", "flow")).lower()
    series: list[dict] = []
    for bk in buckets:
        where = (f"WHERE {tcol} < '{bk['end']}'" if mode == "asof"
                 else f"WHERE {tcol} >= '{bk['start']}' AND {tcol} < '{bk['end']}'")
        card = resolve_kpi(svc, spec, where)
        series.append({"bucket": bk["label"], "value": card["value"],
                       "components": card["components"]})
    # Başlık = SON dönem (as-of); seri grafik/tablo için ayrı taşınır.
    last = series[-1] if series else {}
    return {
        "kpi": spec["name"], "label": spec.get("label", spec["name"]),
        "unit": spec.get("unit"), "lower_is_better": bool(spec.get("lower_is_better")),
        "formula": spec.get("formula"), "explain": spec.get("explain"),
        "granularity": gran, "series": series,
        "value": last.get("value"), "components": last.get("components", []),
    }
