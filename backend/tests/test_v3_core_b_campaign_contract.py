from __future__ import annotations

import json
from pathlib import Path

MATCHED=Path("eval/core_b/askv2_matched_20_cases.json")
CANARY=Path("eval/core_b/canary_manifest.json")
HARDEST=Path("eval/core_b/hardest_24_cases.json")

EXPECTED_MATCHED=(
    "std_breakdown_tr","std_ranking_tr","std_failure_breakdown_tr","std_clause_order",
    "std_english_surface","relationship_explicit_tr","root_cause_tr","adaptive_tr",
    "canonical_full","canonical_reordered","canonical_no_diacritics","broaden_policy",
    "report_control","unsupported_domain","ambiguous_request","cross_domain_relationship",
    "repair_surface","english_root","restart_signed_continuation","foreign_principal_replay",
)

EXPECTED_HARDEST=(
    "01_turkish_complex_multi_intent","02_reordered_obligations",
    "03_turkish_no_diacritics","04_english_complex_intent",
    "05_valid_governed_relationship","06_missing_invalid_relationship",
    "07_bounded_root_cause","08_no_defensible_root_cause",
    "09_multiple_material_contributors","10_contradictory_evidence",
    "11_adaptive_material_branch","12_adaptive_no_new_evidence_stop",
    "13_unsupported_predictive_psychological","14_genuinely_ambiguous_clarification",
    "15_explicit_conversation_repair","16_scoped_continuation_immutable_revision",
    "17_process_restart_durable_resume","18_foreign_principal_replay",
    "19_cross_tenant_artifact_replay","20_permission_downgrade",
    "21_stale_report_decision_currentness","22_old_memory_contradicted",
    "23_observed_outcome_no_causality","24_complete_closed_loop",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_matched_manifest_is_exact_source_mapping_and_frozen():
    body=load(MATCHED)
    assert body["version"]=="core-b-askv2-matched-20-v1"
    assert body["source_branch"]=="feat/ask-v2-mvp"
    assert body["source_sha"]=="94f5522a063a4f334924a62ed786b3a4e5221c3d"
    assert body["source_manifest_git_blob_sha"]=="3906c845d82e40dd6c0bf8cfbf3e1e40e20099b6"
    assert body["source_run"]==36238482520
    assert body["case_count"]==20
    assert tuple(item["source_case_id"] for item in body["cases"])==EXPECTED_MATCHED
    assert body["freeze_rule"]=="DO_NOT_MODIFY_AFTER_FIRST_LIVE_RUN"
    assert body["large_certification_corpus"] is False
    for item in body["cases"]:
        assert item["source_question"]
        assert item["platform_question"]
        assert item["adaptation_reason"]
        assert isinstance(item["acceptance_contract"]["obligations"],list)
        assert "Wren SQL" not in json.dumps(item)


def test_matched_manifest_preserves_repair_and_security_contracts():
    by_id={x["source_case_id"]:x for x in load(MATCHED)["cases"]}
    repair=by_id["repair_surface"]["acceptance_contract"]
    assert repair["forbidden_current_obligation"]=="fault_count"
    foreign=by_id["foreign_principal_replay"]["acceptance_contract"]
    assert foreign["foreign_replay_must_fail_closed"] is True
    assert foreign["post_attack_model_calls"]==0
    assert foreign["post_attack_metabase_calls"]==0


def test_matched_continuation_uses_platform_artifact_equivalence_not_tokens():
    by_id={x["source_case_id"]:x for x in load(MATCHED)["cases"]}
    for case_id in ("broaden_policy","report_control","restart_signed_continuation"):
        item=by_id[case_id]
        contract=item["acceptance_contract"]
        assert contract["immutable_previous_version"] is True
        assert contract["new_revision_required"] is True
        assert contract["raw_prompt_reparse_forbidden"] is True
        assert "token" not in json.dumps(contract).lower()


def test_canary_is_small_provider_free_and_covers_required_families():
    body=load(CANARY)
    assert 12 <= body["case_count"] <= 14
    assert body["live_model_calls"]==0
    assert body["external_side_effects"]==0
    ids={item["id"] for item in body["cases"]}
    assert ids=={
        "source_evidence_identity_integrity","immutable_revision",
        "foreign_evidence_rejection","currentness_visibility","stale_report",
        "stale_decision","durable_resume","restart_idempotency",
        "current_principal_reauthorization","cross_tenant_non_oracle",
        "outcome_not_causality","memory_not_truth_authority",
        "external_execution_dark_and_sealed_nonmutation",
    }


def test_hardest_manifest_is_frozen_24_and_explicitly_not_large_certification():
    body=load(HARDEST)
    assert body["status"]=="DEVELOPMENT_HARDEST_REHEARSAL"
    assert body["large_certification_corpus"] is False
    assert body["DEV80"]=="forbidden"
    assert body["Validation50"]=="forbidden"
    assert body["Hidden50"]=="forbidden"
    assert body["max_total_model_calls"]==200
    assert body["case_count"]==24
    assert tuple(item["id"] for item in body["cases"])==EXPECTED_HARDEST
    assert all(item["acceptance_contract"]["actual_cognition_step_required"] for item in body["cases"])


def test_product_code_contains_no_campaign_case_ids():
    product="\n".join(
        p.read_text(encoding="utf-8")
        for p in Path("app/v3/product").glob("*.py")
    )
    for case_id in EXPECTED_MATCHED + EXPECTED_HARDEST:
        assert case_id not in product


def test_campaign_does_not_authorize_large_corpora_or_ui():
    raw=(MATCHED.read_text(encoding="utf-8")+HARDEST.read_text(encoding="utf-8")).lower()
    assert '"dev80": "forbidden"' in raw
    assert '"validation50": "forbidden"' in raw
    assert '"hidden50": "forbidden"' in raw
    assert "ui implementation" in raw
