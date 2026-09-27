from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "eval" / "v2_day6_5_j1b_real_flow_frozen.json"
HARNESS = ROOT / "lab" / "v2_day6_5_luna_same_frozen_control.py"


def _module():
    spec = importlib.util.spec_from_file_location("d65_luna_control", HARNESS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_luna_control_reuses_exact_frozen_j1b_corpus():
    doc = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert doc["version"] == "d65-j1b-semantic-family-v1-frozen"
    assert len(doc["cases"]) == 20
    assert len(doc["temporal_scenarios"]) == 8
    assert hashlib.sha256(CORPUS.read_bytes()).hexdigest()


def test_luna_control_is_single_model_no_fallback_cascade_or_threshold():
    module = _module()
    assert module.MODEL == "openai/gpt-5.6-luna"
    assert module.MAX_TOKENS == 512
    text = HARNESS.read_text(encoding="utf-8")
    assert '"provider": {"allow_fallbacks": False}' in text
    assert '"reasoning": {"enabled": False}' in text
    assert '"fallback": False' in text
    assert '"cascade": False' in text
    assert '"confidence_threshold": False' in text
    assert "StructuredSemanticCandidateDecisionProvider" in text
    assert "StructuredTemporalNormalizationProvider" in text
    assert "ManagerSemanticResolutionAdapter" in text


def test_luna_control_green_requires_all_defined_p0_zero():
    text = HARNESS.read_text(encoding="utf-8")
    for key in (
        "silent_semantic_wrong",
        "unsafe_ambiguity_auto_pick",
        "candidate_escape",
        "cross_tenant_leak",
        "semantic_provider_failure",
        "semantic_invalid_typed_contract",
        "real_flow_temporal_wrong",
        "temporal_invalid_typed_contract",
        "temporal_provider_failure",
        "hidden_fallback",
    ):
        assert key in text
    assert "all(value == 0 for value in p0.values())" in text
