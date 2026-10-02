"""Small independent semantic reference model for Brain V2.1 tests.

This module deliberately models laws, not Dima's runtime implementation.
Production code must never import from backend/tests/semantic_spec.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from itertools import product
from typing import FrozenSet, Iterable


class GoalKind(StrEnum):
    DIRECT = "DIRECT"
    BREAKDOWN = "BREAKDOWN"
    RANKING = "RANKING"
    COMPARE = "COMPARE"
    RELATIONSHIP = "RELATIONSHIP"
    ROOT_CAUSE = "ROOT_CAUSE"
    REPORT = "REPORT"


class PeriodStructure(StrEnum):
    NONE = "NONE"
    SINGLE_WINDOW = "SINGLE_WINDOW"
    BASELINE_CANDIDATE = "BASELINE_CANDIDATE"
    EVIDENCE_WINDOW = "EVIDENCE_WINDOW"
    EFFECT_PERIOD = "EFFECT_PERIOD"


class EntityCardinality(StrEnum):
    NONE = "NONE"
    ONE = "ONE"
    MULTIPLE = "MULTIPLE"


class MaterialShape(StrEnum):
    ONE_METRIC = "ONE_METRIC"
    MULTI_METRIC = "MULTI_METRIC"
    METRIC_PLUS_BREAKOUT = "METRIC_PLUS_BREAKOUT"
    COMPARATIVE = "COMPARATIVE"


class RankingKind(StrEnum):
    NONE = "NONE"
    ASC = "ASC"
    DESC = "DESC"
    TOP_K = "TOP_K"


class MutationKind(StrEnum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"
    NARROW = "NARROW"
    EXPAND = "EXPAND"
    CHANGE_PERIOD = "CHANGE_PERIOD"
    CHANGE_METRIC = "CHANGE_METRIC"
    CHANGE_BREAKDOWN = "CHANGE_BREAKDOWN"
    RESET = "RESET"


class PresentationKind(StrEnum):
    NONE = "NONE"
    ANSWER = "ANSWER"
    REPORT = "REPORT"


class TerminalDisposition(StrEnum):
    FULFILLED = "FULFILLED"
    LIMITED = "LIMITED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class SemanticCase:
    goal: GoalKind
    period: PeriodStructure
    entity: EntityCardinality
    material: MaterialShape
    ranking: RankingKind
    presentation: PresentationKind


@dataclass(frozen=True)
class ReferenceScope:
    """Symbolic user scope; identifiers intentionally carry no benchmark vocabulary."""

    entities: FrozenSet[str] = frozenset()
    metrics: FrozenSet[str] = frozenset()
    breakdowns: FrozenSet[str] = frozenset()
    periods: FrozenSet[str] = frozenset()
    version: int = 1


@dataclass(frozen=True)
class ReferencePatch:
    """Independent partial-update law.

    None means the facet is absent and therefore unchanged. A present empty set is
    an explicit removal/clear. A present non-empty set is an explicit replacement.
    This intentionally does not mirror Dima's ScopePatchOperation DTO.
    """

    entities: FrozenSet[str] | None = None
    metrics: FrozenSet[str] | None = None
    breakdowns: FrozenSet[str] | None = None
    periods: FrozenSet[str] | None = None


def apply_reference_patch(scope: ReferenceScope, patch: ReferencePatch) -> ReferenceScope:
    updates = {}
    for name in ("entities", "metrics", "breakdowns", "periods"):
        value = getattr(patch, name)
        if value is not None:
            updates[name] = value
    if not updates:
        return scope
    candidate = replace(scope, **updates)
    materially_changed = any(
        getattr(candidate, name) != getattr(scope, name)
        for name in ("entities", "metrics", "breakdowns", "periods")
    )
    if not materially_changed:
        return scope
    return replace(candidate, version=scope.version + 1)


def patches_commute(
    scope: ReferenceScope,
    left: ReferencePatch,
    right: ReferencePatch,
) -> bool:
    """Independent-facet patch operations must commute."""

    left_facets = {
        name
        for name in ("entities", "metrics", "breakdowns", "periods")
        if getattr(left, name) is not None
    }
    right_facets = {
        name
        for name in ("entities", "metrics", "breakdowns", "periods")
        if getattr(right, name) is not None
    }
    if left_facets & right_facets:
        return False
    return apply_reference_patch(
        apply_reference_patch(scope, left), right
    ) == apply_reference_patch(
        apply_reference_patch(scope, right), left
    )


@dataclass(frozen=True)
class AdmissionSpec:
    required: FrozenSet[str]
    observed: FrozenSet[str]
    permitted: FrozenSet[str]
    tenant_matches: bool = True
    principal_matches: bool = True
    scope_version_matches: bool = True
    current: bool = True


def semantic_admission_allowed(spec: AdmissionSpec) -> bool:
    """Law 2: semantic compatibility plus exact security/currentness identity."""

    return (
        spec.required.issubset(spec.observed)
        and spec.observed.issubset(spec.permitted)
        and spec.tenant_matches
        and spec.principal_matches
        and spec.scope_version_matches
        and spec.current
    )


@dataclass(frozen=True)
class CompletionSpec:
    required_owner_ids: FrozenSet[str]
    terminal_owner_ids: FrozenSet[str]
    presentation_requested: bool


def completion_allows_presentation(spec: CompletionSpec) -> bool:
    """Law 4: presentation is callable from terminal USER_MUST owners."""

    return (
        spec.presentation_requested
        and spec.required_owner_ids.issubset(spec.terminal_owner_ids)
    )


@dataclass(frozen=True)
class AdaptiveSpec:
    unresolved_discrimination: bool
    preserves_scope: bool
    material_fingerprint_changes: bool
    executable_by_existing_metabot_path: bool
    produces_newer_evidence_on_success: bool
    duplicate_material: bool = False


def legal_next_test(spec: AdaptiveSpec) -> bool:
    """Law 5: a NextTest is legal only when it can add governed information."""

    return (
        spec.unresolved_discrimination
        and spec.preserves_scope
        and spec.material_fingerprint_changes
        and spec.executable_by_existing_metabot_path
        and spec.produces_newer_evidence_on_success
        and not spec.duplicate_material
    )


class ChangeTemporalDisposition(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    EXPLICIT_BOUNDED = "EXPLICIT_BOUNDED"
    OBSERVE_GOVERNED_TIME = "OBSERVE_GOVERNED_TIME"
    CLARIFY_TIME_AXIS = "CLARIFY_TIME_AXIS"
    BLOCKED_NO_TIME_AXIS = "BLOCKED_NO_TIME_AXIS"


def reference_change_temporal_disposition(
    *,
    effect_is_change: bool,
    explicit_period_count: int,
    governed_temporal_dimension_count: int,
) -> ChangeTemporalDisposition:
    """Law 6: CHANGE intent is not identical to explicit period authority.

    Explicit periods remain exact user scope. Without an explicit period, one
    uniquely governed time axis is enough to request temporal observation
    material without inventing a calendar filter. Ambiguous or absent axes are
    typed terminals, never incidental representation exceptions.
    """

    if not effect_is_change:
        return ChangeTemporalDisposition.NOT_APPLICABLE
    if explicit_period_count > 0:
        return ChangeTemporalDisposition.EXPLICIT_BOUNDED
    if governed_temporal_dimension_count == 1:
        return ChangeTemporalDisposition.OBSERVE_GOVERNED_TIME
    if governed_temporal_dimension_count > 1:
        return ChangeTemporalDisposition.CLARIFY_TIME_AXIS
    return ChangeTemporalDisposition.BLOCKED_NO_TIME_AXIS


@dataclass(frozen=True)
class TemporalRoleSpec:
    material_window: str | None = None
    baseline_period: str | None = None
    comparison_period: str | None = None
    effect_period: str | None = None
    evidence_window: str | None = None


def temporal_roles_are_distinct(spec: TemporalRoleSpec) -> bool:
    """Law 6: role identity is preserved even when some interval values coincide."""

    populated = {
        role: value
        for role, value in (
            ("material_window", spec.material_window),
            ("baseline_period", spec.baseline_period),
            ("comparison_period", spec.comparison_period),
            ("effect_period", spec.effect_period),
            ("evidence_window", spec.evidence_window),
        )
        if value is not None
    }
    # Distinctness here means no role was discarded; interval equality is legal.
    return len(populated) == sum(
        value is not None
        for value in (
            spec.material_window,
            spec.baseline_period,
            spec.comparison_period,
            spec.effect_period,
            spec.evidence_window,
        )
    )


def semantic_matrix() -> tuple[SemanticCase, ...]:
    """Finite deterministic matrix used for coverage accounting.

    The full cross-product is intentionally small enough to enumerate in CI.
    """

    return tuple(
        SemanticCase(*values)
        for values in product(
            GoalKind,
            PeriodStructure,
            EntityCardinality,
            MaterialShape,
            RankingKind,
            PresentationKind,
        )
    )


def pair_coverage(
    cases: Iterable[SemanticCase],
) -> dict[str, tuple[tuple[str, str], ...]]:
    dimensions = (
        "goal",
        "period",
        "entity",
        "material",
        "ranking",
        "presentation",
    )
    output: dict[str, set[tuple[str, str]]] = {}
    for left_index, left in enumerate(dimensions):
        for right in dimensions[left_index + 1 :]:
            key = f"{left}×{right}"
            values = output.setdefault(key, set())
            for case in cases:
                values.add(
                    (
                        str(getattr(case, left).value),
                        str(getattr(case, right).value),
                    )
                )
    return {
        key: tuple(sorted(values))
        for key, values in sorted(output.items())
    }
