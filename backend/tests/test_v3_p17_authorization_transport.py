from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from lab.metabase.p17.authorization_transport import (
    AUTHORIZATION_DIR,
    CURRENT_ATTEMPT_IN_FAMILY,
    CURRENT_FAILURE_FAMILY_ID,
    EXPECTED_BRANCH,
    EXPECTED_DECISION,
    EXPECTED_MODEL,
    EXPECTED_PRODUCT_SHA,
    HISTORICAL_RECEIPTS,
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


def _name(
    family: str = CURRENT_FAILURE_FAMILY_ID,
    attempt: int = CURRENT_ATTEMPT_IN_FAMILY,
) -> str:
    return f"{family}--attempt-{attempt:03d}.json"


def _receipt(
    parent: str,
    *,
    failure_family_id: str = CURRENT_FAILURE_FAMILY_ID,
    attempt_in_family: int = CURRENT_ATTEMPT_IN_FAMILY,
    authorization_id: str | None = None,
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
    authorization_id = authorization_id or (
        f"{failure_family_id}--attempt-{attempt_in_family:03d}"
    )
    return {
        "decision": decision,
        "branch": branch,
        "failure_family_id": failure_family_id,
        "attempt_in_family": attempt_in_family,
        "authorization_id": authorization_id,
        "candidate_product_sha": candidate_product_sha,
        "dispatch_parent_sha": dispatch_parent_sha or parent,
        "provider_free_run_id": 123456789,
        "governance_run_id": 987654321,
        "model": model,
        "max_manager_calls": max_manager_calls,
        "sol_budget": sol_budget,
        "engine_build_budget": engine_build_budget,
        "c1_budget": c1_budget,
        "purpose": "bounded autonomous P17 family recovery certification",
        "previous_red_run_id": 36140130559,
        "root_fix_sha": EXPECTED_PRODUCT_SHA,
    }


def _add_receipt(
    root: Path,
    parent: str,
    *,
    name: str | None = None,
    payload: dict | None = None,
) -> tuple[str, str]:
    path = AUTHORIZATION_DIR + (name or _name())
    value = payload or _receipt(parent)
    _write(root, path, json.dumps(value, indent=2) + "\n")
    dispatch = _commit(root, "dispatch")
    return dispatch, path


def _verify(
    root: Path,
    dispatch: str,
    *,
    family: str = CURRENT_FAILURE_FAMILY_ID,
    attempt: int = CURRENT_ATTEMPT_IN_FAMILY,
):
    return verify_dispatch_authorization(
        root,
        dispatch_sha=dispatch,
        branch=EXPECTED_BRANCH,
        expected_failure_family_id=family,
        expected_attempt_in_family=attempt,
    )


def test_accepts_one_exact_family_aware_added_receipt(tmp_path: Path):
    root, parent = _repo(tmp_path)
    dispatch, path = _add_receipt(root, parent)

    verified = _verify(root, dispatch)

    assert verified.path == path
    assert verified.dispatch_parent_sha == parent
    assert verified.failure_family_id == CURRENT_FAILURE_FAMILY_ID
    assert verified.attempt_in_family == CURRENT_ATTEMPT_IN_FAMILY
    assert verified.previous_red_run_id == 36140130559


def test_modified_receipt_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    first, path = _add_receipt(root, parent)
    payload = _receipt(first)
    _write(root, path, json.dumps(payload, indent=2) + "\n")
    modified = _commit(root, "modify receipt")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, modified)


def test_pre_existing_receipt_without_new_receipt_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    _add_receipt(root, parent)
    _write(root, "note.txt", "unrelated\n")
    dispatch = _commit(root, "no new receipt")

    with pytest.raises(
        AuthorizationTransportError,
        match="exactly one new authorization receipt",
    ):
        _verify(root, dispatch)


@pytest.mark.parametrize("historical_path", sorted(HISTORICAL_RECEIPTS))
def test_historical_receipt_delete_readd_is_rejected(
    tmp_path: Path,
    historical_path: str,
):
    root, _ = _repo(tmp_path)
    _write(root, historical_path, "{}\n")
    _commit(root, "historical receipt")
    (root / historical_path).unlink()
    _commit(root, "delete historical receipt")
    _write(root, historical_path, "{}\n")
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
        family = f"family-{index}"
        _write(
            root,
            AUTHORIZATION_DIR + _name(family, 1),
            json.dumps(
                _receipt(
                    parent,
                    failure_family_id=family,
                    attempt_in_family=1,
                ),
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


def test_wrong_family_filename_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    dispatch, _ = _add_receipt(
        root,
        parent,
        name=_name("p17-native-analytics", CURRENT_ATTEMPT_IN_FAMILY),
    )

    with pytest.raises(
        AuthorizationTransportError,
        match="path does not match failure family attempt",
    ):
        _verify(root, dispatch)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("candidate_product_sha", "0" * 40, "candidate_product_sha"),
        ("branch", "wrong-branch", "branch"),
        ("failure_family_id", "p17-native-analytics", "failure_family_id"),
        ("attempt_in_family", 3, "attempt_in_family"),
        ("decision", "DMP-DEC-0051", "decision"),
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
        _verify(root, dispatch)


def test_wrong_authorization_id_is_rejected(tmp_path: Path):
    root, parent = _repo(tmp_path)
    payload = _receipt(parent, authorization_id="wrong-id")
    dispatch, _ = _add_receipt(root, parent, payload=payload)

    with pytest.raises(
        AuthorizationTransportError,
        match="authorization_id",
    ):
        _verify(root, dispatch)


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


@pytest.mark.parametrize("attempt", [0, 4])
def test_attempt_outside_family_budget_is_rejected(
    tmp_path: Path,
    attempt: int,
):
    root, _ = _repo(tmp_path)
    with pytest.raises(
        AuthorizationTransportError,
        match="attempt_in_family",
    ):
        verify_dispatch_authorization(
            root,
            dispatch_sha=_git(root, "rev-parse", "HEAD"),
            expected_failure_family_id=CURRENT_FAILURE_FAMILY_ID,
            expected_attempt_in_family=attempt,
        )


def test_non_machine_safe_family_id_is_rejected(tmp_path: Path):
    root, _ = _repo(tmp_path)
    with pytest.raises(
        AuthorizationTransportError,
        match="machine-safe",
    ):
        verify_dispatch_authorization(
            root,
            dispatch_sha=_git(root, "rev-parse", "HEAD"),
            expected_failure_family_id="P17 Manager Schema",
            expected_attempt_in_family=2,
        )


def test_event_changed_file_projection_is_irrelevant_to_authorization_truth():
    source = Path(
        "lab/metabase/p17/authorization_transport.py"
    ).read_text(encoding="utf-8")

    assert "GITHUB_EVENT_PATH" not in source
    assert "head_commit" not in source
    assert "diff-tree" in source
    assert "cat-file" in source


def test_historical_recovery_001_remains_legacy_not_forward_identity():
    source = Path(
        "lab/metabase/p17/authorization_transport.py"
    ).read_text(encoding="utf-8")

    assert "autonomous-luna-recovery-001.json" in source
    assert "failure_family_id" in source
    assert "attempt_in_family" in source
    assert "recovery_cycle" not in source


def test_repository_historical_recovery_001_receipt_is_unchanged_legacy_evidence():
    path = Path(
        "lab/metabase/p17/authorizations/autonomous-luna-recovery-001.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload == {
        "decision": "DMP-DEC-0051",
        "branch": "feat/dima-metabase-platform",
        "authorization_id": "autonomous-luna-recovery-001",
        "recovery_cycle": 1,
        "candidate_product_sha": (
            "d1bc5291b315ff19c3456d08ff1820e983d85942"
        ),
        "dispatch_parent_sha": (
            "6e3f6ae55f4a4db1211f8f49d259dd3522d14a62"
        ),
        "provider_free_run_id": 36139719694,
        "governance_run_id": 36140014952,
        "model": "openai/gpt-5.6-luna",
        "max_manager_calls": 8,
        "sol_budget": 0,
        "engine_build_budget": 0,
        "c1_budget": 0,
        "purpose": (
            "Recovery Cycle 1 corrected trajectory-invariant autonomous "
            "P17 cognition certification"
        ),
    }
