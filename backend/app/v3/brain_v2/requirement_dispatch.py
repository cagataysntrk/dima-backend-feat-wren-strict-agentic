"""Deterministic accepted-requirement owner dispatch for Brain V2.1."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchGoalKind,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RequirementOwner(StrEnum):
    DIRECT_EVIDENCE = "DIRECT_EVIDENCE"
    P18 = "P18"
    P19 = "P19"
    P20 = "P20"


class RequirementDispatch(Frozen):
    requirement_id: str = Field(min_length=1)
    owner: RequirementOwner
    analytical: bool


_DIRECT_KINDS = frozenset(
    {
        ResearchGoalKind.COMPARISON,
        ResearchGoalKind.PERFORMANCE,
        ResearchGoalKind.TREND,
        ResearchGoalKind.BREAKDOWN,
        ResearchGoalKind.RANKING,
        ResearchGoalKind.OTHER,
    }
)


def dispatch_requirements(brief: ResearchBrief) -> tuple[RequirementDispatch, ...]:
    """Map typed accepted requirement kinds to their sealed owner.

    This function never interprets source text and never chooses an analytical
    plan. It only projects already accepted requirement authority.
    """

    output: list[RequirementDispatch] = []
    must_ids = set(brief.must_requirement_ids)
    for question in brief.questions:
        if question.goal_id not in must_ids:
            continue
        if question.kind == ResearchGoalKind.RELATIONSHIP:
            owner = RequirementOwner.P18
        elif question.kind == ResearchGoalKind.ROOT_CAUSE:
            owner = RequirementOwner.P19
        elif question.kind in _DIRECT_KINDS:
            owner = RequirementOwner.DIRECT_EVIDENCE
        else:
            raise ValueError(
                f"unsupported accepted analytical requirement kind:{question.kind}"
            )
        output.append(
            RequirementDispatch(
                requirement_id=question.goal_id,
                owner=owner,
                analytical=True,
            )
        )

    for deliverable in brief.deliverables:
        if deliverable.requirement_id not in must_ids:
            continue
        if deliverable.kind == PresentationKind.NONE:
            continue
        output.append(
            RequirementDispatch(
                requirement_id=deliverable.requirement_id,
                owner=RequirementOwner.P20,
                analytical=False,
            )
        )

    if len({item.requirement_id for item in output}) != len(output):
        raise ValueError("accepted requirement identity is not unique")
    return tuple(output)
