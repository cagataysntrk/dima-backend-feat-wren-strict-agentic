"""/sadmin/connections — müşteri DB bağlantı yönetimi (ADR-0017 Faz 2).

Sır (parola) AES-256-GCM ile şifrelenir (KEK yalnız admin ortamında —
``DIMA_CRED_KEK``); host/port/db gibi meta ``conn_meta_json``'da düz durur
(sır DEĞİL — control-plane-sema.md). Test-connection ve introspection bu fazda
yalnız mssql (pyodbc) destekler; upcyman ``CompanyIntegration`` deseninin taşınmasıdır.
"""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from control_plane import audit
from control_plane.config import get_auth_settings
from control_plane.crypto import CredKeyError, decrypt_secret, encrypt_secret
from control_plane.db import get_session
from control_plane.models import DbConnection, Tenant

from admin_app.schemas import (
    ConnectionCreate,
    ConnectionOut,
    ConnectionTestOut,
    FingerprintOut,
)

router = APIRouter(prefix="/sadmin/connections", tags=["sadmin-connections"])

_SUPPORTED = {"mssql", "sqlserver"}


def _meta(conn: DbConnection) -> dict:
    try:
        return json.loads(conn.conn_meta_json) if conn.conn_meta_json else {}
    except ValueError:
        return {}


def _out(conn: DbConnection, tenant: Tenant | None) -> ConnectionOut:
    meta = _meta(conn)
    return ConnectionOut(
        id=str(conn.id),
        tenant=tenant.slug if tenant else "",
        datasource=conn.datasource,
        topology=conn.topology,
        host=str(meta.get("host") or ""),
        port=int(meta.get("port") or 0),
        database=str(meta.get("database") or ""),
        user=str(meta.get("user") or ""),
        has_secret=conn.secret_ciphertext is not None,
    )


def _get(session: Session, cid: str) -> tuple[DbConnection, Tenant | None]:
    try:
        conn = session.get(DbConnection, _uuid.UUID(cid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz bağlantı id")
    if conn is None:
        raise HTTPException(status_code=404, detail="Bağlantı bulunamadı")
    return conn, session.get(Tenant, conn.tenant_id)


def _pyodbc_connect(conn: DbConnection):
    """conn_meta + çözülmüş sır → canlı pyodbc bağlantısı (yalnız mssql)."""
    if conn.datasource not in _SUPPORTED:
        raise HTTPException(
            status_code=501,
            detail=f"Bu fazda yalnız mssql destekli (istenen: {conn.datasource})")
    try:
        import pyodbc
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="pyodbc/ODBC sürücüsü bu ortamda kurulu değil")
    meta = _meta(conn)
    if conn.secret_ciphertext is None:
        raise HTTPException(status_code=409, detail="Bağlantının kayıtlı sırrı yok")
    try:
        password = decrypt_secret(conn.secret_ciphertext, get_auth_settings().cred_kek)
    except CredKeyError as exc:
        raise HTTPException(status_code=500, detail=f"KEK hatası: {exc}")
    parts = [
        "DRIVER={ODBC Driver 18 for SQL Server}",
        f"SERVER={meta.get('host')},{meta.get('port') or 1433}",
        f"DATABASE={meta.get('database')}",
        f"UID={meta.get('user')}",
        f"PWD={password}",
    ]
    if meta.get("trust_server_certificate", True):
        parts.append("TrustServerCertificate=yes")
    try:
        return pyodbc.connect(";".join(parts), timeout=10)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bağlantı kurulamadı: {exc}")


@router.get("", response_model=list[ConnectionOut])
def list_connections(session: Session = Depends(get_session)) -> list[ConnectionOut]:
    return [_out(c, session.get(Tenant, c.tenant_id))
            for c in session.exec(select(DbConnection)).all()]


@router.post("", response_model=ConnectionOut, status_code=201)
def create_connection(body: ConnectionCreate, request: Request,
                      session: Session = Depends(get_session)) -> ConnectionOut:
    try:
        tenant = session.get(Tenant, _uuid.UUID(body.tenant_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz tenant id")
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant bulunamadı")
    if body.datasource not in _SUPPORTED:
        raise HTTPException(
            status_code=400, detail=f"Desteklenmeyen datasource: {body.datasource}")
    try:
        secret = encrypt_secret(body.password, get_auth_settings().cred_kek)
    except CredKeyError as exc:
        # KEK yoksa sır YAZILMAZ (fail-closed) — düz metin saklama yolu yoktur.
        raise HTTPException(status_code=500, detail=f"KEK hatası: {exc}")
    conn = DbConnection(
        tenant_id=tenant.id,
        datasource=body.datasource,
        topology="cloud_direct",
        conn_meta_json=json.dumps({
            "host": body.host, "port": body.port, "database": body.database,
            "user": body.user,
            "trust_server_certificate": body.trust_server_certificate,
        }),
        secret_ciphertext=secret,
    )
    session.add(conn)
    session.commit()
    session.refresh(conn)
    audit.record(getattr(request.state, "principal", None), "connection_create",
                 nl_question=f"tenant: {tenant.slug} → {body.datasource} "
                 f"{body.host}:{body.port}/{body.database} ({body.user})",
                 ip=request.client.host if request.client else None)
    return _out(conn, tenant)


@router.delete("/{cid}", status_code=204)
def delete_connection(cid: str, request: Request,
                      session: Session = Depends(get_session)) -> None:
    conn, tenant = _get(session, cid)
    session.delete(conn)
    session.commit()
    audit.record(getattr(request.state, "principal", None), "connection_delete",
                 nl_question=f"tenant: {tenant.slug if tenant else '?'} → {cid}",
                 ip=request.client.host if request.client else None)


@router.post("/{cid}/test", response_model=ConnectionTestOut)
def test_connection(cid: str, request: Request,
                    session: Session = Depends(get_session)) -> ConnectionTestOut:
    conn, tenant = _get(session, cid)
    live = _pyodbc_connect(conn)
    try:
        cur = live.cursor()
        cur.execute("SELECT DB_NAME(), @@VERSION")
        db_name, version = cur.fetchone()
        cur.close()
    finally:
        live.close()
    audit.record(getattr(request.state, "principal", None), "connection_test",
                 nl_question=f"tenant: {tenant.slug if tenant else '?'} → ok",
                 ip=request.client.host if request.client else None)
    return ConnectionTestOut(ok=True, database=db_name,
                             server_version=version.splitlines()[0].strip())


@router.get("/{cid}/fingerprint", response_model=FingerprintOut)
def fingerprint_connection(cid: str, request: Request,
                           session: Session = Depends(get_session)) -> FingerprintOut:
    """Tablo introspection'ı + kaynak pack imza eşleşmesi + Logo firma/dönem keşfi.

    Panel akışı: bağlantı kur → test → fingerprint → önerilen kaynağı ve (önekli
    şemada) kapsamı TenantConfig'e onayla (superadmin karar verir, sistem önerir)."""
    from app.config import get_settings
    from app.packs import list_packs

    from admin_app.fingerprint import logo_kapsamlari, match_packs

    conn, tenant = _get(session, cid)
    live = _pyodbc_connect(conn)
    try:
        cur = live.cursor()
        cur.execute("SELECT name FROM sys.tables WHERE is_ms_shipped = 0")
        tables = [r[0] for r in cur.fetchall()]
        cur.close()
    finally:
        live.close()

    packs = list_packs(get_settings().resolved_project_dir().parent)
    oneriler = match_packs(tables, packs.get("kaynaklar", []))
    kapsamlar = logo_kapsamlari(tables)
    audit.record(getattr(request.state, "principal", None), "connection_fingerprint",
                 nl_question=f"tenant: {tenant.slug if tenant else '?'} → "
                 f"{len(tables)} tablo, öneri: {[o['key'] for o in oneriler]}",
                 ip=request.client.host if request.client else None)
    return FingerprintOut(tablo_sayisi=len(tables), oneriler=oneriler,
                          logo_kapsamlari=kapsamlar)
