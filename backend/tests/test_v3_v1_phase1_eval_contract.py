from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab.metabase.core_b.round2_feature_benchmark import _select_cases


ROUND2 = Path("eval/dima_neutral_feature_benchmark_round2.json")
FIXTURE = Path("eval/round2_neutral_machine_fixture.json")
METAMORPHIC = Path("eval/v1/phase1_metamorphic_manifest.json")
BROAD_PAID_WORKFLOW = Path("../.github/workflows/dima-v1-phase1-p12-live.yml")
PINPOINT_PAID_WORKFLOW = Path("../.github/workflows/dima-v1-phase1-p12-pinpoint-live.yml")


def test_round2_frozen_manifest_is_exact_shape_and_eval_only_data():
    manifest = json.loads(ROUND2.read_text(encoding="utf-8"))
    assert manifest["version"] == "dima-neutral-feature-benchmark-round2-v2"
    assert manifest["case_count"] == 30
    assert manifest["common_feature_count"] == 10
    assert manifest["same_prompt_required"] is True
    assert manifest["same_fixture_required"] is True
    cases = manifest["cases"]
    assert len(cases) == 30
    assert len({item["id"] for item in cases}) == 30
    assert {
        (item["feature_id"], item["difficulty"])
        for item in cases
    } == {
        (f"F{feature:02d}", difficulty)
        for feature in range(1, 11)
        for difficulty in ("simple", "medium", "hard")
    }
    serialized = json.dumps(manifest, ensure_ascii=False).lower()
    for forbidden_key in (
        '"sql"',
        '"mbql"',
        '"dataset_query"',
        '"join_plan"',
        '"query_plan"',
    ):
        assert forbidden_key not in serialized


def test_round2_pinpoint_selector_is_exact_closed_allowlist():
    manifest = json.loads(ROUND2.read_text(encoding="utf-8"))
    selected = _select_cases(manifest, ("F02_M", "F07_M"))
    assert [item["id"] for item in selected] == ["F02_M", "F07_M"]
    assert [item["max_model_calls"] for item in selected] == [8, 12]


def test_round2_pinpoint_selector_defaults_to_frozen_full_corpus():
    manifest = json.loads(ROUND2.read_text(encoding="utf-8"))
    selected = _select_cases(manifest)
    assert len(selected) == 30


@pytest.mark.parametrize(
    "case_ids",
    [
        ("F02_M", "F02_M"),
        ("F02_M", "NOT_A_CASE"),
    ],
)
def test_round2_pinpoint_selector_fails_closed(case_ids):
    manifest = json.loads(ROUND2.read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError):
        _select_cases(manifest, case_ids)


def test_round2_neutral_fixture_is_frozen_substrate_neutral_40_rows():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["schema_version"] == "round2_neutral_machine_fixture_v1"
    assert len(fixture["rows"]) == 40
    serialized = json.dumps(fixture, ensure_ascii=False).lower()
    assert "wren_mdl" not in serialized
    assert "expected_sql" not in serialized
    assert "mbql" not in serialized
    assert {row[1] for row in fixture["rows"]} == {
        "Assembly",
        "Packaging",
        "Utilities",
        "Maintenance",
        "Quality",
    }


def test_paid_governance_forbids_broad_execution_and_push_paid_triggers():
    source = BROAD_PAID_WORKFLOW.read_text(encoding="utf-8")
    assert "\n  push:" not in source
    assert "DIMA_OPENROUTER_API_KEY" not in source
    assert "round2_feature_benchmark.py" not in source
    assert "broad 30-case paid benchmark is forbidden" in source


def test_pinpoint_paid_workflow_is_sequential_closed_budget():
    source = PINPOINT_PAID_WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in source
    assert "phase1-r-live-1-luna-trigger-20260930" in source
    assert "phase1-r-live-2-trigger-20260930" in source
    assert "phase1-r-live-3-trigger-20260930" in source
    assert "phase1-v4-trigger-20260929" in source
    assert "phase1-rca-trigger-20260929" in source
    assert "phase1-f05-trigger-20260929" in source
    assert "phase1-f08-trigger-20260929" in source
    assert "phase1-f06-trigger-20260929" in source
    assert "phase1-f10-trigger-20260930" in source
    assert "phase1-f07-trigger-20260930" in source
    assert "phase1-f04-trigger-20260930" in source
    assert "git fetch --no-tags --depth=1 origin feat/dima-metabase-platform" in source
    assert 'PRODUCT_BEHAVIOR_SHA: "c2a0cfda12ab6b1329ef56171b6a5d8e58eda005"' in source
    assert 'test "$ENGINE_SHA" = "0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c"' in source
    assert 'test "$CERTIFICATION_RUN_ID" = "36610103287"' in source
    assert 'test "$RUNTIME_TAG" = "v0.63.18-dima.8"' in source
    assert "backend/eval/v1/authorizations/phase1-final-pinpoint-live-v3.json" not in source
    assert "repository_dispatch" not in source
    assert "R_LIVE_1_ONE_PASS" in source
    assert "R_LIVE_2_ADAPTIVE" in source
    assert "R_LIVE_3_DISCOVERY" in source
    assert "SCOPE_CURRENTNESS_HARD_V4" in source
    assert "RCA_P19_HARD_V2" in source
    assert "RELATIONSHIP_F05_H_RECOVERY" in source
    assert "REPORT_F08_H_RECOVERY" in source
    assert "ADAPTIVE_F06_H_RETENTION" in source
    assert "CONVERSATION_F10_H_RECOVERY" in source
    assert "RCA_F07_H_RECOVERY" in source
    assert "MULTI_INTENT_F04_H_RECOVERY" in source
    assert 'HARD_PROVIDER_REQUEST_CEILING: "24"' in source
    assert 'PROMPT_TOKEN_CEILING: "350000"' in source
    assert 'COMPLETION_TOKEN_CEILING: "16000"' in source
    assert 'REASONING_TOKEN_CEILING: "12000"' in source
    assert 'PROVIDER_COST_CEILING: "1.00"' in source
    assert "--source-ceiling research_intake=2" in source
    assert "--source-ceiling metabase=16" in source
    assert "--source-ceiling p17_manager=4" in source
    assert "--source-ceiling p19_manager=2" in source
    assert "--ceiling 0" in source
    assert "actual_provider_request_count" in source
    assert "MB_LLM_OPENROUTER_API_BASE_URL" in source
    assert '--max-orchestration-boundary-units "12"' in source
    assert 'echo "max_orchestration_units=12"' in source
    assert "F02_M" not in source
    assert "F07_M" not in source
    assert "round2_feature_benchmark.py" not in source
    assert "validate_phase1_round2.py" not in source
    assert "PINPOINT_ARTIFACT_READY_FOR_HUMAN_INSPECTION" in source
    assert "mechanical_verdict" in source
    assert "manual_quality_status" in source
    assert "manual_quality_score" in source
    assert "quality_score" in source
    assert "manual_adjudication_required" in source
    assert "MANUAL_ARTIFACT_ADJUDICATION_ONLY" in source
    assert '--checkout-sha "${GITHUB_SHA}"' in source


def test_phase1_metamorphic_manifest_is_structural_not_prose_scoring():
    manifest = json.loads(METAMORPHIC.read_text(encoding="utf-8"))
    assert manifest["authority"] == "EVAL_ONLY"
    assert len(manifest["cases"]) == 12
    text = json.dumps(manifest, ensure_ascii=False).lower()
    for forbidden in (
        "winner",
        "score threshold",
        "exact answer prose",
        "prompt-specific patch",
        "sql planner",
        "mbql planner",
    ):
        assert forbidden not in text
