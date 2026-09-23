"""Provider-free contract gate for the manual Day7 LIVE SOL corpus/harness."""

from __future__ import annotations

from pathlib import Path

import yaml

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

    assert cases["relationship_unsafe"]["require_typed_block"] is True
    assert cases["duplicate_safety"]["require_unique_task_side_effects"] is True
    assert cases["insufficient_evidence"]["require_zero_row_observation"] is True
    assert cases["high_cardinality"]["max_fanout_selected"] == 2
    assert cases["no_unnecessary_branch"]["max_derived_executions"] == 0
