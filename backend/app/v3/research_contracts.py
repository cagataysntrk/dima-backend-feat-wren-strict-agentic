"""Canonical typed Research entry contracts.

These models are grounded input artifacts consumed by sealed P14+ authorities.
They do not interpret language, execute analytics, or revive the historical Ask-v2 runtime.
"""
from __future__ import annotations

from datetime import date, datetime
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


class ResearchNativeVerificationBinding(FrozenModel):
    """Grounded native metadata for one observed query occurrence.

    native_metric_entity_id is the forward V1 governed metric identity.
    aggregation and argument_kind remain historical/diagnostic metadata and
    must not become forward semantic authority over Metabase query planning.
    """

    candidate_id: str = Field(min_length=1)
    table_name: str = Field(min_length=1)
    schema_name: str | None = None
    column_name: str | None = None
    aggregation: str | None = None
    argument_kind: Literal[
        "all_rows",
        "field",
        "field_or_expression",
        "expression",
    ] | None = None
    native_metric_entity_id: str | None = None

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.column_name is None
            and self.native_metric_entity_id is None
            and self.argument_kind != "all_rows"
        ):
            raise ValueError(
                "native verification binding requires a column, native metric identity, "
                "or explicit all_rows aggregation"
            )
        if self.aggregation is not None and not self.aggregation.strip():
            raise ValueError("aggregation must be null or non-empty")
        return self


class ResearchSemanticRef(FrozenModel):
    source_mention: str
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None = None
    value: str | None = None
    cube_names: tuple[str, ...] = ()
    sensitive: bool = False


class ResearchTimePeriod(FrozenModel):
    """Accepted semantic period with exact half-open bounds.

    Bounds are interpreted by Research Intake cognition and then frozen as
    Research authority. No month-name or prompt parser exists here.
    """

    source_text: str = Field(min_length=1)
    time_dimension_candidate_id: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)

    @model_validator(mode="after")
    def half_open_iso_range(self):
        def parse(value: str):
            if "T" in value:
                try:
                    return ("datetime", datetime.fromisoformat(value))
                except ValueError as exc:
                    raise ValueError(
                        "Research datetime bounds must be ISO-8601"
                    ) from exc
            try:
                return ("date", date.fromisoformat(value))
            except ValueError as exc:
                raise ValueError(
                    "Research date bounds must be ISO-8601"
                ) from exc

        start_kind, start_value = parse(self.start)
        end_kind, end_value = parse(self.end)
        if start_kind != end_kind:
            raise ValueError(
                "Research time bounds must use the same date/datetime shape"
            )
        if start_value >= end_value:
            raise ValueError("Research time period end must be after start")
        return self


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
    target_periods: tuple[ResearchTimePeriod, ...] = ()
    target_temporal_dimension_ids: tuple[str, ...] = ()
    target_native_verification_bindings: tuple[
        ResearchNativeVerificationBinding, ...
    ] = ()
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
    periods: tuple[ResearchTimePeriod, ...] = ()
    temporal_dimension_ids: tuple[str, ...] = ()
    native_verification_bindings: tuple[
        ResearchNativeVerificationBinding, ...
    ] = ()
    scope_version: ScopeVersion = Field(
        default_factory=lambda: ScopeVersion(version_id="scope_v1", ordinal=1)
    )

    @model_validator(mode="after")
    def coherent_material_scope(self):
        if len(self.time_surfaces) != len(set(self.time_surfaces)):
            raise ValueError("Research time surfaces must be unique")
        period_sources = [item.source_text for item in self.periods]
        if len(period_sources) != len(set(period_sources)):
            raise ValueError("Research periods must have unique source_text")
        if self.periods and set(period_sources) != set(self.time_surfaces):
            raise ValueError(
                "typed Research periods must exactly cover accepted time surfaces"
            )
        semantic_ids = {item.candidate_id for item in self.semantic_refs}
        dimension_ids = {
            item.candidate_id
            for item in self.semantic_refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        }
        if len(self.temporal_dimension_ids) != len(
            set(self.temporal_dimension_ids)
        ):
            raise ValueError("Research temporal dimension ids must be unique")
        if not set(self.temporal_dimension_ids).issubset(dimension_ids):
            raise ValueError(
                "Research temporal dimensions must be accepted dimension refs"
            )
        if any(
            item.time_dimension_candidate_id
            not in set(self.temporal_dimension_ids)
            for item in self.periods
        ):
            raise ValueError(
                "Research period time dimension must be explicitly temporal"
            )
        binding_ids = [
            item.candidate_id for item in self.native_verification_bindings
        ]
        if len(binding_ids) != len(set(binding_ids)):
            raise ValueError("Research native verification bindings must be unique")
        if not set(binding_ids).issubset(semantic_ids):
            raise ValueError(
                "Research native verification binding is outside accepted scope"
            )
        return self


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
    old_periods = tuple(current_scope.periods)
    new_periods = tuple(mutation.target_periods)
    retained_refs = old_refs & new_refs
    retained_temporal_ids = (
        set(current_scope.temporal_dimension_ids) & retained_refs
    )
    if not retained_temporal_ids.issubset(
        set(mutation.target_temporal_dimension_ids)
    ):
        raise ValueError(
            "scope mutation cannot drop retained temporal dimension identity"
        )
    current_binding_ids = {
        item.candidate_id
        for item in current_scope.native_verification_bindings
    }
    target_binding_ids = {
        item.candidate_id
        for item in mutation.target_native_verification_bindings
    }
    if not (current_binding_ids & retained_refs).issubset(
        target_binding_ids
    ):
        raise ValueError(
            "scope mutation cannot drop retained native verification binding"
        )
    if (
        current_scope.periods
        and mutation.target_time_surfaces
        and not mutation.target_periods
    ):
        raise ValueError(
            "scope mutation cannot drop typed period authority"
        )
    if old_refs == new_refs and old_times == new_times and old_periods == new_periods:
        raise ValueError("scope mutation must materially change accepted scope")
    if mutation.kind == ScopeMutationKind.ADD:
        if not old_refs.issubset(new_refs) or not old_times.issubset(new_times):
            raise ValueError("ADD cannot remove accepted scope")
    elif mutation.kind == ScopeMutationKind.REMOVE:
        if not new_refs.issubset(old_refs) or not new_times.issubset(old_times):
            raise ValueError("REMOVE cannot add accepted scope")
    elif mutation.kind == ScopeMutationKind.CHANGE_PERIOD:
        if (
            old_refs != new_refs
            or (old_times == new_times and old_periods == new_periods)
        ):
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
        if (
            old_other != new_other
            or not new_entities < old_entities
            or old_times != new_times
            or old_periods != new_periods
        ):
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
        if (
            old_other != new_other
            or not old_entities < new_entities
            or old_times != new_times
            or old_periods != new_periods
        ):
            raise ValueError("EXPAND_ENTITY must only expand entity values")
    elif mutation.kind == ScopeMutationKind.CHANGE_METRIC:
        metric_kinds = {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        old_metrics = {x.candidate_id for x in current_scope.semantic_refs if x.target_kind in metric_kinds}
        new_metrics = {x.candidate_id for x in mutation.target_semantic_refs if x.target_kind in metric_kinds}
        if (old_refs-old_metrics)!=(new_refs-new_metrics) or old_metrics==new_metrics or old_times!=new_times or old_periods!=new_periods:
            raise ValueError("CHANGE_METRIC must only change metrics")
    elif mutation.kind == ScopeMutationKind.CHANGE_BREAKDOWN:
        old_dims = {x.candidate_id for x in current_scope.semantic_refs if x.target_kind == SemanticTargetKind.DIMENSION}
        new_dims = {x.candidate_id for x in mutation.target_semantic_refs if x.target_kind == SemanticTargetKind.DIMENSION}
        if (old_refs-old_dims)!=(new_refs-new_dims) or old_dims==new_dims or old_times!=new_times or old_periods!=new_periods:
            raise ValueError("CHANGE_BREAKDOWN must only change dimensions")
    next_ordinal = current_scope.scope_version.ordinal + 1
    next_scope = ResearchScope(
        semantic_refs=mutation.target_semantic_refs,
        time_surfaces=mutation.target_time_surfaces,
        periods=mutation.target_periods,
        temporal_dimension_ids=mutation.target_temporal_dimension_ids,
        native_verification_bindings=(
            mutation.target_native_verification_bindings
        ),
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
