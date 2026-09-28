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
        "SCOPE_CURRENTNESS_HARD_V3",
        "RCA_P19_HARD_V2",
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
    assert "SCOPE_CURRENTNESS_HARD_V3" in workflow
    assert "RCA_P19_HARD_V2" in workflow
    assert "probe_id" in workflow
    assert "max-orchestration-boundary-units \"12\"" in workflow
    assert "F02_M" not in workflow
    assert "F07_M" not in workflow
    assert "validate_phase1_round2.py" not in workflow
    assert "--manifest eval/dima_neutral_feature_benchmark_round2.json" not in workflow
    assert "backend/eval/v1/authorizations/phase1-final-pinpoint-live-v3.json" in workflow
    assert "\n  push:\n" in workflow
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
