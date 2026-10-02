"""Bounded native-material repair policy.

Dima does not plan analytics here. It classifies whether one failed generated
native occurrence may be sent back to the SAME Metabot planner for a bounded
regeneration under the unchanged typed analytical contract.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MaterialRepairDisposition(StrEnum):
    REPAIR = "REPAIR"
    TERMINAL_LIMIT = "TERMINAL_LIMIT"


class MaterialRepairDecision(Frozen):
    disposition: MaterialRepairDisposition
    validation_code: str = Field(min_length=1)
    repair_attempt: int = Field(ge=0, le=1)
    require_new_query_fingerprint: bool = True
    preserve_scope_identity: bool = True
    preserve_material_contract: bool = True


# These failures say the generated analytical occurrence did not expose material
# the already-accepted contract requires. They are planner-output defects, not
# permission/currentness/domain-authority defects.
_REPAIRABLE_MATERIAL_VALIDATION_CODES = frozenset(
    {
        "R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
        "R1_RESULT_CHANGE_COVERAGE_INCOMPLETE",
        "R1_RESULT_TEMPORAL_COLUMN_MISMATCH",
        "R1_RESULT_CHANGE_TEMPORAL_COLUMN_REQUIRED",
    }
)


def decide_material_repair(
    *,
    validation_code: str,
    prior_repair_attempts: int,
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
        repair_attempt=1 if repairable else min(prior_repair_attempts, 1),
    )


def material_repair_feedback(decision: MaterialRepairDecision) -> dict[str, object]:
    """Structured feedback for the existing Metabot planner.

    The accepted analytical contract remains the sole semantic authority.
    """

    if decision.disposition != MaterialRepairDisposition.REPAIR:
        raise ValueError("terminal material limitation has no repair feedback")
    return {
        "schema": "dima_material_repair_feedback_v1",
        "validation_code": decision.validation_code,
        "repair_attempt": decision.repair_attempt,
        "required_action": "REGENERATE_NATIVE_QUERY",
        "require_new_query_fingerprint": decision.require_new_query_fingerprint,
        "preserve_scope_identity": decision.preserve_scope_identity,
        "preserve_material_contract": decision.preserve_material_contract,
    }
