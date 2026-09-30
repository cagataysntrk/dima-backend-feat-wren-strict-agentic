from __future__ import annotations

import json
from pathlib import Path

from lab.metabase.core_b.phase1_pinpoint_live import (
    MAX_ORCHESTRATION_BOUNDARY_UNITS,
    PROBES,
    OrchestrationBudget,
    PinpointBudgetExceeded,
    _mechanical_r_live,
    _mechanical_verdict,
    _model_ceiling_events,
    _native_resource_binding_rows,
    build_catalog,
)
from lab.metabase.core_b.runtime.seed_phase1_pinpoint_metrics import (
    entity_value_bindings_from_fixture,
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
        "entity_values": [
            {
                "candidate_id": "entity_value.0123456789abcdef01234567",
                "canonical_name": "Packaging",
                "source_mention": "Packaging",
                "dimension_candidate_id": "dimension.department",
                "dimension_name": "department",
                "value": "Packaging",
                "column_name": "department",
                "field_id": 17,
            }
        ],
    }


def test_final_pinpoint_probes_are_closed_and_not_benchmark_cases():
    assert tuple(PROBES) == (
        "R_LIVE_1_ONE_PASS",
        "R_LIVE_2_ADAPTIVE",
        "R_LIVE_3_DISCOVERY",
        "SCOPE_CURRENTNESS_HARD_V4",
        "RCA_P19_HARD_V2",
        "RELATIONSHIP_F05_H_RECOVERY",
        "REPORT_F08_H_RECOVERY",
        "ADAPTIVE_F06_H_RETENTION",
        "CONVERSATION_F10_H_RECOVERY",
        "RCA_F07_H_RECOVERY",
        "MULTI_INTENT_F04_H_RECOVERY",
    )
    assert MAX_ORCHESTRATION_BOUNDARY_UNITS == 12
    from lab.metabase.core_b.phase1_pinpoint_live import METABOT_MODEL, MODEL
    assert MODEL == "openai/gpt-5.6-luna"
    assert METABOT_MODEL == "openrouter/openai/gpt-5.6-luna"
    assert "terra" not in MODEL.casefold()
    assert "terra" not in METABOT_MODEL.casefold()
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
        "CONVERSATION_F10_H_RECOVERY": "F10_H",
        "RCA_F07_H_RECOVERY": "F07_H",
        "MULTI_INTENT_F04_H_RECOVERY": "F04_H",
    }
    for probe_id, case_id in bindings.items():
        probe = PROBES[probe_id]
        assert probe["historical_round2_case_id"] == case_id
        expected_turns = tuple(
            cases[case_id].get("turns") or (cases[case_id]["question"],)
        )
        assert probe["turns"] == expected_turns
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
    entity_refs = {
        item.candidate_id: item
        for item in catalog.semantic_refs
        if item.target_kind.value == "entity_value"
    }
    assert set(entity_refs) == {"entity_value.0123456789abcdef01234567"}
    assert entity_refs["entity_value.0123456789abcdef01234567"].value == "Packaging"
    entity_binding = next(
        item
        for item in catalog.native_verification_bindings
        if item.candidate_id == "entity_value.0123456789abcdef01234567"
    )
    assert entity_binding.column_name == "department"


def test_entity_value_authority_has_exact_durable_native_binding():
    manifest = {
        "schema_version": "phase1_pinpoint_native_bindings_v1",
        "database_id": 9,
        "table_id": 11,
        "metrics": [],
        "dimensions": [],
        "entity_values": [
            {
                "candidate_id": "entity_value.0123456789abcdef01234567",
                "canonical_name": "Cell Blue",
                "dimension_name": "department",
                "value": "Cell Blue",
                "column_name": "department",
                "field_id": 17,
            }
        ],
    }
    rows = _native_resource_binding_rows(manifest)
    assert len(rows) == 1
    row = rows[0]
    assert row.candidate_id == "entity_value.0123456789abcdef01234567"
    assert row.candidate_kind == "entity_value"
    assert row.locator_kind == "field"
    assert row.metabase_database_id == 9
    assert row.metabase_table_id == 11
    assert row.metabase_field_id == 17
    assert row.resource_entity_id == "metabase:field:17"
    assert len(row.resource_fingerprint) == 64


def test_fixture_entity_authority_is_derived_from_exact_fixture_values(tmp_path):
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "columns": [
                    ["department", "text"],
                    ["machine_id", "text"],
                ],
                "rows": [
                    ["Cell Blue", "M-2"],
                    ["Cell Red", "M-1"],
                    ["Cell Blue", "M-3"],
                ],
            }
        ),
        encoding="utf-8",
    )
    first = entity_value_bindings_from_fixture(
        fixture=fixture,
        fields={"department": 17, "machine_id": 19},
    )
    second = entity_value_bindings_from_fixture(
        fixture=fixture,
        fields={"department": 17, "machine_id": 19},
    )
    assert first == second
    assert {
        (item["dimension_candidate_id"], item["value"])
        for item in first
    } == {
        ("dimension.department", "Cell Blue"),
        ("dimension.department", "Cell Red"),
        ("dimension.machine_id", "M-1"),
        ("dimension.machine_id", "M-2"),
        ("dimension.machine_id", "M-3"),
    }
    assert len({item["candidate_id"] for item in first}) == len(first)


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
    assert "R_LIVE_1_ONE_PASS" in workflow
    assert "R_LIVE_2_ADAPTIVE" in workflow
    assert "R_LIVE_3_DISCOVERY" in workflow
    assert "SCOPE_CURRENTNESS_HARD_V4" in workflow
    assert "RCA_P19_HARD_V2" in workflow
    assert "RELATIONSHIP_F05_H_RECOVERY" in workflow
    assert "REPORT_F08_H_RECOVERY" in workflow
    assert "ADAPTIVE_F06_H_RETENTION" in workflow
    assert "CONVERSATION_F10_H_RECOVERY" in workflow
    assert "RCA_F07_H_RECOVERY" in workflow
    assert "MULTI_INTENT_F04_H_RECOVERY" in workflow
    assert "probe_id" in workflow
    assert "max-orchestration-boundary-units \"12\"" in workflow
    assert "F02_M" not in workflow
    assert "F07_M" not in workflow
    assert "validate_phase1_round2.py" not in workflow
    assert "--manifest eval/dima_neutral_feature_benchmark_round2.json" not in workflow
    assert "backend/eval/v1/authorizations/phase1-final-pinpoint-live-v3.json" not in workflow
    assert "phase1-r-live-1-product-repair-luna-trigger-20260930" in workflow
    assert "phase1-r-live-2-trigger-20260930" in workflow
    assert "phase1-r-live-3-trigger-20260930" in workflow
    assert "phase1-v4-trigger-20260929" in workflow
    assert "phase1-rca-trigger-20260929" in workflow
    assert "phase1-f05-trigger-20260929" in workflow
    assert "phase1-f08-trigger-20260929" in workflow
    assert "phase1-f06-trigger-20260929" in workflow
    assert "phase1-f10-trigger-20260930" in workflow
    assert "phase1-f07-trigger-20260930" in workflow
    assert "phase1-f04-trigger-20260930" in workflow
    assert "feat/dima-metabase-platform" in workflow
    assert 'PRODUCT_BEHAVIOR_SHA: "cb89bc94acf0d88b5b37a94b1160ad77daa1bb86"' in workflow
    assert 'assert report["candidate_product_sha"] == "cb89bc94acf0d88b5b37a94b1160ad77daa1bb86"' in workflow
    assert 'test "$ENGINE_SHA" = "0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c"' in workflow
    assert 'test "$CERTIFICATION_RUN_ID" = "36610103287"' in workflow
    assert 'test "$RUNTIME_TAG" = "v0.63.18-dima.8"' in workflow
    assert "--fixture eval/round2_neutral_machine_fixture.json" in workflow
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

def test_model_ceiling_events_are_separate_privacy_safe_telemetry():
    report = {
        "exception": {
            "error_code": "UNAVAILABLE",
            "cause_code": "COGNITION_OUTPUT_BUDGET_EXHAUSTED",
            "cause_detail": "do-not-persist-this-detail",
        },
        "provider_receipt": {
            "events": [
                {
                    "ordinal": 2,
                    "source": "p17_manager",
                    "forwarded": False,
                    "blocked_reason": "PROVIDER_COMPLETION_TOKEN_CEILING_REACHED",
                }
            ]
        },
        "transport_traces": {
            "research_intake": [
                {
                    "call_ordinal_by_role": 1,
                    "model": "openai/gpt-5.6-luna",
                    "finish_reason": "length",
                    "native_finish_reason": "max_output_tokens",
                    "max_completion_tokens": 4096,
                }
            ]
        },
    }
    events = _model_ceiling_events(report)
    codes = {item["code"] for item in events}
    assert "COGNITION_OUTPUT_BUDGET_EXHAUSTED" in codes
    assert "PROVIDER_COMPLETION_TOKEN_CEILING_REACHED" in codes
    assert "MODEL_OUTPUT_LENGTH_LIMIT" in codes
    serialized = json.dumps(events, sort_keys=True)
    assert "do-not-persist-this-detail" not in serialized
    assert "prompt" not in serialized.casefold()
    assert "reasoning_text" not in serialized.casefold()


def test_mechanical_verdict_is_automated_but_manual_quality_remains_separate():
    report = {
        "exception": None,
        "provider_receipt_error": None,
        "within_orchestration_boundary_budget": True,
        "turn_count_executed": 1,
        "turn_count_expected": 1,
        "turns": [{"ready": True}],
        "provider_receipt": {
            "blocked_request_count": 0,
        },
        "actual_provider_request_count": 4,
        "hard_provider_request_ceiling": 24,
        "mechanical_observations": {
            "p19_called_when_required": True,
        },
    }
    assert _mechanical_verdict(report) == "PASS"
    report["mechanical_observations"]["p19_called_when_required"] = False
    assert _mechanical_verdict(report) == "FAIL"


def test_pinpoint_workflow_persists_manual_quality_as_pending_not_auto_score():
    workflow = (
        Path(__file__).parents[2]
        / ".github"
        / "workflows"
        / "dima-v1-phase1-p12-pinpoint-live.yml"
    ).read_text(encoding="utf-8")
    assert 'report["mechanical_verdict"] == "PASS"' in workflow
    assert 'report["manual_quality_status"] == "PENDING"' in workflow
    assert 'report["manual_quality_score"] is None' in workflow



def _phase15_mode_turn(*, mode: str, native_results: int, p17_calls: int) -> dict:
    owner_calls = ["P14", "P14"] + ["P17"] * p17_calls + ["P19", "P20"]
    return {
        "ready": True,
        "brief_payload": {
            "questions": [
                {
                    "goal_id": "g_root",
                    "causal_competition": {
                        "effect_semantic_id": "metric.effect",
                        "candidate_mechanism_semantic_ids": [
                            "metric.h1",
                            "metric.h2",
                        ],
                        "diagnostic_dimension_ids": [],
                    },
                }
            ]
        },
        "native_results": [{"query": index} for index in range(native_results)],
        "evidence_by_session": {"rs_" + "1" * 24: ["evi_" + "1" * 24]},
        "root_cause_state": {"root_cause_candidates": []},
        "p19_assessment_refs": ["p19a_" + "1" * 24],
        "p19_case_snapshots": [
            {
                "hypotheses": [
                    {
                        "hypothesis": {"hypothesis_id": "p19h_" + "1" * 24},
                        "groundings": [
                            {
                                "source_kind": "P14_EVIDENCE",
                                "source_ref": "evi_" + "1" * 24,
                            }
                        ],
                    },
                    {
                        "hypothesis": {"hypothesis_id": "p19h_" + "2" * 24},
                        "groundings": [
                            {
                                "source_kind": "P14_EVIDENCE",
                                "source_ref": "evi_" + "1" * 24,
                            }
                        ],
                    },
                ]
            }
        ],
        "reasoning_records": [],
        "composition_payload": {
            "owner_calls": owner_calls,
            "completion_ledger": {"requirement_complete": True},
            "root_cause_mode_results": [
                {
                    "mode": mode,
                    "user_seeded_candidates": True,
                    "analytical_reentry_count": 1 if mode == "ADAPTIVE" else 0,
                }
            ],
        },
    }


def test_phase15_one_pass_mechanics_require_one_goal_one_acquisition_no_p17():
    observations = _mechanical_r_live(
        "R_LIVE_1_ONE_PASS",
        _phase15_mode_turn(mode="ONE_PASS", native_results=1, p17_calls=0),
    )
    assert observations["one_analytical_obligation"] is True
    assert observations["one_initial_native_acquisition"] is True
    assert observations["no_redundant_p17_cognition"] is True
    assert observations["all_user_must_requirements_complete"] is True


def test_phase15_adaptive_mechanics_require_exactly_one_discriminating_reentry():
    observations = _mechanical_r_live(
        "R_LIVE_2_ADAPTIVE",
        _phase15_mode_turn(mode="ADAPTIVE", native_results=2, p17_calls=1),
    )
    assert observations["one_analytical_obligation"] is True
    assert observations["initial_plus_one_discriminating_acquisition"] is True
    assert observations["one_p17_discriminating_owner_call"] is True
    assert observations["all_user_must_requirements_complete"] is True


def _one_pass_provider_report(
    *,
    total: int = 12,
    intake: int = 1,
    metabase: int = 10,
    p17: int = 0,
    p19: int = 1,
    prompt_tokens: int = 180000,
) -> dict:
    turn = _phase15_mode_turn(mode="ONE_PASS", native_results=1, p17_calls=0)
    return {
        "probe_id": "R_LIVE_1_ONE_PASS",
        "exception": None,
        "within_orchestration_boundary_budget": True,
        "turn_count_executed": 1,
        "turn_count_expected": 1,
        "turns": [turn],
        "provider_receipt": {
            "blocked_request_count": 0,
            "provider_requests_by_source": {
                "research_intake": intake,
                "metabase": metabase,
                "p17_manager": p17,
                "p19_manager": p19,
            },
            "prompt_tokens": prompt_tokens,
        },
        "actual_provider_request_count": total,
        "hard_provider_request_ceiling": 24,
        "mechanical_observations": _mechanical_r_live(
            "R_LIVE_1_ONE_PASS",
            turn,
        ),
    }


def test_phase15_one_pass_readiness_slo_accepts_exact_operational_boundary():
    assert _mechanical_verdict(_one_pass_provider_report()) == "PASS"


@pytest.mark.parametrize(
    ("override", "value"),
    (
        ("total", 13),
        ("intake", 2),
        ("metabase", 11),
        ("p17", 1),
        ("prompt_tokens", 180001),
    ),
)
def test_phase15_one_pass_readiness_slo_fails_closed(override, value):
    report = _one_pass_provider_report(**{override: value})
    assert _mechanical_verdict(report) == "FAIL"
