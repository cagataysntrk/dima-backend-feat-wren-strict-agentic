"""Exact-Git, failure-family-aware authorization transport for DMP-DEC-0052.

Authorization truth comes from immutable commit objects plus exact parent→HEAD
change status. GitHub event projections and commit-message semantics are never
authorization truth.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


AUTHORIZATION_DIR = "backend/lab/metabase/p17/authorizations/"
HISTORICAL_RECEIPTS = frozenset(
    {
        "backend/lab/metabase/p17/AUTONOMOUS_LUNA_AUTHORIZATION.json",
        (
            "backend/lab/metabase/p17/authorizations/"
            "autonomous-luna-recovery-001.json"
        ),
        (
            "backend/lab/metabase/p17/authorizations/"
            "p17-manager-structured-schema--attempt-002.json"
        ),
    }
)
EXPECTED_BRANCH = "feat/dima-metabase-platform"
EXPECTED_DECISION = "DMP-DEC-0052"
EXPECTED_PRODUCT_SHA = "e6ab0bcf29bcbc17004c045a4391235ebc1fed19"
EXPECTED_MODEL = "openai/gpt-5.6-luna"
CURRENT_FAILURE_FAMILY_ID = "p17-manager-semantic-output"
CURRENT_ATTEMPT_IN_FAMILY = 2
MAX_ATTEMPT_IN_FAMILY = 3
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
    failure_family_id: str
    attempt_in_family: int
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
    previous_red_run_id: int | None = None
    root_fix_sha: str | None = None


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


def _optional_positive_int(payload: dict, key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AuthorizationTransportError(
            f"authorization field must be a positive integer: {key}"
        )
    return value


def _machine_safe_family_id(value: str) -> bool:
    if not value or value[0] == "-" or value[-1] == "-":
        return False
    return all(ch.islower() or ch.isdigit() or ch == "-" for ch in value)


def _expected_receipt_path(
    failure_family_id: str,
    attempt_in_family: int,
) -> str:
    if not _machine_safe_family_id(failure_family_id):
        raise AuthorizationTransportError(
            "failure_family_id is not machine-safe"
        )
    if not 1 <= attempt_in_family <= MAX_ATTEMPT_IN_FAMILY:
        raise AuthorizationTransportError(
            "attempt_in_family must be between 1 and 3"
        )
    return (
        AUTHORIZATION_DIR
        + failure_family_id
        + "--attempt-"
        + f"{attempt_in_family:03d}"
        + ".json"
    )


def verify_dispatch_authorization(
    repo_root: Path,
    *,
    dispatch_sha: str,
    branch: str = EXPECTED_BRANCH,
    expected_failure_family_id: str = CURRENT_FAILURE_FAMILY_ID,
    expected_attempt_in_family: int = CURRENT_ATTEMPT_IN_FAMILY,
    run_git: RunGit | None = None,
) -> AuthorizationReceipt:
    """Verify one append-only family-aware receipt from exact Git history."""

    expected_path = _expected_receipt_path(
        expected_failure_family_id,
        expected_attempt_in_family,
    )
    if branch != EXPECTED_BRANCH:
        raise AuthorizationTransportError(
            "authorization branch is not allowed"
        )

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

    if any(path in HISTORICAL_RECEIPTS for _, path in changes):
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
    if added[0] != expected_path:
        raise AuthorizationTransportError(
            "authorization receipt path does not match failure family attempt"
        )

    payload = _load_receipt(repo_root, expected_path)
    exact = {
        "decision": EXPECTED_DECISION,
        "branch": EXPECTED_BRANCH,
        "failure_family_id": expected_failure_family_id,
        "attempt_in_family": expected_attempt_in_family,
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
    expected_authorization_id = (
        expected_failure_family_id
        + "--attempt-"
        + f"{expected_attempt_in_family:03d}"
    )
    if authorization_id != expected_authorization_id:
        raise AuthorizationTransportError(
            "authorization_id does not match failure family attempt"
        )

    provider_free_run_id = _require_int(payload, "provider_free_run_id")
    governance_run_id = _require_int(payload, "governance_run_id")
    max_manager_calls = _require_int(payload, "max_manager_calls")
    sol_budget = _require_int(payload, "sol_budget")
    engine_build_budget = _require_int(payload, "engine_build_budget")
    c1_budget = _require_int(payload, "c1_budget")
    previous_red_run_id = _optional_positive_int(
        payload,
        "previous_red_run_id",
    )
    root_fix_sha = payload.get("root_fix_sha")
    if root_fix_sha is not None:
        root_fix_sha = str(root_fix_sha).strip() or None

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
        raise AuthorizationTransportError(
            "authorization purpose is required"
        )

    return AuthorizationReceipt(
        path=expected_path,
        authorization_id=authorization_id,
        failure_family_id=expected_failure_family_id,
        attempt_in_family=expected_attempt_in_family,
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
        previous_red_run_id=previous_red_run_id,
        root_fix_sha=root_fix_sha,
    )
