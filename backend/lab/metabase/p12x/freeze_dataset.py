#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import duckdb

SRC = Path(os.environ["BOYAHANE_DUCKDB"]).resolve()
OUT = Path(os.environ.get("P12X_OUT", "lab/metabase/p12x/artifacts")).resolve()
REPO_SHA = os.environ["BOYAHANE_REPO_SHA"]
GIT_BLOB_SHA = os.environ["BOYAHANE_GIT_BLOB_SHA"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(SRC), read_only=True)
    tables = [
        row[0]
        for row in con.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='main' AND table_type='BASE TABLE'
            ORDER BY table_name
            """
        ).fetchall()
    ]

    schema_tables = []
    profile_tables = []
    total_rows = 0
    for table in tables:
        quoted = qident(table)
        row_count = int(con.execute(f"SELECT COUNT(*) FROM main.{quoted}").fetchone()[0])
        total_rows += row_count
        columns = [
            {
                "name": name,
                "type": dtype,
                "nullable": nullable == "YES",
                "ordinal": int(ordinal),
            }
            for name, dtype, nullable, ordinal in con.execute(
                """
                SELECT column_name, data_type, is_nullable, ordinal_position
                FROM information_schema.columns
                WHERE table_schema='main' AND table_name=?
                ORDER BY ordinal_position
                """,
                [table],
            ).fetchall()
        ]
        constraints = []
        for ctype, names in con.execute(
            """
            SELECT constraint_type, constraint_column_names
            FROM duckdb_constraints()
            WHERE schema_name='main' AND table_name=?
            ORDER BY constraint_type, constraint_column_names::VARCHAR
            """,
            [table],
        ).fetchall():
            constraints.append({"type": ctype, "columns": list(names or [])})

        schema_tables.append(
            {
                "table": table,
                "row_count": row_count,
                "columns": columns,
                "constraints": constraints,
            }
        )

        profile_cols = []
        for col in columns:
            name = col["name"]
            dtype = str(col["type"]).upper()
            qc = qident(name)
            item = {"name": name, "type": dtype}
            try:
                distinct = int(con.execute(f"SELECT COUNT(DISTINCT {qc}) FROM main.{quoted}").fetchone()[0])
                item["distinct_count"] = distinct
                if dtype in {"VARCHAR", "BOOLEAN"} and distinct <= 20:
                    vals = con.execute(
                        f"SELECT DISTINCT {qc} FROM main.{quoted} WHERE {qc} IS NOT NULL ORDER BY {qc} LIMIT 20"
                    ).fetchall()
                    item["sample_values"] = [r[0] for r in vals]
                elif dtype in {"DATE", "TIMESTAMP", "TIMESTAMP WITH TIME ZONE", "TIMESTAMP_NS"}:
                    lo, hi = con.execute(f"SELECT MIN({qc}), MAX({qc}) FROM main.{quoted}").fetchone()
                    item["min"] = None if lo is None else str(lo)
                    item["max"] = None if hi is None else str(hi)
                elif any(token in dtype for token in ("INT", "DOUBLE", "DECIMAL", "FLOAT", "REAL", "HUGEINT")):
                    lo, hi = con.execute(f"SELECT MIN({qc}), MAX({qc}) FROM main.{quoted}").fetchone()
                    item["min"] = lo
                    item["max"] = hi
            except Exception as exc:
                item["profile_error"] = f"{type(exc).__name__}: {exc}"
            profile_cols.append(item)
        profile_tables.append({"table": table, "row_count": row_count, "columns": profile_cols})

    schema = {"schema": "main", "tables": schema_tables}
    schema_hash = canonical_hash(schema)
    identity = {
        "repo": "cagataysntrk/metabase-boyahane",
        "repo_sha": REPO_SHA,
        "duckdb_git_blob_sha1": GIT_BLOB_SHA,
        "duckdb_sha256": sha256_file(SRC),
        "duckdb_size_bytes": SRC.stat().st_size,
        "table_count": len(tables),
        "row_count": total_rows,
        "schema_sha256": schema_hash,
    }
    profile = {"dataset_identity": identity, "tables": profile_tables}

    if len(tables) != 80:
        raise SystemExit(f"expected 80 tables, observed {len(tables)}")
    if total_rows != 462_962:
        raise SystemExit(f"expected 462962 rows, observed {total_rows}")

    (OUT / "dataset_identity.json").write_text(json.dumps(identity, ensure_ascii=False, indent=2) + "\n")
    (OUT / "schema_snapshot.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n")
    (OUT / "dataset_profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2, default=str) + "\n")
    print(json.dumps(identity, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
