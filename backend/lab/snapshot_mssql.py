"""Müşteri DB'sinden lab'e SELECT-tabanlı snapshot (ADR-0017 "tek seferlik ayna").

Salt-okunur erişimle çalışır (BACKUP yetkisi istemez). Bağlantı control-plane'den
(tenant slug ile) çözülür; hedef, lab SQL Server'ında `<SLUG>_SNAP` veritabanıdır.
Tekrar çalıştırılabilir (tablo bazında DROP+yeniden yükleme).

Motor `admin_app/clone/engine.py`'de (admin clone API ile ORTAK) — bu CLI onun ince kabuğu.
Self-clone guard engine'de: kaynak bağlantısı yanlışlıkla klonun kendisine bakıyorsa
(demo runtime bağlantısı clone'a çevrilince olur) tam-ayna İPTAL edilir (hedefi boşaltmaz).

Kullanım:
    .venv/bin/python lab/snapshot_mssql.py gitas --core          # pack gereksinim tabloları
    .venv/bin/python lab/snapshot_mssql.py gitas --all           # kaynaktaki TÜM tablolar
    .venv/bin/python lab/snapshot_mssql.py gitas TBLCASABIT TBLX # açık tablo listesi
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # dima-backend kökü

from admin_app.clone.adapters import MssqlSource, MssqlTarget, SelfCloneError
from admin_app.clone.engine import full_clone, target_db_name

LAB = {"host": "127.0.0.1", "port": "14333", "user": "sa", "password": "DimaLab!2026"}


def source_connection(slug: str):
    from sqlmodel import Session, select

    from admin_app.routers.connections import _pyodbc_connect
    from control_plane.db import engine
    from control_plane.models import DbConnection, Tenant

    with Session(engine) as s:
        t = s.exec(select(Tenant).where(Tenant.slug == slug)).one()
        conns = s.exec(select(DbConnection).where(DbConnection.tenant_id == t.id)).all()
    # KAYNAK = canlı/upstream (cloud_direct). Ayna (api_sync) clone HEDEFİ, kaynak DEĞİL —
    # onu kaynak seçmek self-clone olurdu (guard yakalar). cloud_direct'i tercih et.
    conn = next((c for c in conns if c.topology == "cloud_direct"),
                conns[0] if conns else None)
    if conn is None:
        raise SystemExit(f"{slug}: bağlantı yok")
    return _pyodbc_connect(conn)


def lab_connection():
    import pyodbc

    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={LAB['host']},{LAB['port']};DATABASE=master;"
        f"UID={LAB['user']};PWD={LAB['password']};TrustServerCertificate=yes;",
        autocommit=True)


def core_tables(slug: str) -> list[str]:
    """Şirketin kaynak pack'lerinin gereksinim tabloları (şablonsuz olanlar)."""
    import yaml

    from app.config import get_settings

    base = get_settings().resolved_project_dir().parent
    company = yaml.safe_load((base / "companies" / slug / "company.yml").read_text())
    tables: list[str] = []
    for k in company.get("kaynaklar") or []:
        spec = yaml.safe_load((base / "packs" / "kaynak" / k / "gereksinim.yml").read_text())
        for m in spec["modeller"]:
            tab = m["tablo"]
            if "{" in tab:  # şablonlu (Logo) — kapsamla çözülür, snapshot'ta atla
                tab = tab.replace("{firma}", f"{company.get('firma_no', 0):03d}") \
                         .replace("{donem}", f"{company.get('donem_no', 1):02d}")
            tables.append(tab)
    return tables


def snapshot(slug: str, tables: list[str]) -> None:
    from app.wren_service import WrenService

    source = MssqlSource(source_connection(slug), WrenService._fix_tr)
    target = MssqlTarget(lab_connection())
    db = target_db_name(slug)

    def _progress(done, total, tab, rows, status):
        if total <= 30 or rows or status.startswith("fail"):
            print(f"  {tab}: {rows:,} satır → {db}" if not status.startswith("fail")
                  else f"  {tab}: HATA, atlandı ({status[5:]})")

    # full_clone içinde self-clone guard + CREATE DATABASE otomatik.
    counts = full_clone(source, target, db, tables, _progress)
    print(f"  → {counts['ok']} tablo OK, {counts['skip']} boş/atlandı, "
          f"{counts['fail']} hata, toplam {counts['rows']:,} satır")
    source.close(); target.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("tables", nargs="*")
    ap.add_argument("--core", action="store_true", help="pack gereksinim tabloları")
    ap.add_argument("--all", action="store_true", help="kaynaktaki TÜM base tablolar (tam ayna)")
    args = ap.parse_args()
    if args.all:
        src = source_connection(args.slug)
        tables = MssqlSource(src).list_tables()
        src.close()
    else:
        tables = args.tables or (core_tables(args.slug) if args.core else [])
    if not tables:
        raise SystemExit("Tablo verin, --core ya da --all kullanın")
    print(f"{args.slug}: {len(tables)} tablo snapshot'lanıyor…")
    try:
        snapshot(args.slug, tables)
    except SelfCloneError as exc:
        raise SystemExit(f"İPTAL — {exc}")


if __name__ == "__main__":
    main()
