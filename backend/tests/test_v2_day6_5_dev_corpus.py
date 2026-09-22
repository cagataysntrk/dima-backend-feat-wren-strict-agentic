"""Static integrity checks for the visible Day 6.5 DEV corpus."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day6_5_dev_cases.yaml"
MANIFEST = ROOT / "eval" / "v2_day6_5_eval_manifest.yaml"


def test_day65_dev_corpus_is_complete_and_taxonomy_balanced():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    cases = list(doc["cases"])

    assert doc["visibility"] == "VISIBLE_TO_DEVELOPMENT"
    assert doc["target_total"] == 80
    assert doc["current_seed_count"] == 80
    assert len(cases) == 80

    ids = [str(case["id"]) for case in cases]
    assert len(ids) == len(set(ids))

    required_metadata = set(manifest["required_case_metadata"])
    actual_key_map = {
        "case_id": "id",
        "taxonomy": "taxonomy",
        "source_language": "source_language",
        "expected_obligations": "expected_obligations",
        "expected_exclusions": "expected_exclusions",
        "expected_deliverables": "expected_deliverables",
        "expected_ambiguities": "expected_ambiguities",
        "expected_representability": "expected_representability",
        "allowed_work_modes": "allowed_work_modes",
        "expected_authority_family": "expected_authority_family",
        "expected_terminal_state": "expected_terminal_state",
        "requires_adaptive_branch": "requires_adaptive_branch",
        "adversarial_flags": "adversarial_flags",
    }
    assert required_metadata == set(actual_key_map)

    for case in cases:
        for _, actual_key in actual_key_map.items():
            assert actual_key in case, f"{case['id']} missing {actual_key}"
        assert case["source_language"] == "tr"
        assert str(case["prompt"]).strip()
        assert case["expected_terminal_state"] in {"ACCEPTED", "CLARIFICATION"}
        assert case["expected_representability"] in {
            "STANDARD_LOSSLESS",
            "RESEARCH_REQUIRED",
            "CLARIFICATION_REQUIRED",
            "UNSUPPORTED",
        }

        allowed_work_modes = set(case["allowed_work_modes"])
        authority_family = case["expected_authority_family"]
        if case["expected_representability"] == "STANDARD_LOSSLESS":
            assert allowed_work_modes == {
                "STANDARD_DIRECT",
                "STANDARD_BUILDER",
            }
            assert authority_family == "AcceptedStandardAuthority"
        elif case["expected_representability"] == "RESEARCH_REQUIRED":
            assert allowed_work_modes == {"RESEARCH"}
            assert authority_family == "AcceptedResearchAuthority"
        else:
            assert allowed_work_modes == set()
            assert authority_family == "NONE"

    required_taxonomy = set(manifest["taxonomy"])
    actual_taxonomy = {
        str(tag)
        for case in cases
        for tag in case.get("taxonomy", [])
    }
    assert required_taxonomy <= actual_taxonomy


def test_hidden_prompt_text_is_not_embedded_in_dev_corpus():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    blob = CASES.read_text(encoding="utf-8")
    assert "EXTERNAL_SEALED" not in blob
    assert all(
        "hidden" not in {str(tag).casefold() for tag in case.get("taxonomy", [])}
        for case in doc["cases"]
    )
