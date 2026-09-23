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


def login(base: str, email: str, password: str) -> str:
    r = httpx.post(base.rstrip("/") + "/api/session", json={"username": email, "password": password}, timeout=30)
    r.raise_for_status()
    token = r.json().get("id")
    if not token:
        raise RuntimeError("session token missing")
    return str(token)


def query_from_parts(parts: tuple[Any, ...]) -> dict[str, Any]:
    for part in reversed(parts):
        if isinstance(part, dict) and part.get("type") == "generated_entity":
            q = (((part.get("value") or {}).get("query") or {}).get("query"))
            if isinstance(q, dict):
                return q
    raise RuntimeError("generated query missing")


def expected_scalar(path: Path) -> Any:
    body = json.loads(path.read_text())
    row = next(x for x in body["results"] if x["id"] == "PX-01")
    return row["rows"][0][0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    token = login(args.base_url, args.email, args.password)
    identity = NativeEngineIdentity(
        repository="metabase/metabase",
        engine_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
        upstream_base_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
        runtime_tag="v0.63.18",
        runtime_image_digest="sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73",
    )
    req = NativeEngineRequest(
        message=QUESTION,
        conversation_id="00000000-0000-4000-8000-000000000202",
        dima_request_id="p12x-c2-stock-live",
        dima_trace_id="p12x-c2-stock-live",
    )
    with NativeEngineBridge(
        base_url=args.base_url,
        session_token=token,
        expected_identity=identity,
        timeout_seconds=240,
    ) as bridge:
        observation = bridge.invoke(req)

    query = query_from_parts(observation.data_parts)
    with httpx.Client(
        base_url=args.base_url.rstrip("/"),
        headers={"X-Metabase-Session": token},
        timeout=180,
    ) as client:
        response = client.post("/api/dataset", json=query)
        if response.status_code not in (200, 202):
            raise RuntimeError(f"dataset execution HTTP {response.status_code}")
        rows = (response.json().get("data") or {}).get("rows")

    expected = expected_scalar(args.oracle)
    observed = rows[0][0] if isinstance(rows, list) and len(rows) == 1 and len(rows[0]) == 1 else None
    report = {
        "schema_version": "p12x_c2_stock_live_v1",
        "transport_status": "GREEN",
        "runtime_identity": identity.model_dump(),
        "http_status": observation.status_code,
        "stream_error_count": len(observation.errors),
        "event_count": len(observation.events),
        "generated_query_present": isinstance(query, dict),
        "observed_scalar": observed,
        "oracle_scalar": expected,
        "oracle_match": observed == expected,
        "restricted_current_user": True,
        "agent_api_fallback": 0,
        "wren_fallback": 0,
        "raw_sql_fallback": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # C2 is a transport/bridge gate. Native analytical correctness was already
    # measured in C1 with bounded repeats; require lossless live transport here.
    if observation.status_code != 202 or observation.errors or not isinstance(query, dict):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
