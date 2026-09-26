#!/usr/bin/env python3
"""Seed the frozen substrate-neutral Core-B fixture into Postgres."""
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
    if body.get("schema_version")!="core_b_neutral_machine_fixture_v1":
        raise RuntimeError("unexpected fixture schema")
    if body.get("table")!="machine_operations":
        raise RuntimeError("unexpected fixture table")
    if body["provenance"].get("wren_mdl") or body["provenance"].get("wren_query_contracts") or body["provenance"].get("expected_sql"):
        raise RuntimeError("neutral fixture contains forbidden engine-specific truth")
    required={"machine downtime","fault count","department","performance"}
    if set(body["provenance"].get("concepts") or ())!=required:
        raise RuntimeError("fixture concept coverage drift")

    host=os.environ.get("PGHOST","127.0.0.1")
    port=int(os.environ.get("PGPORT","5432"))
    db=os.environ["PGDATABASE"]
    user=os.environ["PGUSER"]
    password=os.environ["PGPASSWORD"]
    readonly=os.environ["CORE_B_READONLY_USER"]
    readonly_password=os.environ["CORE_B_READONLY_PASSWORD"]

    conn=psycopg.connect(host=host,port=port,dbname=db,user=user,password=password,autocommit=True)
    with conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS machine_operations")
        cur.execute("""
            CREATE TABLE machine_operations (
              event_date date NOT NULL,
              department text NOT NULL,
              machine_id text NOT NULL,
              machine_downtime_minutes integer NOT NULL CHECK (machine_downtime_minutes >= 0),
              fault_count integer NOT NULL CHECK (fault_count >= 0),
              performance_score numeric(6,2) NOT NULL CHECK (performance_score >= 0 AND performance_score <= 100)
            )
        """)
        cur.executemany(
            "INSERT INTO machine_operations(event_date,department,machine_id,machine_downtime_minutes,fault_count,performance_score) VALUES (%s,%s,%s,%s,%s,%s)",
            body["rows"],
        )
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s",(readonly,))
        exists=cur.fetchone() is not None
        if not exists:
            cur.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(readonly),sql.Literal(readonly_password)
                )
            )
        else:
            cur.execute(
                sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                    sql.Identifier(readonly),sql.Literal(readonly_password)
                )
            )
        cur.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(db),sql.Identifier(readonly)))
        cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(readonly)))
        cur.execute(sql.SQL("GRANT SELECT ON TABLE machine_operations TO {}").format(sql.Identifier(readonly)))
        cur.execute("ANALYZE machine_operations")
        cur.execute("SELECT count(*) FROM machine_operations")
        count=int(cur.fetchone()[0])
    if count != len(body["rows"]):
        raise RuntimeError("fixture row count mismatch")
    print(json.dumps({"fixture_fingerprint":fingerprint(args.fixture),"rows":count,"table":"machine_operations"},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
