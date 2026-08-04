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

        from app.kademeli_dusus import istekten_rapor

        return SchemaResponse(**{**wren_for_request(request).schema(),
                                 **istekten_rapor(request)})
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _katman_b(request: Request, wren, sql: str) -> None:
    """FAZ 1.3b — **Katman B'nin İLK GERÇEK ÇAĞRI YOLU.**

    Ölçüldü: `enforce_query` bir stub'dı **ve çağıranı yoktu**. Bir stub'ı doldurmak
    yetmez; katman ancak **çağrıldığı yerde** vardır.

    ## Neden ham SQL ucu

    `POST /query` semantik katmanı **atlayarak** kullanıcı SQL'i alan yoldur — Katman B'nin
    en doğrudan hedefi. `/ask`'in Discovery dalı **ikinci** çağrı yoludur ve ayrı bir
    turda bağlanır: `routers/ask.py` **risk sınırındadır** (`OPERASYON.md §3`), yani
    dokunan madde demete girmez, kendi kapısını koşar. Sessizce atlanmadı — **sırası
    yazıldı**.

    ## Neden burada, `WrenService`'te değil

    `WrenService` **şirket** kapsamlıdır, **kullanıcı** kapsamlı değil: `principal`'ı
    bilmez. Yetki kararını oraya taşımak, servise kimlik bilgisi sızdırmak ve iki farklı
    kapsamı tek nesnede bindirmek olurdu.
    """
    from control_plane.authorize import enforce_query

    # `get_current_principal` onu isteğe **zaten** iliştiriyor (`request.state.principal`);
    # bağımlılığı ikinci kez çözmek, aynı token'ı iki kez doğrulamak olurdu.
    principal = getattr(request.state, "principal", None)
    if principal is None or getattr(principal, "is_superadmin", False):
        return                       # superadmin: ADR-0015 K7 — ENGEL değil GÖRÜNÜRLÜK
    izinliler = _allowlist(request, principal)
    if izinliler is None:
        return                       # Katman B yapılandırılmamış — Katman A yönetir
    from app.katman_b import referans_modeller

    adlar = {m.get("name") for m in (wren.schema().get("models") or []) if m.get("name")}
    enforce_query(principal, sorted(referans_modeller(sql, adlar)), izinliler)


def _allowlist(request: Request, principal) -> set[str] | None:
    """`ModelPermission` allowlist'i — oturum yoksa **None** (yapılandırılmamış).

    ⚠ `None` ile `set()` farkı burada da korunur: DB'ye ulaşamamak *"izin yok"* demek
    değildir. Ulaşılamayan bir yetki deposunu **boş allowlist** saymak, bir altyapı
    arızasını **tam kesintiye** çevirirdi.
    """
    try:
        from app.katman_b import izinli_modeller
        from control_plane.db import get_session
    except ImportError:
        return None
    try:
        with next(get_session()) as oturum:                  # type: ignore[call-overload]
            return izinli_modeller(principal, oturum)
    except Exception:                                        # noqa: BLE001
        return None


@router.post("/query", response_model=QueryResult,
             dependencies=[Depends(require("sql:run")), Depends(require_company)])
def run_query(request: Request, body: QueryRequest) -> QueryResult:
    settings = get_settings()
    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)
    try:
        from app.company_registry import wren_for_request

        wren = wren_for_request(request)
        _katman_b(request, wren, body.sql)
        # FAZ 1.2 — kimlik motora GEÇER: kolon düzeyi erişim denetimi (`motor_cls`)
        # zorunlu bir session property ister ve o property principal'dan türer.
        result = wren.query(body.sql, limit=limit,
                            principal=getattr(request.state, "principal", None))
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
