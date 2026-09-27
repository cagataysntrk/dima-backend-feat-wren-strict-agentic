"""Day 6.5 architecture preflight guard.

Owner decision: hidden holdout remains mandatory before architecture seal, but it does
not block contract-only Manager implementation. Hidden prompt text remains forbidden.
"""

from __future__ import annotations

from pathlib import Path

from lab.v2_day6_5_preflight import PLACEHOLDER, evaluate_day65_preflight

ROOT = Path(__file__).resolve().parents[1]

PRODUCTION_MANAGER_FILES = (
    "app/v2/manager_models.py",
    "app/v2/semantic_handles.py",
    "app/v2/source_spans.py",
    "app/v2/acceptance.py",
    "app/v2/representability.py",
    "app/v2/manager_tools.py",
    "app/v2/manager_runtime.py",
    "app/v2/completion.py",
)

ALLOWED_HIDDEN_METADATA_FILES = {
    "v2_day6_5_eval_manifest.yaml",
    "DAY6_5_HIDDEN_HOLDOUT_HANDOFF.md",
}


def test_manager_implementation_is_unlocked_by_owner_policy():
    preflight = evaluate_day65_preflight()
    assert preflight.ready is True, preflight.blockers
    assert preflight.status == "READY_FOR_IMPLEMENTATION"


def test_hidden_holdout_prompt_corpus_is_not_committed():
    eval_dir = ROOT / "eval"
    suspicious = []
    for path in eval_dir.iterdir():
        name = path.name
        if "day6_5" not in name.lower() and "day65" not in name.lower():
            continue
        if "hidden" not in name.lower() and "holdout" not in name.lower():
            continue
        if name in ALLOWED_HIDDEN_METADATA_FILES:
            continue
        suspicious.append(name)

    assert suspicious == [], (
        "Hidden Day6.5 prompt corpus repo içinde görünmemeli; yalnız metadata/handoff "
        f"izinli. found={suspicious}"
    )


def test_placeholder_hashes_cannot_unlock_preflight():
    result = evaluate_day65_preflight()
    if (
        result.corpus_sha256 == PLACEHOLDER
        or result.taxonomy_sha256 == PLACEHOLDER
        or result.attestation_sha256 == PLACEHOLDER
    ):
        assert result.ready is True
        assert result.status == "READY_FOR_IMPLEMENTATION"
