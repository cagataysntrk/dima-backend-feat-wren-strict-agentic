#!/usr/bin/env python3
"""C2 live probe through the typed Dima NativeEngineBridge.

This is benchmark tooling. It preserves the bridge's native-only analytical seam and
records scope/permission evidence around the bridge call without changing product authority.
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
    NativeEngineBridgeError,
    NativeEngineStreamError,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest


WAREHOUSE = "Dima Analytics Lab"


def login(base: str, email: str, password: str) -> str:
    response = httpx.post(
        base.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    if not token:
        raise RuntimeError("restricted session token missing")
    return str(token)


def wait_catalog(client: httpx.Client, timeout: int = 240) -> dict[str, Any]:
    deadline = time.time() + timeout
    last: Any = None
    while time.time() < deadline:
        response = client.post(
            "/api/agent/v1/search",
            json={"term_queries": ["satis_siparisleri"], "semantic_queries": []},
        )
        if response.status_code == 200:
            body = response.json()
            data = body.get("data") or []
            exact = [
                item
                for item in data
                if isinstance(item, dict)
                and item.get("database_name") == WAREHOUSE
                and str(item.get("name") or "").casefold() == "satis_siparisleri"
            ]
            if exact:
                return {"search_total": body.get("total_count"), "first": exact[0]}
            last = {"total": body.get("total_count"), "names": [x.get("name") for x in data[:8] if isinstance(x, dict)]}
        else:
            last = {"status": response.status_code, "body": response.text[:500]}
        time.sleep(3)
    raise RuntimeError(f"Boyahane catalog not ready: {last}")


def safe_version(props: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(props, dict):
        for key, value in props.items():
            if "version" in str(key).lower() and isinstance(
                value, (str, int, float, bool, type(None), dict)
            ):
                out[str(key)] = value
    return out


def generated_query(data_parts: tuple[Any, ...]) -> dict[str, Any] | None:
    for part in reversed(data_parts):
        if not isinstance(part, dict) or part.get("type") != "generated_entity":
            continue
        value = part.get("value") or {}
        query = (value.get("query") or {}).get("query")
        if isinstance(query, dict):
            return query
    return None


def write_failure(
    *,
    output: Path,
    question: str,
    failure_class: str,
    error: str,
    props: dict[str, Any],
    permissions: Any,
    catalog: dict[str, Any],
    elapsed: float,
) -> int:
    artifact = {
        "status_code": None,
        "question": question,
        "latency_seconds": round(elapsed, 6),
        "session_version_fields": safe_version(props),
        "metabot_permissions": permissions,
        "catalog_probe": catalog,
        "answer_text": "",
        "tool_calls": [],
        "tool_results": [],
        "data_parts": [],
        "errors": [{
            "type": "c2_bridge_failure",
            "failure_class": failure_class,
            "error": error,
        }],
        "finish": None,
        "final_state": None,
        "generated_query": None,
        "generated_query_dataset_result": None,
        "raw_line_count": 0,
        "native_agent_invocation_count": 1,
        "agent_api_analytical_fallback": 0,
        "wren_fallback": 0,
        "raw_sql_fallback": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"captured_failure": failure_class, "artifact": str(output)}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-base-sha", required=True)
    ap.add_argument("--runtime-tag", default="v0.63.18-dima.0")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    token = login(base, args.email, args.password)
    headers = {"X-Metabase-Session": token, "Accept": "application/json"}

    with httpx.Client(base_url=base, headers=headers, timeout=60) as evidence_client:
        props_response = evidence_client.get("/api/session/properties")
        props_response.raise_for_status()
        props = props_response.json()
        permissions_response = evidence_client.get("/api/metabot/permissions/user-permissions")
        permissions_response.raise_for_status()
        permissions = permissions_response.json()
        catalog = wait_catalog(evidence_client)

    identity = NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_base_sha,
        runtime_tag=args.runtime_tag,
    )
    request = NativeEngineRequest(
        message=args.question,
        conversation_id=uuid.uuid4(),
        dima_request_id=f"p12x-c2-{args.case_id.lower()}-{uuid.uuid4()}",
        dima_trace_id=f"p12x-c2-trace-{uuid.uuid4()}",
    )

    started = time.perf_counter()
    try:
        with NativeEngineBridge(
            base_url=base,
            session_token=token,
            expected_identity=identity,
            timeout_seconds=240.0,
        ) as bridge:
            observation = bridge.invoke(request)
    except NativeEngineStreamError as exc:
        observation = exc.observation
    except NativeEngineBridgeError as exc:
        return write_failure(
            output=args.output,
            question=args.question,
            failure_class=type(exc).__name__,
            error=str(exc),
            props=props,
            permissions=permissions,
            catalog=catalog,
            elapsed=time.perf_counter() - started,
        )

    query = generated_query(observation.data_parts)
    dataset_result: dict[str, Any] | None = None
    if query is not None:
        with httpx.Client(base_url=base, headers=headers, timeout=180) as client:
            response = client.post("/api/dataset", json=query)
            dataset_result = {"status": response.status_code}
            if response.status_code in (200, 202):
                body = response.json()
                data = body.get("data") or {}
                dataset_result.update({
                    "rows": data.get("rows"),
                    "cols": data.get("cols"),
                    "row_count": len(data.get("rows") or []),
                    "database_id": body.get("database_id"),
                    "native_form": data.get("native_form"),
                })
            else:
                dataset_result["body"] = response.text[:2000]

    artifact = {
        "status_code": observation.status_code,
        "question": args.question,
        "case_id": args.case_id,
        "latency_seconds": round(observation.latency_ms / 1000.0, 6),
        "session_version_fields": safe_version(props),
        "metabot_permissions": permissions,
        "catalog_probe": catalog,
        "answer_text": "".join(observation.text_parts),
        "tool_calls": list(observation.tool_calls),
        "tool_results": list(observation.tool_results),
        "data_parts": list(observation.data_parts),
        "errors": list(observation.errors),
        "finish": observation.finish_parts[-1] if observation.finish_parts else None,
        "final_state": observation.final_state,
        "generated_query": query,
        "generated_query_dataset_result": dataset_result,
        "raw_line_count": len(observation.events),
        "native_agent_invocation_count": 1,
        "agent_api_analytical_fallback": 0,
        "wren_fallback": 0,
        "raw_sql_fallback": 0,
        "bridge_engine_identity": observation.engine_identity.model_dump(mode="json"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "case_id": args.case_id,
        "status_code": observation.status_code,
        "has_generated_query": query is not None,
        "errors": list(observation.errors),
        "dataset_rows": None if dataset_result is None else dataset_result.get("rows"),
        "event_count": len(observation.events),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
