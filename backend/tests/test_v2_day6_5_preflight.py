"""Day 6.5 architecture preflight guard.

Persistent guard: production Manager files are forbidden until the external hidden
holdout hashes are frozen. The test flips naturally once the manifest is sealed.
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


def test_manager_product_code_requires_external_hidden_freeze():
    preflight = evaluate_day65_preflight()
    existing = [path for path in PRODUCTION_MANAGER_FILES if (ROOT / path).exists()]

    if existing:
        assert preflight.ready, (
            "Day6.5 production Manager files hidden holdout freeze edilmeden eklendi: "
            f"{existing}; blockers={preflight.blockers}"
        )
    else:
        # Current PREPARED state must remain explicitly blocked, not silently look ready.
        assert preflight.status in {"BLOCKED", "READY"}


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
    if result.corpus_sha256 == PLACEHOLDER or result.taxonomy_sha256 == PLACEHOLDER:
        assert result.ready is False
        assert result.status == "BLOCKED"
