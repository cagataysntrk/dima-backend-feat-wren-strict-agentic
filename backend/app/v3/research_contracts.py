"""Canonical typed Research entry contracts.

These models are grounded input artifacts consumed by sealed P14+ authorities.
They do not interpret language, execute analytics, or revive the historical Ask-v2 runtime.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class ScopeMutationKind(StrEnum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"
    NARROW_ENTITY = "NARROW_ENTITY"
    EXPAND_ENTITY = "EXPAND_ENTITY"
    CHANGE_PERIOD = "CHANGE_PERIOD"
    CHANGE_METRIC = "CHANGE_METRIC"
    CHANGE_BREAKDOWN = "CHANGE_BREAKDOWN"
    RESET = "RESET"


class ScopeVersion(FrozenModel):
    version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    ordinal: int = Field(ge=1)
    parent_version_id: str | None = None

    @model_validator(mode="after")
    def coherent(self):
        if self.version_id != f"scope_v{self.ordinal}":
            raise ValueError("scope version id/ordinal mismatch")
        if (self.ordinal == 1) != (self.parent_version_id is None):
            raise ValueError("scope version parent mismatch")
        return self


class ScopeMutation(FrozenModel):
    kind: ScopeMutationKind
    source_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    target_semantic_refs: tuple[ResearchSemanticRef, ...] = ()
    target_time_surfaces: tuple[str, ...] = ()
    reason: str = Field(min_length=1, max_length=1000)


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
    scope_version: ScopeVersion = Field(
        default_factory=lambda: ScopeVersion(version_id="scope_v1", ordinal=1)
    )


class TurnScopeContract(FrozenModel):
    previous_scope: ResearchScope
    current_scope: ResearchScope
    mutation: ScopeMutation

    @model_validator(mode="after")
    def coherent(self):
        previous = self.previous_scope.scope_version
        current = self.current_scope.scope_version
        if self.mutation.source_version_id != previous.version_id:
            raise ValueError("scope mutation source version mismatch")
        if current.ordinal != previous.ordinal + 1:
            raise ValueError("scope mutation must advance one version")
        if current.parent_version_id != previous.version_id:
            raise ValueError("scope version parent mismatch")
        return self


def apply_scope_mutation(
    current_scope: ResearchScope,
    mutation: ScopeMutation,
) -> TurnScopeContract:
    if mutation.source_version_id != current_scope.scope_version.version_id:
        raise ValueError("scope mutation was formed against another scope version")
    old_refs = {item.candidate_id for item in current_scope.semantic_refs}
    new_refs = {item.candidate_id for item in mutation.target_semantic_refs}
    old_times = set(current_scope.time_surfaces)
    new_times = set(mutation.target_time_surfaces)
    if old_refs == new_refs and old_times == new_times:
        raise ValueError("scope mutation must materially change accepted scope")
    if mutation.kind == ScopeMutationKind.ADD:
        if not old_refs.issubset(new_refs) or not old_times.issubset(new_times):
            raise ValueError("ADD cannot remove accepted scope")
    elif mutation.kind == ScopeMutationKind.REMOVE:
        if not new_refs.issubset(old_refs) or not new_times.issubset(old_times):
            raise ValueError("REMOVE cannot add accepted scope")
    elif mutation.kind == ScopeMutationKind.CHANGE_PERIOD:
        if old_refs != new_refs or old_times == new_times:
            raise ValueError("CHANGE_PERIOD must only change time scope")
    elif mutation.kind == ScopeMutationKind.NARROW_ENTITY:
        old_entities = {
            item.candidate_id for item in current_scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        }
        new_entities = {
            item.candidate_id for item in mutation.target_semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        }
        old_other = old_refs - old_entities
        new_other = new_refs - new_entities
        if old_other != new_other or not new_entities < old_entities or old_times != new_times:
            raise ValueError("NARROW_ENTITY must only narrow entity values")
    elif mutation.kind == ScopeMutationKind.EXPAND_ENTITY:
        old_entities = {
            item.candidate_id for item in current_scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        }
        new_entities = {
            item.candidate_id for item in mutation.target_semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        }
        old_other = old_refs - old_entities
        new_other = new_refs - new_entities
        if old_other != new_other or not old_entities < new_entities or old_times != new_times:
            raise ValueError("EXPAND_ENTITY must only expand entity values")
    elif mutation.kind == ScopeMutationKind.CHANGE_METRIC:
        metric_kinds = {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        old_metrics = {x.candidate_id for x in current_scope.semantic_refs if x.target_kind in metric_kinds}
        new_metrics = {x.candidate_id for x in mutation.target_semantic_refs if x.target_kind in metric_kinds}
        if (old_refs-old_metrics)!=(new_refs-new_metrics) or old_metrics==new_metrics or old_times!=new_times:
            raise ValueError("CHANGE_METRIC must only change metrics")
    elif mutation.kind == ScopeMutationKind.CHANGE_BREAKDOWN:
        old_dims = {x.candidate_id for x in current_scope.semantic_refs if x.target_kind == SemanticTargetKind.DIMENSION}
        new_dims = {x.candidate_id for x in mutation.target_semantic_refs if x.target_kind == SemanticTargetKind.DIMENSION}
        if (old_refs-old_dims)!=(new_refs-new_dims) or old_dims==new_dims or old_times!=new_times:
            raise ValueError("CHANGE_BREAKDOWN must only change dimensions")
    next_ordinal = current_scope.scope_version.ordinal + 1
    next_scope = ResearchScope(
        semantic_refs=mutation.target_semantic_refs,
        time_surfaces=mutation.target_time_surfaces,
        scope_version=ScopeVersion(
            version_id=f"scope_v{next_ordinal}",
            ordinal=next_ordinal,
            parent_version_id=current_scope.scope_version.version_id,
        ),
    )
    return TurnScopeContract(
        previous_scope=current_scope,
        current_scope=next_scope,
        mutation=mutation,
    )


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
