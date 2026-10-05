"""Versioned analytical anti-corruption boundary for Brain V2.1.

The DTOs in this module are projections, never a second source of business
truth. ResearchBrief/ResearchQuestion/ResearchScope own accepted meaning;
Metabase/Metabot own analytical realization. Dima consumes only stable semantic
execution facts and never reverse-engineers MBQL/query topology here.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import (
    AnalyticalEvidenceSynthesisRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalRequestObservation,
    AnalyticalRankingInvariant,
)
from app.v3.research_contracts import (
    PresentationKind,
    RankingBasis,
    ResearchBrief,
    ResearchGoalKind,
    ResearchQuestion,
    ResearchScope,
    SemanticTargetKind,
    TemporalRole,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AnalyticalOperation(StrEnum):
    OBSERVE = "OBSERVE"
    BREAKDOWN = "BREAKDOWN"
    COMPARE = "COMPARE"
    RANK = "RANK"
    SELECT = "SELECT"
    DRILLDOWN = "DRILLDOWN"
    RELATE = "RELATE"
    RCA = "RCA"
    REPORT = "REPORT"
    SCOPE_PATCH = "SCOPE_PATCH"


class AnalyticalBoundaryError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class V1GrammarControl(StrEnum):
    """Control-only token in the Product grammar; never sent to Metabase."""

    NEXT_TEST = "NEXT_TEST"


V1_ANALYTICAL_GRAMMAR_VERSION = "dima_analytical_grammar_v1"

_BASE_V1_COMPOSITIONS = frozenset(
    {
        (AnalyticalOperation.OBSERVE,),
        (AnalyticalOperation.OBSERVE, AnalyticalOperation.BREAKDOWN),
        # Existing certified direct surfaces remain legal. Closing V1 must not
        # regress a direct breakdown/ranking request merely because richer
        # compositions are also named.
        (AnalyticalOperation.BREAKDOWN,),
        (AnalyticalOperation.COMPARE,),
        (AnalyticalOperation.COMPARE, AnalyticalOperation.RANK),
        (
            AnalyticalOperation.COMPARE,
            AnalyticalOperation.RANK,
            AnalyticalOperation.SELECT,
            AnalyticalOperation.DRILLDOWN,
        ),
        (AnalyticalOperation.RANK,),
        (
            AnalyticalOperation.RANK,
            AnalyticalOperation.SELECT,
            AnalyticalOperation.DRILLDOWN,
        ),
        (AnalyticalOperation.RELATE,),
        (AnalyticalOperation.RCA,),
        (
            AnalyticalOperation.RCA,
            V1GrammarControl.NEXT_TEST,
            AnalyticalOperation.RCA,
        ),
        (AnalyticalOperation.REPORT,),
    }
)

# A typed scope mutation is a wrapper over an already-supported operation; it
# never manufactures a new analytical primitive.
V1_LEGAL_COMPOSITIONS = frozenset(
    {
        *_BASE_V1_COMPOSITIONS,
        *{
            (AnalyticalOperation.SCOPE_PATCH, *composition)
            for composition in _BASE_V1_COMPOSITIONS
        },
    }
)


def _grammar_token(
    value: AnalyticalOperation | V1GrammarControl | str,
) -> AnalyticalOperation | V1GrammarControl:
    if isinstance(value, (AnalyticalOperation, V1GrammarControl)):
        return value
    try:
        return AnalyticalOperation(value)
    except ValueError:
        try:
            return V1GrammarControl(value)
        except ValueError as exc:
            raise AnalyticalBoundaryError(
                "ANALYTICAL_V1_GRAMMAR_TOKEN_UNSUPPORTED",
                str(value),
            ) from exc


def assert_v1_analytical_composition(
    steps: tuple[AnalyticalOperation | V1GrammarControl | str, ...],
    *,
    complete: bool = True,
) -> tuple[AnalyticalOperation | V1GrammarControl, ...]:
    """Validate only the closed V1 operation graph, never analytical HOW."""

    normalized = tuple(_grammar_token(item) for item in steps)
    if not normalized:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_GRAMMAR_EMPTY",
            "V1 analytical composition cannot be empty",
        )
    if complete:
        if normalized not in V1_LEGAL_COMPOSITIONS:
            raise AnalyticalBoundaryError(
                "ANALYTICAL_V1_COMPOSITION_UNSUPPORTED",
                " -> ".join(item.value for item in normalized),
            )
        return normalized

    if not any(
        candidate[: len(normalized)] == normalized
        for candidate in V1_LEGAL_COMPOSITIONS
    ):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_TRANSITION_UNSUPPORTED",
            " -> ".join(item.value for item in normalized),
        )
    return normalized


def legal_v1_next_steps(
    prefix: tuple[AnalyticalOperation | V1GrammarControl | str, ...],
) -> frozenset[AnalyticalOperation | V1GrammarControl]:
    normalized = tuple(_grammar_token(item) for item in prefix)
    if normalized and not any(
        candidate[: len(normalized)] == normalized
        for candidate in V1_LEGAL_COMPOSITIONS
    ):
        return frozenset()
    return frozenset(
        candidate[len(normalized)]
        for candidate in V1_LEGAL_COMPOSITIONS
        if (
            len(candidate) > len(normalized)
            and candidate[: len(normalized)] == normalized
        )
    )


class AnalyticalFilterV1(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    dimension_semantic_id: str = Field(min_length=1)
    value: str


class AnalyticalPeriodV1(FrozenModel):
    role: TemporalRole
    time_dimension_semantic_id: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)


class AnalyticalRankingV1(FrozenModel):
    kind: Literal["native_metric", "evidence_synthesis"]
    metric: str | None = None
    basis: RankingBasis | None = None
    direction: Literal["asc", "desc", "unspecified"]
    top_k: int | None = Field(default=None, ge=1, le=1000)


class AnalyticalDependencyV1(FrozenModel):
    source_intent_id: str = Field(min_length=1)
    source_selection_id: str | None = Field(default=None, min_length=1)


class AnalyticalIntentV1(FrozenModel):
    """Dima -> Metabase WHAT-only contract."""

    schema_version: Literal["dima_analytical_intent_v1"] = "dima_analytical_intent_v1"
    intent_id: str = Field(min_length=1)
    operation: AnalyticalOperation
    metrics: tuple[str, ...] = Field(min_length=1)
    dimensions: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterV1, ...] = ()
    temporal_periods: tuple[AnalyticalPeriodV1, ...] = ()
    temporal_observation_dimension: str | None = None
    ranking: AnalyticalRankingV1 | None = None
    dependency: AnalyticalDependencyV1 | None = None
    row_grain: tuple[str, ...] = ()
    allowed_semantic_ids: tuple[str, ...] = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    scope_fingerprint: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    tenant_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    expected_resource_entity_ids: tuple[str, ...] = ()
    currentness_token: str = Field(min_length=1)
    security_fingerprint: str = Field(min_length=1)


class AnalyticalEngineIdentityV1(FrozenModel):
    repository: str = Field(min_length=1)
    revision_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    runtime_tag: str = Field(min_length=1)
    image_digest: str | None = None


class AnalyticalManifestDataV1(FrozenModel):
    columns: tuple[Any, ...] = ()
    rows: tuple[Any, ...] = ()


class AnalyticalExecutionManifestV1(FrozenModel):
    """Metabase -> Dima stable execution facts; never a physical query plan."""

    schema_version: Literal["dima_analytical_execution_manifest_v1"] = (
        "dima_analytical_execution_manifest_v1"
    )
    execution_id: str = Field(min_length=1)
    fulfilled_intent_ids: tuple[str, ...] = Field(min_length=1)
    metrics: tuple[str, ...] = Field(min_length=1)
    dimensions: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterV1, ...] = ()
    temporal_periods: tuple[AnalyticalPeriodV1, ...] = ()
    temporal_observation_dimension: str | None = None
    ranking: AnalyticalRankingV1 | None = None
    row_grain: tuple[str, ...] = ()
    result_dependency: AnalyticalDependencyV1 | None = None
    semantic_context_version: str = Field(min_length=1)
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    scope_fingerprint: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    tenant_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    resource_entity_ids: tuple[str, ...] = ()
    currentness_token: str = Field(min_length=1)
    security_fingerprint: str = Field(min_length=1)
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    result_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    engine_identity: AnalyticalEngineIdentityV1
    data: AnalyticalManifestDataV1
    metadata: dict[str, Any] = Field(default_factory=dict)


_OPERATION_BY_GOAL = {
    ResearchGoalKind.COMPARISON: AnalyticalOperation.COMPARE,
    ResearchGoalKind.RELATIONSHIP: AnalyticalOperation.RELATE,
    ResearchGoalKind.PERFORMANCE: AnalyticalOperation.OBSERVE,
    ResearchGoalKind.TREND: AnalyticalOperation.OBSERVE,
    ResearchGoalKind.BREAKDOWN: AnalyticalOperation.BREAKDOWN,
    ResearchGoalKind.RANKING: AnalyticalOperation.RANK,
    ResearchGoalKind.ROOT_CAUSE: AnalyticalOperation.RCA,
}


def _question_metric_ids(question: ResearchQuestion) -> frozenset[str]:
    return frozenset(
        item.candidate_id
        for item in (*question.subject_refs, *question.related_refs)
        if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
    )


def validate_v1_research_brief(
    brief: ResearchBrief,
    *,
    scope_patch: bool = False,
) -> tuple[tuple[AnalyticalOperation | V1GrammarControl, ...], ...]:
    """Project one accepted typed brief onto the closed V1 composition grammar.

    This validates composition only. ResearchBrief/ResearchScope remain semantic
    authority and Metabase/Metabot remain the owner of query realization.
    """

    by_id = {item.goal_id: item for item in brief.questions}
    projected: list[tuple[AnalyticalOperation | V1GrammarControl, ...]] = []

    for question in brief.questions:
        operation = _OPERATION_BY_GOAL.get(question.kind)
        if operation is None:
            raise AnalyticalBoundaryError(
                "ANALYTICAL_V1_OPERATION_UNSUPPORTED",
                question.kind.value,
            )

        dependency = question.result_dependency
        if dependency is None:
            chain: tuple[AnalyticalOperation | V1GrammarControl, ...] = (
                operation,
            )
        else:
            parent = by_id.get(dependency.source_goal_id)
            if parent is None or parent.ranking is None:
                raise AnalyticalBoundaryError(
                    "ANALYTICAL_V1_DEPENDENCY_SOURCE_UNSUPPORTED",
                    dependency.source_goal_id,
                )
            if question.kind != ResearchGoalKind.BREAKDOWN:
                raise AnalyticalBoundaryError(
                    "ANALYTICAL_V1_DEPENDENT_OPERATION_UNSUPPORTED",
                    question.kind.value,
                )

            chain = (
                AnalyticalOperation.RANK,
                AnalyticalOperation.SELECT,
                AnalyticalOperation.DRILLDOWN,
            )
            ranking_metrics = _question_metric_ids(parent)
            if parent.ranking.measure_semantic_id is not None:
                ranking_metrics = frozenset(
                    {parent.ranking.measure_semantic_id}
                )
            comparison_present = any(
                candidate.kind == ResearchGoalKind.COMPARISON
                and bool(ranking_metrics & _question_metric_ids(candidate))
                for candidate in brief.questions
            )
            if comparison_present:
                chain = (AnalyticalOperation.COMPARE, *chain)

        if scope_patch:
            chain = (AnalyticalOperation.SCOPE_PATCH, *chain)
        projected.append(
            assert_v1_analytical_composition(chain)
        )

    if any(
        item.kind == PresentationKind.REPORT
        for item in brief.deliverables
    ):
        report_chain: tuple[
            AnalyticalOperation | V1GrammarControl, ...
        ] = (AnalyticalOperation.REPORT,)
        if scope_patch:
            report_chain = (AnalyticalOperation.SCOPE_PATCH, *report_chain)
        projected.append(
            assert_v1_analytical_composition(report_chain)
        )

    return tuple(projected)


def _ranking_from_contract(
    value: AnalyticalRankingInvariant
    | AnalyticalEvidenceSynthesisRankingInvariant
    | None,
) -> AnalyticalRankingV1 | None:
    if value is None:
        return None
    if isinstance(value, AnalyticalRankingInvariant):
        return AnalyticalRankingV1(
            kind="native_metric",
            metric=value.measure,
            basis=value.basis,
            direction=value.direction,
            top_k=value.limit,
        )
    return AnalyticalRankingV1(
        kind="evidence_synthesis",
        metric=None,
        basis=None,
        direction=value.direction,
        top_k=value.limit,
    )


def _filters_from_contract(
    contract: AnalyticalRequestContract | AnalyticalRequestObservation,
) -> tuple[AnalyticalFilterV1, ...]:
    return tuple(
        AnalyticalFilterV1(
            semantic_ref=item.semantic_ref,
            dimension_semantic_id=item.source_candidate_id,
            value=item.value,
        )
        for item in contract.filters
    )


def _periods_for_contract(
    *,
    scope: ResearchScope,
    contract: AnalyticalRequestContract,
) -> tuple[AnalyticalPeriodV1, ...]:
    """Project accepted period authority without interpreting wording or tuple order."""

    if contract.temporal_change_frame is not None:
        frame = contract.temporal_change_frame
        if frame.baseline_period is not None and frame.comparison_period is not None:
            return (
                AnalyticalPeriodV1(
                    role=TemporalRole.BASELINE_PERIOD,
                    time_dimension_semantic_id=frame.baseline_period.time_dimension,
                    start=frame.baseline_period.start,
                    end=frame.baseline_period.end or "",
                ),
                AnalyticalPeriodV1(
                    role=TemporalRole.COMPARISON_PERIOD,
                    time_dimension_semantic_id=frame.comparison_period.time_dimension,
                    start=frame.comparison_period.start,
                    end=frame.comparison_period.end or "",
                ),
            )
        if frame.span_period is not None:
            return (
                AnalyticalPeriodV1(
                    role=TemporalRole.MATERIAL_WINDOW,
                    time_dimension_semantic_id=frame.span_period.time_dimension,
                    start=frame.span_period.start,
                    end=frame.span_period.end or "",
                ),
            )

    if contract.comparison is not None:
        accepted = tuple(
            item
            for item in scope.periods
            if item.role in {
                TemporalRole.BASELINE_PERIOD,
                TemporalRole.COMPARISON_PERIOD,
            }
        )
        if len(accepted) == 2:
            return tuple(
                AnalyticalPeriodV1(
                    role=item.role,
                    time_dimension_semantic_id=item.time_dimension_candidate_id,
                    start=item.start,
                    end=item.end,
                )
                for item in accepted
            )

    if contract.period is not None:
        exact = tuple(
            item
            for item in scope.periods
            if (
                item.time_dimension_candidate_id == contract.period.time_dimension
                and item.start >= contract.period.start
                and contract.period.end is not None
                and item.end <= contract.period.end
            )
        )
        if exact:
            return tuple(
                AnalyticalPeriodV1(
                    role=item.role,
                    time_dimension_semantic_id=item.time_dimension_candidate_id,
                    start=item.start,
                    end=item.end,
                )
                for item in exact
            )

    return ()


def project_analytical_intent_v1(
    *,
    question: ResearchQuestion,
    scope: ResearchScope,
    contract: AnalyticalRequestContract,
    tenant_id: str,
    principal_id: str,
    currentness_token: str,
    security_fingerprint: str,
    expected_resource_entity_ids: tuple[str, ...] = (),
) -> AnalyticalIntentV1:
    """Project existing Dima typed state into the V1 anti-corruption boundary."""

    operation = _OPERATION_BY_GOAL.get(question.kind)
    if operation is None:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_OPERATION_UNSUPPORTED",
            question.kind.value,
        )
    allowed = tuple(
        dict.fromkeys(item.candidate_id for item in scope.semantic_refs)
    )
    dependency = (
        AnalyticalDependencyV1(source_intent_id=question.result_dependency.source_goal_id)
        if question.result_dependency is not None
        else None
    )
    return AnalyticalIntentV1(
        intent_id=question.goal_id,
        operation=operation,
        metrics=contract.metric_refs,
        dimensions=contract.dimension_refs,
        filters=_filters_from_contract(contract),
        temporal_periods=_periods_for_contract(scope=scope, contract=contract),
        temporal_observation_dimension=(
            contract.temporal_observation.time_dimension
            if contract.temporal_observation is not None
            else None
        ),
        ranking=_ranking_from_contract(contract.ranking),
        dependency=dependency,
        row_grain=tuple(dict.fromkeys((*contract.dimension_refs, *contract.grain_constraints))),
        allowed_semantic_ids=allowed,
        semantic_context_version=contract.semantic_context_version,
        scope_lineage_id=contract.scope_identity.lineage_id,
        scope_version_id=scope.scope_version.version_id,
        scope_fingerprint=contract.scope_fingerprint,
        tenant_id=tenant_id,
        principal_id=principal_id,
        expected_resource_entity_ids=expected_resource_entity_ids,
        currentness_token=currentness_token,
        security_fingerprint=security_fingerprint,
    )


def project_execution_manifest_v1(
    *,
    intent: AnalyticalIntentV1,
    observation: AnalyticalRequestObservation,
    execution_id: str,
    query_fingerprint: str,
    result_hash: str,
    engine_identity: AnalyticalEngineIdentityV1,
    data_columns: tuple[Any, ...],
    data_rows: tuple[Any, ...],
    resource_entity_ids: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> AnalyticalExecutionManifestV1:
    """Project an already-verified stable semantic observation; no MBQL inspection."""

    return AnalyticalExecutionManifestV1(
        execution_id=execution_id,
        fulfilled_intent_ids=(intent.intent_id,),
        metrics=observation.metric_refs,
        dimensions=observation.dimension_refs,
        filters=_filters_from_contract(observation),
        temporal_periods=intent.temporal_periods,
        temporal_observation_dimension=(
            observation.temporal_observation.time_dimension
            if observation.temporal_observation is not None
            else None
        ),
        ranking=_ranking_from_contract(observation.ranking),
        row_grain=tuple(
            dict.fromkeys((*observation.dimension_refs, *observation.grain_constraints))
        ),
        result_dependency=intent.dependency,
        semantic_context_version=intent.semantic_context_version,
        scope_lineage_id=observation.scope_identity.lineage_id,
        scope_version_id=observation.scope_identity.version_id,
        scope_fingerprint=intent.scope_fingerprint,
        tenant_id=intent.tenant_id,
        principal_id=intent.principal_id,
        resource_entity_ids=resource_entity_ids,
        currentness_token=intent.currentness_token,
        security_fingerprint=intent.security_fingerprint,
        query_fingerprint=query_fingerprint,
        result_hash=result_hash,
        engine_identity=engine_identity,
        data=AnalyticalManifestDataV1(columns=data_columns, rows=data_rows),
        metadata=metadata or {},
    )


def _filter_key(value: AnalyticalFilterV1) -> tuple[str, str, str]:
    return (value.semantic_ref, value.dimension_semantic_id, value.value)


def _period_key(value: AnalyticalPeriodV1) -> tuple[str, str, str, str]:
    return (
        value.role.value,
        value.time_dimension_semantic_id,
        value.start,
        value.end,
    )


def verify_analytical_fulfillment_v1(
    intent: AnalyticalIntentV1,
    manifest: AnalyticalExecutionManifestV1,
) -> None:
    """One fail-closed semantic admission law for the V1 boundary."""

    exact = (
        ("tenant", intent.tenant_id, manifest.tenant_id),
        ("principal", intent.principal_id, manifest.principal_id),
        ("semantic_context", intent.semantic_context_version, manifest.semantic_context_version),
        ("scope_lineage", intent.scope_lineage_id, manifest.scope_lineage_id),
        ("scope_version", intent.scope_version_id, manifest.scope_version_id),
        ("scope_fingerprint", intent.scope_fingerprint, manifest.scope_fingerprint),
        ("currentness", intent.currentness_token, manifest.currentness_token),
        ("security", intent.security_fingerprint, manifest.security_fingerprint),
    )
    for label, required, observed in exact:
        if required != observed:
            raise AnalyticalBoundaryError(
                "ANALYTICAL_V1_EXACT_CONTEXT_MISMATCH",
                f"{label}: expected={required!r} observed={observed!r}",
            )

    if intent.intent_id not in set(manifest.fulfilled_intent_ids):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_INTENT_NOT_FULFILLED",
            intent.intent_id,
        )
    if tuple(intent.expected_resource_entity_ids) != tuple(manifest.resource_entity_ids):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_RESOURCE_IDENTITY_MISMATCH",
            "execution resource identity differs from the accepted intent",
        )

    allowed = set(intent.allowed_semantic_ids)
    observed_semantic_ids = set(manifest.metrics) | set(manifest.dimensions)
    observed_semantic_ids |= {item.dimension_semantic_id for item in manifest.filters}
    foreign = observed_semantic_ids - allowed
    if foreign:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_FOREIGN_SEMANTIC_ID",
            ",".join(sorted(foreign)),
        )

    if not set(intent.metrics).issubset(manifest.metrics):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_METRIC_COVERAGE_MISMATCH",
            "required metrics are not fulfilled",
        )
    if not set(intent.dimensions).issubset(manifest.dimensions):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_DIMENSION_COVERAGE_MISMATCH",
            "required dimensions are not fulfilled",
        )

    required_filters = {_filter_key(item) for item in intent.filters}
    observed_filters = {_filter_key(item) for item in manifest.filters}
    if required_filters != observed_filters:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_FILTER_SCOPE_MISMATCH",
            "execution filters differ from accepted intent",
        )

    required_periods = {_period_key(item) for item in intent.temporal_periods}
    observed_periods = {_period_key(item) for item in manifest.temporal_periods}
    if required_periods != observed_periods:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_TEMPORAL_SCOPE_MISMATCH",
            "execution periods/roles differ from accepted intent",
        )
    if intent.temporal_observation_dimension != manifest.temporal_observation_dimension:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_TEMPORAL_OBSERVATION_MISMATCH",
            "governed temporal observation identity differs",
        )
    if intent.ranking != manifest.ranking:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_RANKING_MISMATCH",
            "ranking basis/metric/direction/top-k differs",
        )
    if not set(intent.row_grain).issubset(manifest.row_grain):
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_ROW_GRAIN_MISMATCH",
            "required row grain is not fulfilled",
        )
    if intent.dependency != manifest.result_dependency:
        raise AnalyticalBoundaryError(
            "ANALYTICAL_V1_DEPENDENCY_MISMATCH",
            "result dependency differs from accepted intent",
        )
