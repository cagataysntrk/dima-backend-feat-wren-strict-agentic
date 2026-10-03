"""Hypothesis strategies for independent semantic-law testing."""
from __future__ import annotations

from hypothesis import strategies as st

from .model import (
    AdaptiveSpec,
    AdmissionSpec,
    EntityCardinality,
    GoalKind,
    MaterialShape,
    PeriodStructure,
    PresentationKind,
    RankingKind,
    ReferencePatch,
    ReferenceScope,
    SemanticCase,
)


_SYMBOLIC_METRICS = ("metric.m1", "metric.m2", "metric.m3")
_SYMBOLIC_ENTITIES = ("entity.e1", "entity.e2")
_SYMBOLIC_BREAKDOWNS = ("dimension.d1", "dimension.d2")
_SYMBOLIC_PERIODS = ("period.p1", "period.p2")


def semantic_cases():
    return st.builds(
        SemanticCase,
        goal=st.sampled_from(tuple(GoalKind)),
        period=st.sampled_from(tuple(PeriodStructure)),
        entity=st.sampled_from(tuple(EntityCardinality)),
        material=st.sampled_from(tuple(MaterialShape)),
        ranking=st.sampled_from(tuple(RankingKind)),
        presentation=st.sampled_from(tuple(PresentationKind)),
    )


def reference_scopes():
    return st.builds(
        ReferenceScope,
        entities=st.frozensets(st.sampled_from(_SYMBOLIC_ENTITIES), max_size=2),
        metrics=st.frozensets(
            st.sampled_from(_SYMBOLIC_METRICS), min_size=1, max_size=3
        ),
        breakdowns=st.frozensets(
            st.sampled_from(_SYMBOLIC_BREAKDOWNS), max_size=2
        ),
        periods=st.frozensets(st.sampled_from(_SYMBOLIC_PERIODS), max_size=2),
        version=st.integers(min_value=1, max_value=20),
    )


def reference_patches():
    def optional_set(values):
        return st.one_of(
            st.none(),
            st.frozensets(st.sampled_from(values), max_size=len(values)),
        )

    return st.builds(
        ReferencePatch,
        entities=optional_set(_SYMBOLIC_ENTITIES),
        metrics=optional_set(_SYMBOLIC_METRICS),
        breakdowns=optional_set(_SYMBOLIC_BREAKDOWNS),
        periods=optional_set(_SYMBOLIC_PERIODS),
    )


def admission_specs():
    universe = ("semantic.s1", "semantic.s2", "semantic.s3")

    @st.composite
    def _spec(draw):
        permitted = draw(
            st.frozensets(st.sampled_from(universe), min_size=1, max_size=3)
        )
        observed = draw(
            st.frozensets(
                st.sampled_from(tuple(sorted(permitted))),
                min_size=0,
                max_size=len(permitted),
            )
        )
        required = draw(
            st.frozensets(
                st.sampled_from(tuple(sorted(permitted))),
                min_size=0,
                max_size=len(permitted),
            )
        )
        return AdmissionSpec(
            required=required,
            observed=observed,
            permitted=permitted,
            tenant_matches=draw(st.booleans()),
            principal_matches=draw(st.booleans()),
            scope_version_matches=draw(st.booleans()),
            current=draw(st.booleans()),
        )

    return _spec()


def adaptive_specs():
    return st.builds(
        AdaptiveSpec,
        unresolved_discrimination=st.booleans(),
        preserves_scope=st.booleans(),
        material_fingerprint_changes=st.booleans(),
        executable_by_existing_metabot_path=st.booleans(),
        produces_newer_evidence_on_success=st.booleans(),
        duplicate_material=st.booleans(),
    )



def saturation_cases():
    from .saturation import (
        AdaptiveDecisionKind,
        BreakoutKind,
        ComparisonType,
        MetricCardinality,
        PeriodRole,
        PresentationRequirement,
        RankingDirection,
        ResultDependencyKind,
        SaturationCase,
        ScopeMutationKind,
        TopK,
    )
    from .model import RankingBasis

    return st.builds(
        SaturationCase,
        intent=st.sampled_from(tuple(GoalKind)),
        metric_cardinality=st.sampled_from(tuple(MetricCardinality)),
        entity_cardinality=st.sampled_from(tuple(EntityCardinality)),
        period_role=st.sampled_from(tuple(PeriodRole)),
        comparison_type=st.sampled_from(tuple(ComparisonType)),
        ranking_basis=st.sampled_from(tuple(RankingBasis)),
        ranking_direction=st.sampled_from(tuple(RankingDirection)),
        top_k=st.sampled_from(tuple(TopK)),
        breakout=st.sampled_from(tuple(BreakoutKind)),
        result_dependency=st.sampled_from(tuple(ResultDependencyKind)),
        scope_mutation=st.sampled_from(tuple(ScopeMutationKind)),
        adaptive_decision=st.sampled_from(tuple(AdaptiveDecisionKind)),
        presentation_requirement=st.sampled_from(tuple(PresentationRequirement)),
    )
