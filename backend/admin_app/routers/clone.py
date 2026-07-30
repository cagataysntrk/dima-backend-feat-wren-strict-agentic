"""/sadmin/connections/{cid}/clone|sync — müşteri DB ayna yönetimi (ADR-0017 K9 api_sync).

Bir 'source' bağlantısından (canlı/upstream) tabloları lab'e (ya da tenant'ın api_sync
mirror'ına) kopyalar. İki mod:
  - clone (full): TÜM (ya da core/list) tabloları DROP+yeniden yükle (tam ayna).
  - sync (incremental): db_sync watermark'ıyla yalnız yeni/DEĞİŞMİŞ satır → upsert.

Motor admin_app/clone/engine (CLI snapshot ile ORTAK). İş arka plan thread'inde koşar, CloneJob
satırına ilerleme yazar; panel poll'lar. GÜVENLİK: assert_not_self_clone — kaynak == hedef
ise iş 'failed' (klonu kendine kopyalayıp boşaltma faciası önlenir). JENERİK: kaynak/hedef
mssql adaptörü arkasında (postgres/mysql aynı arayüzle eklenir).
"""

from __future__ import annotations

import threading
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from admin_app.routers.connections import _get, _meta, _pyodbc_connect
from admin_app.schemas import CloneCard, CloneEndpoint, CloneJobOut, CloneStart
from control_plane.config import get_auth_settings
from control_plane.crypto import decrypt_secret
from control_plane.db import engine, get_session
from control_plane.models import CloneJob, DbConnection, SyncState, Tenant

router = APIRouter(prefix="/sadmin/connections", tags=["sadmin-clone"])

# Kaynak olarak: mssql native + SQLAlchemy sürücüsü kurulu HER datasource (registry karar verir).
_SOURCE_OK = {"mssql", "sqlserver", "postgres", "postgresql", "mysql", "mariadb",
              "oracle", "clickhouse"}


def _job_out(job: CloneJob, tenant: Tenant | None) -> CloneJobOut:
    return CloneJobOut(
        id=str(job.id), tenant=tenant.slug if tenant else "", kind=job.kind,
        status=job.status, target_db=job.target_db, total_tables=job.total_tables,
        done_tables=job.done_tables, ok_tables=job.ok_tables, skip_tables=job.skip_tables,
        fail_tables=job.fail_tables, rows_total=job.rows_total,
        current_table=job.current_table, message=job.message, error=job.error,
        started_at=job.started_at.isoformat(),
        finished_at=job.finished_at.isoformat() if job.finished_at else None)


def _endpoint(conn: DbConnection) -> CloneEndpoint:
    m = _meta(conn)
    return CloneEndpoint(
        id=str(conn.id), host=str(m.get("host") or ""), port=int(m.get("port") or 0),
        database=str(m.get("database") or ""), user=str(m.get("user") or ""),
        datasource=conn.datasource, topology=conn.topology)


def _autocommit_connect(conn: DbConnection, database: str = "master"):
    """Hedef (lab/mirror) için autocommit + master bağlantısı (CREATE DATABASE/USE için)."""
    import pyodbc

    meta = _meta(conn)
    pwd = decrypt_secret(conn.secret_ciphertext, get_auth_settings().cred_kek)
    parts = [
        "DRIVER={ODBC Driver 18 for SQL Server}",
        f"SERVER={meta.get('host')},{meta.get('port') or 1433}",
        f"DATABASE={database}", f"UID={meta.get('user')}", f"PWD={pwd}",
    ]
    if meta.get("trust_server_certificate", True):
        parts.append("TrustServerCertificate=yes")
    return pyodbc.connect(";".join(parts), autocommit=True)


def _default_lab_connect():
    """Hedef bağlantı verilmemişse varsayılan lab (127.0.0.1:14333)."""
    from lab.snapshot_mssql import lab_connection

    return lab_connection()


def _resolve_tables(scope: str, tables: list[str] | None, slug: str, source) -> list[str]:
    if scope == "list":
        if not tables:
            raise HTTPException(status_code=400, detail="scope='list' için tablo listesi gerekli")
        return tables
    if scope == "core":
        from lab.snapshot_mssql import core_tables
        return core_tables(slug)
    return source.list_tables()  # all (datasource-bağımsız: mssql/postgres/…)


def _build_source(src_conn: DbConnection):
    """Kaynak adaptörü kur — mssql native (pyodbc + mojibake fix); diğerleri SQLAlchemy."""
    from admin_app.clone.adapters import source_for
    from app.wren_service import WrenService

    ds = src_conn.datasource.lower()
    pyodbc_src = _pyodbc_connect(src_conn) if ds in ("mssql", "sqlserver") else None
    pwd = None
    if pyodbc_src is None and src_conn.secret_ciphertext is not None:
        pwd = decrypt_secret(src_conn.secret_ciphertext, get_auth_settings().cred_kek)
    return source_for(ds, _meta(src_conn), pwd, pyodbc_src, WrenService._fix_tr)


def _run_job(job_id: _uuid.UUID, source_cid: _uuid.UUID, target_cid: _uuid.UUID | None,
             kind: str, scope: str, tables: list[str] | None) -> None:
    """Arka plan thread: clone/sync'i koşar, CloneJob'a ilerleme yazar. Kendi Session'ı."""
    from datetime import datetime

    from admin_app.clone.adapters import SelfCloneError, target_for
    from admin_app.clone.engine import full_clone, incremental_sync, target_db_name

    def _set(**kw):
        with Session(engine) as s:
            j = s.get(CloneJob, job_id)
            for k, v in kw.items():
                setattr(j, k, v)
            s.add(j); s.commit()

    source = target = None
    try:
        with Session(engine) as s:
            src_conn = s.get(DbConnection, source_cid)
            slug = s.get(Tenant, src_conn.tenant_id).slug
            tgt_conn = s.get(DbConnection, target_cid) if target_cid else None
            if tgt_conn is None:  # tenant'ın api_sync mirror'ı varsa hedef O
                tgt_conn = next((c for c in s.exec(select(DbConnection).where(
                    DbConnection.tenant_id == src_conn.tenant_id)).all()
                    if c.topology == "api_sync" and c.id != source_cid), None)

        source = _build_source(src_conn)
        if tgt_conn is not None:
            db = _meta(tgt_conn).get("database") or target_db_name(slug)
            target = target_for("mssql", _autocommit_connect(tgt_conn, "master"))
        else:
            db = target_db_name(slug)
            target = target_for("mssql", _default_lab_connect())

        table_list = _resolve_tables(scope, tables, slug, source)
        _set(status="running", target_db=db, total_tables=len(table_list))

        def _progress(done, total, tab, rows, status):
            with Session(engine) as s:
                j = s.get(CloneJob, job_id)
                j.done_tables = done
                j.current_table = tab
                j.rows_total = (j.rows_total or 0) + (rows if not status.startswith("fail") else 0)
                if status.startswith("fail"):
                    j.fail_tables += 1
                elif status == "skip":
                    j.skip_tables += 1
                else:
                    j.ok_tables += 1
                s.add(j); s.commit()

        if kind == "sync":
            counts = incremental_sync(source, target, db, table_list,
                                      _mk_state_get(source_cid), _mk_state_set(source_cid),
                                      _progress)
        else:
            counts = full_clone(source, target, db, table_list, _progress)

        _set(status="completed", finished_at=datetime.utcnow(), current_table=None,
             message=(f"{counts.get('ok', 0)} tablo OK, {counts.get('skip', 0)} atlandı, "
                      f"{counts.get('fail', 0)} hata, {counts.get('rows', 0):,} satır"))
    except SelfCloneError as exc:
        _set(status="failed", finished_at=datetime.utcnow(),
             error=f"Self-clone reddedildi: {exc}")
    except Exception as exc:  # noqa: BLE001
        _set(status="failed", finished_at=datetime.utcnow(), error=str(exc)[:500])
    finally:
        for a in (source, target):
            if a is not None:
                a.close()


def _mk_state_get(source_cid: _uuid.UUID):
    def _get_wm(table: str):
        with Session(engine) as s:
            row = s.exec(select(SyncState).where(
                SyncState.connection_id == source_cid,
                SyncState.table_name == table)).first()
        if row is None or row.watermark_value is None:
            return None
        if row.watermark_mode == "rowversion":
            return bytes.fromhex(row.watermark_value)
        return row.watermark_value
    return _get_wm


def _mk_state_set(source_cid: _uuid.UUID):
    def _set_wm(table: str, new_wm, rows: int):
        from datetime import datetime
        mode = "rowversion" if isinstance(new_wm, (bytes, bytearray)) else "datetime"
        val = (new_wm.hex() if isinstance(new_wm, (bytes, bytearray))
               else (str(new_wm) if new_wm is not None else None))
        with Session(engine) as s:
            row = s.exec(select(SyncState).where(
                SyncState.connection_id == source_cid,
                SyncState.table_name == table)).first()
            if row is None:
                row = SyncState(connection_id=source_cid, table_name=table)
            row.watermark_mode = mode if new_wm is not None else row.watermark_mode
            row.watermark_value = val if new_wm is not None else row.watermark_value
            row.row_count = (row.row_count or 0) + rows
            row.last_synced_at = datetime.utcnow()
            s.add(row); s.commit()
    return _set_wm


def _start(cid: str, kind: str, body: CloneStart, session: Session) -> CloneJobOut:
    conn, tenant = _get(session, cid)
    if conn.datasource.lower() not in _SOURCE_OK:
        raise HTTPException(
            status_code=501,
            detail=f"Desteklenmeyen kaynak datasource: {conn.datasource} "
            f"(mssql native + SQLAlchemy sürücülü olanlar). Driver kurulu mu?")
    target_cid = _uuid.UUID(body.target_conn_id) if body.target_conn_id else None
    job = CloneJob(tenant_id=conn.tenant_id, source_conn_id=conn.id,
                   target_conn_id=target_cid, kind=kind, status="pending")
    session.add(job)
    session.commit()
    session.refresh(job)
    threading.Thread(target=_run_job, args=(job.id, conn.id, target_cid, kind,
                     body.scope, body.tables), daemon=True).start()
    return _job_out(job, tenant)


@router.post("/{cid}/clone", response_model=CloneJobOut, status_code=202)
def start_clone(cid: str, body: CloneStart,
                session: Session = Depends(get_session)) -> CloneJobOut:
    """Tam ayna clone başlat (arka plan). scope: all|core|list."""
    return _start(cid, "clone", body, session)


@router.post("/{cid}/sync", response_model=CloneJobOut, status_code=202)
def start_sync(cid: str, body: CloneStart,
               session: Session = Depends(get_session)) -> CloneJobOut:
    """Incremental sync başlat — yalnız yeni/değişmiş satır (watermark). scope: all|core|list."""
    return _start(cid, "sync", body, session)


@router.get("/{cid}/jobs", response_model=list[CloneJobOut])
def list_jobs(cid: str, session: Session = Depends(get_session)) -> list[CloneJobOut]:
    conn, tenant = _get(session, cid)
    jobs = session.exec(select(CloneJob).where(CloneJob.source_conn_id == conn.id)
                        .order_by(CloneJob.started_at.desc())).all()
    return [_job_out(j, tenant) for j in jobs]


# İş durumu (poll) — tekil job. /sadmin/clone-jobs/{job_id}
jobs_router = APIRouter(prefix="/sadmin/clone-jobs", tags=["sadmin-clone"])


@jobs_router.get("/{job_id}", response_model=CloneJobOut)
def get_job(job_id: str, session: Session = Depends(get_session)) -> CloneJobOut:
    try:
        job = session.get(CloneJob, _uuid.UUID(job_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz job id")
    if job is None:
        raise HTTPException(status_code=404, detail="İş bulunamadı")
    return _job_out(job, session.get(Tenant, job.tenant_id))


@jobs_router.get("", response_model=list[CloneJobOut])
def list_all_jobs(session: Session = Depends(get_session)) -> list[CloneJobOut]:
    jobs = session.exec(select(CloneJob).order_by(CloneJob.started_at.desc())).all()
    return [_job_out(j, session.get(Tenant, j.tenant_id)) for j in jobs]


# Tenant başına clone kartı — canlı + klon YAN YANA + son clone. /sadmin/clone/overview
overview_router = APIRouter(prefix="/sadmin/clone", tags=["sadmin-clone"])


@overview_router.get("/overview", response_model=list[CloneCard])
def clone_overview(session: Session = Depends(get_session)) -> list[CloneCard]:
    """Her tenant için: canlı (cloud_direct) + klon (api_sync) uçları + son/aktif clone işi."""
    cards: list[CloneCard] = []
    for t in session.exec(select(Tenant).order_by(Tenant.slug)).all():
        conns = session.exec(select(DbConnection).where(
            DbConnection.tenant_id == t.id)).all()
        live = next((c for c in conns if c.topology == "cloud_direct"), None)
        clone = next((c for c in conns if c.topology == "api_sync"), None)
        # api_sync/cloud_direct etiketi yoksa ilk bağlantıyı 'live' olarak göster (geriye dönük).
        if live is None and clone is None and conns:
            live = conns[0]
        jobs = session.exec(select(CloneJob).where(CloneJob.tenant_id == t.id)
                            .order_by(CloneJob.started_at.desc())).all()
        active = next((j for j in jobs if j.status in ("pending", "running")), None)
        done = next((j for j in jobs if j.status in ("completed", "failed")), None)
        cards.append(CloneCard(
            tenant=t.slug, tenant_id=str(t.id),
            live=_endpoint(live) if live else None,
            clone=_endpoint(clone) if clone else None,
            last_clone_at=(done.finished_at or done.started_at).isoformat() if done else None,
            last_clone_status=done.status if done else None,
            last_clone_kind=done.kind if done else None,
            last_clone_rows=done.rows_total if done else None,
            active_job_id=str(active.id) if active else None))
    return cards
