"""Independent 13-dimension semantic saturation model for Brain V2.1.

This module is test-only.  It deliberately models semantic combinations instead
of benchmark prompts, provider wording, or runtime routing heuristics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations, product
from typing import Iterable

from .model import (
    AdaptiveSpec,
    CompletionSpec,
    EntityCardinality,
    GoalKind,
    PeriodStructure,
    RankingBasis,
    ResultDependencyDisposition,
    completion_allows_presentation,
    legal_next_test,
    ranking_basis_is_coherent,
    result_dependency_disposition,
)


class MetricCardinality(StrEnum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"


class PeriodRole(StrEnum):
    NONE = "NONE"
    MATERIAL_WINDOW = "MATERIAL_WINDOW"
    BASELINE = "BASELINE"
    COMPARISON = "COMPARISON"
    EFFECT = "EFFECT"
    EVIDENCE = "EVIDENCE"


class ComparisonType(StrEnum):
    NONE = "NONE"
    PERIOD = "PERIOD"
    ENTITY = "ENTITY"
    METRIC = "METRIC"


class RankingDirection(StrEnum):
    NONE = "NONE"
    ASC = "ASC"
    DESC = "DESC"


class TopK(StrEnum):
    NONE = "NONE"
    ONE = "ONE"
    FIVE = "FIVE"


class BreakoutKind(StrEnum):
    NONE = "NONE"
    ENTITY = "ENTITY"
    TEMPORAL = "TEMPORAL"
    MULTI = "MULTI"


class ResultDependencyKind(StrEnum):
    NONE = "NONE"
    VERIFIED_PARENT = "VERIFIED_PARENT"
    UNRESOLVED_PARENT = "UNRESOLVED_PARENT"


class ScopeMutationKind(StrEnum):
    NONE = "NONE"
    LOCAL_SET = "LOCAL_SET"
    LOCAL_CLEAR = "LOCAL_CLEAR"
    MULTI_FACET = "MULTI_FACET"


class AdaptiveDecisionKind(StrEnum):
    NONE = "NONE"
    STOP = "STOP"
    NEXT_TEST = "NEXT_TEST"


class PresentationRequirement(StrEnum):
    NONE = "NONE"
    ANSWER = "ANSWER"
    TABLE = "TABLE"
    REPORT = "REPORT"


@dataclass(frozen=True)
class SaturationCase:
    intent: GoalKind
    metric_cardinality: MetricCardinality
    entity_cardinality: EntityCardinality
    period_role: PeriodRole
    comparison_type: ComparisonType
    ranking_basis: RankingBasis
    ranking_direction: RankingDirection
    top_k: TopK
    breakout: BreakoutKind
    result_dependency: ResultDependencyKind
    scope_mutation: ScopeMutationKind
    adaptive_decision: AdaptiveDecisionKind
    presentation_requirement: PresentationRequirement


SATURATION_DIMENSIONS = (
    ("intent", tuple(GoalKind)),
    ("metric_cardinality", tuple(MetricCardinality)),
    ("entity_cardinality", tuple(EntityCardinality)),
    ("period_role", tuple(PeriodRole)),
    ("comparison_type", tuple(ComparisonType)),
    ("ranking_basis", tuple(RankingBasis)),
    ("ranking_direction", tuple(RankingDirection)),
    ("top_k", tuple(TopK)),
    ("breakout", tuple(BreakoutKind)),
    ("result_dependency", tuple(ResultDependencyKind)),
    ("scope_mutation", tuple(ScopeMutationKind)),
    ("adaptive_decision", tuple(AdaptiveDecisionKind)),
    ("presentation_requirement", tuple(PresentationRequirement)),
)


def saturation_dimension_values() -> dict[str, tuple[StrEnum, ...]]:
    return {name: values for name, values in SATURATION_DIMENSIONS}


def _defaults() -> dict[str, StrEnum]:
    return {name: values[0] for name, values in SATURATION_DIMENSIONS}


def saturation_pairwise_matrix() -> tuple[SaturationCase, ...]:
    """Finite deterministic pair-complete challenge matrix.

    This intentionally optimizes for semantic pair coverage, not minimal row
    count.  Every value pair for every pair of dimensions receives at least one
    concrete row while all unrelated dimensions stay at deterministic defaults.
    """

    rows: dict[SaturationCase, None] = {}
    dims = tuple(SATURATION_DIMENSIONS)
    for (left_name, left_values), (right_name, right_values) in combinations(dims, 2):
        for left, right in product(left_values, right_values):
            payload = _defaults()
            payload[left_name] = left
            payload[right_name] = right
            rows[SaturationCase(**payload)] = None
    return tuple(rows)


def saturation_pair_coverage(
    cases: Iterable[SaturationCase],
) -> dict[str, tuple[tuple[str, str], ...]]:
    dimensions = tuple(name for name, _ in SATURATION_DIMENSIONS)
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
    return {key: tuple(sorted(values)) for key, values in sorted(output.items())}


def expected_pair_value_counts() -> dict[str, int]:
    return {
        f"{left_name}×{right_name}": len(left_values) * len(right_values)
        for (left_name, left_values), (right_name, right_values)
        in combinations(SATURATION_DIMENSIONS, 2)
    }


def metric_count(case: SaturationCase) -> int:
    return {
        MetricCardinality.ONE: 1,
        MetricCardinality.TWO: 2,
        MetricCardinality.THREE: 3,
    }[case.metric_cardinality]


def top_k_value(case: SaturationCase) -> int | None:
    return {
        TopK.NONE: None,
        TopK.ONE: 1,
        TopK.FIVE: 5,
    }[case.top_k]


def ranking_period_structure(case: SaturationCase) -> PeriodStructure:
    if case.comparison_type == ComparisonType.PERIOD:
        return PeriodStructure.BASELINE_CANDIDATE
    if case.period_role != PeriodRole.NONE:
        return PeriodStructure.SINGLE_WINDOW
    return PeriodStructure.NONE


@dataclass(frozen=True)
class SaturationOutcome:
    ranking_coherent: bool
    dependency_disposition: ResultDependencyDisposition | None
    adaptive_legal: bool
    presentation_callable: bool
    new_family: bool = False


def classify_saturation_case(case: SaturationCase) -> SaturationOutcome:
    """Project one combination onto independent generic laws.

    The output contains only known semantic dispositions.  If a production
    probe later finds behavior outside these laws, that is a new semantic
    family rather than a reason to add a case-specific branch.
    """

    ranking_coherent = ranking_basis_is_coherent(
        basis=case.ranking_basis,
        period=ranking_period_structure(case),
    )

    dependency = None
    if case.result_dependency != ResultDependencyKind.NONE:
        parent_verified = case.result_dependency == ResultDependencyKind.VERIFIED_PARENT
        dependency = result_dependency_disposition(
            parent_verified=parent_verified,
            selected_value_count=1 if parent_verified else 0,
            scope_version_unchanged=case.scope_mutation == ScopeMutationKind.NONE,
        )

    adaptive = AdaptiveSpec(
        unresolved_discrimination=case.adaptive_decision == AdaptiveDecisionKind.NEXT_TEST,
        preserves_scope=case.scope_mutation == ScopeMutationKind.NONE,
        material_fingerprint_changes=case.adaptive_decision == AdaptiveDecisionKind.NEXT_TEST,
        executable_by_existing_metabot_path=True,
        produces_newer_evidence_on_success=True,
        duplicate_material=False,
    )
    adaptive_legal = legal_next_test(adaptive)

    required = frozenset({"goal.g1"})
    terminal = (
        required
        if case.adaptive_decision != AdaptiveDecisionKind.NEXT_TEST
        else frozenset()
    )
    presentation_callable = completion_allows_presentation(
        CompletionSpec(
            required_owner_ids=required,
            terminal_owner_ids=terminal,
            presentation_requested=(
                case.presentation_requirement != PresentationRequirement.NONE
            ),
        )
    )
    return SaturationOutcome(
        ranking_coherent=ranking_coherent,
        dependency_disposition=dependency,
        adaptive_legal=adaptive_legal,
        presentation_callable=presentation_callable,
    )
