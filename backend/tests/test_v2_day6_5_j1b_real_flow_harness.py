from __future__ import annotations

import json
from pathlib import Path

from app.v2.models import BoundedSemanticContextV0

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "eval" / "v2_day6_5_j1b_real_flow_frozen.json"
HARNESS = ROOT / "lab" / "v2_day6_5_j1b_real_flow.py"


def _doc():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def _norm(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def test_j1b_real_flow_corpus_is_frozen_family_level_and_not_single_case_patch():
    doc = _doc()
    assert doc["version"] == "d65-j1b-semantic-family-v1-frozen"
    assert doc["frozen_before_live_result"] is True
    assert len(doc["cases"]) == 20
    families = {case["family"] for case in doc["cases"]}
    assert {
        "ambiguous_generic_metric",
        "multiple_plausible_candidate",
        "partial_business_alias_unique",
        "under_specified_measure",
        "unique_paraphrase",
    } <= families
    assert len(doc["temporal_scenarios"]) == 8
    BoundedSemanticContextV0.model_validate(doc["context"])


def test_j1b_model_needed_semantic_cases_do_not_accidentally_become_exact_alias_controls():
    doc = _doc()
    aliases = set()
    canonical = set()
    for cube in doc["context"]["cubes"]:
        for field in cube.get("measures", []):
            canonical.add(_norm(field["canonical_name"]))
            aliases.add(_norm(field.get("display") or ""))
            aliases.update(_norm(v) for v in field.get("synonyms", []))
    for field in doc["context"].get("kpis", []):
        canonical.add(_norm(field["canonical_name"]))
        aliases.add(_norm(field.get("display") or ""))
        aliases.update(_norm(v) for v in field.get("synonyms", []))

    for case in doc["cases"]:
        assert _norm(case["surface"]) not in aliases
        assert _norm(case["surface"]) not in canonical


def test_j1b_live_harness_has_no_fallback_cascade_or_threshold_logic():
    text = HARNESS.read_text(encoding="utf-8")
    assert 'TERRA_MODEL = "openai/gpt-5.6-terra"' in text
    assert "JevDecisionProvider" in text
    assert '"fallback": False' in text
    assert '"cascade": False' in text
    assert '"confidence_threshold": False' in text
    assert "tenant-foreign" in text
    assert "ManagerSemanticResolutionAdapter" in text
