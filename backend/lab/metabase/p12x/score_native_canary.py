#!/usr/bin/env python3
"""Executable PX-01 native canary oracle gate.

This is lab-only benchmark proof. It does not define product semantic authority.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_CASE_ID = "PX-01"
EXPECTED_DATABASE_NAME = "Dima Analytics Lab"
EXPECTED_SCHEMA = "public"
EXPECTED_TABLE = "satis_siparisleri"
EXPECTED_RUNTIME_TAG = "v0.63.18"
EXPECTED_RUNTIME_HASH_PREFIX = "2ba2485"
EXPECTED_CORPUS_FINGERPRINT = (
    "fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0"
)


class GateFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateFailure(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def oracle_case(oracle: dict[str, Any], case_id: str) -> dict[str, Any]:
    require(
        oracle.get("corpus_fingerprint") == EXPECTED_CORPUS_FINGERPRINT,
        "oracle corpus fingerprint does not match current frozen corpus",
    )
    matches = [
        item for item in (oracle.get("results") or [])
        if isinstance(item, dict) and item.get("id") == case_id
    ]
    require(len(matches) == 1, f"oracle must contain exactly one {case_id} result")
    case = matches[0]
    require(case.get("kind") == "query", f"{case_id} must be a query oracle")
    require(case.get("comparison") == "scalar", f"{case_id} must use scalar comparison")
    rows = case.get("rows")
    require(
        isinstance(rows, list)
        and len(rows) == 1
        and isinstance(rows[0], list)
        and len(rows[0]) == 1,
        f"{case_id} oracle must be exactly one scalar cell",
    )
    return case


def runtime_version(native: dict[str, Any]) -> dict[str, Any]:
    fields = native.get("session_version_fields")
    require(isinstance(fields, dict), "native artifact has no session_version_fields")
    version = fields.get("version")
    require(isinstance(version, dict), "native artifact has no structured runtime version")
    require(version.get("tag") == EXPECTED_RUNTIME_TAG, "native runtime tag drift")
    observed_hash = str(version.get("hash") or "")
    require(
        observed_hash.startswith(EXPECTED_RUNTIME_HASH_PREFIX),
        "native runtime source hash drift",
    )
    return version


def exact_resource(native: dict[str, Any]) -> dict[str, Any]:
    catalog = native.get("catalog_probe")
    require(isinstance(catalog, dict), "native artifact has no catalog_probe")
    resource = catalog.get("first")
    require(isinstance(resource, dict), "catalog probe has no exact first resource")
    require(resource.get("type") == "table", "catalog resource must be a table")
    require(
        resource.get("database_name") == EXPECTED_DATABASE_NAME,
        "benchmark database identity drift",
    )
    require(resource.get("database_schema") == EXPECTED_SCHEMA, "benchmark schema drift")
    require(resource.get("name") == EXPECTED_TABLE, "benchmark table identity drift")
    require(isinstance(resource.get("database_id"), int), "catalog database_id missing")
    require(isinstance(resource.get("id"), int), "catalog table id missing")
    return resource


def generated_query(native: dict[str, Any], resource: dict[str, Any]) -> dict[str, Any]:
    query = native.get("generated_query")
    require(isinstance(query, dict), "native generated query is missing")
    require(query.get("type") == "query", "native generated query is not MBQL query")
    require(
        query.get("database") == resource["database_id"],
        "generated query database does not match exact Boyahane runtime database",
    )
    inner = query.get("query")
    require(isinstance(inner, dict), "generated MBQL query body is missing")
    require(
        inner.get("source-table") == resource["id"],
        "generated query source-table does not match exact satis_siparisleri runtime table",
    )
    return query


def dataset_payload(native: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = native.get("generated_query_dataset_result")
    require(isinstance(result, dict), "generated query execution result is missing")
    status = result.get("status")
    require(status in {200, 202}, f"unexpected /api/dataset status: {status!r}")

    if isinstance(result.get("rows"), list):
        payload = {"data": {"rows": result["rows"], "cols": result.get("cols")}}
    else:
        body = result.get("body")
        require(isinstance(body, str) and body.strip(), "dataset result has no rows or JSON body")
        parsed = json.loads(body)
        require(isinstance(parsed, dict), "dataset response body is not an object")
        payload = parsed
    return int(status), payload


def executed_scalar(native: dict[str, Any]) -> Any:
    _status, payload = dataset_payload(native)
    data = payload.get("data")
    require(isinstance(data, dict), "dataset response has no data object")
    rows = data.get("rows")
    require(
        isinstance(rows, list)
        and len(rows) == 1
        and isinstance(rows[0], list)
        and len(rows[0]) == 1,
        "executed result must be exactly one scalar cell",
    )
    return rows[0][0]


def same_scalar(observed: Any, expected: Any) -> bool:
    if isinstance(observed, bool) or isinstance(expected, bool):
        return observed == expected
    if isinstance(observed, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(float(observed), float(expected), rel_tol=0.0, abs_tol=0.0)
    return observed == expected


def error_counts(native: dict[str, Any]) -> tuple[int, int]:
    stream_errors = native.get("errors")
    require(isinstance(stream_errors, list), "native errors field must be a list")

    tool_errors = 0
    tool_results = native.get("tool_results")
    require(isinstance(tool_results, list), "native tool_results field must be a list")
    for item in tool_results:
        if not isinstance(item, dict):
            continue
        if item.get("isError") is True or item.get("is_error") is True or item.get("error"):
            tool_errors += 1
    return len(stream_errors), tool_errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--case-id", default=EXPECTED_CASE_ID)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report: dict[str, Any] = {
        "case_id": args.case_id,
        "status": "RED",
        "checks": {},
        "expected_corpus_fingerprint": EXPECTED_CORPUS_FINGERPRINT,
    }
    try:
        require(args.case_id == EXPECTED_CASE_ID, "this gate is intentionally PX-01 only")
        native = load_json(args.native)
        oracle = load_json(args.oracle)
        case = oracle_case(oracle, args.case_id)
        expected = case["rows"][0][0]

        require(native.get("question") == "Haziran 2026'da kaç satış siparişi açıldı?", "PX-01 question drift")
        require(native.get("status_code") == 202, "native agent-streaming did not return HTTP 202")

        version = runtime_version(native)
        resource = exact_resource(native)
        _query = generated_query(native, resource)
        observed = executed_scalar(native)
        stream_errors, tool_errors = error_counts(native)

        require(same_scalar(observed, expected), f"executed scalar {observed!r} != oracle {expected!r}")
        require(stream_errors == 0, f"provider/stream errors={stream_errors}")
        require(tool_errors == 0, f"structured tool errors={tool_errors}")

        report.update({
            "status": "GREEN",
            "corpus_fingerprint": oracle["corpus_fingerprint"],
            "runtime": version,
            "resource": {
                "database_id": resource["database_id"],
                "database_name": resource["database_name"],
                "schema": resource["database_schema"],
                "table_id": resource["id"],
                "table_name": resource["name"],
            },
            "observed_scalar": observed,
            "oracle_scalar": expected,
            "provider_stream_errors": stream_errors,
            "structured_tool_errors": tool_errors,
            "checks": {
                "current_corpus_identity": "PASS",
                "px01_identity": "PASS",
                "pinned_runtime": "PASS",
                "generated_query": "PASS",
                "boyahane_exact_resource": "PASS",
                "executed_equals_oracle": "PASS",
                "provider_tool_errors_zero": "PASS",
            },
        })
        exit_code = 0
    except Exception as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
        exit_code = 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
