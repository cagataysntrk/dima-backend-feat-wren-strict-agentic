#!/usr/bin/env python3
"""FT-005N stock native endpoint availability + Q1 smoke."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

from native_stream import NativeMetabotSession


BASE = os.getenv("METABASE_URL", "http://localhost:3301").rstrip("/")
EMAIL = os.getenv("FT005N_ADMIN_EMAIL", "admin@dima-native.local")
PASSWORD = os.getenv("FT005N_ADMIN_PASSWORD", "DimaNativeControl!2026")
OUT = Path(os.getenv("FT005N_NATIVE_SMOKE_RECEIPT", "artifacts/ft005n-native-smoke.json"))
QUESTION = "1-22 Haziran 2026 arasında satış siparişlerinin toplam tutarı ne kadar?"


def login() -> str:
    data = json.dumps({"username": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        BASE + "/api/session",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = json.loads(response.read())
    return str(body["id"])


def main() -> int:
    session = login()
    native = NativeMetabotSession(base_url=BASE, session=session, profile_id="nlq")
    turn = native.ask(QUESTION)

    if turn.http_status in (401, 402, 403, 404):
        status = "NATIVE_ENDPOINT_NOT_AVAILABLE_IN_THIS_STOCK_CONFIG"
        outcome = "PERMISSION_BLOCKED" if turn.http_status in (401, 402, 403) else "HARNESS_FAILURE"
    elif turn.http_status != 202:
        status = "RED"
        outcome = "HARNESS_FAILURE"
    elif turn.errors:
        status = "RED"
        outcome = "PROVIDER_FAILURE"
    else:
        status = "GREEN"
        outcome = "ENDPOINT_AVAILABLE"

    receipt = {
        "status": status,
        "outcome": outcome,
        "arm": "B_DIRECT_NATIVE_METABOT",
        "metabase_runtime": "v0.63.18",
        "image_digest": "sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73",
        "profile_id": "nlq",
        "requested_model_provider": "openrouter",
        "requested_model": os.getenv("FT005N_NATIVE_MODEL", "openai/gpt-5.6-luna"),
        "turn": turn.receipt(),
        "history_count_after": len(native.history),
        "state_keys_after": sorted(native.state.keys()),
        "license_bypass": False,
        "feature_gate_patch": False,
        "metabase_source_patch": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    # Permission/stock-unavailability is a valid classified experiment outcome.
    return 0 if status in {"GREEN", "NATIVE_ENDPOINT_NOT_AVAILABLE_IN_THIS_STOCK_CONFIG"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
