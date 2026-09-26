"""Pre-comparison canary manifest contract; provider-free only."""

from __future__ import annotations

import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
MANIFEST = BACKEND / "eval" / "v2_precomparison_canary_manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_canary_has_required_small_continuous_size_and_unique_cases():
    manifest = _manifest()
    cases = manifest["cases"]
    ids = [item["id"] for item in cases]
    assert 8 <= len(cases) <= 16
    assert manifest["case_count"] == len(cases)
    assert len(ids) == len(set(ids))


def test_canary_nodes_are_real_provider_free_pytest_nodes():
    for item in _manifest()["cases"]:
        path_text, test_name = item["node"].split("::", 1)
        path = BACKEND / path_text
        assert path.exists(), item["node"]
        text = path.read_text(encoding="utf-8")
        assert f"def {test_name}(" in text, item["node"]


def test_canary_never_consumes_large_certification_corpora_or_live_providers():
    manifest = _manifest()
    forbidden = set(manifest["forbidden"])
    assert {"DEV80", "Validation50", "Hidden50", "live provider calls"} <= forbidden
    raw = json.dumps(manifest).lower()
    assert "workflow_dispatch paid" not in raw
