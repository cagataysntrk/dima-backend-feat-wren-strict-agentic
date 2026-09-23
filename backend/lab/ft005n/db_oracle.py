"""Independent FT-005N Boyahane oracle from the frozen corpus.

No Metabase or model calls. Executes only hidden oracle specs against the frozen
Boyahane DuckDB source.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


def q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def execute_spec(con, spec: dict):
    table = q(spec["table"])
    aggregation = spec["aggregation"]
    where = []
    params = []
    date_field = spec.get("date_field")
    if date_field:
        where.append(f"{q(date_field)} >= ?")
        params.append(spec["start"])
        where.append(f"{q(date_field)} < ?")
        params.append(spec["end_exclusive"])
    where_sql = " WHERE " + " AND ".join(where) if where else ""

    if aggregation == "COUNT":
        sql = f"SELECT COUNT(*) FROM main.{table}{where_sql}"
        value = con.execute(sql, params).fetchone()[0]
        return {"kind": "scalar", "value": int(value)}

    if aggregation != "SUM":
        raise RuntimeError(f"unsupported oracle aggregation: {aggregation}")

    measure = q(spec["measure"])
    breakdown = spec.get("breakdown")
    if not breakdown:
        sql = f"SELECT COALESCE(SUM({measure}), 0) FROM main.{table}{where_sql}"
        value = con.execute(sql, params).fetchone()[0]
        return {"kind": "scalar", "value": float(value)}

    group = q(breakdown)
    sql = (
        f"SELECT {group}, COALESCE(SUM({measure}),0) "
        f"FROM main.{table}{where_sql} "
        f"GROUP BY {group} ORDER BY {group}"
    )
    rows = con.execute(sql, params).fetchall()
    return {
        "kind": "breakdown",
        "dimension": breakdown,
        "rows": [
            {"key": key, "value": float(value)}
            for key, value in rows
        ],
    }


def main(source: Path, corpus: Path, out: Path) -> None:
    payload = json.loads(corpus.read_text())
    assert payload["corpus_id"] == "FT005N_SEAM_CORPUS_V1"
    con = duckdb.connect(str(source), read_only=True)

    results = []
    for suite in payload["suites"]:
        if not suite["suite_id"].startswith("boyahane_"):
            continue
        for case in suite["cases"]:
            spec = case.get("hidden_oracle")
            if not spec:
                continue
            results.append(
                {
                    "case_id": case["case_id"],
                    "oracle": execute_spec(con, spec),
                }
            )

    receipt = {
        "corpus_id": payload["corpus_id"],
        "boyahane_sha": payload["source_control"]["boyahane_sha"],
        "source": source.name,
        "result_source": "DIRECT_FROZEN_DUCKDB",
        "model_calls": 0,
        "metabase_calls": 0,
        "results": results,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main(args.source, args.corpus, args.out)
