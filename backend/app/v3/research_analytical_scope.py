"""Shared accepted analytical-scope contract for P14/P17 native Research.

Authority remains the immutable accepted ResearchBrief. This module only projects
that authority into the existing AnalyticalRequestContract and checks one engine-
attested native occurrence before it can become governed Evidence.

No SQL/MBQL parser, query planner, fuzzy matcher or prompt classifier lives here.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalFilterInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalRequestObservation,
    AnalyticalScopeIdentity,
    NativeAnalyticalRequestObservation,
    assert_request_invariants,
)
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.research import ResearchSession
from app.v3.research_contracts import (
    PresentationKind,
    ResearchNativeVerificationBinding,
    ResearchQuestion,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchAnalyticalScopeError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class NativeFieldLocator(Frozen):
    field_id: int = Field(gt=0)
    table_id: int = Field(gt=0)
    table_name: str = Field(min_length=1)
    schema_name: str | None = None
    column_name: str = Field(min_length=1)


class NativeTableLocator(Frozen):
    table_id: int = Field(gt=0)
    table_name: str = Field(min_length=1)
    schema_name: str | None = None


def _question(session: ResearchSession, obligation_id: str) -> ResearchQuestion:
    brief = session.accepted_brief
    if brief is None:
        raise ResearchAnalyticalScopeError(
            "R1_ACCEPTED_BRIEF_REQUIRED",
            "native analytical scope requires the immutable accepted ResearchBrief",
        )
    item = next(
        (question for question in brief.questions if question.goal_id == obligation_id),
        None,
    )
    if item is None:
        raise ResearchAnalyticalScopeError(
            "R1_ANALYTICAL_OBLIGATION_UNKNOWN",
            obligation_id,
        )
    return item


def _unique_refs(values: tuple[ResearchSemanticRef, ...], kinds: set[SemanticTargetKind]):
    output: list[ResearchSemanticRef] = []
    seen: set[str] = set()
    for item in values:
        if item.target_kind in kinds and item.candidate_id not in seen:
            output.append(item)
            seen.add(item.candidate_id)
    return tuple(output)


def _period(value) -> AnalyticalPeriodInvariant:
    return AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension=value.time_dimension_candidate_id,
        start=value.start,
        end=value.end,
    )


def analytical_scope_contract(
    *,
    session: ResearchSession,
    obligation_id: str,
) -> AnalyticalRequestContract:
    """Project one accepted Research question into material request invariants."""

    brief = session.accepted_brief
    if brief is None:
        raise ResearchAnalyticalScopeError(
            "R1_ACCEPTED_BRIEF_REQUIRED",
            "Research session has no accepted ResearchBrief",
        )
    question = _question(session, obligation_id)
    question_refs = tuple((*question.subject_refs, *question.related_refs))
    metrics = _unique_refs(
        question_refs,
        {SemanticTargetKind.METRIC, SemanticTargetKind.KPI},
    )
    if not metrics:
        raise ResearchAnalyticalScopeError(
            "R1_METRIC_SCOPE_REQUIRED",
            "native analytical occurrence requires at least one accepted metric/KPI",
        )

    period_dimension_ids = {
        item.time_dimension_candidate_id for item in brief.scope.periods
    }
    dimensions = tuple(
        item
        for item in _unique_refs(
            question_refs,
            {SemanticTargetKind.DIMENSION},
        )
        if item.candidate_id not in period_dimension_ids
    )
    filters = _unique_refs(
        tuple(brief.scope.semantic_refs),
        {SemanticTargetKind.ENTITY_VALUE},
    )
    filter_invariants: list[AnalyticalFilterInvariant] = []
    for item in filters:
        if not item.dimension_name or item.value is None:
            raise ResearchAnalyticalScopeError(
                "R1_FILTER_BINDING_INCOMPLETE",
                item.candidate_id,
            )
        filter_invariants.append(
            AnalyticalFilterInvariant(
                semantic_ref=item.candidate_id,
                source_candidate_id=item.candidate_id,
                dimension_name=item.dimension_name,
                value=item.value,
            )
        )

    periods = tuple(brief.scope.periods)
    if brief.scope.time_surfaces and not periods:
        raise ResearchAnalyticalScopeError(
            "R1_TYPED_TIME_SCOPE_REQUIRED",
            "accepted textual time scope lacks exact typed period authority",
        )
    if len(periods) > 2:
        raise ResearchAnalyticalScopeError(
            "R1_TIME_SCOPE_TOO_COMPLEX",
            "initial R1 contract supports at most two explicit accepted periods",
        )

    period = None
    comparison = None
    if len(periods) == 1:
        period = _period(periods[0])
    elif len(periods) == 2:
        if question.comparisons:
            comparison = AnalyticalComparisonInvariant(
                mode="explicit_periods",
                reference_period=_period(periods[0]),
                base_period=_period(periods[1]),
            )
        else:
            # Two accepted periods without a comparison still define one bounded
            # material time window. No language interpretation occurs here.
            starts = sorted(item.start for item in periods)
            ends = sorted(item.end for item in periods)
            time_dims = {item.time_dimension_candidate_id for item in periods}
            if len(time_dims) != 1:
                raise ResearchAnalyticalScopeError(
                    "R1_TIME_DIMENSION_DRIFT",
                    "one analytical occurrence cannot span two time dimensions",
                )
            period = AnalyticalPeriodInvariant(
                kind="explicit_half_open_window",
                time_dimension=next(iter(time_dims)),
                start=starts[0],
                end=ends[-1],
            )

    ranking = None
    if question.ranking is not None:
        value = question.ranking
        if value.direction == "unspecified" or value.limit is None:
            raise ResearchAnalyticalScopeError(
                "R1_RANKING_BASIS_INCOMPLETE",
                "material ranking requires exact direction and limit",
            )
        if len(metrics) != 1:
            raise ResearchAnalyticalScopeError(
                "R1_RANKING_BASIS_AMBIGUOUS",
                "multi-metric ranking requires a separately typed ranking basis",
            )
        ranking = AnalyticalRankingInvariant(
            measure=metrics[0].candidate_id,
            direction=value.direction,
            limit=value.limit,
        )

    outputs = tuple(
        item.kind.value
        for item in brief.deliverables
        if item.kind != PresentationKind.NONE
    )
    return AnalyticalRequestContract(
        authority_id=session.authority_id,
        request_ref=f"{session.session_id}:{obligation_id}",
        semantic_context_version=session.context_version,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id=session.lineage_id,
            version_id=brief.scope.scope_version.version_id,
        ),
        metric_refs=tuple(item.candidate_id for item in metrics),
        dimension_refs=tuple(item.candidate_id for item in dimensions),
        filters=tuple(filter_invariants),
        period=period,
        comparison=comparison,
        ranking=ranking,
        grain_constraints=tuple(item.candidate_id for item in dimensions),
        requested_output_surfaces=tuple(dict.fromkeys(outputs)),
    )


def native_request_context(contract: AnalyticalRequestContract) -> dict[str, Any]:
    """Semantic-only context given to Metabot; physical verifier bindings stay out."""

    return {
        "dima_analytical_scope": contract.model_dump(mode="json"),
    }


def _refs(session: ResearchSession) -> dict[str, ResearchSemanticRef]:
    brief = session.accepted_brief
    assert brief is not None
    return {item.candidate_id: item for item in brief.scope.semantic_refs}


def _bindings(
    session: ResearchSession,
) -> dict[str, ResearchNativeVerificationBinding]:
    brief = session.accepted_brief
    assert brief is not None
    return {
        item.candidate_id: item
        for item in brief.scope.native_verification_bindings
    }


def _require_binding(
    bindings: Mapping[str, ResearchNativeVerificationBinding],
    candidate_id: str,
    *,
    column_required: bool,
) -> ResearchNativeVerificationBinding:
    binding = bindings.get(candidate_id)
    if binding is None:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_VERIFICATION_BINDING_REQUIRED",
            candidate_id,
        )
    if column_required and not binding.column_name:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_COLUMN_BINDING_REQUIRED",
            candidate_id,
        )
    return binding


def _locator(
    locators: Mapping[int, NativeFieldLocator],
    field_id: int,
) -> NativeFieldLocator:
    value = locators.get(field_id)
    if value is None:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_FIELD_METADATA_MISSING",
            str(field_id),
        )
    return value


def _matches_binding(
    binding: ResearchNativeVerificationBinding,
    locator: NativeFieldLocator,
) -> bool:
    return (
        locator.table_name == binding.table_name
        and locator.schema_name == binding.schema_name
        and locator.column_name == binding.column_name
    )


def _assert_metric_scope(
    *,
    contract: AnalyticalRequestContract,
    refs: Mapping[str, ResearchSemanticRef],
    bindings: Mapping[str, ResearchNativeVerificationBinding],
    attestation: NativeAttestationEnvelope,
    locators: Mapping[int, NativeFieldLocator],
    table_locators: Mapping[int, NativeTableLocator],
) -> None:
    manifest = attestation.manifest
    if manifest.aggregation_count != len(contract.metric_refs):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_METRIC_SCOPE_MISMATCH",
            "native aggregation count differs from accepted metric scope",
        )
    unmatched = list(manifest.aggregations)
    metric_refs_by_entity = {
        item.metabase_metric_entity_id: item
        for item in manifest.native_metric_references
    }
    for semantic_ref in contract.metric_refs:
        if semantic_ref not in refs:
            raise ResearchAnalyticalScopeError(
                "R1_SEMANTIC_REF_OUTSIDE_ACCEPTED_SCOPE",
                semantic_ref,
            )
        binding = _require_binding(
            bindings,
            semantic_ref,
            column_required=False,
        )
        if binding.native_metric_entity_id is not None:
            native_ref = metric_refs_by_entity.get(binding.native_metric_entity_id)
            if native_ref is None:
                raise ResearchAnalyticalScopeError(
                    "R1_NATIVE_METRIC_IDENTITY_MISMATCH",
                    semantic_ref,
                )
            if native_ref.aggregation_index >= len(manifest.aggregations):
                raise ResearchAnalyticalScopeError(
                    "R1_NATIVE_METRIC_ATTESTATION_INVALID",
                    semantic_ref,
                )
            fact = manifest.aggregations[native_ref.aggregation_index]
            if binding.aggregation and fact.operator != binding.aggregation:
                raise ResearchAnalyticalScopeError(
                    "R1_NATIVE_METRIC_AGGREGATION_MISMATCH",
                    semantic_ref,
                )
            if fact in unmatched:
                unmatched.remove(fact)
            continue

        if binding.aggregation is None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_BINDING_INCOMPLETE",
                semantic_ref,
            )
        match = None
        for fact in unmatched:
            if fact.operator != binding.aggregation:
                continue
            if binding.argument_kind is not None and (
                fact.argument_kind != binding.argument_kind
            ):
                continue
            if binding.argument_kind == "all_rows":
                if fact.referenced_field_ids:
                    continue
                table_id = manifest.primary_source_table_id
                table = (
                    table_locators.get(table_id)
                    if table_id is not None
                    else None
                )
                if table is None:
                    continue
                if (
                    table.table_name != binding.table_name
                    or table.schema_name != binding.schema_name
                ):
                    continue
                match = fact
                break
            if binding.column_name is None or len(fact.referenced_field_ids) != 1:
                continue
            locator = _locator(locators, fact.referenced_field_ids[0])
            if _matches_binding(binding, locator):
                match = fact
                break
        if match is None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_SCOPE_MISMATCH",
                semantic_ref,
            )
        unmatched.remove(match)
    if unmatched:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_METRIC_SCOPE_MISMATCH",
            "native occurrence contains an unaccepted aggregation",
        )


def _assert_filter_scope(
    *,
    contract: AnalyticalRequestContract,
    refs: Mapping[str, ResearchSemanticRef],
    bindings: Mapping[str, ResearchNativeVerificationBinding],
    attestation: NativeAttestationEnvelope,
    locators: Mapping[int, NativeFieldLocator],
) -> None:
    manifest = attestation.manifest
    if manifest.non_temporal_filter_count != len(contract.filters):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_FILTER_SCOPE_MISMATCH",
            "native non-temporal filter count differs from accepted scope",
        )
    if len(manifest.textual_equality_predicates) != len(contract.filters):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_FILTER_SHAPE_UNSUPPORTED",
            "accepted entity filters require exact textual equality attestation",
        )
    unmatched = list(manifest.textual_equality_predicates)
    for expected in contract.filters:
        if expected.source_candidate_id not in refs:
            raise ResearchAnalyticalScopeError(
                "R1_SEMANTIC_REF_OUTSIDE_ACCEPTED_SCOPE",
                expected.source_candidate_id,
            )
        binding = _require_binding(
            bindings,
            expected.source_candidate_id,
            column_required=True,
        )
        match = None
        for predicate in unmatched:
            if predicate.literal_value != expected.value:
                continue
            if _matches_binding(
                binding,
                _locator(locators, predicate.field_id),
            ):
                match = predicate
                break
        if match is None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_FILTER_SCOPE_MISMATCH",
                expected.source_candidate_id,
            )
        unmatched.remove(match)


def _time_field_ref(
    contract: AnalyticalRequestContract,
) -> str | None:
    if contract.period is not None:
        return contract.period.time_dimension
    if contract.comparison is not None:
        dims = {
            contract.comparison.base_period.time_dimension,
            contract.comparison.reference_period.time_dimension,
        }
        if len(dims) != 1:
            raise ResearchAnalyticalScopeError(
                "R1_TIME_DIMENSION_DRIFT",
                "comparison periods use different time dimensions",
            )
        return next(iter(dims))
    return None


def _assert_time_scope(
    *,
    contract: AnalyticalRequestContract,
    refs: Mapping[str, ResearchSemanticRef],
    bindings: Mapping[str, ResearchNativeVerificationBinding],
    attestation: NativeAttestationEnvelope,
    locators: Mapping[int, NativeFieldLocator],
) -> int | None:
    manifest = attestation.manifest
    time_ref = _time_field_ref(contract)
    if time_ref is None:
        if manifest.temporal_predicates:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_TIME_SCOPE_MISMATCH",
                "native occurrence introduced unaccepted temporal scope",
            )
        return None

    if time_ref not in refs:
        raise ResearchAnalyticalScopeError(
            "R1_TIME_DIMENSION_OUTSIDE_SCOPE",
            time_ref,
        )
    expected = (
        contract.period
        if contract.period is not None
        else AnalyticalPeriodInvariant(
            kind="comparison_coverage",
            time_dimension=time_ref,
            start=min(
                contract.comparison.reference_period.start,
                contract.comparison.base_period.start,
            ),
            end=max(
                contract.comparison.reference_period.end or "",
                contract.comparison.base_period.end or "",
            ),
        )
    )
    if expected.end is None:
        raise ResearchAnalyticalScopeError(
            "R1_OPEN_ENDED_TIME_SCOPE_UNSUPPORTED",
            "R1 requires a bounded period before Evidence admission",
        )

    predicates = tuple(attestation.manifest.temporal_predicates)
    if len(predicates) != 2:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "exact half-open accepted period requires two attested bounds",
        )
    field_ids = {item.time_field_id for item in predicates}
    if len(field_ids) != 1:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "temporal bounds target different native fields",
        )
    field_id = next(iter(field_ids))
    time_binding = _require_binding(
        bindings,
        time_ref,
        column_required=True,
    )
    if not _matches_binding(
        time_binding,
        _locator(locators, field_id),
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_FIELD_MISMATCH",
            time_ref,
        )
    lower = next(
        (
            item for item in predicates
            if item.lower_bound is not None and item.upper_bound is None
        ),
        None,
    )
    upper = next(
        (
            item for item in predicates
            if item.upper_bound is not None and item.lower_bound is None
        ),
        None,
    )
    if (
        lower is None
        or upper is None
        or lower.lower_bound != expected.start
        or lower.lower_inclusive is not True
        or upper.upper_bound != expected.end
        or upper.upper_inclusive is not False
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "native temporal bounds differ from accepted half-open period",
        )
    return field_id


def _assert_breakout_and_ranking(
    *,
    contract: AnalyticalRequestContract,
    refs: Mapping[str, ResearchSemanticRef],
    bindings: Mapping[str, ResearchNativeVerificationBinding],
    attestation: NativeAttestationEnvelope,
    locators: Mapping[int, NativeFieldLocator],
    time_field_id: int | None,
) -> None:
    manifest = attestation.manifest
    expected_dimensions = [refs[item] for item in contract.dimension_refs]
    expected_field_keys = set()
    for ref in expected_dimensions:
        binding = _require_binding(
            bindings,
            ref.candidate_id,
            column_required=True,
        )
        expected_field_keys.add(
            (
                binding.schema_name,
                binding.table_name,
                binding.column_name,
            )
        )
    if contract.comparison is not None and time_field_id is not None:
        time_locator = _locator(locators, time_field_id)
        expected_field_keys.add(
            (
                time_locator.schema_name,
                time_locator.table_name,
                time_locator.column_name,
            )
        )

    observed_items = tuple(
        (
            _locator(locators, item.field_id).schema_name,
            _locator(locators, item.field_id).table_name,
            _locator(locators, item.field_id).column_name,
        )
        for item in manifest.breakouts
    )
    observed_field_keys = set(observed_items)
    if (
        len(observed_items) != len(observed_field_keys)
        or observed_field_keys != expected_field_keys
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_DIMENSION_SCOPE_MISMATCH",
            "native breakout set differs from accepted dimension scope",
        )

    ranking = contract.ranking
    if ranking is None:
        if manifest.limit is not None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_RANKING_SCOPE_MISMATCH",
                "native occurrence introduced an unaccepted LIMIT",
            )
        return
    if (
        manifest.limit != ranking.limit
        or len(manifest.order_bys) != 1
        or manifest.order_bys[0].target_kind != "aggregation"
        or manifest.order_bys[0].direction != ranking.direction
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
            "native ranking differs from accepted ranking invariant",
        )


def assert_attested_native_scope(
    *,
    session: ResearchSession,
    obligation_id: str,
    contract: AnalyticalRequestContract,
    attestation: NativeAttestationEnvelope,
    field_locators: Mapping[int, NativeFieldLocator],
    table_locators: Mapping[int, NativeTableLocator],
    expected_engine: NativeEngineIdentity,
    expected_metabase_subject: int,
) -> NativeAnalyticalRequestObservation:
    """Fail closed unless the exact attested occurrence preserves accepted scope."""

    manifest = attestation.manifest
    runtime = manifest.runtime_identity
    if (
        runtime.repository != expected_engine.repository
        or runtime.revision_sha != expected_engine.engine_sha
        or runtime.upstream_base_sha != expected_engine.upstream_base_sha
        or runtime.runtime_tag != expected_engine.runtime_tag
        or runtime.build_identity != expected_engine.build_identity
        or (
            expected_engine.runtime_image_identity is not None
            and runtime.image_identity != expected_engine.runtime_image_identity
        )
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_ENGINE_IDENTITY_MISMATCH",
            "scope attestation came from a different engine identity",
        )
    if manifest.authenticated_metabase_subject != expected_metabase_subject:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_SUBJECT_MISMATCH",
            "scope attestation belongs to a different Metabase subject",
        )
    if manifest.material_query_count != 1:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_QUERY_COUNT_MISMATCH",
            "one Research occurrence must attest exactly one material query",
        )

    refs = _refs(session)
    bindings = _bindings(session)
    _assert_metric_scope(
        contract=contract,
        refs=refs,
        bindings=bindings,
        attestation=attestation,
        locators=field_locators,
        table_locators=table_locators,
    )
    _assert_filter_scope(
        contract=contract,
        refs=refs,
        bindings=bindings,
        attestation=attestation,
        locators=field_locators,
    )
    time_field_id = _assert_time_scope(
        contract=contract,
        refs=refs,
        bindings=bindings,
        attestation=attestation,
        locators=field_locators,
    )
    _assert_breakout_and_ranking(
        contract=contract,
        refs=refs,
        bindings=bindings,
        attestation=attestation,
        locators=field_locators,
        time_field_id=time_field_id,
    )

    observation = AnalyticalRequestObservation(
        scope_identity=contract.scope_identity,
        metric_refs=contract.metric_refs,
        dimension_refs=contract.dimension_refs,
        filters=contract.filters,
        period=contract.period,
        comparison=contract.comparison,
        ranking=contract.ranking,
        grain_constraints=contract.grain_constraints,
        requested_output_surfaces=contract.requested_output_surfaces,
    )
    assert_request_invariants(contract, observation)
    return NativeAnalyticalRequestObservation(
        attestation_id=manifest.attestation_id,
        native_conversation_id=manifest.native_conversation_id,
        native_query_id=manifest.native_query_id,
        exact_artifact_fingerprint=manifest.exact_pmbql_fingerprint,
        request=observation,
    )
