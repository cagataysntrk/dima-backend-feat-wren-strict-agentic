"""Schema + raw SQL endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app import katman_b
from app.auth.dependencies import require, require_company
from app.config import get_settings
from app.features import resolve_for
from app.schemas import QueryRequest, QueryResult, SchemaResponse
from app.wren_service import UnsafeSqlError

router = APIRouter(tags=["query"])


@router.get("/schema", response_model=SchemaResponse,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def get_schema(request: Request, scope: str | None = None) -> SchemaResponse:
    """Katalog — **FAZ 2.3'ten beri kapsam merceğiyle daraltılabilir.**

    🔴 Mercek bir **GÖRÜNÜRLÜK** aracıdır, bir **güvenlik sınırı DEĞİL**: burada yapılan
    tek şey, dönen **cube listesini kısaltmaktır**. Yetkiyi `authorize()` + RLS koyar ve
    merceği kapatmak **hiçbir yetki açmaz** — kapı bunu tersinden de doğruluyor
    (`daralt()` her zaman tam kümenin **alt kümesini** döner).

    ⚠ Mercek `/schema`'ya bağlandı, `/ask`'e değil: kullanıcının **gördüğü katalog**
    burada üretiliyor. Cevaplama yoluna bağlamak, bir görünürlük tercihini **sonuca**
    karıştırmak olurdu — aynı soru, mercek değişince farklı sayı döndürürdü.
    """
    try:
        from app.company_registry import wren_for_request

        from app import kapsam as _kapsam
        from app.kademeli_dusus import istekten_rapor

        sema = dict(wren_for_request(request).schema())
        p = getattr(request.state, "principal", None)
        if "kapsam_mercegi" in resolve_for(get_settings(), p):
            k = _kapsam.gecerli(scope)
            if not _kapsam.izinli_mi(k, p):
                raise HTTPException(
                    status_code=403,
                    detail="`portfoy` kapsamı için çok-tenant yetkisi gerekiyor.")
            gorunur = set(_kapsam.daralt(sema, k, departman=getattr(p, "departman", None)))
            sema["cubes"] = [c for c in (sema.get("cubes") or [])
                             if c.get("name") in gorunur]
        return SchemaResponse(**{**sema, **istekten_rapor(request)})
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# FAZ 1.3b — Katman B'nin **TEK SAHİBİ** `app/katman_b.py::zorla`'dır.
#
# ⟳ **FAZ 1.3b/2 (2026-08-04): gövde BURADAN TAŞINDI.** İlk turda bu dosyada özel bir
# `_katman_b`/`_allowlist` çifti vardı ve gerekçesi yazılıydı (*"`/ask`'in Discovery dalı
# İKİNCİ çağrı yoludur ve ayrı bir turda bağlanır"*). O tur geldi — ve ikinci bir kopya
# yazmak *"aynı kuralın iki sahibi"* olurdu: biri güncellenir, öteki unutulurdu ve bir
# güvenlik katmanı için bu **en sessiz** kırılma biçimidir. Taşındı, kopyalanmadı.


@router.post("/query", response_model=QueryResult,
             dependencies=[Depends(require("sql:run")), Depends(require_company)])
def run_query(request: Request, body: QueryRequest) -> QueryResult:
    settings = get_settings()
    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)
    try:
        from app.company_registry import wren_for_request

        wren = wren_for_request(request)
        katman_b.zorla(request, wren, body.sql)
        # FAZ 1.2 — kimlik motora GEÇER: kolon düzeyi erişim denetimi (`motor_cls`)
        # zorunlu bir session property ister ve o property principal'dan türer.
        result = wren.query(body.sql, limit=limit,
                            principal=getattr(request.state, "principal", None))
    except katman_b.ModelErisimReddi as exc:
        # 🔴 FAZ 1.3b/2 — **YETKİ REDDİ BİR SORGU HATASI DEĞİLDİR.** Bugüne kadar aşağıdaki
        # `except Exception` onu yakalayıp **422** ("engine / DB errors") döndürüyordu:
        # istemci bunu *"sorgum bozuk"* diye okur, geliştirici motorda arar. Bir yetki
        # sınırının kendini bir ARIZA gibi göstermesi, sınırın kendisini görünmez kılar.
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except UnsafeSqlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # engine / DB errors
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    # AUDIT (ADR-0014 Karar 6): ham SQL erişimi de kanıtlanabilir iz bırakır.
    from control_plane import audit

    principal = getattr(request.state, "principal", None)
    # PII maskeleme (Faz 4.14, 1 Ağustos 2026): `/query` ham SQL'dir (`sql:run`,
    # analyst+) — cube katalogunun aksine HERHANGİ bir kolonu seçebilir (ör.
    # `personel_ozluk.tc_kimlik`) — bu yüzden BU uç da app/pii.py'den geçer
    # (app/routers/ask.py::_finish ile AYNI ilke). Paylaşılan `mask_query_result`
    # (1 Ağustos 2026 doğrulama turu) — `/report`/pano/zamanlanmış teslim de AYNISINI kullanır.
    from app.pii import mask_query_result

    result, unmasked_pii_shown = mask_query_result(result, principal)
    if unmasked_pii_shown:
        audit.record(principal, "pii_view", generated_sql=body.sql,
                    ip=request.client.host if request.client else None)

    audit.record(principal, "query",
                 generated_sql=body.sql, rows_returned=result.get("row_count"),
                 ip=request.client.host if request.client else None)
    return QueryResult(**result)


@router.post("/dry-plan", dependencies=[Depends(require("sql:run")),
                                        Depends(require_company)])
def dry_plan(request: Request, body: QueryRequest) -> dict:
    """Transpile SQL through the semantic layer (no DB execution)."""
    try:
        from app.company_registry import wren_for_request

        return {"planned_sql": wren_for_request(request).dry_plan(
            body.sql, principal=getattr(request.state, "principal", None))}
    except UnsafeSqlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
