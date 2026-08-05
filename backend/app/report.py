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
                # NOT (31 Temmuz 2026): "measure_units" YANLIŞ anahtardı — schema() dict'i ölçü
                # birimlerini "units" adıyla taşıyor (bkz. app/wren_service.py:236); bu yüzden
                # `recommend()`'in birim-farkındalığı burada da HİÇ devreye giremiyordu (`/ask`,
                # `/cube`, dashboards.py'deki AYNI hata sınıfı, bkz. app/routers/ask.py `_attach_viz`).
                block["viz"] = viz.recommend(result, cube_query=viz_cq,
                                             **viz.meta_args(cmeta))
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
        # 🔴 FAZ 5.13b — **SABİT YAPI**. Aşağıdaki üç bölüm `pages`'in YANINDA durur,
        # içinde değil: bir dışa aktarıcı sayfaları atlasa bile kapak ve **kaynak
        # listesi** elinde kalır.
        **yapi(spec, blocks),
    }


def yapi(spec: dict, blocks: list[dict]) -> dict[str, Any]:
    """FAZ 5.13b — raporun **sabit yapısı**: kapak → yönetici özeti → kaynaklar.

    ## 🔴 `contract_id` ALTTA KALIR — her formatta

    Yol haritasının şartı: *"PDF'e döküldüğünde bile `contract_id` altta kalır."* Bunun
    tek güvenilir yolu onu **bir sunum katmanına değil, yapının kendisine** koymaktır:
    `kaynaklar` listesi `pages`'ten **bağımsızdır** ve bir dışa aktarıcı sayfaları
    atlasa, kırpsa ya da yeniden düzenlese bile **onu düşürmez**.

    ⚠ *Bir kanıt, taşındığı kabın şekline bağlıysa kanıt değildir.*

    ## ⊘ ÖLÇÜLEMEYEN: Word · Excel  — ama **PDF ÖLÇÜLÜR**

    Yol haritası *"dört formatta da `contract_id` var"* diyor. Ölçüldü ve **ilk beyanım
    yanlıştı**: `docx`/`openpyxl` gerçekten yok, ama **PDF VAR** — `ReportView`'in
    `window.print()` yolu. Tarayıcı baskısı bir dışa aktarımdır ve kaynak listesi o
    baskıda **görünmek zorundadır** (`print:hidden` OLMAMALI).

    *Var olan bir yolu "ölçülemez" ilan etmek, ölçmemenin en kolay yoludur.*

    ## Yönetici özeti neden buradan üretiliyor

    İçgörü kartlarının **birleşimi**dir ve `interpret()`'in zaten hesapladığı olgulardan
    gelir — **yeni bir anlatı motoru yazılmaz**. LLM çağrılmaz; özet bir **derleme**dir,
    bir yorum değil.
    """
    from datetime import date

    kaynaklar = [
        {"blok": b.get("title") or f"#{i + 1}", "contract_id": b.get("contract_id"),
         "cube": (b.get("cube_query") or {}).get("cube")}
        for i, b in enumerate(blocks)
    ]
    olgular: list[str] = []
    for b in blocks:
        for f in ((b.get("interpretation") or {}).get("facts") or [])[:2]:
            metin = str(f.get("text") or "").strip()
            if metin and metin not in olgular:
                olgular.append(metin)
    return {
        "kapak": {
            "baslik": spec.get("title") or "Rapor",
            "tarih": str(spec.get("tarih") or date.today().isoformat()),
            # ⚠ Yazar **uydurulmaz**: verilmediyse `None` kalır. Bir raporun altına
            # olmayan bir ad yazmak, o raporu kimsenin savunmadığı bir belge yapar.
            "yazar": spec.get("yazar") or None,
        },
        "yonetici_ozeti": olgular[:8],
        # 🔴 KAYNAK LİSTESİ — `pages`'ten BAĞIMSIZ ve her formatta altta kalır.
        "kaynaklar": kaynaklar,
        # ⊘ Kapının ölçemediği şey **yazılı**: bu üç dışa aktarıcı depoda YOK.
        # ⚠ **PDF listede DEĞİL**: `window.print()` yolu var ve kaynak listesi o baskıda
        # görünüyor (`ReportView`, `print:hidden` taşımıyor). *Var olan bir yolu
        # "ölçülemez" ilan etmek, ölçmemenin en kolay yoludur.*
        "olculemeyen_formatlar": ["word", "excel"],
    }
