"""Typed current-scope projection for Brain V2 P19 cognition.

This module carries no epistemic or analytical authority. It projects the
already-resolved ResearchScope into a closed provider-facing packet so P19
cannot reconstruct current scope from historical objective prose.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.v3.research_contracts import (
    ResearchBrief,
    SemanticTargetKind,
)
from app.v3.research_scope_patch import scope_fingerprint


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P19EntityScope(Frozen):
    candidate_id: str = Field(min_length=1)
    dimension_name: str = Field(min_length=1)
    value: str = Field(min_length=1)


class P19PeriodScope(Frozen):
    time_dimension_candidate_id: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)
    role: str = Field(min_length=1)


class P19ScopeAuthority(Frozen):
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(min_length=1)
    scope_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    metric_refs: tuple[str, ...] = ()
    dimension_refs: tuple[str, ...] = ()
    entity_filters: tuple[P19EntityScope, ...] = ()
    periods: tuple[P19PeriodScope, ...] = ()


class P19ScopeContextError(RuntimeError):
    pass


def project_p19_scope_authority(
    *,
    brief: ResearchBrief,
    scope_lineage_id: str,
    expected_scope_fingerprint: str,
) -> P19ScopeAuthority:
    """Project one resolved scope and verify its fingerprint before cognition."""

    actual = scope_fingerprint(
        brief.scope,
        context_version=brief.context_version,
    )
    if actual != expected_scope_fingerprint:
        raise P19ScopeContextError(
            "P19 current-scope projection fingerprint drift: "
            f"expected={expected_scope_fingerprint} observed={actual}"
        )

    metric_refs = tuple(
        sorted(
            item.candidate_id
            for item in brief.scope.semantic_refs
            if item.target_kind in {
                SemanticTargetKind.METRIC,
                SemanticTargetKind.KPI,
            }
        )
    )
    dimension_refs = tuple(
        sorted(
            item.candidate_id
            for item in brief.scope.semantic_refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        )
    )
    entity_filters = tuple(
        P19EntityScope(
            candidate_id=item.candidate_id,
            dimension_name=item.dimension_name or "",
            value=item.value or "",
        )
        for item in sorted(
            (
                item
                for item in brief.scope.semantic_refs
                if item.target_kind == SemanticTargetKind.ENTITY_VALUE
            ),
            key=lambda value: value.candidate_id,
        )
    )
    periods = tuple(
        P19PeriodScope(
            time_dimension_candidate_id=item.time_dimension_candidate_id,
            start=item.start,
            end=item.end,
            role=item.role.value,
        )
        for item in sorted(
            brief.scope.periods,
            key=lambda value: (
                value.time_dimension_candidate_id,
                value.start,
                value.end,
                value.role.value,
            ),
        )
    )
    return P19ScopeAuthority(
        scope_lineage_id=scope_lineage_id,
        scope_version_id=brief.scope.scope_version.version_id,
        scope_fingerprint=expected_scope_fingerprint,
        metric_refs=metric_refs,
        dimension_refs=dimension_refs,
        entity_filters=entity_filters,
        periods=periods,
    )
