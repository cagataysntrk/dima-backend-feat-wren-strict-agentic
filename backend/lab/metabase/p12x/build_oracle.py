#!/usr/bin/env python3
"""Freeze P12X corpus fingerprint and independent DuckDB oracle."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb

HERE = Path(__file__).resolve().parent
CORPUS_PATH = HERE / "corpus_v1.json"
DB = Path(os.environ["BOYAHANE_DUCKDB"]).resolve()
OUT = Path(os.environ.get("P12X_OUT", HERE / "artifacts")).resolve()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, tuple):
        return [jsonable(v) for v in value]
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    return value


def main() -> None:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    cases = corpus.get("cases") or []
    ids = [c["id"] for c in cases]
    if not (12 <= len(cases) <= 16):
        raise SystemExit(f"corpus must contain 12..16 cases, got {len(cases)}")
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate P12X case ids")
    required = {
        "simple_count","simple_sum_metric","metric_breakdown","time_filtered_metric",
        "previous_period_comparison","top_n_ranking","entity_value_filter",
        "multilingual_retrieval","followup_context","ambiguous_resource_or_metric",
        "wrong_join_trap","grain_trap","query_tool_repair_opportunity",
        "missing_nonexistent_value"
    }
    families = {c["family"] for c in cases}
    missing = sorted(required - families)
    if missing:
        raise SystemExit(f"missing required families: {missing}")

    con = duckdb.connect(str(DB), read_only=True)
    results = []
    for case in cases:
        spec = case["oracle"]
        kind = spec["kind"]
        result = {"id": case["id"], "family": case["family"], "kind": kind}
        if kind == "query":
            cur = con.execute(spec["sql"])
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
            if columns != spec["columns"]:
                raise SystemExit(f"{case['id']} oracle columns drift: {columns} != {spec['columns']}")
            result.update({
                "comparison": spec["comparison"],
                "columns": columns,
                "rows": jsonable(rows),
                "numeric_tolerance": spec.get("numeric_tolerance", 0),
            })
        elif kind == "no_match":
            rows = jsonable(con.execute(spec["validation_sql"]).fetchall())
            if rows != spec["expected_validation"]:
                raise SystemExit(f"{case['id']} no-match fixture invalid: {rows}")
            result.update({
                "validation_rows": rows,
                "acceptable_outcomes": spec["acceptable_outcomes"],
                "must_not_publish_numeric_answer": bool(spec["must_not_publish_numeric_answer"]),
            })
        elif kind == "clarify":
            result.update({
                "acceptable_outcomes": spec["acceptable_outcomes"],
                "reason": spec["reason"],
                "must_not_publish_numeric_answer": bool(spec["must_not_publish_numeric_answer"]),
            })
        else:
            raise SystemExit(f"unsupported oracle kind {kind!r}")
        results.append(result)

    fingerprint = canonical_hash(corpus)
    oracle = {
        "schema_version": "p12x_oracle_v1",
        "corpus_fingerprint": fingerprint,
        "dataset": corpus["dataset"],
        "case_count": len(cases),
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "corpus_v1.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "corpus_fingerprint.json").write_text(json.dumps({
        "corpus_fingerprint": fingerprint,
        "case_count": len(cases),
        "case_ids": ids,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "oracle_v1.json").write_text(json.dumps(oracle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"corpus_fingerprint": fingerprint, "case_count": len(cases)}, sort_keys=True))


if __name__ == "__main__":
    main()
