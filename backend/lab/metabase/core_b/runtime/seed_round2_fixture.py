#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import psycopg
from psycopg import sql

def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixture",type=Path,required=True)
    args=ap.parse_args()
    body=json.loads(args.fixture.read_text(encoding="utf-8"))
    if body.get("schema_version")!="round2_neutral_machine_fixture_v1":
        raise RuntimeError("unexpected round2 fixture schema")
    rows=body["rows"]
    host=os.environ.get("PGHOST","127.0.0.1"); port=int(os.environ.get("PGPORT","5432"))
    db=os.environ["PGDATABASE"]; user=os.environ["PGUSER"]; password=os.environ["PGPASSWORD"]
    readonly=os.environ["CORE_B_READONLY_USER"]; readonly_password=os.environ["CORE_B_READONLY_PASSWORD"]
    conn=psycopg.connect(host=host,port=port,dbname=db,user=user,password=password,autocommit=True)
    with conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS machine_operations")
        cur.execute("""
          CREATE TABLE machine_operations (
            event_date date NOT NULL,
            department text NOT NULL,
            machine_id text NOT NULL,
            machine_downtime_minutes integer NOT NULL,
            fault_count integer NOT NULL,
            performance_score numeric(8,2) NOT NULL,
            maintenance_delay_hours numeric(8,2) NOT NULL,
            spare_part_delay_hours numeric(8,2) NOT NULL,
            pm_compliance_pct numeric(8,2) NOT NULL,
            changeover_count integer NOT NULL,
            operator_absence_hours numeric(8,2) NOT NULL
          )
        """)
        cur.executemany(
          "INSERT INTO machine_operations VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
          rows,
        )
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s",(readonly,))
        if cur.fetchone() is None:
            cur.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(readonly),sql.Literal(readonly_password)))
        else:
            cur.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(sql.Identifier(readonly),sql.Literal(readonly_password)))
        cur.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(db),sql.Identifier(readonly)))
        cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(readonly)))
        cur.execute(sql.SQL("GRANT SELECT ON TABLE machine_operations TO {}").format(sql.Identifier(readonly)))
        cur.execute("ANALYZE machine_operations")
        cur.execute("SELECT count(*) FROM machine_operations"); count=int(cur.fetchone()[0])
    if count != len(rows): raise RuntimeError("row count mismatch")
    print(json.dumps({"fixture_fingerprint":fingerprint(args.fixture),"rows":count},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
