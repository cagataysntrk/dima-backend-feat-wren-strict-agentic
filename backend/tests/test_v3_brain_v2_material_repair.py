from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from app.v3.brain_v2.material_repair import (
    MaterialRepairDisposition,
    decide_material_repair,
    material_repair_feedback,
)


_REPAIRABLE = (
    "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
    "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE",
    "R1_RESULT_TEMPORAL_COLUMN_MISMATCH",
    "R1_RESULT_CHANGE_TEMPORAL_COLUMN_REQUIRED",
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
    )
    feedback = material_repair_feedback(decision)

    assert feedback == {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": code,
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
