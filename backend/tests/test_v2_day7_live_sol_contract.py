"""Provider-free contract gate for the manual Day7 LIVE SOL corpus/harness."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import yaml

import lab.v2_day7_manager_live_sol as live
from lab.v2_day7_manager_live_sol import MDL_VERSION, semantic_schema


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day7_live_sol_cases.yaml"


def _document():
    return yaml.safe_load(CASES.read_text(encoding="utf-8"))


def test_live_sol_corpus_is_small_workers_one_and_reference_ceiling():
    doc = _document()
    cases = list(doc["cases"])

    assert 10 <= len(cases) <= 15
    assert doc["policy"]["workers"] == 1
    assert doc["policy"]["manager_role"] == "RESEARCH_MANAGER"
    assert doc["policy"]["model_ceiling"] == "openai/gpt-5.6-sol"
    assert doc["policy"]["derived_family_manager_coverage"] is False
    assert len({case["id"] for case in cases}) == len(cases)


def test_live_sol_corpus_contains_required_day7_high_information_families():
    kinds = {case["kind"] for case in _document()["cases"]}

    assert {
        "standard",
        "breakdown",
        "rank",
        "compare",
        "multi_obligation",
        "relationship_safe",
        "relationship_unsafe",
        "adaptive",
        "no_unnecessary_branch",
        "high_cardinality",
        "duplicate_safety",
        "insufficient_evidence",
        "budget_pressure",
    }.issubset(kinds)

    assert not {"trend", "contribution", "peer_compare"}.intersection(kinds)


def test_live_sol_hard_caps_are_never_relaxed_in_case_oracles():
    for case in _document()["cases"]:
        assert int(case.get("max_queries", 8)) <= 8

    budget = next(
        case for case in _document()["cases"]
        if case["kind"] == "budget_pressure"
    )
    assert budget["allow_budget_exhausted"] is True


def test_live_relationship_fixture_carries_explicit_wren_truth_and_fresh_fanout_proof():
    schema = semantic_schema()
    rel = next(
        item
        for item in schema["relationships"]
        if item["name"] == "ops_events_line_master"
    )

    assert rel["models"] == ["ops_events", "line_master"]
    assert rel["join_type"] == "MANY_TO_ONE"
    assert rel["certified"] == "olculdu:saglikli"
    assert rel["fanout_proof"]["status"] == "HEALTHY"
    assert rel["fanout_proof"]["certificate_mdl_version"] == MDL_VERSION
    assert rel["fanout_proof"]["current_mdl_version"] == MDL_VERSION

    ops = next(cube for cube in schema["cubes"] if cube["name"] == "ops_delta")
    origin = ops["dimension_origin"]["department_axis_d"]
    assert origin == {
        "model": "line_master",
        "column": "department",
        "relationship": "ops_events_line_master",
        "hops": 1,
    }


def test_live_oracles_include_safety_specific_checks_not_only_answer_success():
    cases = {case["kind"]: case for case in _document()["cases"]}

    assert cases["multi_obligation"]["expected_preacceptance_state"] == "NEEDS_CLARIFICATION"
    assert cases["multi_obligation"]["max_queries"] == 0
    assert cases["relationship_unsafe"]["expected_preacceptance_state"] == "NEEDS_CLARIFICATION"
    assert cases["relationship_unsafe"]["max_queries"] == 0
    assert cases["duplicate_safety"]["require_unique_task_side_effects"] is True
    assert cases["insufficient_evidence"]["require_zero_row_observation"] is True
    assert cases["high_cardinality"]["max_fanout_selected"] == 2
    assert cases["no_unnecessary_branch"]["max_derived_executions"] == 0


def test_preacceptance_oracle_scores_fail_closed_without_contract_or_execution():
    case = {
        "id": "clarify",
        "kind": "multi_obligation",
        "expected_preacceptance_state": "NEEDS_CLARIFICATION",
        "expected_observation_kind": "material_grounding_gap",
        "expect_no_ledger": True,
        "max_queries": 0,
    }
    body = {
        "snapshot": {
            "state": "NEEDS_CLARIFICATION",
            "accepted_contract_id": None,
            "manager_turns": 1,
            "tool_calls": 1,
            "data_queries": 0,
        },
        "observations": [{"kind": "material_grounding_gap"}],
        "ledger": None,
    }
    response = SimpleNamespace(status_code=200)

    checks = live._case_checks(
        case,
        response=response,
        body=body,
        query_delta=0,
    )

    assert checks["preacceptance_state"] is True
    assert checks["accepted_contract_absent"] is True
    assert checks["zero_data_queries"] is True
    assert checks["ledger_absent"] is True
    assert checks["expected_observation"] is True
    assert "accepted_contract" not in checks
    assert "must_tools" not in checks


WORKFLOW = ROOT.parent / ".github" / "workflows" / "v2-day7-live-sol.yml"


def test_live_sol_sealed_model_topology_and_workers_one():
    assert live.LIVE_MANAGER_MODEL == "openai/gpt-5.6-sol"
    assert live.LIVE_LINKER_MODEL == "openai/gpt-5.6-luna"
    assert live.LIVE_TEMPORAL_MODEL == "openai/gpt-5.6-sol"

    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    dispatch = workflow["on"]["workflow_dispatch"]["inputs"]
    assert dispatch["manager_model"]["default"] == "openai/gpt-5.6-sol"
    assert dispatch["linker_model"]["default"] == "openai/gpt-5.6-luna"
    assert dispatch["temporal_model"]["default"] == "openai/gpt-5.6-sol"


def test_provider_failure_classifier_keeps_transport_out_of_product_semantics():
    assert (
        live._classify_provider_failure(
            '403 Client Error | body={"error":{"message":"Key limit exceeded (total limit)"}}'
        )
        == live.MeasurementValidity.PROVIDER_QUOTA_FAILURE
    )
    assert (
        live._classify_provider_failure("401 Client Error: Unauthorized")
        == live.MeasurementValidity.PROVIDER_AUTH_FAILURE
    )
    assert (
        live._classify_provider_failure("429 Client Error: Too Many Requests")
        == live.MeasurementValidity.PROVIDER_QUOTA_FAILURE
    )
    assert (
        live._classify_provider_failure("503 Server Error: Service Unavailable")
        == live.MeasurementValidity.PROVIDER_UNAVAILABLE
    )
    assert live._classify_provider_failure("schema output omitted an obligation") is None


def test_provider_preflight_uses_one_role_scoped_strict_schema_call(monkeypatch):
    calls = []

    class FakeManager:
        def structured_json(self, system, user, *, schema, schema_name):
            calls.append(
                {
                    "system": system,
                    "user": user,
                    "schema": schema,
                    "schema_name": schema_name,
                }
            )
            return json.dumps({"status": "ok"})

    profile = SimpleNamespace(
        provider="openrouter",
        model="openai/gpt-5.6-sol",
    )
    monkeypatch.setattr(
        live,
        "_build_role_scoped_manager_models",
        lambda settings: (
            FakeManager(),
            profile,
            object(),
            SimpleNamespace(provider="openrouter", model="openai/gpt-5.6-luna"),
            object(),
            SimpleNamespace(provider="openrouter", model="openai/gpt-5.6-sol"),
        ),
    )

    result = live._provider_preflight(object())

    assert result["ok"] is True
    assert result["measurement_validity"] == "VALID"
    assert result["model"] == "openai/gpt-5.6-sol"
    assert len(calls) == 1
    assert calls[0]["schema_name"] == "dima_day7_provider_preflight_v1"
    assert calls[0]["schema"]["properties"]["status"]["enum"] == ["ok"]


def test_invalid_provider_case_is_not_scored_as_behavior_or_hard_safety_failure():
    preflight = {
        "ok": True,
        "measurement_validity": live.MeasurementValidity.VALID.value,
    }
    record = {
        "case_id": "C1",
        "kind": "standard",
        "question": "q",
        "latency_s": 0.1,
        "status_code": 200,
        "terminal_status": None,
        "snapshot": {},
        "query_delta": 0,
        "checks": {"accepted_contract": False},
        "behavior_evaluable": False,
        "measurement_validity": live.MeasurementValidity.PROVIDER_QUOTA_FAILURE.value,
        "behavior_pass": None,
        "model_errors": [],
        "observations": [],
        "ledger": None,
    }
    payload = live._aggregate_live_records(
        document={"version": "test"},
        records=[record],
        selected_cases=1,
        service_query_count=0,
        preflight=preflight,
    )

    assert payload["measurement_valid"] is False
    assert payload["measurement_validity"] == "PROVIDER_QUOTA_FAILURE"
    assert payload["selected_cases"] == 1
    assert payload["evaluable_cases"] == 0
    assert payload["provider_failure_cases"] == 1
    assert payload["behavior_pass_rate"] is None
    assert payload["hard_safety_failures"] == []
    assert payload["status"] == "invalid_measurement"


def test_valid_model_cognition_failure_remains_behavior_evaluable():
    body = {
        "observations": [
            {
                "kind": "model_error",
                "message": "structured action invalid after one format retry",
            }
        ]
    }
    assert (
        live._case_measurement_validity(
            status_code=200,
            body=body,
            json_ok=True,
        )
        == live.MeasurementValidity.VALID
    )



def test_provider_preflight_reads_http_error_response_body_for_quota(monkeypatch):
    class FakeResponse:
        text = '{"error":{"message":"Key limit exceeded (total limit)"}}'

    class FakeHttpError(RuntimeError):
        def __init__(self):
            super().__init__("403 Client Error: Forbidden")
            self.response = FakeResponse()

    class FailingManager:
        def structured_json(self, system, user, *, schema, schema_name):
            raise FakeHttpError()

    profile = SimpleNamespace(
        provider="openrouter",
        model="openai/gpt-5.6-sol",
    )
    monkeypatch.setattr(
        live,
        "_build_role_scoped_manager_models",
        lambda settings: (
            FailingManager(),
            profile,
            object(),
            SimpleNamespace(provider="openrouter", model="openai/gpt-5.6-luna"),
            object(),
            SimpleNamespace(provider="openrouter", model="openai/gpt-5.6-sol"),
        ),
    )

    result = live._provider_preflight(object())

    assert result["ok"] is False
    assert result["measurement_validity"] == "PROVIDER_QUOTA_FAILURE"
    assert "Key limit exceeded" in result["message"]


def test_main_preflight_failure_stops_before_corpus_or_service(tmp_path, monkeypatch):
    cases = tmp_path / "cases.yaml"
    cases.write_text(
        yaml.safe_dump(
            {
                "version": "test",
                "cases": [
                    {
                        "id": "C1",
                        "kind": "standard",
                        "question": "net geliri göster",
                    },
                    {
                        "id": "C2",
                        "kind": "rank",
                        "question": "ürünleri sırala",
                    },
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    output = tmp_path / "report.json"

    monkeypatch.setattr(
        live,
        "_provider_preflight",
        lambda settings: {
            "measurement_validity": "PROVIDER_QUOTA_FAILURE",
            "ok": False,
            "provider": "openrouter",
            "model": "openai/gpt-5.6-sol",
            "message": "403 Key limit exceeded",
            "latency_s": 0.01,
        },
    )

    def forbidden_service():
        raise AssertionError("corpus infrastructure must not start after failed preflight")

    monkeypatch.setattr(live, "Day7LiveSyntheticService", forbidden_service)
    monkeypatch.setattr(
        "sys.argv",
        [
            "v2_day7_manager_live_sol.py",
            "--cases",
            str(cases),
            "--output",
            str(output),
        ],
    )

    code = live.main()
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert code == 2
    assert payload["status"] == "invalid_measurement"
    assert payload["measurement_valid"] is False
    assert payload["measurement_validity"] == "PROVIDER_QUOTA_FAILURE"
    assert payload["selected_cases"] == 2
    assert payload["evaluable_cases"] == 0
    assert payload["provider_failure_cases"] == 2
    assert payload["behavior_pass_rate"] is None
    assert payload["hard_safety_failures"] == []
    assert payload["total_service_queries"] == 0
    assert payload["records"] == []
