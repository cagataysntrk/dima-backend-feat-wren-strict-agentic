"""Dönemsel kıyas (YoY/MoM) — çok-yıl veriyle DETERMİNİSTİK period-shift (LLM'siz).

Jenerik sorgu-modifier'ı (cube_query["compare"] = "yoy"|"mom") — metrik DEĞİL. Cari dönemi
bir dönem geri kaydırıp iki seriyi YIL-İÇİ KONUMA göre hizalar (2026-03-15 ↔ 2025-03-15,
ay+gün) → grafik geçen yılı saydam ikinci seri olarak üst üste çizer. Açık-uçlu "bu yıl"
YTD'ye sınırlanır (simetrik pencere). /ask (NL yolu) ve /cube (chip yolu) ortak kullanır.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from app import cube_router


def time_dim_of(schema: dict, cube: str | None) -> str:
    """Cube'un zaman boyutu adı (parti/oee=tarih, enerji/ik=donem_tarih). Yoksa 'tarih'."""
    meta = cube_router._cube_meta(schema, cube) or {}
    tds = meta.get("time_dimensions") or ["tarih"]
    td0 = tds[0]
    return td0.get("name") if isinstance(td0, dict) else td0


def _merge(cur: list[dict], prev: list[dict], measures: list[str], dims: list[str],
           mode: str = "yoy") -> tuple[list[dict], list[str]]:
    """İki seriyi yıl-BAĞIMSIZ konuma (boyutlar + ay,gün) göre hizala; %değişim ekle."""
    cols0 = list(cur[0].keys()) if cur else (list(prev[0].keys()) if prev else [])
    timecols = [c for c in cols0 if c not in dims and c not in measures]

    def _ymd(v, dy: int = 0):
        """(yıl+dy, ay, gün) — datetime ya da ISO string. Hizalama anahtarı."""
        yr, mo, d = getattr(v, "year", None), getattr(v, "month", None), getattr(v, "day", None)
        if mo is None and isinstance(v, str):
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})", v)
            if m:
                yr, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return None if mo is None else ((yr or 0) + dy, mo, d)

    def key(row: dict, shift_yr: int) -> tuple:
        # cari: tam tarih; geçen: +shift_yr yıl kaydır (2024-03 → 2025-03 hizası, YoY konumu).
        k = tuple(row.get(d) for d in dims)
        for tc in timecols:
            k = k + (_ymd(row.get(tc), shift_yr),)
        return k

    shift = 1 if mode == "yoy" else 1  # prev anahtarını cari'ye taşımak için +1 dönem
    prev_ix = {key(r, shift): r for r in prev}
    out = []
    for r in cur:
        pr = prev_ix.get(key(r, 0), {})
        nr = dict(r)
        for m in measures:
            c, p = r.get(m), pr.get(m)
            nr[f"{m}_gecen"] = p
            nr[f"{m}_degisim_yuzde"] = (round((c - p) / p * 100, 1)
                if isinstance(c, (int, float)) and isinstance(p, (int, float)) and p else None)
        out.append(nr)
    cols = cols0 + [f"{m}_gecen" for m in measures] + [f"{m}_degisim_yuzde" for m in measures]
    return out, cols


def compute(service, cq: dict, mode: str, time_dim: str, limit: int | None = None,
            execute: bool = True) -> dict[str, Any]:
    """Kıyas sonucu: {base_cq, base_sql, columns, rows, row_count}. base = compare'sız sorgu;
    cari dönem YTD'ye sınırlanır, geçen dönem simetrik kaydırılır (yoy=-1 yıl, mom=-1 ay)."""
    base = {k: v for k, v in cq.items() if k != "compare"}
    flt = list(base.get("filters") or [])
    has_gran = bool(base.get("timeDimensions"))      # aylık/günlük ZAMAN SERİSİ mi?
    has_tf = any(f.get("dimension") == time_dim for f in flt)
    has_lte = any(f.get("dimension") == time_dim and f.get("operator") == "lte" for f in flt)
    if not has_gran:
        # AGREGAT / kırılım (zaman ekseni YOK): kıyas için TANIMLI dönem gerekir — dönem yoksa
        # cari = bu yıl (YTD); açık-uçlu dönem de bugüne sınırlanır (simetrik pencere).
        if not has_tf:
            flt.append({"dimension": time_dim, "operator": "gte", "value": f"{date.today().year}-01-01"})
            has_tf = True
        if not has_lte:
            flt.append({"dimension": time_dim, "operator": "lte", "value": date.today().isoformat()})
    elif has_tf and not has_lte:
        # ZAMAN SERİSİ + açık-uçlu dönem ("bu yıl aylık") → YTD sınırla.
        flt.append({"dimension": time_dim, "operator": "lte", "value": date.today().isoformat()})
    # ZAMAN SERİSİ + dönem YOK ("aylık ciro geçen yıla göre") → SINIRLAMA yok: TÜM seri (30 ay)
    # gösterilir; her ayın geçen-yıl karşılığı +1 yıl hizasıyla gelir (2024'ün öncesi yok → boş).
    base["filters"] = flt
    base_sql = service.cube_sql(base)
    cur = (service.query(base_sql, limit=limit) or {}).get("rows", []) if execute else []
    prev_cq = dict(base)
    prev_cq["filters"] = cube_router.shift_period_back(flt, mode, time_dim)
    prev = (service.query(service.cube_sql(prev_cq), limit=limit) or {}).get("rows", []) if execute else []
    rows, cols = _merge(cur, prev, base.get("measures") or [], base.get("dimensions") or [], mode)
    return {"base_cq": base, "base_sql": base_sql, "columns": cols, "rows": rows, "row_count": len(rows)}
