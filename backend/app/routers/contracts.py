"""Query Contract uçları (ADR-0010): listele, görüntüle, REPLAY (üç seviyeli teşhis)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import require, require_company
from app.config import get_settings
from app.contracts import result_hash, sql_equal
from control_plane.authorize import Principal

# Rapor görmekle eşdeğer: viewer dahil herkes okuyabilir/replay edebilir.
router = APIRouter(tags=["contracts"], dependencies=[Depends(require("contract:read"))])


def _scope(request: Request) -> tuple[str | None, bool]:
    """(tenant_id, include_legacy) — tenant_id'siz eski kayıtlar yalnız aktif
    şirketin tenant'ına görünür (tenant-RLS)."""
    p: Principal | None = getattr(request.state, "principal", None)
    tid = getattr(p, "tenant_id", None)
    legacy = p is not None and p.tenant_slug == get_settings().company
    return tid, legacy


@router.get("/contracts")
def list_contracts(request: Request, limit: int = 20) -> dict:
    store = request.app.state.contracts
    tid, legacy = _scope(request)
    return {"contracts": store.recent(limit=min(limit, 100), tenant_id=tid,
                                      include_legacy=legacy)}


@router.get("/contracts/{cid}")
def get_contract(request: Request, cid: str) -> dict:
    tid, legacy = _scope(request)
    rec = request.app.state.contracts.get(cid, tenant_id=tid, include_legacy=legacy)
    if rec is None:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı.")
    return rec


@router.get("/contracts/{cid}/replay", dependencies=[Depends(require_company)])
def replay_contract(request: Request, cid: str) -> dict:
    """Sözleşmeyi bugün yeniden oynat ve farkı TEŞHİS et.

    CubeQuery varsa IR bugünkü şemayla YENİDEN DERLENİR (SQL-sözleşmeden güçlü:
    şema evrimi sonrası da cevap verir); yoksa saklanan SQL aynen koşulur.
    """
    store = request.app.state.contracts
    from app.company_registry import wren_for_request

    svc = wren_for_request(request)
    tid, legacy = _scope(request)
    rec = store.get(cid, tenant_id=tid, include_legacy=legacy)
    if rec is None:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı.")

    new_sql: str | None = None
    compile_error: str | None = None
    if rec.get("cube_query"):
        try:
            new_sql = svc.cube_sql(rec["cube_query"])
        except Exception as exc:
            compile_error = str(exc)
    if new_sql is None and compile_error is None:
        new_sql = rec.get("sql")

    if compile_error is not None:
        return {
            "contract": rec,
            "replay": {
                "verdict": "DERLENEMEDİ — CubeQuery bugünkü şemada geçersiz (cube/ölçü kaldırılmış olabilir)",
                "error": compile_error,
                "schema_version_now": svc.mdl_version,
                "schema_changed": svc.mdl_version != rec.get("schema_version"),
            },
        }

    res = svc.query(new_sql, limit=1000)
    nh = result_hash(res)
    sql_match = sql_equal(new_sql, rec.get("sql"))
    result_match = nh == rec.get("result_hash")
    if result_match:
        verdict = "AYNI — sonuç birebir doğrulandı"
    elif sql_match:
        verdict = "VERİ DEĞİŞTİ — aynı SQL bugün farklı sonuç veriyor (kaynağa kayıt girmiş/değişmiş; motor masum)"
    else:
        verdict = "TANIM DEĞİŞTİ — aynı CubeQuery bugün farklı SQL üretiyor (cube/şema evrimi)"
    return {
        "contract": rec,
        "replay": {
            "sql": new_sql,
            "result_hash": nh,
            "row_count": res.get("row_count"),
            "sql_match": sql_match,
            "result_match": result_match,
            "schema_version_now": svc.mdl_version,
            "schema_changed": svc.mdl_version != rec.get("schema_version"),
            "verdict": verdict,
        },
    }
