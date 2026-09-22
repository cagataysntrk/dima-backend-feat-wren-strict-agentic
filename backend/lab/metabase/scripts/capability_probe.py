#!/usr/bin/env python3
"""Runtime capability probe for Metabase v0.63.18 M2 lab."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request


BASE = os.environ.get("METABASE_URL", f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}").rstrip("/")
ADMIN_EMAIL = os.environ.get("MB_ADMIN_EMAIL", "admin@dima-lab.local")
ADMIN_PASSWORD = os.environ.get("MB_ADMIN_PASSWORD", "DimaMetabaseLabAdmin!2026")
WAREHOUSE_NAME = "Dima Analytics Lab"


def call(method, path, payload=None, *, session=None, allowed=()):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if session:
        headers["X-Metabase-Session"] = session
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = raw.decode(errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw.decode(errors="replace")
        if exc.code in allowed:
            return exc.code, body
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from exc


def list_payload(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("data", "items"):
            if isinstance(body.get(key), list):
                return body[key]
    return []


def login():
    status, body = call("POST", "/api/session", {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert status == 200
    token = (body or {}).get("id")
    assert token
    return token


def wait_orders(session, seconds=180):
    deadline = time.time() + seconds
    while time.time() < deadline:
        status, body = call(
            "POST",
            "/api/agent/v1/search",
            {"term_queries": ["orders"], "semantic_queries": []},
            session=session,
            allowed=(400, 403, 404),
        )
        if status == 200:
            rows = (body or {}).get("data") or []
            matches = [x for x in rows if x.get("type") == "table" and str(x.get("name", "")).lower() == "orders"]
            if matches:
                return matches[0]
        time.sleep(3)
    raise RuntimeError("orders table did not become discoverable through Agent API")


def database_name(session, database_id):
    status, body = call(
        "POST",
        "/api/agent/v1/read-resource",
        {"uris": [f"metabase://database/{database_id}"]},
        session=session,
    )
    assert status == 200
    resources = (body or {}).get("resources") or []
    assert resources
    content = resources[0].get("content") or {}
    return content.get("name") or WAREHOUSE_NAME


def main(out_path=None):
    receipt = {
        "metabase_runtime": "v0.63.18",
        "process_health": False,
        "unauthenticated_agent_denied": False,
        "agent_api_ping": False,
        "search": False,
        "read_resource": False,
        "construct_query": False,
        "execute_query": False,
        "combined_query": False,
        "continuation_observed": False,
        "raw_sql_disabled": False,
        "observed_page_rows": None,
        "observed_second_page_rows": None,
    }

    status, health = call("GET", "/api/health")
    receipt["process_health"] = status == 200

    unauth_status, _ = call("GET", "/api/agent/v1/ping", allowed=(401, 403))
    receipt["unauthenticated_agent_denied"] = unauth_status in (401, 403)

    session = login()
    status, ping = call("GET", "/api/agent/v1/ping", session=session)
    receipt["agent_api_ping"] = status == 200 and (ping or {}).get("message") == "pong"

    table = wait_orders(session)
    receipt["search"] = True
    database_id = int(table["database_id"])
    db_name = database_name(session, database_id)
    receipt["read_resource"] = True

    schema = str(table.get("database_schema") or "public")
    table_name = str(table["name"])
    portable = {
        "lib/type": "mbql/query",
        "stages": [{
            "lib/type": "mbql.stage/mbql",
            "source-table": [db_name, schema, table_name],
            "limit": 205,
        }],
    }

    status, constructed = call(
        "POST",
        "/api/agent/v2/construct-query",
        {"query": portable},
        session=session,
    )
    encoded = (constructed or {}).get("query")
    receipt["construct_query"] = status == 200 and isinstance(encoded, str) and bool(encoded)

    status, executed = call(
        "POST",
        "/api/agent/v1/execute",
        {"query": encoded},
        session=session,
    )
    receipt["execute_query"] = status == 202 and (executed or {}).get("status") == "completed"

    status, first = call(
        "POST",
        "/api/agent/v2/query",
        {"query": portable},
        session=session,
    )
    receipt["combined_query"] = status == 202 and (first or {}).get("status") == "completed"
    receipt["observed_page_rows"] = int((first or {}).get("row_count") or 0)
    continuation = (first or {}).get("continuation_token")
    receipt["continuation_observed"] = bool(continuation)

    if continuation:
        status, second = call(
            "POST",
            "/api/agent/v2/query",
            {"continuation_token": continuation},
            session=session,
        )
        assert status == 202 and (second or {}).get("status") == "completed"
        receipt["observed_second_page_rows"] = int((second or {}).get("row_count") or 0)

    raw_status, _ = call(
        "POST",
        "/api/agent/v1/execute-sql",
        {"database_id": database_id, "sql": "select 1"},
        session=session,
        allowed=(403,),
    )
    receipt["raw_sql_disabled"] = raw_status == 403

    required = (
        "process_health",
        "unauthenticated_agent_denied",
        "agent_api_ping",
        "search",
        "read_resource",
        "construct_query",
        "execute_query",
        "combined_query",
        "continuation_observed",
        "raw_sql_disabled",
    )
    failed = [key for key in required if not receipt[key]]
    if receipt["observed_page_rows"] is None or receipt["observed_page_rows"] > 200:
        failed.append("page_budget")
    if failed:
        raise RuntimeError(f"capability probe failed: {failed}; receipt={receipt}")

    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    print(rendered)
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(rendered + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out")
    args = parser.parse_args()
    main(args.json_out)
