#!/usr/bin/env python3
"""Idempotent bootstrap for the isolated M2 Metabase lab.

This script configures lab runtime state only. It does not import Dima product code and
does not establish Dima→Metabase routing.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request


BASE = os.environ.get("METABASE_URL", f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}").rstrip("/")
ADMIN_EMAIL = os.environ.get("MB_ADMIN_EMAIL", "admin@dima-lab.local")
ADMIN_PASSWORD = os.environ.get("MB_ADMIN_PASSWORD", "DimaMetabaseLabAdmin!2026")
SITE_NAME = os.environ.get("MB_SITE_NAME", "Dima Metabase Lab")
RESTRICTED_EMAIL = os.environ.get("MB_RESTRICTED_EMAIL", "restricted@dima-lab.local")
RESTRICTED_PASSWORD = os.environ.get("MB_RESTRICTED_PASSWORD", "DimaMetabaseLabRestricted!2026")
RESTRICTED_GROUP = os.environ.get("MB_RESTRICTED_GROUP", "Dima Lab Restricted")
ANALYTICS_DB_NAME = os.environ.get("ANALYTICS_DB_NAME", "dima_analytics")
ANALYTICS_DB_USER = os.environ.get("ANALYTICS_DB_USER", "dima_analytics")
ANALYTICS_DB_PASSWORD = os.environ.get("ANALYTICS_DB_PASSWORD", "dima-analytics-lab")
WAREHOUSE_NAME = "Dima Analytics Lab"


class HttpError(RuntimeError):
    def __init__(self, status: int, body: object):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


def request(method: str, path: str, payload=None, *, session: str | None = None):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if session:
        headers["X-Metabase-Session"] = session
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw.decode(errors="replace")
        raise HttpError(exc.code, body) from exc


def wait_health(seconds: int = 240) -> None:
    deadline = time.time() + seconds
    last = None
    while time.time() < deadline:
        try:
            status, body = request("GET", "/api/health")
            if status == 200:
                print(json.dumps({"health": body, "status": status}))
                return
        except Exception as exc:  # startup probe only
            last = repr(exc)
        time.sleep(2)
    raise RuntimeError(f"Metabase health timeout; last={last}")


def login() -> str:
    _, body = request("POST", "/api/session", {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    token = str((body or {}).get("id") or "")
    if not token:
        raise RuntimeError("admin session token missing")
    return token


def ensure_setup() -> str:
    _, props = request("GET", "/api/session/properties")
    if not bool((props or {}).get("has-user-setup")):
        token = (props or {}).get("setup-token")
        if not token:
            raise RuntimeError("fresh Metabase has no setup-token")
        payload = {
            "token": token,
            "user": {
                "email": ADMIN_EMAIL,
                "first_name": "Dima",
                "last_name": "Lab Admin",
                "password": ADMIN_PASSWORD,
            },
            "prefs": {"allow_tracking": False, "site_name": SITE_NAME},
            "database": {
                "name": WAREHOUSE_NAME,
                "engine": "postgres",
                "details": {
                    "host": "analytics-db",
                    "port": 5432,
                    "dbname": ANALYTICS_DB_NAME,
                    "user": ANALYTICS_DB_USER,
                    "password": ANALYTICS_DB_PASSWORD,
                },
            },
        }
        _, body = request("POST", "/api/setup", payload)
        session = str((body or {}).get("id") or "")
        if not session:
            session = login()
        print("initial setup completed")
        return session
    print("initial setup already complete")
    return login()


def set_setting(session: str, key: str, value) -> None:
    request("PUT", f"/api/setting/{key}", {"value": value}, session=session)
    print(f"setting {key}={value!r}")


def list_payload(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("data", "items"):
            if isinstance(body.get(key), list):
                return body[key]
    return []


def ensure_database(session: str) -> int:
    _, body = request("GET", "/api/database", session=session)
    for item in list_payload(body):
        if item.get("name") == WAREHOUSE_NAME:
            return int(item["id"])
    _, created = request(
        "POST",
        "/api/database",
        {
            "name": WAREHOUSE_NAME,
            "engine": "postgres",
            "details": {
                "host": "analytics-db",
                "port": 5432,
                "dbname": ANALYTICS_DB_NAME,
                "user": ANALYTICS_DB_USER,
                "password": ANALYTICS_DB_PASSWORD,
            },
        },
        session=session,
    )
    return int(created["id"])


def ensure_group(session: str) -> int:
    _, body = request("GET", "/api/permissions/group", session=session)
    for item in list_payload(body):
        if item.get("name") == RESTRICTED_GROUP:
            return int(item["id"])
    _, created = request("POST", "/api/permissions/group", {"name": RESTRICTED_GROUP}, session=session)
    return int(created["id"])


def ensure_user(session: str) -> int:
    _, body = request("GET", "/api/user", session=session)
    for item in list_payload(body):
        if item.get("email") == RESTRICTED_EMAIL:
            return int(item["id"])
    _, created = request(
        "POST",
        "/api/user",
        {
            "email": RESTRICTED_EMAIL,
            "first_name": "Dima",
            "last_name": "Restricted",
            "password": RESTRICTED_PASSWORD,
        },
        session=session,
    )
    return int(created["id"])


def ensure_membership(session: str, user_id: int, group_id: int) -> None:
    _, body = request("GET", "/api/permissions/membership", session=session)
    memberships = []
    if isinstance(body, dict):
        memberships = body.get(str(group_id)) or body.get(group_id) or []
        if not memberships:
            memberships = [m for value in body.values() if isinstance(value, list) for m in value]
    for item in memberships:
        if int(item.get("user_id", -1)) == user_id and int(item.get("group_id", group_id)) == group_id:
            return
    try:
        request(
            "POST",
            "/api/permissions/membership",
            {"user_id": user_id, "group_id": group_id},
            session=session,
        )
    except HttpError as exc:
        # Some runtime versions represent default membership differently; only an exact
        # duplicate/validation conflict is tolerable, never auth/server errors.
        if exc.status not in (400, 409):
            raise


def main() -> None:
    wait_health()
    session = ensure_setup()
    set_setting(session, "ai-features-enabled", True)
    set_setting(session, "agent-api-enabled", True)
    set_setting(session, "mcp-execute-sql-enabled", False)
    database_id = ensure_database(session)
    group_id = ensure_group(session)
    user_id = ensure_user(session)
    ensure_membership(session, user_id, group_id)
    print(json.dumps({
        "bootstrap": "ok",
        "database_id": database_id,
        "restricted_group_id": group_id,
        "restricted_user_id": user_id,
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"bootstrap failed: {exc}", file=sys.stderr)
        raise
