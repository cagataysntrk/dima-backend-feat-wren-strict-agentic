#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx

BASE = os.getenv("DIMA_ENGINE_URL", "http://127.0.0.1:3312").rstrip("/")
ADMIN_EMAIL = os.environ["FT005N_ENGINE_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["FT005N_ENGINE_ADMIN_PASSWORD"]
WAREHOUSE = "Dima Analytics Lab"


def wait_health() -> None:
    deadline = time.time() + 300
    while time.time() < deadline:
        try:
            r = httpx.get(BASE + "/api/health", timeout=5)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("engine health timeout")


def login() -> str:
    r = httpx.post(
        BASE + "/api/session",
        json={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json().get("id")
    if not token:
        raise RuntimeError("engine admin session missing")
    return str(token)


def client(session: str) -> httpx.Client:
    return httpx.Client(
        base_url=BASE,
        headers={"X-Metabase-Session": session, "Accept": "application/json"},
        timeout=60,
    )


def setup_if_needed() -> str:
    props = httpx.get(BASE + "/api/session/properties", timeout=30)
    props.raise_for_status()
    body = props.json()
    if body.get("has-user-setup"):
        return login()
    token = body.get("setup-token")
    if not token:
        raise RuntimeError("setup-token missing")
    r = httpx.post(
        BASE + "/api/setup",
        json={
            "token": token,
            "user": {
                "email": ADMIN_EMAIL,
                "first_name": "Dima",
                "last_name": "E2E",
                "password": ADMIN_PASSWORD,
            },
            "prefs": {"allow_tracking": False, "site_name": "Dima Native E2E"},
            "database": {
                "name": WAREHOUSE,
                "engine": "postgres",
                "details": {
                    "host": "analytics-db",
                    "port": 5432,
                    "dbname": "boyahane",
                    "user": "metabase_boyahane",
                    "password": os.environ["BOYAHANE_READONLY_PASSWORD"],
                },
            },
        },
        timeout=60,
    )
    r.raise_for_status()
    session = (r.json() or {}).get("id")
    return str(session) if session else login()


def items(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("data", "items", "groups"):
            value = body.get(key)
            if isinstance(value, list):
                return value
    return []


def main() -> None:
    wait_health()
    session = setup_if_needed()
    with client(session) as c:
        dbs = c.get("/api/database")
        dbs.raise_for_status()
        database = next((x for x in items(dbs.json()) if x.get("name") == WAREHOUSE), None)
        if database:
            database_id = int(database["id"])
        else:
            created = c.post(
                "/api/database",
                json={
                    "name": WAREHOUSE,
                    "engine": "postgres",
                    "details": {
                        "host": "analytics-db",
                        "port": 5432,
                        "dbname": "boyahane",
                        "user": "metabase_boyahane",
                        "password": os.environ["BOYAHANE_READONLY_PASSWORD"],
                    },
                },
            )
            created.raise_for_status()
            database_id = int(created.json()["id"])

        deadline = time.time() + 240
        while True:
            meta = c.get(f"/api/database/{database_id}/metadata")
            if meta.status_code == 200:
                tables = (meta.json() or {}).get("tables") or []
                if any(t.get("name") == "satis_siparisleri" for t in tables):
                    break
            if time.time() >= deadline:
                raise RuntimeError("Boyahane metadata sync timeout")
            time.sleep(3)

        collection = c.post(
            "/api/collection",
            json={"name": "Dima E2E", "description": "native engine e2e"},
        )
        collection.raise_for_status()
        collection_id = int(collection.json()["id"])

        dashboard = c.post(
            "/api/dashboard",
            json={"name": "Dima E2E", "collection_id": collection_id},
        )
        dashboard.raise_for_status()
        dashboard_id = int(dashboard.json()["id"])

        groups = c.get("/api/permissions/group")
        groups.raise_for_status()
        admin_group = next((x for x in items(groups.json()) if x.get("name") == "Administrators"), None)
        if not admin_group:
            raise RuntimeError("Administrators group missing")

        key_res = c.post(
            "/api/api-key",
            json={"name": "Dima E2E Tenant", "group_id": int(admin_group["id"])},
        )
        key_res.raise_for_status()
        api_key = str(key_res.json().get("unmasked_key") or "")
        if not api_key.startswith("mb_"):
            raise RuntimeError("tenant API key missing")

    print(f"::add-mask::{api_key}")
    tenant_headers = {"X-API-Key": api_key, "Accept": "application/json"}
    perms = httpx.get(
        BASE + "/api/metabot/permissions/user-permissions",
        headers=tenant_headers,
        timeout=30,
    )
    perms.raise_for_status()
    resolved = (perms.json() or {}).get("permissions") or {}
    if resolved.get("metabot") != "yes" or resolved.get("metabot-nlq") != "yes":
        raise RuntimeError(f"native Metabot permission mismatch: {resolved}")

    tenant = {
        "boyahane": {
            "name": "Demo Boyahane",
            "apiKey": api_key,
            "databaseId": database_id,
            "collectionId": collection_id,
            "dashboardId": dashboard_id,
            "schema": "public",
        }
    }
    env_file = Path(os.environ["GITHUB_ENV"])
    with env_file.open("a", encoding="utf-8") as out:
        out.write(f"DIMA_ENGINE_URL={BASE}\n")
        out.write(f"DIMA_ENGINE_ADMIN_API_KEY={api_key}\n")
        out.write("DIMA_ENGINE_TENANTS<<__DIMA_TENANTS__\n")
        out.write(json.dumps(tenant, separators=(",", ":")) + "\n")
        out.write("__DIMA_TENANTS__\n")

    print(json.dumps({
        "engine_release": "0.63.18-dima.0",
        "engine_digest": "sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9",
        "database_id": database_id,
        "collection_id": collection_id,
        "dashboard_id": dashboard_id,
        "metabot_permissions": resolved,
        "api_key_recorded": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
