#!/usr/bin/env python3
"""Bootstrap isolated FT-005N A1 Boyahane control without patching Metabase."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE = os.getenv("METABASE_URL", "http://localhost:3301").rstrip("/")
ADMIN_EMAIL = os.getenv("FT005N_ADMIN_EMAIL", "admin@dima-native.local")
ADMIN_PASSWORD = os.getenv("FT005N_ADMIN_PASSWORD", "DimaNativeControl!2026")
SITE_NAME = "Dima FT005N Native Control"
READONLY_PASSWORD = os.environ["BOYAHANE_READONLY_PASSWORD"]
OPENROUTER_KEY = os.environ["DIMA_OPENROUTER_API_KEY"]
REQUEST_MODEL = os.getenv("FT005N_NATIVE_MODEL", "openai/gpt-5.6-luna")


class HttpError(RuntimeError):
    def __init__(self, status: int, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


def call(method: str, path: str, payload=None, *, session=None, allowed=()):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if session:
        headers["X-Metabase-Session"] = session
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = raw.decode(errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw.decode(errors="replace")
        if exc.code in allowed:
            return exc.code, body
        raise HttpError(exc.code, body) from exc


def wait_health() -> None:
    deadline = time.time() + 300
    while time.time() < deadline:
        try:
            status, _ = call("GET", "/api/health")
            if status == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Metabase health timeout")


def login() -> str:
    _, body = call(
        "POST",
        "/api/session",
        {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    token = str((body or {}).get("id") or "")
    if not token:
        raise RuntimeError("admin session missing")
    return token


def ensure_setup() -> str:
    _, props = call("GET", "/api/session/properties")
    if not bool((props or {}).get("has-user-setup")):
        setup_token = (props or {}).get("setup-token")
        if not setup_token:
            raise RuntimeError("fresh Metabase setup-token missing")
        _, body = call(
            "POST",
            "/api/setup",
            {
                "token": setup_token,
                "user": {
                    "email": ADMIN_EMAIL,
                    "first_name": "Dima",
                    "last_name": "Native Control",
                    "password": ADMIN_PASSWORD,
                },
                "prefs": {"allow_tracking": False, "site_name": SITE_NAME},
                "database": {
                    "name": "Boyahane",
                    "engine": "postgres",
                    "details": {
                        "host": "postgres",
                        "port": 5432,
                        "dbname": "boyahane",
                        "user": "metabase_boyahane",
                        "password": READONLY_PASSWORD,
                    },
                },
            },
        )
        session = str((body or {}).get("id") or "")
        return session or login()
    return login()


def set_setting(session: str, key: str, value) -> None:
    encoded = urllib.parse.quote(key, safe="")
    call("PUT", f"/api/setting/{encoded}", {"value": value}, session=session)


def main() -> None:
    wait_health()
    session = ensure_setup()

    set_setting(session, "ai-features-enabled?", True)
    set_setting(session, "agent-api-enabled?", True)
    set_setting(session, "metabot-enabled?", True)

    # Stock supported API: configure OpenRouter provider/model. Never print the key.
    status, settings = call(
        "PUT",
        "/api/metabot/settings",
        {
            "provider": "openrouter",
            "model": REQUEST_MODEL,
            "api-key": OPENROUTER_KEY,
        },
        session=session,
        allowed=(400, 403, 404),
    )

    _, databases = call("GET", "/api/database", session=session)
    database_rows = (
        databases.get("data", [])
        if isinstance(databases, dict)
        else databases
    )
    database_names = sorted(
        str(item.get("name") or "")
        for item in (database_rows or [])
        if isinstance(item, dict)
    )
    if "Boyahane" not in database_names:
        raise RuntimeError(
            f"A1_CONTROL_DATABASE_MISSING: {database_names}"
        )
    if any("sample" in name.lower() for name in database_names):
        raise RuntimeError(
            f"A1_SAMPLE_DATABASE_CONTAMINATION: {database_names}"
        )

    _, props = call("GET", "/api/session/properties")
    safe = {
        "bootstrap": "ok",
        "metabase_version": (props or {}).get("version"),
        "metabot_settings_status": status,
        "requested_provider": "openrouter",
        "requested_model": REQUEST_MODEL,
        "configured_provider_model": (
            settings.get("value") if status == 200 and isinstance(settings, dict) else None
        ),
        "provider_configuration_error": (
            settings if status != 200 else None
        ),
        "database_names": database_names,
        "sample_database_present": False,
        "secret_recorded": False,
    }
    print(json.dumps(safe, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FT005N bootstrap failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
