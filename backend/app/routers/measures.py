"""/measures — Discovery→Promote ölçü yaşam-döngüsü (Faz 2d, 31 Temmuz 2026).

Discovery (ham-SQL LLM) yolunun ürettiği cevaplar `MeasureCandidate` taslağı olarak
best-effort yakalanır (`app/routers/ask.py::_capture_measure_candidate`). Bu router
reviewer'ın (`analyst`: yalnız görüntüle — `measure:read`; `admin`+: onayla/reddet/
deprecate et — `measure:approve`) bunları karara bağlamasını sağlar.

PUBLIC-PLANE (admin_app'in ayrı superadmin JWT'si DEĞİL) — `admin_app/routers/synonyms.py`'nin
kanıtlanmış aday→onay→additive-overlay deseninin ÖLÇÜ-seviyesi genişlemesi. Blast-radius
KATEGORİK olarak farklı (yanlış bir ölçü = yeni SQL/join/agregasyon riski — çift-sayım/grain
uyuşmazlığı; yanlış bir eşanlamlıdan çok daha tehlikeli): onay AYRICA `expression`'ı
`dry_plan`'dan geçirir + eşleşen bir altın-vaka (golden_case) zorunlu kılar. Geri-alma YAML'dan
SİLME değil `MeasureOverride` (suppress) overlay'idir — kanıt silinmez (ADR ilkesi), eski VQR/
dashboard/Contract kullanımları kırılmaz.
"""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, col, select

from app.auth.dependencies import require, require_company
from app.company_registry import wren_for_request
from control_plane.db import get_session
from control_plane.models import MeasureCandidate, MeasureOverride

router = APIRouter(prefix="/measures", tags=["measures"])

_EVAL_CASES_PATH = Path(__file__).resolve().parent.parent.parent / "eval" / "cases.yaml"


def _principal(request: Request):
    return getattr(request.state, "principal", None)


def _scope_slug(principal) -> str | None:
    """Superadmin hariç, aday sorguları yalnız KENDİ tenant'ına kapsanır (izolasyon)."""
    if principal is None or getattr(principal, "is_superadmin", False):
        return None
    return getattr(principal, "tenant_slug", None)


def _out(c: MeasureCandidate) -> dict:
    return {
        "id": str(c.id), "status": c.status, "company": c.company,
        "tenant_id": str(c.tenant_id) if c.tenant_id else None,
        "question": c.question, "sql": c.sql,
        "sample_rows": json.loads(c.sample_rows_json) if c.sample_rows_json else None,
        "cube": c.cube, "measure_name": c.measure_name, "expression": c.expression,
        "measure_type": c.measure_type, "label": c.label,
        "synonyms": json.loads(c.synonyms_json) if c.synonyms_json else [],
        "lower_is_better": c.lower_is_better, "golden_case_id": c.golden_case_id,
        "review_note": c.review_note, "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
    }


@router.get("/candidates",
           dependencies=[Depends(require("measure:read")), Depends(require_company)])
def list_candidates(request: Request, status: str | None = None, limit: int = 100,
                    session: Session = Depends(get_session)) -> dict:
    """Aday listesi (durum filtresi) — yalnız KENDİ tenant'ı (superadmin hepsini görür)."""
    p = _principal(request)
    q = select(MeasureCandidate).where(col(MeasureCandidate.deleted_at).is_(None))
    slug = _scope_slug(p)
    if slug is not None:
        q = q.where(MeasureCandidate.company == slug)
    if status:
        q = q.where(MeasureCandidate.status == status)
    q = q.order_by(col(MeasureCandidate.created_at).desc()).limit(limit)
    return {"candidates": [_out(c) for c in session.exec(q).all()]}


def _get_candidate(session: Session, cid: str, principal) -> MeasureCandidate:
    try:
        c = session.get(MeasureCandidate, _uuid.UUID(cid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz id")
    if c is None or c.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Aday bulunamadı")
    slug = _scope_slug(principal)
    if slug is not None and c.company != slug:
        raise HTTPException(status_code=404, detail="Aday bulunamadı")  # varlığı sızmaz
    return c


@router.get("/candidates/{cid}",
           dependencies=[Depends(require("measure:read")), Depends(require_company)])
def get_candidate(cid: str, request: Request,
                  session: Session = Depends(get_session)) -> dict:
    c = _get_candidate(session, cid, _principal(request))
    out = _out(c)
    # Hedef cube ZATEN seçilmişse (ikinci bir inceleme turu), çakışma ön-kontrolü göster.
    if c.cube and c.measure_name:
        try:
            schema = wren_for_request(request).schema()
            cube_meta = next((x for x in schema.get("cubes", []) if x.get("name") == c.cube), None)
            out["name_conflict"] = bool(
                cube_meta and c.measure_name in (cube_meta.get("measures") or []))
        except Exception:
            out["name_conflict"] = None
    return out


@router.get("/candidates/{cid}/blast-radius",
           dependencies=[Depends(require("measure:read")), Depends(require_company)])
def blast_radius(cid: str, request: Request, cube: str, measure_name: str,
                 session: Session = Depends(get_session)) -> dict:
    """En-iyi-çaba kullanım taraması (deprecate ÖNCESİ): `verified_query`/`dashboard_widget`/
    `contract_log`'un `cube_query_json`'ında (yapısal) + Discovery kayıtlarının ham `sql`
    metninde (Contract'ın Discovery-yolu kayıtları CubeQuery taşımaz — yalnız METİN arama
    mümkün) bu ölçü adı aranır. TAM değil YAKLAŞIK bir sayıdır — reviewer'a "N potansiyel
    kullanım" olarak gösterilir, deprecate'i ENGELLEMEZ, yalnız bilgilendirir."""
    _get_candidate(session, cid, _principal(request))  # yalnız erişim/varlık kontrolü
    from control_plane.models import ContractLog, DashboardWidget, VerifiedQuery

    def _cq_hits(rows: list[str | None]) -> int:
        n = 0
        for raw in rows:
            if not raw:
                continue
            try:
                cq = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if cq.get("cube") == cube and measure_name in (cq.get("measures") or []):
                n += 1
        return n

    vqr_rows = session.exec(select(VerifiedQuery.cube_query_json).where(
        col(VerifiedQuery.deleted_at).is_(None))).all()
    widget_rows = session.exec(select(DashboardWidget.cube_query_json).where(
        col(DashboardWidget.deleted_at).is_(None))).all()
    contract_cq_rows = session.exec(select(ContractLog.cube_query_json)).all()
    contract_sql_rows = session.exec(select(ContractLog.sql).where(
        col(ContractLog.cube_query_json).is_(None))).all()

    text_hits = sum(1 for sql in contract_sql_rows if sql and measure_name in sql)

    return {
        "verified_query": _cq_hits(vqr_rows),
        "dashboard_widget": _cq_hits(widget_rows),
        "contract_log_structured": _cq_hits(contract_cq_rows),
        "contract_log_raw_sql_text_match": text_hits,
        "note": "Yaklaşık tarama (best-effort) — özellikle ham-SQL metin eşleşmesi TAM değildir.",
    }


class MeasureReject(BaseModel):
    note: str | None = None


@router.post("/candidates/{cid}/reject",
            dependencies=[Depends(require("measure:approve")), Depends(require_company)])
def reject_candidate(cid: str, body: MeasureReject, request: Request,
                     session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    c = _get_candidate(session, cid, p)
    if c.status not in ("draft", "pending_review"):
        raise HTTPException(status_code=409, detail=f"Aday zaten '{c.status}' durumunda")
    c.status = "rejected"
    c.review_note = body.note
    c.reviewed_by = _uuid.UUID(p.user_id) if p and getattr(p, "user_id", None) else None
    c.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(c)
    session.commit()
    from control_plane import audit

    audit.record(p, "measure_reject", nl_question=f"aday reddedildi: {c.question[:80]}",
                ip=request.client.host if request.client else None)
    return _out(c)


class GoldenCaseIn(BaseModel):
    id: str
    q: str
    tags: list[str] = []
    expect: str = "answer"
    shape: dict = {}


class MeasureApprove(BaseModel):
    cube: str
    measure_name: str
    expression: str
    type: str = "DOUBLE"
    label: str | None = None
    synonyms: list[str] = []
    lower_is_better: bool | None = None
    golden_case: GoldenCaseIn


def _yaml_inline(v) -> str:
    s = yaml.safe_dump(v, default_flow_style=True, allow_unicode=True, sort_keys=False).strip()
    if s.endswith("\n..."):
        s = s[:-4]
    elif s == "...":
        s = ""
    return s


def _append_golden_case(case: GoldenCaseIn) -> None:
    """`eval/cases.yaml`'a yeni bir vaka EKLER (dosya sonuna, salt metin — ruamel/pyyaml
    tam-dosya round-trip YAPILMAZ: bu dosya bol açıklayıcı bölüm-yorumlarıyla dolu, tam
    parse+dump bunları SİLERDİ; salt-ekleme dosyanın geri kalanını bayt-birebir korur)."""
    lines = [f"- id: {_yaml_inline(case.id)}", f"  q: {_yaml_inline(case.q)}"]
    if case.tags:
        lines.append(f"  tags: {_yaml_inline(case.tags)}")
    lines.append(f"  expect: {_yaml_inline(case.expect)}")
    if case.shape:
        lines.append(f"  shape: {_yaml_inline(case.shape)}")
    text = "\n".join(lines) + "\n"
    with _EVAL_CASES_PATH.open("a", encoding="utf-8") as f:
        f.write(text)


@router.post("/candidates/{cid}/approve",
            dependencies=[Depends(require("measure:approve")), Depends(require_company)])
def approve_candidate(cid: str, body: MeasureApprove, request: Request,
                      session: Session = Depends(get_session)) -> dict:
    """Adayı kalıcı MDL ölçüsüne yükseltir: (1) hedef cube'da AD ÇAKIŞMASI yok mu, (2)
    `expression` GERÇEK şemaya karşı `dry_plan`'dan geçiyor mu, (3) eşleşen bir altın-vaka
    zorunlu (Pydantic model zaten `golden_case` alanını required yapıyor) — YALNIZ bunların
    HEPSİ geçerse YAML'a yazılır + eval/cases.yaml'a eklenir + tenant'ın şeması TAZELENİR
    (materializer'ın 60sn döngüsü BU değişikliği YAKALAMAZ — TenantConfig'e dayanır, ham
    YAML dosya değişikliğine değil; bu yüzden burada AÇIKÇA tetiklenir)."""
    p = _principal(request)
    c = _get_candidate(session, cid, p)
    if c.status not in ("draft", "pending_review"):
        raise HTTPException(status_code=409, detail=f"Aday zaten '{c.status}' durumunda")

    service = wren_for_request(request)
    schema = service.schema()
    cube_meta = next((x for x in schema.get("cubes", []) if x.get("name") == body.cube), None)
    if cube_meta is None:
        raise HTTPException(status_code=400, detail=f"Bilinmeyen cube: {body.cube}")
    if body.measure_name in (cube_meta.get("measures") or []):
        raise HTTPException(status_code=409,
                            detail=f"'{body.measure_name}' ölçüsü '{body.cube}'da ZATEN var")

    from app import mdl_writer
    from app.config import get_settings

    settings = get_settings()
    base = service.project_dir.parent
    company = getattr(service, "company_slug", None) or settings.company
    try:
        yaml_path = mdl_writer.resolve_cube_yaml_for_edit(base, company, body.cube,
                                                          service.project_dir)
    except mdl_writer.MeasureWriteError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    base_object = mdl_writer.cube_base_object(yaml_path)
    if not base_object:
        raise HTTPException(status_code=400,
                            detail=f"Cube base_object bulunamadı: {body.cube}")

    try:
        service.dry_plan(f"SELECT {body.expression} AS val FROM {base_object}")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"expression geçersiz (dry_plan): {exc}")

    try:
        mdl_writer.add_measure_to_cube_yaml(
            yaml_path, measure_name=body.measure_name, expression=body.expression,
            type_=body.type, synonyms=body.synonyms, lower_is_better=body.lower_is_better,
            label=body.label)
    except mdl_writer.MeasureWriteError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    _append_golden_case(body.golden_case)

    # Şema tazeleme: materializer'ın TenantConfig-tabanlı 60sn döngüsü ham YAML dosya
    # değişikliğini YAKALAMAZ (bkz. app/materialize.py) — burada AÇIKÇA tetiklenir.
    if company == settings.company:
        from app.compose import compose_and_build

        compose_and_build(settings)
        service.invalidate_schema_cache()
    else:
        registry = getattr(request.app.state, "company_registry", None)
        if registry is not None:
            registry.invalidate(company)

    c.status = "approved"
    c.cube = body.cube
    c.measure_name = body.measure_name
    c.expression = body.expression
    c.measure_type = body.type
    c.label = body.label
    c.synonyms_json = json.dumps(body.synonyms, ensure_ascii=False)
    c.lower_is_better = body.lower_is_better
    c.golden_case_id = body.golden_case.id
    c.reviewed_by = _uuid.UUID(p.user_id) if p and getattr(p, "user_id", None) else None
    c.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(c)
    session.commit()

    from control_plane import audit

    audit.record(p, "measure_approve",
                nl_question=f"{body.cube}.{body.measure_name} onaylandı (aday: {c.question[:80]})",
                generated_sql=body.expression,
                ip=request.client.host if request.client else None)
    return _out(c)


class MeasureDeprecate(BaseModel):
    reason: str | None = None
    superseded_by_measure: str | None = None


@router.post("/candidates/{cid}/deprecate",
            dependencies=[Depends(require("measure:approve")), Depends(require_company)])
def deprecate_candidate(cid: str, body: MeasureDeprecate, request: Request,
                        session: Session = Depends(get_session)) -> dict:
    """Onaylanmış bir ölçüyü YAML'dan SİLMEDEN NL-routing'ten gizler (`MeasureOverride`
    overlay — `WrenService._apply_measure_overrides`): eski VQR/dashboard/Contract
    kullanımları KIRILMAZ (kanıt silinmez), yalnız `route()` bir daha ÖNERMEZ."""
    p = _principal(request)
    c = _get_candidate(session, cid, p)
    if c.status != "approved":
        raise HTTPException(status_code=409,
                            detail=f"Yalnız 'approved' adaylar deprecate edilebilir (şu an: {c.status})")
    if not c.cube or not c.measure_name:
        raise HTTPException(status_code=409, detail="Adayın cube/measure_name bilgisi eksik")

    override = MeasureOverride(
        scope_type="tenant" if c.company else "global", scope_id=c.company or None,
        cube=c.cube, measure_name=c.measure_name, reason=body.reason,
        candidate_id=c.id, superseded_by_measure=body.superseded_by_measure,
        updated_by=_uuid.UUID(p.user_id) if p and getattr(p, "user_id", None) else None,
    )
    session.add(override)
    c.status = "deprecated"
    c.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(c)
    session.commit()

    service = wren_for_request(request)
    service.invalidate_schema_cache()  # overlay hemen görünsün (compose gerekmez)

    from control_plane import audit

    audit.record(p, "measure_deprecate",
                nl_question=f"{c.cube}.{c.measure_name} gizlendi (NL-routing'ten) — {body.reason or ''}",
                ip=request.client.host if request.client else None)
    return _out(c)
