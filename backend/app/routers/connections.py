"""Tenant-kendi-hizmeti DB bağlama sihirbazı (Faz 4.5, 31 Temmuz 2026 — dış yol haritası
1.1/1.2/1.4/1.8/kısmen 1.11a-e'nin GERÇEK-DB-ODAKLI karşılığı).

`admin_app/routers/connections.py`'nin (superadmin-only, yalnız mssql) TENANT-PLANE
karşılığı: bir tenant kullanıcısı KENDİ Postgres veritabanına bağlanabilir, gerçek şema
introspection'ından (app/db_introspect.py) üretilen taslak MDL'i İNCELEYİP onaylayabilir.
Tenant HER ZAMAN principal'dan türetilir — request body'den ASLA (backend/CLAUDE.md:
"Tenant DAİMA token'dan türetilir, request girdisinden asla").

Bu, 4.3'te (Excel/CSV) BİLEREK yapılmayan kalıcılık/çok-tablo/ilişki desteğinin doğru
yeridir: gerçek bir ilişkisel veritabanının FK'leri introspect EDİLİR (tahmin değil)."""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.auth.dependencies import require, require_company
from app.logging_setup import get_logger
from app.schemas import (
    ConnectionConfirmResult,
    ConnectionDraft,
    ConnectionTestResult,
    DraftCube,
    DraftRelationship,
    TenantConnectionCreate,
    TenantConnectionOut,
)
from control_plane.config import get_auth_settings
from control_plane.crypto import CredKeyError, decrypt_secret, encrypt_secret
from control_plane.db import engine
from control_plane.models import DbConnection

router = APIRouter(prefix="/connections", tags=["connections"])
_log = get_logger("connections")


def _tenant_uuid(request: Request) -> _uuid.UUID:
    principal = getattr(request.state, "principal", None)
    tid = getattr(principal, "tenant_id", None)
    if not tid:
        raise HTTPException(status_code=403, detail="Tenant bağlamı yok (superadmin bu uçları kullanamaz).")
    try:
        return _uuid.UUID(str(tid))
    except ValueError:
        raise HTTPException(status_code=403, detail="Geçersiz tenant bağlamı.")


def _url_for(body: TenantConnectionCreate) -> str:
    from app.db_introspect import build_sqlalchemy_url

    try:
        return build_sqlalchemy_url(body.datasource, host=body.host, port=body.port,
                                    database=body.database, user=body.user,
                                    password=body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _out(conn: DbConnection) -> TenantConnectionOut:
    meta = json.loads(conn.conn_meta_json) if conn.conn_meta_json else {}
    return TenantConnectionOut(
        id=str(conn.id), datasource=conn.datasource,
        host=str(meta.get("host") or ""), port=int(meta.get("port") or 0),
        database=str(meta.get("database") or ""), user=str(meta.get("user") or ""),
        has_secret=conn.secret_ciphertext is not None,
    )


def _get_own(session: Session, request: Request, cid: str) -> DbConnection:
    """Yalnız ARAYAN TENANT'IN KENDİ bağlantısı — başka tenant'ın bağlantı id'si 404 döner
    (varlık sızmaz, admin_app'in _get'inden farkı tam olarak bu tenant-izolasyonu)."""
    tenant_uuid = _tenant_uuid(request)
    try:
        conn = session.get(DbConnection, _uuid.UUID(cid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz bağlantı id")
    if conn is None or conn.tenant_id != tenant_uuid:
        raise HTTPException(status_code=404, detail="Bağlantı bulunamadı")
    return conn


def _decrypt_url(conn: DbConnection) -> str:
    from app.db_introspect import build_sqlalchemy_url

    meta = json.loads(conn.conn_meta_json) if conn.conn_meta_json else {}
    if conn.secret_ciphertext is None:
        raise HTTPException(status_code=409, detail="Bağlantının kayıtlı sırrı yok.")
    try:
        password = decrypt_secret(conn.secret_ciphertext, get_auth_settings().cred_kek)
    except CredKeyError as exc:
        raise HTTPException(status_code=500, detail=f"KEK hatası: {exc}")
    return build_sqlalchemy_url(conn.datasource, host=str(meta.get("host") or ""),
                                port=int(meta.get("port") or 5432),
                                database=str(meta.get("database") or ""),
                                user=str(meta.get("user") or ""), password=password)


@router.post("/test", response_model=ConnectionTestResult,
             dependencies=[Depends(require("connection:write")), Depends(require_company)])
def test_new_connection(body: TenantConnectionCreate) -> ConnectionTestResult:
    """Kaydetmeden ÖNCE dry-run — sihirbazın "bağlantıyı test et" adımı (hiçbir şey
    kaydedilmez, yalnız `SELECT 1` doğrular)."""
    from app.db_introspect import ConnectionTestError, check_connection

    url = _url_for(body)
    try:
        check_connection(url)
    except ConnectionTestError as exc:
        return ConnectionTestResult(ok=False, detail=str(exc))
    return ConnectionTestResult(ok=True, detail="Bağlantı başarılı.")


@router.post("", response_model=TenantConnectionOut, status_code=201,
             dependencies=[Depends(require("connection:write")), Depends(require_company)])
def create_connection(body: TenantConnectionCreate, request: Request) -> TenantConnectionOut:
    """Fail-closed: dry-run BAŞARISIZSA sır DB'ye asla yazılmaz (admin_app'in
    test_connection'ıyla AYNI ilke, burada create-öncesi zorunlu adım)."""
    from app.db_introspect import ConnectionTestError, check_connection

    url = _url_for(body)
    try:
        check_connection(url)
    except ConnectionTestError as exc:
        raise HTTPException(status_code=400, detail=f"Bağlantı kurulamadı: {exc}")

    tenant_uuid = _tenant_uuid(request)
    try:
        secret = encrypt_secret(body.password, get_auth_settings().cred_kek)
    except CredKeyError as exc:
        raise HTTPException(status_code=500, detail=f"KEK hatası: {exc}")

    conn = DbConnection(
        tenant_id=tenant_uuid, datasource=body.datasource, topology="cloud_direct",
        conn_meta_json=json.dumps({"host": body.host, "port": body.port,
                                   "database": body.database, "user": body.user}),
        secret_ciphertext=secret, read_only_verified=False,
    )
    with Session(engine) as s:
        s.add(conn)
        s.commit()
        s.refresh(conn)

    from control_plane import audit

    audit.record(getattr(request.state, "principal", None), "connection_create",
                nl_question=f"{body.datasource} {body.host}:{body.port}/{body.database} "
                           f"({body.user})",
                ip=request.client.host if request.client else None)
    return _out(conn)


@router.get("", response_model=list[TenantConnectionOut],
           dependencies=[Depends(require("connection:read")), Depends(require_company)])
def list_connections(request: Request) -> list[TenantConnectionOut]:
    tenant_uuid = _tenant_uuid(request)
    with Session(engine) as s:
        conns = s.exec(select(DbConnection).where(
            DbConnection.tenant_id == tenant_uuid)).all()
    return [_out(c) for c in conns]


@router.delete("/{cid}", status_code=204,
               dependencies=[Depends(require("connection:write")), Depends(require_company)])
def delete_connection(cid: str, request: Request) -> None:
    with Session(engine) as s:
        conn = _get_own(s, request, cid)
        s.delete(conn)
        s.commit()

    from control_plane import audit

    audit.record(getattr(request.state, "principal", None), "connection_delete",
                nl_question=cid, ip=request.client.host if request.client else None)


@router.get("/{cid}/draft", response_model=ConnectionDraft,
           dependencies=[Depends(require("connection:write")), Depends(require_company)])
def get_draft(cid: str, request: Request) -> ConnectionDraft:
    """İnceleme ekranı için taslak üretir — HİÇBİR DOSYAYA YAZMAZ (yalnız `/confirm`
    yazar, bkz. app/db_introspect.py::draft_mdl docstring'i)."""
    from app.db_introspect import draft_mdl, introspect_schema

    with Session(engine) as s:
        conn = _get_own(s, request, cid)
        url = _decrypt_url(conn)
    try:
        tables = introspect_schema(url)
    except Exception as exc:  # noqa: BLE001 - kullanıcıya dürüst hata, sunucuyu düşürme
        _log.warning("şema introspection başarısız", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Şema okunamadı: {str(exc)[:300]}")
    raw = draft_mdl(tables)
    return ConnectionDraft(
        cubes=[DraftCube(**c) for c in raw["cubes"]],
        relationships=[DraftRelationship(**r) for r in raw["relationships"]],
    )


@router.post("/{cid}/confirm", response_model=ConnectionConfirmResult,
            dependencies=[Depends(require("connection:write")), Depends(require_company)])
def confirm_draft(cid: str, body: ConnectionDraft, request: Request) -> ConnectionConfirmResult:
    """Kullanıcının (muhtemelen düzenlediği) taslağı GERÇEK YAML'a yazar (model+cube+
    relationships.yml — app/mdl_writer.py::write_introspected_schema) — yalnız
    `include=True` cube'lar. Şema TEKRAR introspect edilir: client'ın gönderdiği kolon
    TİPLERİNE güvenilmez (yalnız include/sınıflandırma KARARLARI alınır) — tipler HER
    ZAMAN taze introspection'dan gelir (güvenlik: client keyfi tip uyduramaz).

    KAPSAM SINIRI (bilerek, sessizce değil): bu uç tenant'ın datasource'unu duckdb'den
    postgres'e GEÇİRMEZ — yalnız companies/<slug>/ İÇİNE yeni model/cube/ilişki EKLER.
    Tenant'ın ANA sorgu motoru hâlâ mevcut yapılandırmasını kullanır; bu yeni cube'ların
    NL-routing'e görünür olması için tenant'ın compose/datasource ayarının da bu DB'yi
    işaret etmesi gerekir — bu AYRI, daha büyük bir karar (ayrı onay turu gerektirir)."""
    from app.config import get_settings
    from app.db_introspect import introspect_schema
    from app.mdl_writer import write_introspected_schema

    with Session(engine) as s:
        conn = _get_own(s, request, cid)
        url = _decrypt_url(conn)
    try:
        tables = introspect_schema(url)
    except Exception as exc:  # noqa: BLE001 - kullanıcıya dürüst hata, sunucuyu düşürme
        _log.warning("onay öncesi yeniden-introspection başarısız", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Şema okunamadı: {str(exc)[:300]}")

    principal = getattr(request.state, "principal", None)
    settings = get_settings()
    company = getattr(principal, "tenant_slug", None) or settings.company
    base = settings.resolved_project_dir().parent

    draft_dict = {
        "cubes": [c.model_dump() for c in body.cubes],
        "relationships": [r.model_dump() for r in body.relationships],
    }
    written, added = write_introspected_schema(base, company, tables, draft_dict)

    if written:
        registry = getattr(request.app.state, "company_registry", None)
        if registry is not None:
            registry.invalidate(company)

    from control_plane import audit

    audit.record(principal, "connection_confirm",
                nl_question=f"{company}: {len(written)} cube, {added} ilişki yazıldı",
                ip=request.client.host if request.client else None)
    return ConnectionConfirmResult(written_cubes=written, written_relationships=added)
