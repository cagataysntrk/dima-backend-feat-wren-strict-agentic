#!/usr/bin/env python3
"""Fail-closed compatibility entrypoint for DMP-DEC-0051 recovery certification.

Historical screenplay logic lives in recursive_manager_scenario_lab.py.
This entrypoint only verifies one append-only recovery authorization receipt
against exact Git parent→HEAD object truth, then transfers control to the
DMP-DEC-0050 autonomous canary. GitHub event changed-file projections are not
authorization truth.
"""
from __future__ import annotations

import os
import runpy
from pathlib import Path

from lab.metabase.p17.authorization_transport import (
    AuthorizationTransportError,
    verify_dispatch_authorization,
)


AUTONOMOUS = Path(__file__).with_name("autonomous_manager_canary.py")
REPO_ROOT = Path(__file__).resolve().parents[4]


def _recovery_cycle() -> int:
    raw = os.environ.get("DIMA_P17_RECOVERY_CYCLE", "1").strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise AuthorizationTransportError(
            "DIMA_P17_RECOVERY_CYCLE must be an integer"
        ) from exc
    if value not in {1, 2, 3}:
        raise AuthorizationTransportError(
            "DIMA_P17_RECOVERY_CYCLE must be 1, 2, or 3"
        )
    return value


def _verify_exact_git_authorization() -> None:
    github_sha = os.environ.get("GITHUB_SHA", "").strip()
    github_ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
    if not github_sha:
        raise AuthorizationTransportError(
            "DMP-DEC-0051 live entrypoint requires GITHUB_SHA"
        )
    if github_ref_name != "feat/dima-metabase-platform":
        raise AuthorizationTransportError(
            "DMP-DEC-0051 live entrypoint requires the certified branch"
        )

    verify_dispatch_authorization(
        REPO_ROOT,
        dispatch_sha=github_sha,
        branch=github_ref_name,
        recovery_cycle=_recovery_cycle(),
    )


if __name__ == "__main__":
    _verify_exact_git_authorization()
    runpy.run_path(str(AUTONOMOUS), run_name="__main__")
