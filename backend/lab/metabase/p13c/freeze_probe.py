#!/usr/bin/env python3
"""Provider-free P13C frozen-fixture probe.

This script does not choose a semantic value. It reports exact same-table textual values and
independent June-2026 row counts from the pinned Boyahane DuckDB so one case can be frozen
without inventing a value.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duckdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not args.duckdb.is_file():
        raise RuntimeError(f"frozen DuckDB missing: {args.duckdb}")

    con = duckdb.connect(str(args.duckdb), read_only=True)
    columns = {
        str(row[0]): str(row[1])
        for row in con.execute("DESCRIBE satis_siparisleri").fetchall()
    }
    if columns.get("kanal", "").upper() not in {"VARCHAR", "TEXT"}:
        raise RuntimeError(f"satis_siparisleri.kanal is not textual: {columns.get('kanal')!r}")

    rows = con.execute(
        """
        SELECT
            kanal,
            COUNT(*)::BIGINT AS total_count,
            SUM(
                CASE
                    WHEN acilis_tarihi >= DATE '2026-06-01'
                     AND acilis_tarihi < DATE '2026-07-01'
                    THEN 1 ELSE 0
                END
            )::BIGINT AS june_2026_count
        FROM satis_siparisleri
        WHERE kanal IS NOT NULL
        GROUP BY kanal
        ORDER BY kanal
        """
    ).fetchall()

    values = [
        {
            "value": row[0],
            "python_type": type(row[0]).__name__,
            "total_count": int(row[1]),
            "june_2026_count": int(row[2]),
        }
        for row in rows
    ]
    if not values:
        raise RuntimeError("satis_siparisleri.kanal has no non-null values")
    if any(item["python_type"] != "str" for item in values):
        raise RuntimeError(f"kanal returned non-string value(s): {values!r}")

    eligible = [item for item in values if item["june_2026_count"] > 0]
    payload = {
        "schema_version": "p13c_fixture_probe_v1",
        "dataset": {
            "repository": "cagataysntrk/metabase-boyahane",
            "revision_sha": "f0c4a6b053ead52ca2eac80002c448323dc34a35",
            "duckdb_sha256": sha256_file(args.duckdb),
        },
        "source": {
            "schema": "main",
            "table": "satis_siparisleri",
            "field": "kanal",
            "field_type": columns["kanal"],
        },
        "cardinality": len(values),
        "values": values,
        "eligible_june_2026_values": eligible,
        "selection": "NOT_YET_FROZEN",
        "model_calls": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
