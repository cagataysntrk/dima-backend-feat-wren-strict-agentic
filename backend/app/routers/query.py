"""Schema + raw SQL endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import require, require_company
from app.config import get_settings
from app.schemas import QueryRequest, QueryResult, SchemaResponse
from app.wren_service import UnsafeSqlError

router = APIRouter(tags=["query"])


@router.get("/schema", response_model=SchemaResponse,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def get_schema(request: Request) -> SchemaResponse:
    try:
        from app.company_registry import wren_for_request

        return SchemaResponse(**wren_for_request(request).schema())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/query", response_model=QueryResult,
             dependencies=[Depends(require("sql:run")), Depends(require_company)])
def run_query(request: Request, body: QueryRequest) -> QueryResult:
    settings = get_settings()
    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)
    try:
        from app.company_registry import wren_for_request

        result = wren_for_request(request).query(body.sql, limit=limit)
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
    # (app/routers/ask.py::_finish ile AYNI ilke).
    if result.get("rows"):
        from app.pii import mask_rows
        from control_plane.authorize import can

        has_pii_view = principal is not None and can(principal, "pii:view")
        masked_rows, found = mask_rows(result["rows"])
        if found:
            if has_pii_view:
                audit.record(principal, "pii_view", generated_sql=body.sql,
                            ip=request.client.host if request.client else None)
            else:
                result = {**result, "rows": masked_rows}

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

        return {"planned_sql": wren_for_request(request).dry_plan(body.sql)}
    except UnsafeSqlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
