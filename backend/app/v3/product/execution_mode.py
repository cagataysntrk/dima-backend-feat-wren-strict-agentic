"""Deterministic Dima V1 Product execution-mode router.

The router selects only an existing owner path. It has no analytics, query,
semantic-resolution or epistemic authority.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.v3.product.contracts import ProductInvestigationRequirement
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchGoalKind,
    SemanticTargetKind,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProductExecutionMode(StrEnum):
    FAST = "FAST"
    GUIDED = "GUIDED"
    INVESTIGATION = "INVESTIGATION"


class ExecutionModeDecision(Frozen):
    mode: ProductExecutionMode
    reason_codes: tuple[str, ...]


def _measure_count(question) -> int:
    refs = (*question.subject_refs, *question.related_refs)
    return len(
        {
            item.candidate_id
            for item in refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        }
    )


def classify_execution_mode(
    brief: ResearchBrief,
    *,
    investigation_requirements: tuple[ProductInvestigationRequirement, ...] = (),
    counter_evidence_required: bool = False,
) -> ExecutionModeDecision:
    """Classify owner depth from accepted typed contracts only."""

    if investigation_requirements:
        return ExecutionModeDecision(
            mode=ProductExecutionMode.INVESTIGATION,
            reason_codes=("TYPED_ADAPTIVE_INVESTIGATION",),
        )
    if counter_evidence_required:
        return ExecutionModeDecision(
            mode=ProductExecutionMode.INVESTIGATION,
            reason_codes=("TYPED_COUNTER_EVIDENCE",),
        )

    kinds = {question.kind for question in brief.questions}
    if ResearchGoalKind.ROOT_CAUSE in kinds:
        return ExecutionModeDecision(
            mode=ProductExecutionMode.INVESTIGATION,
            reason_codes=("ROOT_CAUSE",),
        )

    reasons: list[str] = []
    if ResearchGoalKind.RELATIONSHIP in kinds:
        reasons.append("RELATIONSHIP")
    if any(_measure_count(question) >= 2 for question in brief.questions):
        reasons.append("MULTI_METRIC")
    if ResearchGoalKind.OTHER in kinds:
        reasons.append("UNSPECIALIZED_COMPLEX_GOAL")
    if reasons:
        return ExecutionModeDecision(
            mode=ProductExecutionMode.GUIDED,
            reason_codes=tuple(dict.fromkeys(reasons)),
        )

    return ExecutionModeDecision(
        mode=ProductExecutionMode.FAST,
        reason_codes=("DIRECT_ANALYTICAL",),
    )
