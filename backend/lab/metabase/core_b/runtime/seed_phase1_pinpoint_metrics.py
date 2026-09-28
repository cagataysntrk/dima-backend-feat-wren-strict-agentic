#!/usr/bin/env python3
"""Create governed native Metabase metric resources for Phase-1 pinpoint probes.

Lab/runtime fixture setup only. This module does not infer business semantics.
Every metric definition is a closed mapping over the frozen neutral fixture.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "phase1_pinpoint_native_bindings_v1"
TABLE_NAME = "machine_operations"

_METRIC_SPECS = (
    ("metric.machine_downtime_minutes", "Machine Downtime Minutes", "machine_downtime_minutes", "sum"),
    ("metric.fault_count", "Fault Count", "fault_count", "sum"),
    ("metric.performance_score", "Performance Score", "performance_score", "avg"),
    ("metric.maintenance_delay_hours", "Maintenance Delay Hours", "maintenance_delay_hours", "sum"),
    ("metric.spare_part_delay_hours", "Spare Part Delay Hours", "spare_part_delay_hours", "sum"),
    ("metric.pm_compliance_pct", "Preventive Maintenance Compliance", "pm_compliance_pct", "avg"),
    ("metric.changeover_count", "Changeover Count", "changeover_count", "sum"),
    ("metric.operator_absence_hours", "Operator Absence Hours", "operator_absence_hours", "sum"),
)


def metric_specs() -> tuple[tuple[str, str, str, str], ...]:
    return _METRIC_SPECS


def metric_card_payload(
    *,
    database_id: int,
    table_id: int,
    field_id: int,
    name: str,
    aggregation: str,
) -> dict[str, Any]:
    if aggregation not in {"sum", "avg"}:
        raise ValueError("pinpoint metric aggregation must be a closed fixture choice")
    return {
        "name": name,
        "type": "metric",
        "dataset_query": {
            "database": database_id,
            "type": "query",
            "query": {
                "source-table": table_id,
                "aggregation": [
                    [aggregation, ["field", field_id, None]],
                ],
            },
        },
        "display": "scalar",
        "visualization_settings": {},
        "description": (
            "Governed Phase-1 pinpoint fixture metric over machine_operations."
        ),
    }


def _request(
    base_url: str,
    method: str,
    path: str,
    *,
    session: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if session:
        headers["X-Metabase-Session"] = session
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw.decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {path}: {body}") from exc


def _login(base_url: str, email: str, password: str) -> str:
    body = _request(
        base_url,
        "POST",
        "/api/session",
        payload={"username": email, "password": password},
    )
    token = str((body or {}).get("id") or "")
    if not token:
        raise RuntimeError("Metabase session token missing")
    return token


def _fixture_metadata(
    base_url: str,
    session: str,
) -> tuple[int, int, dict[str, int]]:
    databases = _request(base_url, "GET", "/api/database", session=session)
    items = databases.get("data", []) if isinstance(databases, dict) else []
    warehouse = next(
        (
            item
            for item in items
            if isinstance(item, dict)
            and item.get("name") == "Dima Core B Neutral Fixture"
        ),
        None,
    )
    if not warehouse:
        raise RuntimeError("neutral fixture database not found")
    database_id = int(warehouse["id"])
    metadata = _request(
        base_url,
        "GET",
        f"/api/database/{database_id}/metadata",
        session=session,
    )
    tables = metadata.get("tables", []) if isinstance(metadata, dict) else []
    table = next(
        (
            item
            for item in tables
            if isinstance(item, dict) and item.get("name") == TABLE_NAME
        ),
        None,
    )
    if not table:
        raise RuntimeError("machine_operations table not found")
    table_id = int(table["id"])
    fields = {
        str(item["name"]): int(item["id"])
        for item in table.get("fields", [])
        if isinstance(item, dict)
        and isinstance(item.get("name"), str)
        and isinstance(item.get("id"), int)
    }
    required = {spec[2] for spec in _METRIC_SPECS} | {
        "department",
        "event_date",
        "machine_id",
    }
    missing = sorted(required - fields.keys())
    if missing:
        raise RuntimeError("fixture fields missing: " + ",".join(missing))
    return database_id, table_id, fields


def _create_metrics(
    *,
    base_url: str,
    admin_session: str,
    database_id: int,
    table_id: int,
    fields: dict[str, int],
) -> list[dict[str, Any]]:
    created: list[dict[str, Any]] = []
    for candidate_id, name, column_name, aggregation in _METRIC_SPECS:
        body = _request(
            base_url,
            "POST",
            "/api/card",
            session=admin_session,
            payload=metric_card_payload(
                database_id=database_id,
                table_id=table_id,
                field_id=fields[column_name],
                name=name,
                aggregation=aggregation,
            ),
        )
        if not isinstance(body, dict):
            raise RuntimeError(f"metric creation returned no object: {candidate_id}")
        metric_id = body.get("id")
        entity_id = body.get("entity_id")
        if not isinstance(metric_id, int) or not str(entity_id or "").strip():
            raise RuntimeError(
                f"metric lacks stable native identity: {candidate_id}"
            )
        created.append(
            {
                "candidate_id": candidate_id,
                "canonical_name": name,
                "table_name": TABLE_NAME,
                "column_name": column_name,
                "metabase_metric_id": metric_id,
                "native_metric_entity_id": str(entity_id),
                "fixture_definition": {
                    "aggregation": aggregation,
                    "field_id": fields[column_name],
                },
            }
        )
    return created


def _verify_restricted_visibility(
    *,
    base_url: str,
    restricted_session: str,
    metrics: list[dict[str, Any]],
) -> None:
    for item in metrics:
        body = _request(
            base_url,
            "GET",
            f"/api/card/{item['metabase_metric_id']}",
            session=restricted_session,
        )
        if not isinstance(body, dict):
            raise RuntimeError("restricted metric lookup returned no object")
        if str(body.get("entity_id") or "") != item["native_metric_entity_id"]:
            raise RuntimeError(
                "restricted principal cannot observe governed metric identity"
            )
        if body.get("type") != "metric":
            raise RuntimeError("governed resource is not a Metabase metric")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    admin_email = os.environ["MB_ADMIN_EMAIL"]
    admin_password = os.environ["MB_ADMIN_PASSWORD"]
    restricted_email = os.environ["MB_RESTRICTED_EMAIL"]
    restricted_password = os.environ["MB_RESTRICTED_PASSWORD"]

    admin = _login(args.base_url, admin_email, admin_password)
    database_id, table_id, fields = _fixture_metadata(args.base_url, admin)
    metrics = _create_metrics(
        base_url=args.base_url,
        admin_session=admin,
        database_id=database_id,
        table_id=table_id,
        fields=fields,
    )
    restricted = _login(
        args.base_url,
        restricted_email,
        restricted_password,
    )
    _verify_restricted_visibility(
        base_url=args.base_url,
        restricted_session=restricted,
        metrics=metrics,
    )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "table_name": TABLE_NAME,
        "database_id": database_id,
        "table_id": table_id,
        "metrics": metrics,
        "dimensions": [
            {
                "candidate_id": "dimension.department",
                "column_name": "department",
            },
            {
                "candidate_id": "dimension.event_date",
                "column_name": "event_date",
            },
            {
                "candidate_id": "dimension.machine_id",
                "column_name": "machine_id",
            },
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "native_binding_manifest": str(args.output),
                "metric_count": len(metrics),
                "restricted_visibility": "PASSED",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
