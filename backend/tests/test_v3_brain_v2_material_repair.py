from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from app.v3.research_material_repair import (
    MaterialRepairDisposition,
    decide_material_repair,
    material_repair_feedback,
)


_REPAIRABLE = (
    "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
    "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE",
    "R1_RESULT_TEMPORAL_COLUMN_MISMATCH",
    "R1_RESULT_CHANGE_TEMPORAL_COLUMN_REQUIRED",
    "R1_NATIVE_RANKING_REQUIRED_MISSING",
    "R1_NATIVE_RANKING_BASIS_MISMATCH",
    "NATIVE_MATERIAL_RANKING_TARGET_UNSUPPORTED",
)

_NON_REPAIRABLE = (
    "R1_NATIVE_FILTER_SCOPE_MISMATCH",
    "R1_NATIVE_RANKING_SCOPE_MISMATCH",
    "R1_RESULT_TEMPORAL_BINDING_REQUIRED",
    "P14_NATIVE_RESULT_FINGERPRINT_MISMATCH",
    "P14_NATIVE_EXECUTION_PROVENANCE_INVALID",
)


@pytest.mark.parametrize("code", _REPAIRABLE)
def test_first_material_coverage_miss_allows_one_planner_repair(code: str) -> None:
    decision = decide_material_repair(
        validation_code=code,
        prior_repair_attempts=0,
    )

    assert decision.disposition == MaterialRepairDisposition.REPAIR
    assert decision.repair_attempt == 1
    assert decision.require_new_query_fingerprint is True
    assert decision.preserve_scope_identity is True
    assert decision.preserve_material_contract is True


@pytest.mark.parametrize("code", _REPAIRABLE)
def test_second_material_coverage_miss_is_terminal_limit(code: str) -> None:
    decision = decide_material_repair(
        validation_code=code,
        prior_repair_attempts=1,
    )

    assert decision.disposition == MaterialRepairDisposition.TERMINAL_LIMIT


@pytest.mark.parametrize("code", _NON_REPAIRABLE)
def test_authority_or_integrity_failures_are_never_repaired(code: str) -> None:
    decision = decide_material_repair(
        validation_code=code,
        prior_repair_attempts=0,
    )

    assert decision.disposition == MaterialRepairDisposition.TERMINAL_LIMIT


@given(
    code=st.sampled_from(_REPAIRABLE),
)
def test_repair_feedback_is_structured_and_contract_preserving(code: str) -> None:
    decision = decide_material_repair(
        validation_code=code,
        prior_repair_attempts=0,
        validation_detail="symbolic missing required semantic material",
    )
    feedback = material_repair_feedback(decision)

    assert feedback == {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": code,
        "validation_detail": "symbolic missing required semantic material",
        "repair_attempt": 1,
        "required_action": "REGENERATE_NATIVE_QUERY",
        "require_new_query_fingerprint": True,
        "preserve_scope_identity": True,
        "preserve_material_contract": True,
    }


def test_terminal_limit_has_no_planner_feedback() -> None:
    decision = decide_material_repair(
        validation_code="R1_NATIVE_FILTER_SCOPE_MISMATCH",
        prior_repair_attempts=0,
    )

    with pytest.raises(ValueError, match="no repair feedback"):
        material_repair_feedback(decision)



def test_ranking_repair_feedback_carries_exact_expected_and_observed_shape() -> None:
    decision = decide_material_repair(
        validation_code="R1_NATIVE_RANKING_BASIS_MISMATCH",
        prior_repair_attempts=0,
        validation_detail="observed native ranking basis differs",
        expected_semantic_shape={
            "ranking_basis": "change",
            "direction": "desc",
        },
        observed_semantic_shape={
            "ranking_basis": "level",
            "direction": "desc",
        },
    )

    feedback = material_repair_feedback(decision)

    assert feedback["expected_semantic_shape"] == {
        "ranking_basis": "change",
        "direction": "desc",
    }
    assert feedback["observed_semantic_shape"] == {
        "ranking_basis": "level",
        "direction": "desc",
    }


@pytest.mark.parametrize(
    "code",
    (
        "R1_NATIVE_RANKING_SCOPE_MISMATCH",
        "R1_NATIVE_FILTER_SCOPE_MISMATCH",
        "R1_NATIVE_RESOURCE_DATABASE_MISMATCH",
    ),
)
def test_ranking_or_authority_mismatch_never_becomes_repairable(code: str) -> None:
    decision = decide_material_repair(
        validation_code=code,
        prior_repair_attempts=0,
    )
    assert decision.disposition == MaterialRepairDisposition.TERMINAL_LIMIT


def test_engine_observer_ranking_shape_miss_preserves_typed_expected_authority() -> None:
    expected = {
        "ranking": {
            "kind": "native_metric",
            "measure": "metric.symbolic",
            "direction": "desc",
            "limit": 2,
            "basis": "change",
        },
        "temporal_change_frame": {
            "mode": "PAIR",
            "time_dimension": "dimension.time",
        },
    }
    decision = decide_material_repair(
        validation_code="NATIVE_MATERIAL_RANKING_TARGET_UNSUPPORTED",
        validation_detail="ranking target has no stable governed identity",
        prior_repair_attempts=0,
        expected_semantic_shape=expected,
    )

    feedback = material_repair_feedback(decision)

    assert decision.disposition == MaterialRepairDisposition.REPAIR
    assert feedback["expected_semantic_shape"] == expected
    assert feedback["preserve_material_contract"] is True
