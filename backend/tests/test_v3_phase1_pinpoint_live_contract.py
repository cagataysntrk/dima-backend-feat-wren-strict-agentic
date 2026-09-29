from __future__ import annotations

import json
from pathlib import Path

from lab.metabase.core_b.phase1_pinpoint_live import (
    MAX_ORCHESTRATION_BOUNDARY_UNITS,
    PROBES,
    OrchestrationBudget,
    PinpointBudgetExceeded,
    build_catalog,
)
from lab.metabase.core_b.runtime.seed_phase1_pinpoint_metrics import (
    metric_card_payload,
    metric_specs,
)


def _bindings():
    return {
        "schema_version": "phase1_pinpoint_native_bindings_v1",
        "table_name": "machine_operations",
        "metrics": [
            {
                "candidate_id": candidate_id,
                "column_name": column,
                "native_metric_entity_id": f"native-{index}",
            }
            for index, (candidate_id, _name, column, _agg)
            in enumerate(metric_specs(), start=1)
        ],
    }


def test_final_pinpoint_probes_are_closed_and_not_benchmark_cases():
    assert tuple(PROBES) == (
        "SCOPE_CURRENTNESS_HARD_V4",
        "RCA_P19_HARD_V2",
        "RELATIONSHIP_F05_H_RECOVERY",
        "REPORT_F08_H_RECOVERY",
        "ADAPTIVE_F06_H_RETENTION",
    )
    assert MAX_ORCHESTRATION_BOUNDARY_UNITS == 12
    from lab.metabase.core_b.phase1_pinpoint_live import MODEL
    assert MODEL == "openai/gpt-5.6-terra"
    serialized = json.dumps(PROBES, ensure_ascii=False)
    assert "F02_M" not in serialized
    assert "F07_M" not in serialized
    assert "Mayıs ve Haziran 2026" in serialized
    assert "maintenance delay" in serialized
    assert "spare-part delay" in serialized
    assert "supporting ve challenging evidence" in serialized
    assert "gözlem, bulgu, hipotez, karşı kanıt" in serialized
    assert "en az iki farklı analitik derinleşme" in serialized


def test_recovery_growth_probes_bind_exact_frozen_round2_historical_requests():
    manifest = json.loads(
        (Path(__file__).parents[1] / "eval" / "dima_neutral_feature_benchmark_round2.json")
        .read_text(encoding="utf-8")
    )
    cases = {item["id"]: item for item in manifest["cases"]}
    bindings = {
        "RELATIONSHIP_F05_H_RECOVERY": "F05_H",
        "REPORT_F08_H_RECOVERY": "F08_H",
        "ADAPTIVE_F06_H_RETENTION": "F06_H",
    }
    for probe_id, case_id in bindings.items():
        probe = PROBES[probe_id]
        assert probe["historical_round2_case_id"] == case_id
        assert probe["turns"] == (cases[case_id]["question"],)
        assert probe["manual_contract"]
    assert all(
        probe["historical_round2_case_id"] is None
        for probe_id, probe in PROBES.items()
        if probe_id in {"SCOPE_CURRENTNESS_HARD_V4", "RCA_P19_HARD_V2"}
    )


def test_pinpoint_budget_blocks_thirteenth_boundary_before_network():
    budget = OrchestrationBudget(12)
    for _ in range(12):
        budget.consume("test")
    assert budget.used == 12
    try:
        budget.consume("test")
    except PinpointBudgetExceeded as exc:
        assert exc.code == "PINPOINT_ORCHESTRATION_BOUNDARY_BUDGET_EXHAUSTED"
    else:
        raise AssertionError("thirteenth boundary was not blocked")
    assert budget.used == 12


def test_live_catalog_binds_all_metrics_to_governed_native_resources():
    catalog = build_catalog(_bindings())
    assert catalog.temporal_dimension_ids == ("dimension.event_date",)
    metric_refs = {
        item.candidate_id
        for item in catalog.semantic_refs
        if item.target_kind.value == "metric"
    }
    native = {
        item.candidate_id: item.native_metric_entity_id
        for item in catalog.native_verification_bindings
        if item.candidate_id in metric_refs
    }
    assert set(native) == metric_refs
    assert all(native.values())


def test_metric_fixture_setup_is_closed_and_creates_metric_cards():
    specs = metric_specs()
    assert len(specs) == 8
    assert {item[0] for item in specs} >= {
        "metric.machine_downtime_minutes",
        "metric.fault_count",
        "metric.maintenance_delay_hours",
        "metric.spare_part_delay_hours",
    }
    payload = metric_card_payload(
        database_id=7,
        table_id=11,
        field_id=13,
        name="Machine Downtime Minutes",
        aggregation="sum",
    )
    assert payload["type"] == "metric"
    assert payload["dataset_query"]["query"]["source-table"] == 11
    assert payload["dataset_query"]["query"]["aggregation"] == [
        ["sum", ["field", 13, None]]
    ]


def test_pinpoint_workflow_is_one_probe_per_run_and_no_broad_scorer():
    workflow = (
        Path(__file__).parents[2]
        / ".github"
        / "workflows"
        / "dima-v1-phase1-p12-pinpoint-live.yml"
    ).read_text(encoding="utf-8")
    assert "SCOPE_CURRENTNESS_HARD_V4" in workflow
    assert "RCA_P19_HARD_V2" in workflow
    assert "RELATIONSHIP_F05_H_RECOVERY" in workflow
    assert "REPORT_F08_H_RECOVERY" in workflow
    assert "ADAPTIVE_F06_H_RETENTION" in workflow
    assert "probe_id" in workflow
    assert "max-orchestration-boundary-units \"12\"" in workflow
    assert "F02_M" not in workflow
    assert "F07_M" not in workflow
    assert "validate_phase1_round2.py" not in workflow
    assert "--manifest eval/dima_neutral_feature_benchmark_round2.json" not in workflow
    assert "backend/eval/v1/authorizations/phase1-final-pinpoint-live-v3.json" not in workflow
    assert "phase1-v4-trigger-20260929" in workflow
    assert "phase1-rca-trigger-20260929" in workflow
    assert "phase1-f05-trigger-20260929" in workflow
    assert "phase1-f08-trigger-20260929" in workflow
    assert "phase1-f06-trigger-20260929" in workflow
    assert "feat/dima-metabase-platform" in workflow
    assert 'PRODUCT_BEHAVIOR_SHA: "259c749570e1b6ec9f39e690424e930614702cc3"' in workflow
    assert 'test "$ENGINE_SHA" = "14323cdde4f258c65c63bbd88f1034f814a7ecb3"' in workflow
    assert 'test "$CERTIFICATION_RUN_ID" = "36532842632"' in workflow
    assert 'test "$RUNTIME_TAG" = "v0.63.18-dima.7"' in workflow
    assert "openrouter_counting_proxy.py" in workflow
    assert "--ceiling 0" in workflow
    assert 'HARD_PROVIDER_REQUEST_CEILING: "24"' in workflow
    assert 'PROMPT_TOKEN_CEILING: "350000"' in workflow
    assert 'COMPLETION_TOKEN_CEILING: "16000"' in workflow
    assert 'REASONING_TOKEN_CEILING: "12000"' in workflow
    assert 'PROVIDER_COST_CEILING: "1.00"' in workflow
    for source_limit in (
        "research_intake=2",
        "metabase=16",
        "p17_manager=4",
        "p19_manager=2",
    ):
        assert source_limit in workflow
    assert '--ceiling "$HARD_PROVIDER_REQUEST_CEILING"' in workflow
    assert "MB_LLM_OPENROUTER_API_BASE_URL" in workflow
    assert "actual_provider_request_count" in workflow
    assert "orchestration_boundary_units" in workflow
    assert "PINPOINT_ARTIFACT_READY_FOR_HUMAN_INSPECTION" in workflow
    assert "MANUAL_ARTIFACT_ADJUDICATION_ONLY" in workflow
    assert '--checkout-sha "${GITHUB_SHA}"' in workflow
    assert "round2_feature_benchmark.py" not in workflow
