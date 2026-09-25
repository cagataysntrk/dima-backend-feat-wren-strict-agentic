from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from lab.metabase.p17.authorization_transport import (
    AUTHORIZATION_DIR,
    EXPECTED_BRANCH,
    EXPECTED_DECISION,
    EXPECTED_MODEL,
    EXPECTED_PRODUCT_SHA,
    HISTORICAL_RECEIPT,
    AuthorizationTransportError,
    verify_dispatch_authorization,
)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _write(root: Path, path: str, value: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=Dima Test",
        "-c",
        "user.email=dima-test@example.invalid",
        "commit",
        "-m",
        message,
    )
    return _git(root, "rev-parse", "HEAD")


def _repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "checkout", "-b", EXPECTED_BRANCH)
    _write(root, "README.md", "base\n")
    base = _commit(root, "base")
    return root, base


def _receipt(
    parent: str,
    *,
    authorization_id: str = "autonomous-luna-recovery-001",
    recovery_cycle: int = 1,
    candidate_product_sha: str = EXPECTED_PRODUCT_SHA,
    dispatch_parent_sha: str | None = None,
    branch: str = EXPECTED_BRANCH,
    decision: str = EXPECTED_DECISION,
    model: str = EXPECTED_MODEL,
    max_manager_calls: int = 8,
    sol_budget: int = 0,
    engine_build_budget: int = 0,
    c1_budget: int = 0,
) -> dict:
    return {
        "decision": decision,
        "branch": branch,
        "authorization_id": authorization_id,
        "recovery_cycle": recovery_cycle,
        "candidate_product_sha": candidate_product_sha,
        "dispatch_parent_sha": dispatch_parent_sha or parent,
        "provider_free_run_id": 123456789,
        "governance_run_id": 987654321,
        "model": model,
        "max_manager_calls": max_manager_calls,
        "sol_budget": sol_budget,
        "engine_build_budget": engine_build_budget,
        "c1_budget": c1_budget,
        "purpose": "bounded autonomous P17 recovery certification",
    }


def _add_receipt(
    root: Path,
    parent: str,
    *,
    name: str = "autonomous-luna-recovery-001.json",
    payload: dict | None = None,
) -> tuple[str, str]:
    path = AUTHORIZATION_DIR + name
    value = payload or _receipt(parent)
    _write(root, path, json.dumps(value, indent=2) + "\n")
    dispatch = _commit(root, "dispatch")
    return dispatch, path


def _verify(root: Path, dispatch: str, *, cycle: int = 1):
    return verify_dispatch_authorization(
        root,
        dispatch_sha=dispatch,
        branch=EXPECTED_BRANCH,
        recovery_cycle=cycle,
    )


def test_detects_exactly_one_new_receipt_from_parent_head_git_diff(tmp_path: Path):
    root, parent = _repo(tmp_path)
    dispatch, path = _add_receipt(root, parent)

    verified = _verify(root, dispatch)

    assert verified.path == path
    assert verified.dispatch_parent_sha == parent
    assert verified.authorization_id == "autonomous-luna-recovery-001"


def test_modified_receipt_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    first, path = _add_receipt(root, parent)
    payload = _receipt(first, authorization_id="pre-existing")
    _write(root, path, json.dumps(payload, indent=2) + "\n")
    modified = _commit(root, "modify receipt")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, modified)


def test_pre_existing_receipt_without_new_receipt_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    first, _ = _add_receipt(root, parent)
    _write(root, "note.txt", "unrelated\n")
    dispatch = _commit(root, "no new receipt")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, dispatch)


def test_deleted_readded_historical_receipt_is_rejected(tmp_path: Path):
    root, _ = _repo(tmp_path)
    _write(root, HISTORICAL_RECEIPT, "{}\n")
    first = _commit(root, "historical receipt")
    (root / HISTORICAL_RECEIPT).unlink()
    _commit(root, "delete historical receipt")
    _write(root, HISTORICAL_RECEIPT, "{}\n")
    dispatch = _commit(root, "readd historical receipt")

    with pytest.raises(
        AuthorizationTransportError,
        match="historical authorization receipt is immutable",
    ):
        _verify(root, dispatch)


def test_zero_new_receipts_is_rejected(tmp_path: Path):
    root, _ = _repo(tmp_path)
    _write(root, "other.txt", "x\n")
    dispatch = _commit(root, "other change")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, dispatch)


def test_two_new_receipts_are_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    for index in (1, 2):
        _write(
            root,
            AUTHORIZATION_DIR + f"receipt-{index}.json",
            json.dumps(
                _receipt(parent, authorization_id=f"receipt-{index}"),
                indent=2,
            )
            + "\n",
        )
    dispatch = _commit(root, "two receipts")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, dispatch)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("candidate_product_sha", "0" * 40, "candidate_product_sha"),
        ("branch", "wrong-branch", "branch"),
        ("recovery_cycle", 2, "recovery_cycle"),
        ("decision", "DMP-DEC-0050", "decision"),
        ("model", "other-model", "model"),
    ],
)
def test_identity_mismatches_are_rejected(
    tmp_path: Path,
    field: str,
    value: object,
    error: str,
):
    root, parent = _repo(tmp_path)
    payload = _receipt(parent)
    payload[field] = value
    dispatch, _ = _add_receipt(root, parent, payload=payload)

    with pytest.raises(AuthorizationTransportError, match=error):
        _verify(root, dispatch, cycle=1)


def test_wrong_dispatch_parent_sha_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    payload = _receipt(parent, dispatch_parent_sha="f" * 40)
    dispatch, _ = _add_receipt(root, parent, payload=payload)

    with pytest.raises(
        AuthorizationTransportError,
        match="dispatch_parent_sha",
    ):
        _verify(root, dispatch)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("max_manager_calls", 9, "manager call budget escalation"),
        ("sol_budget", 1, "Sol budget escalation"),
        ("engine_build_budget", 1, "engine-build budget escalation"),
        ("c1_budget", 1, "C1 budget escalation"),
    ],
)
def test_budget_escalation_is_rejected(
    tmp_path: Path,
    field: str,
    value: int,
    error: str,
):
    root, parent = _repo(tmp_path)
    payload = _receipt(parent)
    payload[field] = value
    dispatch, _ = _add_receipt(root, parent, payload=payload)

    with pytest.raises(AuthorizationTransportError, match=error):
        _verify(root, dispatch)


def test_event_head_commit_added_is_irrelevant_to_authorization_truth():
    source = Path(
        "lab/metabase/p17/authorization_transport.py"
    ).read_text(encoding="utf-8")

    assert "GITHUB_EVENT_PATH" not in source
    assert "head_commit" not in source
    assert "diff-tree" in source
    assert "cat-file" in source
