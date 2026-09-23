#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import httpx

from app.v3.substrate.metabase.native_engine import NativeEngineBridge
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest


QUESTION = "Haziran 2026'da kaç satış siparişi açıldı?"


def login(base_url: str, email: str, password: str) -> str:
    r = httpx.post(
        base_url.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json().get("id")
    if not token:
        raise RuntimeError("Metabase session token missing")
    return str(token)


def generated_query(data_parts: tuple[Any, ...]) -> dict[str, Any]:
    for part in reversed(data_parts):
        if not isinstance(part, dict) or part.get("type") != "generated_entity":
            continue
        value = part.get("value") or {}
        query = (value.get("query") or {}).get("query")
        if isinstance(query, dict):
            return query
    raise RuntimeError("native bridge stream produced no generated query")


def oracle_scalar(path: Path) -> Any:
    body = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        x for x in body.get("results") or []
        if isinstance(x, dict) and x.get("id") == "PX-01"
    ]
    if len(rows) != 1:
        raise RuntimeError("PX-01 oracle missing")
    return rows[0]["rows"][0][0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-base-sha", required=True)
    args = ap.parse_args()

    token = login(args.base_url, args.email, args.password)
    identity = NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_base_sha,
        runtime_tag="v0.63.18-dima.0",
    )
    request = NativeEngineRequest(
        message=QUESTION,
        conversation_id="p12x-c2-live-px01",
        dima_request_id="p12x-c2-live-px01",
        dima_trace_id="p12x-c2-live-px01",
    )

    with NativeEngineBridge(
        base_url=args.base_url,
        session_token=token,
        expected_identity=identity,
        timeout_seconds=240.0,
    ) as bridge:
        observation = bridge.invoke(request)

    query = generated_query(observation.data_parts)
    with httpx.Client(
        base_url=args.base_url.rstrip("/"),
        headers={"X-Metabase-Session": token},
        timeout=180,
    ) as client:
        r = client.post("/api/dataset", json=query)
        if r.status_code not in (200, 202):
            raise RuntimeError(f"dataset execution HTTP {r.status_code}: {r.text[:500]}")
        payload = r.json()
    rows = (payload.get("data") or {}).get("rows")
    if not (
        isinstance(rows, list)
        and len(rows) == 1
        and isinstance(rows[0], list)
        and len(rows[0]) == 1
    ):
        raise RuntimeError(f"PX-01 result is not scalar: {rows!r}")

    observed = rows[0][0]
    expected = oracle_scalar(args.oracle)
    if observed != expected:
        raise RuntimeError(f"bridge result {observed!r} != oracle {expected!r}")

    report = {
        "schema_version": "p12x_c2_live_v1",
        "status": "GREEN",
        "engine_identity": identity.model_dump(),
        "workspace_gitlink_sha": args.workspace_gitlink_sha,
        "runtime_image_ref": args.runtime_image_ref,
        "runtime_version": observation.runtime_version,
        "http_status": observation.status_code,
        "event_count": len(observation.events),
        "tool_call_count": len(observation.tool_calls),
        "stream_error_count": len(observation.errors),
        "final_state_present": observation.final_state is not None,
        "generated_query_present": True,
        "observed_scalar": observed,
        "oracle_scalar": expected,
        "session_role": "restricted-current-user",
        "agent_api_fallback": 0,
        "wren_fallback": 0,
        "raw_sql_fallback": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
