"""Rapor kompozisyonu (ADR-0024, forward) — çok-blok / çok-SAYFA rapor üretimi.

Bir rapor tek grafik değil bir KOMPOZİSYONDUR: bir dizi blok (her biri cube_query → sonuç + viz
kararı), sayfalara bölünmüş. "Sayfalarca rapor üret" (yönetici özeti → trendler → detay) buradan
çıkar. Karar deterministik (LLM yok); her blok viz motorundan (app/viz.py) kendi grafik/tablo/pivot
kararını alır → web/e-posta/PDF AYNI kompozisyonu render eder (cross-surface).

Report := {title, pages: [[Block, ...], ...], block_count}
Block  := {title, cube_query, period, result, viz, error}
"""

from __future__ import annotations

from typing import Any

_DEFAULT_PAGE_SIZE = 3  # sayfa başına blok (yazdırma/PDF dostu)
_MAX_BLOCKS = 24


def compose_report(
    service,
    schema: dict,
    spec: dict,
    *,
    execute: bool = True,
    limit: int = 1000,
) -> dict[str, Any]:
    """spec {title?, blocks:[{cube_query, title?, period?}], page_size?} → Report.

    Her blok: göreli dönem çözülür → cube_sql → sonuç → viz kararı (birim-farkında). Tek blok
    hatası raporu düşürmez (error alanına yazılır). Bloklar `page_size`'lık SAYFALARA bölünür.
    """
    from app import cube_router, viz

    cubes = {c.get("name"): c for c in (schema.get("cubes") or [])}
    blocks: list[dict] = []
    for b in (spec.get("blocks") or [])[:_MAX_BLOCKS]:
        cq = dict(b.get("cube_query") or {})
        period = str(b.get("period") or "").strip()
        if period:
            dfs = cube_router.date_filters(cube_router._norm(period), "tarih")
            cq["filters"] = [
                f for f in cq.get("filters", []) if f.get("dimension") != "tarih"
            ] + dfs
        block: dict[str, Any] = {
            "title": b.get("title"),
            "cube_query": cq,
            "period": period or None,
            "view_hint": b.get("view_hint"),  # widget'ın kayıtlı görünümü (FE onurlandırır)
            "result": None,
            "viz": None,
            "error": None,
        }
        try:
            # DÖNEMSEL KIYAS (YoY/MoM): blok cube_query'sinde compare varsa çöz (chip yolu ile aynı).
            _cmp = cq.get("compare")
            if _cmp in ("yoy", "mom"):
                from app import yoy
                tdn = yoy.time_dim_of(schema, cq.get("cube"))
                o = yoy.compute(service, cq, _cmp, tdn, limit=limit) if execute else None
                result = ({"columns": o["columns"], "rows": o["rows"], "row_count": o["row_count"]}
                          if o else None)
                viz_cq = {**(o["base_cq"] if o else cq), "compare": _cmp}
            else:
                sql = service.cube_sql(cq)
                result = service.query(sql, limit=limit) if execute else None
                viz_cq = cq
            block["result"] = result
            if result:
                cmeta = cubes.get(cq.get("cube")) or {}
                block["viz"] = viz.recommend(
                    result, units=cmeta.get("measure_units") or {},
                    lower_set=cmeta.get("lower_is_better") or [], cube_query=viz_cq,
                )
        except Exception as exc:  # noqa: BLE001 — tek blok hatası raporu düşürmesin
            block["error"] = str(exc)[:200]
        blocks.append(block)

    try:
        page_size = max(1, int(spec.get("page_size") or _DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        page_size = _DEFAULT_PAGE_SIZE
    pages = [blocks[i:i + page_size] for i in range(0, len(blocks), page_size)] or [[]]
    return {
        "title": spec.get("title") or "Rapor",
        "pages": pages,
        "block_count": len(blocks),
    }
