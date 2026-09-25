"""Exact-Git authorization transport for DMP-DEC-0051 recovery cycles.

Authorization truth is derived from immutable commit objects and exact parent→HEAD
change status. GitHub event changed-file projections are intentionally irrelevant.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


AUTHORIZATION_DIR = "backend/lab/metabase/p17/authorizations/"
HISTORICAL_RECEIPT = (
    "backend/lab/metabase/p17/AUTONOMOUS_LUNA_AUTHORIZATION.json"
)
EXPECTED_BRANCH = "feat/dima-metabase-platform"
EXPECTED_DECISION = "DMP-DEC-0051"
EXPECTED_PRODUCT_SHA = "d1bc5291b315ff19c3456d08ff1820e983d85942"
EXPECTED_MODEL = "openai/gpt-5.6-luna"
MAX_MANAGER_CALLS = 8
MAX_SOL_CALLS = 0
MAX_ENGINE_BUILDS = 0
MAX_C1_CALLS = 0


class AuthorizationTransportError(RuntimeError):
    pass


@dataclass(frozen=True)
class AuthorizationReceipt:
    path: str
    authorization_id: str
    recovery_cycle: int
    candidate_product_sha: str
    dispatch_parent_sha: str
    provider_free_run_id: int
    governance_run_id: int
    model: str
    max_manager_calls: int
    sol_budget: int
    engine_build_budget: int
    c1_budget: int
    purpose: str


RunGit = Callable[[Sequence[str]], str]


def _default_git(repo_root: Path) -> RunGit:
    def run(args: Sequence[str]) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    return run


def _commit_parent(git: RunGit, sha: str) -> str:
    raw = git(["cat-file", "-p", sha])
    parents = [
        line.split(" ", 1)[1]
        for line in raw.splitlines()
        if line.startswith("parent ")
    ]
    if len(parents) != 1:
        raise AuthorizationTransportError(
            "dispatch commit must have exactly one parent"
        )
    return parents[0]


def _ensure_parent_object(
    git: RunGit,
    *,
    parent_sha: str,
    branch: str,
) -> None:
    try:
        git(["cat-file", "-e", f"{parent_sha}^{{commit}}"])
        return
    except subprocess.CalledProcessError:
        pass
    # Live checkout is intentionally shallow. Fetch the exact branch to depth 2
    # so parent/tree objects exist locally; authorization still comes from the
    # exact parent→HEAD object diff below, never from event metadata.
    git(["fetch", "--no-tags", "--depth=2", "origin", branch])
    try:
        git(["cat-file", "-e", f"{parent_sha}^{{commit}}"])
    except subprocess.CalledProcessError as exc:
        raise AuthorizationTransportError(
            "dispatch parent Git object is unavailable after exact branch fetch"
        ) from exc


def _parse_name_status(raw: str) -> tuple[tuple[str, str], ...]:
    changes: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        status = fields[0]
        if status.startswith(("R", "C")):
            if len(fields) != 3:
                raise AuthorizationTransportError(
                    "unexpected rename/copy diff-tree shape"
                )
            changes.append((status, fields[1]))
            changes.append((status, fields[2]))
            continue
        if len(fields) != 2:
            raise AuthorizationTransportError(
                "unexpected diff-tree name-status shape"
            )
        changes.append((status, fields[1]))
    return tuple(changes)


def _exact_changes(
    git: RunGit,
    *,
    parent_sha: str,
    dispatch_sha: str,
) -> tuple[tuple[str, str], ...]:
    return _parse_name_status(
        git(
            [
                "diff-tree",
                "--no-commit-id",
                "--name-status",
                "-r",
                parent_sha,
                dispatch_sha,
            ]
        )
    )


def _load_receipt(repo_root: Path, path: str) -> dict:
    receipt_path = (repo_root / path).resolve()
    try:
        receipt_path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise AuthorizationTransportError(
            "authorization receipt escaped repository root"
        ) from exc
    try:
        value = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorizationTransportError(
            "authorization receipt is unreadable"
        ) from exc
    if not isinstance(value, dict):
        raise AuthorizationTransportError(
            "authorization receipt must be a JSON object"
        )
    return value


def _require_int(payload: dict, key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise AuthorizationTransportError(
            f"authorization field must be integer: {key}"
        )
    return value


def verify_dispatch_authorization(
    repo_root: Path,
    *,
    dispatch_sha: str,
    branch: str = EXPECTED_BRANCH,
    recovery_cycle: int | None = None,
    run_git: RunGit | None = None,
) -> AuthorizationReceipt:
    """Verify one append-only authorization receipt from exact Git history."""

    if recovery_cycle is not None and recovery_cycle not in {1, 2, 3}:
        raise AuthorizationTransportError("recovery_cycle must be 1, 2, or 3")
    if branch != EXPECTED_BRANCH:
        raise AuthorizationTransportError("authorization branch is not allowed")

    git = run_git or _default_git(repo_root)
    head = git(["rev-parse", "HEAD"])
    if head != dispatch_sha:
        raise AuthorizationTransportError(
            "dispatch SHA does not match checked-out HEAD"
        )

    parent_sha = _commit_parent(git, dispatch_sha)
    _ensure_parent_object(git, parent_sha=parent_sha, branch=branch)
    changes = _exact_changes(
        git,
        parent_sha=parent_sha,
        dispatch_sha=dispatch_sha,
    )

    if any(path == HISTORICAL_RECEIPT for _, path in changes):
        raise AuthorizationTransportError(
            "historical authorization receipt is immutable"
        )

    namespace_changes = tuple(
        (status, path)
        for status, path in changes
        if path.startswith(AUTHORIZATION_DIR)
    )
    added = tuple(
        path
        for status, path in namespace_changes
        if status == "A" and path.endswith(".json")
    )
    if len(added) != 1:
        raise AuthorizationTransportError(
            "dispatch must add exactly one new authorization receipt"
        )
    if len(namespace_changes) != 1:
        raise AuthorizationTransportError(
            "authorization namespace is append-only"
        )

    path = added[0]
    name = Path(path).name
    prefix = "autonomous-luna-recovery-"
    suffix = ".json"
    if not name.startswith(prefix) or not name.endswith(suffix):
        raise AuthorizationTransportError(
            "authorization receipt filename is not a recovery identity"
        )
    cycle_token = name[len(prefix) : -len(suffix)]
    cycle_by_token = {"001": 1, "002": 2, "003": 3}
    inferred_cycle = cycle_by_token.get(cycle_token)
    if inferred_cycle is None:
        raise AuthorizationTransportError(
            "authorization receipt filename recovery cycle is invalid"
        )
    if recovery_cycle is not None and recovery_cycle != inferred_cycle:
        raise AuthorizationTransportError(
            "authorization filename does not match expected recovery_cycle"
        )
    effective_cycle = inferred_cycle

    payload = _load_receipt(repo_root, path)

    exact = {
        "decision": EXPECTED_DECISION,
        "branch": EXPECTED_BRANCH,
        "recovery_cycle": effective_cycle,
        "candidate_product_sha": EXPECTED_PRODUCT_SHA,
        "dispatch_parent_sha": parent_sha,
        "model": EXPECTED_MODEL,
    }
    for key, expected in exact.items():
        if payload.get(key) != expected:
            raise AuthorizationTransportError(
                f"authorization mismatch: {key}"
            )

    authorization_id = str(payload.get("authorization_id") or "").strip()
    if not authorization_id:
        raise AuthorizationTransportError("authorization_id is required")

    provider_free_run_id = _require_int(payload, "provider_free_run_id")
    governance_run_id = _require_int(payload, "governance_run_id")
    max_manager_calls = _require_int(payload, "max_manager_calls")
    sol_budget = _require_int(payload, "sol_budget")
    engine_build_budget = _require_int(payload, "engine_build_budget")
    c1_budget = _require_int(payload, "c1_budget")

    if provider_free_run_id <= 0 or governance_run_id <= 0:
        raise AuthorizationTransportError(
            "provider-free and governance run IDs must be positive"
        )
    if not 0 < max_manager_calls <= MAX_MANAGER_CALLS:
        raise AuthorizationTransportError("manager call budget escalation")
    if sol_budget != MAX_SOL_CALLS:
        raise AuthorizationTransportError("Sol budget escalation")
    if engine_build_budget != MAX_ENGINE_BUILDS:
        raise AuthorizationTransportError("engine-build budget escalation")
    if c1_budget != MAX_C1_CALLS:
        raise AuthorizationTransportError("C1 budget escalation")

    purpose = str(payload.get("purpose") or "").strip()
    if not purpose:
        raise AuthorizationTransportError("authorization purpose is required")

    return AuthorizationReceipt(
        path=path,
        authorization_id=authorization_id,
        recovery_cycle=effective_cycle,
        candidate_product_sha=EXPECTED_PRODUCT_SHA,
        dispatch_parent_sha=parent_sha,
        provider_free_run_id=provider_free_run_id,
        governance_run_id=governance_run_id,
        model=EXPECTED_MODEL,
        max_manager_calls=max_manager_calls,
        sol_budget=sol_budget,
        engine_build_budget=engine_build_budget,
        c1_budget=c1_budget,
        purpose=purpose,
    )
