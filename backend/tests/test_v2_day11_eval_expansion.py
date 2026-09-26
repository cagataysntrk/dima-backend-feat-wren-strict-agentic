"""Day11 provider-free evaluation-expansion contract.

This suite certifies coverage wiring only. It MUST NOT execute DEV80, Validation50,
Hidden50, live providers, or Product traffic.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml


BACKEND = Path(__file__).resolve().parents[1]
MANIFEST_PATH = BACKEND / "eval" / "v2_day11_eval_expansion_manifest.json"

EXPECTED_FAMILIES = {
    "typo_no_diacritics",
    "incomplete_ellipsis_coreference",
    "topic_switch_and_return",
    "negative_research_unsupported",
    "ambiguity_clarification",
    "repair_versioning",
    "exclusion_control_boundary",
    "trust_plane_bypass",
    "complex_research_root_cause",
    "adaptive_branch_lifecycle",
    "source_truth_revision",
    "actionset_materializability_hydration",
    "signed_continuation_report_immutability",
    "standard_cube_coherence",
    "cross_domain_governance",
    "temporal_and_conversation_repair",
    "tenant_and_principal_isolation",
    "budget_and_no_progress",
}

EXPECTED_METAMORPHIC = {
    "source_owner_order_does_not_change_truth",
    "candidate_order_does_not_change_source_truth",
    "same_source_different_kind_remains_separate",
    "scope_group_generation_is_permutation_stable",
    "scope_group_classifier_is_permutation_invariant",
    "actionset_candidate_order_is_identity_invariant",
    "report_versioning_is_immutable",
}


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _split_ref(ref: str) -> tuple[Path, str]:
    path_text, marker = ref.split("#", 1)
    path = BACKEND / path_text
    assert path.exists(), f"Day11 evidence path does not exist: {path_text}"
    return path, marker


def _assert_marker_exists(ref: str) -> None:
    path, marker = _split_ref(ref)
    text = path.read_text(encoding="utf-8")
    if marker.startswith("taxonomy:"):
        marker = marker.split(":", 1)[1]
    if marker.startswith("test_"):
        assert f"def {marker}(" in text, f"missing test node: {ref}"
    else:
        assert marker in text, f"missing Day11 evidence marker: {ref}"


def test_day11_known_real_world_family_set_is_complete_and_nonempty():
    manifest = _manifest()
    families = manifest["required_real_world_families"]
    ids = [item["id"] for item in families]

    assert len(ids) == len(set(ids))
    assert set(ids) == EXPECTED_FAMILIES
    assert all(item["evidence"] for item in families)
    for item in families:
        for ref in item["evidence"]:
            _assert_marker_exists(ref)


def test_day11_metamorphic_invariants_are_real_test_nodes():
    manifest = _manifest()
    invariants = manifest["metamorphic_invariants"]
    ids = [item["id"] for item in invariants]

    assert len(ids) == len(set(ids))
    assert set(ids) == EXPECTED_METAMORPHIC
    for item in invariants:
        _assert_marker_exists(item["test"])


def test_day11_source_sets_are_inputs_not_product_authority():
    manifest = _manifest()
    sources = manifest["scenario_sources"]
    ids = {item["id"] for item in sources}

    assert {
        "visible_dev80_seed",
        "research_complex",
        "conversation_threads",
        "real_world_legacy",
        "experience_legacy",
    } <= ids
    for item in sources:
        assert (BACKEND / item["path"]).exists()
        assert item["execution_authority"] is False

    legacy = {
        item["id"]: item["role"]
        for item in sources
        if item["id"] in {"real_world_legacy", "experience_legacy"}
    }
    assert legacy == {
        "real_world_legacy": "HISTORICAL_REAL_WORLD_SCENARIO_SOURCE_ONLY",
        "experience_legacy": "HISTORICAL_EXPERIENCE_SCENARIO_SOURCE_ONLY",
    }


def test_day11_does_not_consume_freeze_or_certification_corpora():
    manifest = _manifest()
    policy = manifest["execution_policy"]

    assert policy == {
        "provider_free_only": True,
        "dev80_execution_authorized": False,
        "validation50_execution_authorized": False,
        "hidden50_execution_authorized": False,
        "paid_live_execution_authorized": False,
        "product_code_changes_expected": False,
        "hidden_prompt_text_in_repo_forbidden": True,
    }

    partitions = manifest["corpus_partitions"]
    assert partitions["dev"]["visibility"] == "VISIBLE_TO_DEVELOPMENT"
    assert partitions["dev"]["tuning_allowed"] is True
    assert partitions["dev"]["execution_status"] == "NOT_RUN_BY_DAY11_EXPANSION"

    assert partitions["validation"]["visibility"] == "VISIBLE_AFTER_DEV_FREEZE"
    assert partitions["validation"]["tuning_allowed"] is False
    assert partitions["validation"]["prompt_bodies_committed_by_day11_expansion"] is False
    assert partitions["validation"]["execution_status"] == "NOT_AUTHORIZED"

    hidden = partitions["hidden_holdout"]
    assert hidden["visibility"] == "EXTERNAL_SEALED"
    assert hidden["tuning_allowed"] is False
    assert hidden["prompt_bodies_committed"] is False
    assert hidden["generated_by_current_development_model"] is False
    assert hidden["execution_status"] == "NOT_AUTHORIZED"
    assert (BACKEND / hidden["authority_contract"]).exists()
    assert (BACKEND / hidden["attestation_test"]).exists()

    # Cross-check against the pre-existing freeze contract rather than redefining it.
    d65_manifest = yaml.safe_load(
        (BACKEND / "eval" / "v2_day6_5_eval_manifest.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert d65_manifest["corpus_target"]["dev"]["count"] == 80
    assert d65_manifest["corpus_target"]["validation"]["count"] == 50
    assert d65_manifest["corpus_target"]["hidden_holdout"]["count"] == 50
    assert d65_manifest["freeze_candidate_policy"]["dev80_runs_per_candidate_max"] == 1
    assert (
        d65_manifest["corpus_target"]["hidden_holdout"]["committed_to_repo"]
        is False
    )
    assert (
        d65_manifest["corpus_target"]["hidden_holdout"]["tuning_allowed"]
        is False
    )


def test_day11_visible_dev_seed_remains_exactly_the_declared_80_cases():
    manifest = _manifest()
    dev = manifest["corpus_partitions"]["dev"]
    payload = json.loads((BACKEND / dev["source"]).read_text(encoding="utf-8"))

    assert payload["visibility"] == "VISIBLE_TO_DEVELOPMENT"
    assert payload["target_total"] == 80
    assert payload["current_seed_count"] == 80
    assert len(payload["cases"]) == 80


def test_day11_holdout_partition_contains_no_case_or_prompt_payloads():
    hidden = _manifest()["corpus_partitions"]["hidden_holdout"]

    forbidden_payload_keys = {
        "cases",
        "case",
        "prompts",
        "prompt",
        "questions",
        "question",
        "threads",
        "turns",
    }
    assert forbidden_payload_keys.isdisjoint(hidden)
    assert set(hidden) == {
        "visibility",
        "tuning_allowed",
        "prompt_bodies_committed",
        "generated_by_current_development_model",
        "authority_contract",
        "attestation_test",
        "execution_status",
    }


def test_day11_gates_are_fail_closed_and_do_not_claim_dev80():
    gates = _manifest()["day11_gates"]

    assert gates["all_known_real_world_regression_families_represented"] == 1.0
    assert gates["holdout_separated"] is True
    assert gates["metamorphic_invariants_green"] is True
    assert gates["hidden_prompt_text_committed_max"] == 0
    assert gates["dev80_runs_consumed_by_day11_expansion"] == 0
    assert gates["product_eval_literals_added_max"] == 0
