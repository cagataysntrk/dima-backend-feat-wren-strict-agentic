"""Bounded native-material repair policy.

Dima does not plan analytics here. It classifies whether one failed generated
native occurrence may be sent back to the SAME Metabot planner for a bounded
regeneration under the unchanged typed analytical contract.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MaterialRepairDisposition(StrEnum):
    REPAIR = "REPAIR"
    TERMINAL_LIMIT = "TERMINAL_LIMIT"


class MaterialRepairDecision(Frozen):
    disposition: MaterialRepairDisposition
    validation_code: str = Field(min_length=1)
    validation_detail: str | None = Field(default=None, min_length=1)
    repair_attempt: int = Field(ge=0, le=1)
    require_new_query_fingerprint: bool = True
    preserve_scope_identity: bool = True
    preserve_material_contract: bool = True
    expected_semantic_shape: dict[str, Any] | None = None
    observed_semantic_shape: dict[str, Any] | None = None


# These failures say the generated analytical occurrence did not expose material
# the already-accepted contract requires. They are planner-output defects, not
# permission/currentness/domain-authority defects.
_REPAIRABLE_MATERIAL_VALIDATION_CODES = frozenset(
    {
        "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
        "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE",
        "R1_RESULT_TEMPORAL_COLUMN_MISMATCH",
        "R1_RESULT_CHANGE_TEMPORAL_COLUMN_REQUIRED",
        "R1_NATIVE_RANKING_REQUIRED_MISSING",
        "R1_NATIVE_RANKING_BASIS_MISMATCH",
        "ANALYTICAL_V1_RANKING_MISMATCH",
    }
)


def decide_material_repair(
    *,
    validation_code: str,
    prior_repair_attempts: int,
    validation_detail: str | None = None,
    expected_semantic_shape: dict[str, Any] | None = None,
    observed_semantic_shape: dict[str, Any] | None = None,
) -> MaterialRepairDecision:
    if prior_repair_attempts < 0:
        raise ValueError("prior repair attempts cannot be negative")

    repairable = (
        validation_code in _REPAIRABLE_MATERIAL_VALIDATION_CODES
        and prior_repair_attempts == 0
    )
    return MaterialRepairDecision(
        disposition=(
            MaterialRepairDisposition.REPAIR
            if repairable
            else MaterialRepairDisposition.TERMINAL_LIMIT
        ),
        validation_code=validation_code,
        validation_detail=validation_detail,
        repair_attempt=1 if repairable else min(prior_repair_attempts, 1),
        expected_semantic_shape=expected_semantic_shape,
        observed_semantic_shape=observed_semantic_shape,
    )


def material_repair_feedback(decision: MaterialRepairDecision) -> dict[str, object]:
    """Structured feedback for the existing Metabot planner.

    The accepted analytical contract remains the sole semantic authority.
    """

    if decision.disposition != MaterialRepairDisposition.REPAIR:
        raise ValueError("terminal material limitation has no repair feedback")
    feedback: dict[str, object] = {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": decision.validation_code,
        "repair_attempt": decision.repair_attempt,
        "required_action": "REGENERATE_NATIVE_QUERY",
        "require_new_query_fingerprint": decision.require_new_query_fingerprint,
        "preserve_scope_identity": decision.preserve_scope_identity,
        "preserve_material_contract": decision.preserve_material_contract,
    }
    if decision.validation_detail is not None:
        feedback["validation_detail"] = decision.validation_detail
    if decision.expected_semantic_shape is not None:
        feedback["expected_semantic_shape"] = decision.expected_semantic_shape
    if decision.observed_semantic_shape is not None:
        feedback["observed_semantic_shape"] = decision.observed_semantic_shape
    return feedback
