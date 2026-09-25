#!/usr/bin/env python3
"""Fail-closed compatibility entrypoint for the DMP-DEC-0050 one-shot.

The historical screenplay lives in recursive_manager_scenario_lab.py.
The existing secret-bearing CI transport still invokes this path, so this tiny
entrypoint admits the autonomous canary only when the current push *created*
the supervisor authorization receipt. It supplies no investigation guidance.
"""
from __future__ import annotations

import json
import os
import runpy
from pathlib import Path


AUTH = Path(__file__).with_name("AUTONOMOUS_LUNA_AUTHORIZATION.json")
AUTONOMOUS = Path(__file__).with_name("autonomous_manager_canary.py")


def _verify_one_shot_authorization() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    github_sha = os.environ.get("GITHUB_SHA", "").strip()
    if not event_path or not github_sha:
        raise RuntimeError(
            "DMP-DEC-0050 live entrypoint requires GitHub Actions push identity"
        )
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    if event.get("after") != github_sha:
        raise RuntimeError("GitHub push identity does not match GITHUB_SHA")

    head = event.get("head_commit") or {}
    added = set(head.get("added") or ())
    auth_repo_path = "backend/lab/metabase/p17/AUTONOMOUS_LUNA_AUTHORIZATION.json"
    if auth_repo_path not in added:
        raise RuntimeError(
            "paid autonomous canary requires add-only authorization receipt"
        )
    if not AUTH.is_file():
        raise RuntimeError("DMP-DEC-0050 authorization receipt is missing")

    payload = json.loads(AUTH.read_text(encoding="utf-8"))
    expected = {
        "decision": "DMP-DEC-0050",
        "branch": "feat/dima-metabase-platform",
        "max_paid_runs_after_dmp_0050": 1,
        "sol_calls": 0,
        "engine_builds": 0,
        "c1_calls": 0,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise RuntimeError(f"authorization mismatch: {key}")

    if payload.get("candidate_sha") != event.get("before"):
        raise RuntimeError(
            "authorization candidate_sha must equal the pre-dispatch branch SHA"
        )
    for field in ("provider_free_run_id", "governance_run_id"):
        if not str(payload.get(field, "")).isdigit():
            raise RuntimeError(f"authorization field missing: {field}")


if __name__ == "__main__":
    _verify_one_shot_authorization()
    runpy.run_path(str(AUTONOMOUS), run_name="__main__")
