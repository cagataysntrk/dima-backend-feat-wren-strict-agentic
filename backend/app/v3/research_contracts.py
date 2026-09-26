"""Canonical typed Research entry contracts.

These models are grounded input artifacts consumed by sealed P14+ authorities.
They do not interpret language, execute analytics, or revive the historical Ask-v2 runtime.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PresentationKind(StrEnum):
    EXPLAIN = "explain"
    TABLE = "table"
    CHART = "chart"
    REPORT = "report"
    NONE = "none"


class RankingSurface(FrozenModel):
    text: str = Field(min_length=1)
    direction: Literal["asc", "desc", "unspecified"] = "unspecified"
    limit: int | None = Field(default=None, ge=1, le=1000)


class ComparisonSurface(FrozenModel):
    text: str = Field(min_length=1)


class SemanticTargetKind(StrEnum):
    METRIC = "metric"
    DIMENSION = "dimension"
    ENTITY_VALUE = "entity_value"
    KPI = "kpi"
    CUBE = "cube"


class ResearchGoalKind(StrEnum):
    COMPARISON = "comparison"
    RELATIONSHIP = "relationship"
    PERFORMANCE = "performance"
    TREND = "trend"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    ROOT_CAUSE = "root_cause"
    OTHER = "other"


class ResearchGoalStatus(StrEnum):
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"


class ResearchBriefStatus(StrEnum):
    READY_FOR_RESEARCH = "READY_FOR_RESEARCH"
    BLOCKED = "BLOCKED"


class ResearchSemanticRef(FrozenModel):
    source_mention: str
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None = None
    value: str | None = None
    cube_names: tuple[str, ...] = ()
    sensitive: bool = False


class ResearchUnresolvedRef(FrozenModel):
    source_mention: str
    role: Literal["subject", "related", "goal"]
    reason: str


class ResearchQuestion(FrozenModel):
    goal_id: str
    kind: ResearchGoalKind
    priority: Literal["MUST"] = "MUST"
    source_text: str
    subject_refs: tuple[ResearchSemanticRef, ...] = ()
    related_refs: tuple[ResearchSemanticRef, ...] = ()
    ranking: RankingSurface | None = None
    comparisons: tuple[ComparisonSurface, ...] = ()
    unresolved: tuple[ResearchUnresolvedRef, ...] = ()
    status: ResearchGoalStatus


class ResearchDeliverableRequirement(FrozenModel):
    requirement_id: str
    kind: PresentationKind
    priority: Literal["MUST"] = "MUST"
    source_text: str


class ResearchScope(FrozenModel):
    semantic_refs: tuple[ResearchSemanticRef, ...] = ()
    time_surfaces: tuple[str, ...] = ()


class ResearchBudget(FrozenModel):
    max_data_queries: int | None = Field(default=None, ge=0)
    max_branch_depth: int | None = Field(default=None, ge=0)
    max_llm_turns: int | None = Field(default=None, ge=0)
    max_wall_clock_seconds: int | None = Field(default=None, ge=1)
    assignment: Literal["deferred_to_research_execution_policy"] = (
        "deferred_to_research_execution_policy"
    )


class ResearchBrief(FrozenModel):
    brief_id: str
    objective: str
    scope: ResearchScope
    required_domains: tuple[str, ...] = ()
    questions: tuple[ResearchQuestion, ...] = ()
    deliverables: tuple[ResearchDeliverableRequirement, ...] = ()
    must_requirement_ids: tuple[str, ...] = ()
    blocking_goal_ids: tuple[str, ...] = ()
    budget: ResearchBudget = Field(default_factory=ResearchBudget)
    context_version: str
    status: ResearchBriefStatus
