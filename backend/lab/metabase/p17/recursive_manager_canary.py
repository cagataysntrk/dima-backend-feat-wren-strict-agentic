#!/usr/bin/env python3
"""Fail-closed compatibility entrypoint for DMP-DEC-0052 family recovery.

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
    CURRENT_ATTEMPT_IN_FAMILY,
    CURRENT_FAILURE_FAMILY_ID,
    verify_dispatch_authorization,
)


AUTONOMOUS = Path(__file__).with_name("autonomous_manager_canary.py")
REPO_ROOT = Path(__file__).resolve().parents[4]


def _verify_exact_git_authorization() -> None:
    github_sha = os.environ.get("GITHUB_SHA", "").strip()
    github_ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
    if not github_sha:
        raise AuthorizationTransportError(
            "DMP-DEC-0052 live entrypoint requires GITHUB_SHA"
        )
    if github_ref_name != "feat/dima-metabase-platform":
        raise AuthorizationTransportError(
            "DMP-DEC-0052 live entrypoint requires the certified branch"
        )

    verify_dispatch_authorization(
        REPO_ROOT,
        dispatch_sha=github_sha,
        branch=github_ref_name,
        expected_failure_family_id=CURRENT_FAILURE_FAMILY_ID,
        expected_attempt_in_family=CURRENT_ATTEMPT_IN_FAMILY,
    )


if __name__ == "__main__":
    _verify_exact_git_authorization()
    runpy.run_path(str(AUTONOMOUS), run_name="__main__")

# DMP-DEC-0052 forward family: p17-manager-semantic-output / attempt 2
