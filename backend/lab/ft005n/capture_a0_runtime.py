#!/usr/bin/env python3
"""Non-mutating A0 runtime capture for the current Boyahane Metabase instance.

Run from a machine that already hosts the user's Boyahane compose stack.
Never prints or stores API-key/password values.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def run(*args: str, cwd: Path) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def http(method: str, url: str, payload=None, *, session: str | None = None, allowed=()):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if session:
        headers["X-Metabase-Session"] = session
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
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
        raise


def safe_setting(base: str, session: str, key: str):
    encoded = urllib.parse.quote(key, safe="")
    status, body = http("GET", f"{base}/api/setting/{encoded}", session=session, allowed=(400,403,404))
    return {"status": status, "value": body if status == 200 else None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boyahane-dir", type=Path, required=True)
    parser.add_argument("--base-url", default=os.getenv("FT005N_A0_BASE_URL", "http://localhost:3000"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cwd = args.boyahane_dir.resolve()
    base = args.base_url.rstrip("/")
    configured_images = run("docker", "compose", "config", "--images", cwd=cwd).splitlines()
    container_id = run("docker", "compose", "ps", "-q", "metabase", cwd=cwd)
    if not container_id:
        raise RuntimeError("Boyahane metabase container is not running")

    container = json.loads(
        run("docker", "inspect", container_id, cwd=cwd)
    )[0]
    image_id = str(container.get("Image") or "")
    image = json.loads(
        run("docker", "image", "inspect", image_id, cwd=cwd)
    )[0]

    health_status, health = http("GET", f"{base}/api/health")
    props_status, props = http("GET", f"{base}/api/session/properties")

    receipt = {
        "arm": "A0_OBSERVED_VANILLA",
        "mutation_performed": False,
        "configured_images": configured_images,
        "metabase_container_image_ref": (container.get("Config") or {}).get("Image"),
        "local_image_id": image.get("Id"),
        "repo_digests": image.get("RepoDigests") or [],
        "health_status": health_status,
        "health": health,
        "session_properties_status": props_status,
        "metabase_version": (props or {}).get("version"),
        "admin_settings_captured": False,
        "llm_provider_model": None,
        "ai_features_enabled": None,
        "metabot_enabled": None,
    }

    email = os.getenv("FT005N_A0_ADMIN_EMAIL", "").strip()
    password = os.getenv("FT005N_A0_ADMIN_PASSWORD", "")
    if email and password:
        status, login = http(
            "POST",
            f"{base}/api/session",
            {"username": email, "password": password},
        )
        if status != 200 or not isinstance(login, dict) or not login.get("id"):
            raise RuntimeError("A0 admin login failed")
        session = str(login["id"])
        status, settings = http(
            "GET",
            f"{base}/api/metabot/settings",
            session=session,
            allowed=(403,404),
        )
        receipt["metabot_settings_status"] = status
        if status == 200 and isinstance(settings, dict):
            # The endpoint returns provider/model identity and model metadata, not the saved secret.
            receipt["llm_provider_model"] = settings.get("value")
        receipt["ai_features_enabled"] = safe_setting(
            base, session, "ai-features-enabled?"
        )
        receipt["metabot_enabled"] = safe_setting(
            base, session, "metabot-enabled?"
        )
        receipt["admin_settings_captured"] = True

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
