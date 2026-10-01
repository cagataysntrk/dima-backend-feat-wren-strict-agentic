"""Shared accepted analytical-scope contract for P14/P17 native Research.

Authority remains the immutable accepted ResearchBrief. This module only projects
that authority into the existing AnalyticalRequestContract and checks one engine-
attested native occurrence before it can become governed Evidence.

No SQL/MBQL parser, query planner, fuzzy matcher or prompt classifier lives here.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalEvidenceSynthesisRankingInvariant,
    AnalyticalFilterInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalRequestObservation,
    AnalyticalScopeIdentity,
    AnalyticalTemporalObservationInvariant,
    NativeAnalyticalRequestObservation,
    assert_request_invariants,
)
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.research_contracts import (
    CausalEffectObservation,
    PresentationKind,
    ResearchGoalKind,
    ResearchNativeVerificationBinding,
    ResearchQuestion,
    ResearchSemanticRef,
    SemanticTargetKind,
    TemporalRole,
)
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeMaterialObservation,
)

if TYPE_CHECKING:
    from app.v3.research import ResearchSession


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchAnalyticalScopeError(RuntimeError):
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        last_valid_boundary: str | None = None,
        first_invalid_boundary: str | None = None,
        expected_fingerprint: str | None = None,
        observed_fingerprint: str | None = None,
    ) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.last_valid_boundary = last_valid_boundary
        self.first_invalid_boundary = first_invalid_boundary
        self.expected_fingerprint = expected_fingerprint
        self.observed_fingerprint = observed_fingerprint


def _boundary_fingerprint(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _native_temporal_scope_error(
    *,
    detail: str,
    expected: Mapping[str, Any],
    observed: Mapping[str, Any],
) -> ResearchAnalyticalScopeError:
    expected_payload = json.dumps(
        expected,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    observed_payload = json.dumps(
        observed,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return ResearchAnalyticalScopeError(
        "R1_NATIVE_TIME_SCOPE_MISMATCH",
        (
            f"{detail}; expected_temporal_scope={expected_payload}; "
            f"observed_temporal_scope={observed_payload}"
        ),
        last_valid_boundary="dima.material.compile",
        first_invalid_boundary="dima.native.observe",
        expected_fingerprint=_boundary_fingerprint(expected),
        observed_fingerprint=_boundary_fingerprint(observed),
    )


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


class NativeMaterialBinding(Frozen):
    """Governed business candidate -> stable native identity correlation only."""

    candidate_id: str = Field(min_length=1)
    candidate_kind: str = Field(min_length=1)
    database_id: int = Field(gt=0)
    table_id: int | None = Field(default=None, gt=0)
    field_id: int | None = Field(default=None, gt=0)
    metric_id: int | None = Field(default=None, gt=0)
    metric_entity_id: str | None = None


class CoOriginMaterialRequirement(Frozen):
    """Transient execution-only union of compatible accepted material needs.

    Accepted Research goals remain immutable. This projection is the execution
    center for the minimum governed analytical material one native occurrence
    must make available. It may represent one ROOT_CAUSE goal or a compatible
    anchor+relationship co-origin group; it never becomes a query plan.
    """

    anchor_goal_id: str = Field(min_length=1)
    source_goal_ids: tuple[str, ...] = Field(min_length=1)
    source_fragment_identity: str = Field(
        pattern=r"^(?:fragment|text)-sha256:[a-f0-9]{64}$"
    )
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    semantic_context_version: str = Field(min_length=1)
    required_metric_refs: tuple[str, ...] = Field(min_length=1)
    required_dimension_refs: tuple[str, ...] = ()
    required_temporal_roles: tuple[TemporalRole, ...] = ()


_COORIGIN_ANCHOR_KINDS = frozenset(
    {
        ResearchGoalKind.RANKING,
        ResearchGoalKind.COMPARISON,
        ResearchGoalKind.BREAKDOWN,
        ResearchGoalKind.PERFORMANCE,
        ResearchGoalKind.TREND,
    }
)
_MATERIAL_REF_KINDS = frozenset(
    {
        SemanticTargetKind.METRIC,
        SemanticTargetKind.KPI,
        SemanticTargetKind.DIMENSION,
    }
)


def _material_refs(question: ResearchQuestion) -> tuple[ResearchSemanticRef, ...]:
    return tuple(
        item
        for item in (*question.subject_refs, *question.related_refs)
        if item.target_kind in _MATERIAL_REF_KINDS
    )


def _has_only_material_refs(question: ResearchQuestion) -> bool:
    refs = (*question.subject_refs, *question.related_refs)
    return bool(refs) and all(item.target_kind in _MATERIAL_REF_KINDS for item in refs)


def coorigin_material_requirements(
    session: ResearchSession,
) -> tuple[CoOriginMaterialRequirement, ...]:
    """Project narrow anchor+relationship sharing groups from one accepted session.

    The function never groups across Research sessions, so brief, scope version,
    semantic context, tenant and principal/security lens are structurally shared.
    Provenance matching is exact accepted source_text identity only.
    """

    brief = session.accepted_brief
    if brief is None:
        raise ResearchAnalyticalScopeError(
            "R1_ACCEPTED_BRIEF_REQUIRED",
            "co-origin material projection requires the immutable accepted ResearchBrief",
        )

    by_source: dict[str, list[ResearchQuestion]] = {}
    for question in brief.questions:
        provenance_identity = (
            question.source_fragment_identity
            or (
                "text-sha256:"
                + hashlib.sha256(question.source_text.encode("utf-8")).hexdigest()
            )
        )
        by_source.setdefault(provenance_identity, []).append(question)

    requirements: list[CoOriginMaterialRequirement] = []
    temporal_roles = tuple(
        dict.fromkeys(item.role for item in brief.scope.periods)
    )
    for provenance_identity, group in by_source.items():
        # A typed ROOT_CAUSE goal is itself one material-coverage anchor. User
        # candidates and discovery material are carried as governed semantic
        # refs; no per-candidate native acquisition is opened here.
        root_causes = tuple(
            item
            for item in group
            if (
                item.kind == ResearchGoalKind.ROOT_CAUSE
                and item.causal_competition is not None
                and _has_only_material_refs(item)
            )
        )
        for root in root_causes:
            refs_by_id = {
                item.candidate_id: item
                for item in _material_refs(root)
            }
            causal = root.causal_competition
            ordered_ids = tuple(
                dict.fromkeys(
                    (
                        causal.effect_semantic_id,
                        *causal.candidate_mechanism_semantic_ids,
                        *causal.diagnostic_dimension_ids,
                        *(item.candidate_id for item in _material_refs(root)),
                    )
                )
            )
            missing = [item for item in ordered_ids if item not in refs_by_id]
            if missing:
                raise ResearchAnalyticalScopeError(
                    "R1_CAUSAL_MATERIAL_REF_OUTSIDE_GOAL",
                    ",".join(missing),
                )
            ordered_refs = tuple(refs_by_id[item] for item in ordered_ids)
            metrics = tuple(
                item.candidate_id
                for item in ordered_refs
                if item.target_kind
                in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
            )
            dimensions = tuple(
                item.candidate_id
                for item in ordered_refs
                if item.target_kind == SemanticTargetKind.DIMENSION
            )
            if not metrics:
                raise ResearchAnalyticalScopeError(
                    "R1_COORIGIN_MATERIAL_METRIC_REQUIRED",
                    root.goal_id,
                )
            requirements.append(
                CoOriginMaterialRequirement(
                    anchor_goal_id=root.goal_id,
                    source_goal_ids=(root.goal_id,),
                    source_fragment_identity=provenance_identity,
                    scope_version_id=brief.scope.scope_version.version_id,
                    semantic_context_version=session.context_version,
                    required_metric_refs=metrics,
                    required_dimension_refs=dimensions,
                    required_temporal_roles=temporal_roles,
                )
            )

        relationships = tuple(
            item
            for item in group
            if item.kind == ResearchGoalKind.RELATIONSHIP
            and _has_only_material_refs(item)
        )
        if not relationships:
            continue
        anchors = tuple(item for item in group if item.kind in _COORIGIN_ANCHOR_KINDS)
        if not anchors:
            continue
        if len(anchors) != 1:
            raise ResearchAnalyticalScopeError(
                "R1_COORIGIN_MATERIAL_ANCHOR_AMBIGUOUS",
                "co-origin relationship material has more than one native analytical anchor",
            )
        anchor = anchors[0]

        ordered_refs: list[ResearchSemanticRef] = []
        seen: set[str] = set()
        for question in (anchor, *relationships):
            for ref in _material_refs(question):
                if ref.candidate_id not in seen:
                    ordered_refs.append(ref)
                    seen.add(ref.candidate_id)

        metrics = tuple(
            item.candidate_id
            for item in ordered_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
        dimensions = tuple(
            item.candidate_id
            for item in ordered_refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        )
        if not metrics:
            raise ResearchAnalyticalScopeError(
                "R1_COORIGIN_MATERIAL_METRIC_REQUIRED",
                anchor.goal_id,
            )

        requirements.append(
            CoOriginMaterialRequirement(
                anchor_goal_id=anchor.goal_id,
                source_goal_ids=tuple(item.goal_id for item in (anchor, *relationships)),
                source_fragment_identity=provenance_identity,
                scope_version_id=brief.scope.scope_version.version_id,
                semantic_context_version=session.context_version,
                required_metric_refs=metrics,
                required_dimension_refs=dimensions,
                required_temporal_roles=temporal_roles,
            )
        )
    return tuple(requirements)


def coorigin_material_requirement_for_anchor(
    session: ResearchSession,
    obligation_id: str,
) -> CoOriginMaterialRequirement | None:
    matches = tuple(
        item
        for item in coorigin_material_requirements(session)
        if item.anchor_goal_id == obligation_id
    )
    if len(matches) > 1:
        raise ResearchAnalyticalScopeError(
            "R1_COORIGIN_MATERIAL_REQUIREMENT_AMBIGUOUS",
            obligation_id,
        )
    return matches[0] if matches else None


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
    goal_metrics = _unique_refs(
        question_refs,
        {SemanticTargetKind.METRIC, SemanticTargetKind.KPI},
    )
    if not goal_metrics:
        raise ResearchAnalyticalScopeError(
            "R1_METRIC_SCOPE_REQUIRED",
            "native analytical occurrence requires at least one accepted metric/KPI",
        )

    projection = coorigin_material_requirement_for_anchor(session, obligation_id)
    accepted_refs = {
        item.candidate_id: item for item in brief.scope.semantic_refs
    }
    if projection is None:
        material_metrics = goal_metrics
        material_dimension_refs = _unique_refs(
            question_refs,
            {SemanticTargetKind.DIMENSION},
        )
    else:
        if (
            projection.scope_version_id != brief.scope.scope_version.version_id
            or projection.semantic_context_version != session.context_version
        ):
            raise ResearchAnalyticalScopeError(
                "R1_COORIGIN_MATERIAL_SCOPE_DRIFT",
                obligation_id,
            )
        missing = (
            set(projection.required_metric_refs)
            | set(projection.required_dimension_refs)
        ) - set(accepted_refs)
        if missing:
            raise ResearchAnalyticalScopeError(
                "R1_COORIGIN_MATERIAL_REF_OUTSIDE_ACCEPTED_SCOPE",
                ",".join(sorted(missing)),
            )
        material_metrics = tuple(
            accepted_refs[candidate_id]
            for candidate_id in projection.required_metric_refs
        )
        material_dimension_refs = tuple(
            accepted_refs[candidate_id]
            for candidate_id in projection.required_dimension_refs
        )

    period_dimension_ids = {
        item.time_dimension_candidate_id for item in brief.scope.periods
    }
    filters = _unique_refs(
        tuple(brief.scope.semantic_refs),
        {SemanticTargetKind.ENTITY_VALUE},
    )
    # An exact governed entity equality already fixes its underlying field.
    # Requiring that same field again as a breakout/grain would turn accepted
    # semantic scope into a physical query-shape identity constraint.
    verification_bindings = {
        item.candidate_id: item
        for item in brief.scope.native_verification_bindings
    }
    fixed_filter_fields = {
        (
            binding.schema_name,
            binding.table_name,
            binding.column_name,
        )
        for item in filters
        if (binding := verification_bindings.get(item.candidate_id)) is not None
        and binding.column_name is not None
    }

    def fixed_by_entity_filter(item: ResearchSemanticRef) -> bool:
        binding = verification_bindings.get(item.candidate_id)
        return bool(
            binding is not None
            and binding.column_name is not None
            and (
                binding.schema_name,
                binding.table_name,
                binding.column_name,
            )
            in fixed_filter_fields
        )

    dimensions = tuple(
        item
        for item in material_dimension_refs
        if item.candidate_id not in period_dimension_ids
        and not fixed_by_entity_filter(item)
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
        baseline_periods = tuple(
            item
            for item in periods
            if item.role == TemporalRole.BASELINE_PERIOD
        )
        comparison_periods = tuple(
            item
            for item in periods
            if item.role == TemporalRole.COMPARISON_PERIOD
        )
        has_temporal_comparison_role = bool(
            baseline_periods or comparison_periods
        )
        if has_temporal_comparison_role:
            if (
                len(baseline_periods) != 1
                or len(comparison_periods) != 1
            ):
                raise ResearchAnalyticalScopeError(
                    "R1_TEMPORAL_COMPARISON_ROLE_INCOMPLETE",
                    (
                        "temporal comparison requires exactly one baseline "
                        "and one comparison period"
                    ),
                )
            baseline_period = baseline_periods[0]
            comparison_period = comparison_periods[0]
            if (
                baseline_period.time_dimension_candidate_id
                != comparison_period.time_dimension_candidate_id
            ):
                raise ResearchAnalyticalScopeError(
                    "R1_TIME_DIMENSION_DRIFT",
                    "one comparison cannot span two time dimensions",
                )
            comparison = AnalyticalComparisonInvariant(
                mode="explicit_periods",
                reference_period=_period(baseline_period),
                base_period=_period(comparison_period),
            )
        else:
            # Two typed periods without baseline/comparison roles describe one
            # bounded material window (for example EFFECT_PERIOD +
            # EVIDENCE_WINDOW in RCA). Their wording and tuple order carry no
            # temporal-comparison authority.
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

    temporal_observation = None
    if (
        question.causal_competition is not None
        and question.causal_competition.effect_observation
        == CausalEffectObservation.CHANGE
    ):
        if not periods:
            raise ResearchAnalyticalScopeError(
                "R1_EFFECT_CHANGE_TIME_REQUIRED",
                "causal change observation requires accepted bounded time authority",
            )
        time_dimensions = {
            item.time_dimension_candidate_id for item in periods
        }
        if len(time_dimensions) != 1:
            raise ResearchAnalyticalScopeError(
                "R1_EFFECT_CHANGE_TIME_DIMENSION_AMBIGUOUS",
                "causal change observation requires one governed time dimension",
            )
        temporal_observation = AnalyticalTemporalObservationInvariant(
            kind="change",
            time_dimension=next(iter(time_dimensions)),
            minimum_distinct_values=2,
        )

    ranking = None
    if question.ranking is not None:
        value = question.ranking
        goal_metric_ids = {item.candidate_id for item in goal_metrics}
        explicit_measure = value.measure_semantic_id
        if explicit_measure is not None and explicit_measure not in goal_metric_ids:
            raise ResearchAnalyticalScopeError(
                "R1_RANKING_BASIS_OUTSIDE_SCOPE",
                explicit_measure,
            )

        native_measure = explicit_measure
        if native_measure is None and len(goal_metrics) == 1:
            # Exactly-one metric scope is structurally unambiguous. Destructure
            # the singleton so no ordered-tuple "first metric" authority exists.
            (sole_metric,) = goal_metrics
            native_measure = sole_metric.candidate_id

        if native_measure is not None:
            if value.direction == "unspecified":
                raise ResearchAnalyticalScopeError(
                    "R1_RANKING_DIRECTION_UNRESOLVED",
                    "native metric ranking requires typed asc/desc direction",
                )
            ranking = AnalyticalRankingInvariant(
                measure=native_measure,
                direction=value.direction,
                limit=value.limit,
            )
        else:
            # A multi-metric ranking with no explicit governed basis remains a
            # product/cognition obligation over governed evidence. Dima does
            # not manufacture a native single-metric ORDER BY contract.
            ranking = AnalyticalEvidenceSynthesisRankingInvariant(
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
        scope_fingerprint=brief.scope_fingerprint,
        metric_refs=tuple(item.candidate_id for item in material_metrics),
        dimension_refs=tuple(item.candidate_id for item in dimensions),
        filters=tuple(filter_invariants),
        period=period,
        comparison=comparison,
        temporal_observation=temporal_observation,
        ranking=ranking,
        grain_constraints=tuple(item.candidate_id for item in dimensions),
        requested_output_surfaces=tuple(dict.fromkeys(outputs)),
    )


def material_coverage_period(
    contract: AnalyticalRequestContract,
) -> AnalyticalPeriodInvariant | None:
    """Canonical minimum temporal window one native material acquisition must cover.

    This is a semantic projection of accepted period authority only. It does not
    prescribe filters, MBQL, SQL, bucketing, or physical query shape.
    """

    if contract.period is not None:
        return contract.period
    comparison = contract.comparison
    if comparison is None:
        return None
    periods = (
        comparison.reference_period,
        comparison.base_period,
    )
    time_dimensions = {item.time_dimension for item in periods}
    if len(time_dimensions) != 1:
        raise ResearchAnalyticalScopeError(
            "R1_TIME_DIMENSION_DRIFT",
            "comparison periods use different time dimensions",
        )
    ends = tuple(item.end for item in periods)
    if any(value is None for value in ends):
        raise ResearchAnalyticalScopeError(
            "R1_OPEN_ENDED_TIME_SCOPE_UNSUPPORTED",
            "comparison material coverage requires bounded periods",
        )
    return AnalyticalPeriodInvariant(
        kind="comparison_coverage",
        time_dimension=next(iter(time_dimensions)),
        start=min(item.start for item in periods),
        end=max(str(value) for value in ends),
    )


def native_request_context(contract: AnalyticalRequestContract) -> dict[str, Any]:
    """Semantic-only context given to Metabot; physical verifier bindings stay out."""

    scope = contract.model_dump(mode="json")
    coverage_period = material_coverage_period(contract)
    scope["material_coverage_period"] = (
        coverage_period.model_dump(mode="json")
        if coverage_period is not None
        else None
    )
    if contract.temporal_observation is None:
        # Preserve the sealed context shape for capabilities that do not carry
        # the new CHANGE authority. Only the affected family gets a new field.
        scope.pop("temporal_observation", None)
    return {"dima_analytical_scope": scope}


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
) -> None:
    """Verify governed metric identity, never Metabase's physical aggregation plan."""

    manifest = attestation.manifest
    observed_metric_ids: set[str] = set()
    for item in manifest.native_metric_references:
        if item.aggregation_index >= len(manifest.aggregations):
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_ATTESTATION_INVALID",
                item.metabase_metric_entity_id,
            )
        observed_metric_ids.add(item.metabase_metric_entity_id)

    expected_metric_ids: set[str] = set()
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
        native_metric_id = binding.native_metric_entity_id
        if native_metric_id is None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_RESOURCE_BINDING_REQUIRED",
                (
                    f"{semantic_ref}: forward V1 metric identity requires a "
                    "governed Metabase-native metric resource"
                ),
            )
        if native_metric_id in expected_metric_ids:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_RESOURCE_BINDING_AMBIGUOUS",
                native_metric_id,
            )
        expected_metric_ids.add(native_metric_id)

    if observed_metric_ids != expected_metric_ids:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_METRIC_IDENTITY_MISMATCH",
            (
                "observed governed Metabase metric identities differ from "
                "the accepted material request"
            ),
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



def _date_only(value: Any) -> date | None:
    if isinstance(value, datetime):
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or "T" in value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _calendar_date_boundary(value: Any) -> date | None:
    """Normalize only unambiguous calendar-midnight boundary spellings.

    A date-only native literal is evidence that Metabase expressed this bound
    in the discrete calendar-date domain. Accepted Research bounds may carry
    the same calendar boundary as a naive/UTC midnight datetime. Non-midnight
    or non-UTC offset datetimes remain timestamp semantics and fail closed.
    """

    exact = _date_only(value)
    if exact is not None:
        return exact

    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str) and "T" in value:
        raw = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            result = datetime.fromisoformat(raw)
        except ValueError:
            return None
    else:
        return None

    if (result.hour, result.minute, result.second, result.microsecond) != (
        0,
        0,
        0,
        0,
    ):
        return None
    if result.tzinfo is not None and result.utcoffset() != timedelta(0):
        return None
    return result.date()


def _canonical_datetime_bound(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str) and "T" in value:
        raw = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            result = datetime.fromisoformat(raw)
        except ValueError:
            return None
    else:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def _matches_half_open_temporal_interval(
    *,
    expected_start: str,
    expected_end: str,
    observed_lower: Any,
    lower_inclusive: bool | None,
    observed_upper: Any,
    upper_inclusive: bool | None,
) -> bool:
    """Compare semantic intervals, not an equivalent physical predicate spelling.

    Calendar DATE domains are discrete. Therefore > prior-day and >= start are
    equivalent, as are <= last-day and < next-day. Timestamp domains remain
    continuous: inclusivity stays exactly half-open, while equivalent ISO-8601
    timezone spellings compare by instant.
    """

    observed_lower_date = _date_only(observed_lower)
    observed_upper_date = _date_only(observed_upper)
    expected_start_date = (
        _calendar_date_boundary(expected_start)
        if observed_lower_date is not None
        and observed_upper_date is not None
        else None
    )
    expected_end_date = (
        _calendar_date_boundary(expected_end)
        if observed_lower_date is not None
        and observed_upper_date is not None
        else None
    )
    if (
        expected_start_date is not None
        and expected_end_date is not None
        and observed_lower_date is not None
        and observed_upper_date is not None
    ):
        if lower_inclusive is True:
            normalized_start = observed_lower_date
        elif lower_inclusive is False:
            normalized_start = observed_lower_date + timedelta(days=1)
        else:
            return False

        if upper_inclusive is False:
            normalized_end = observed_upper_date
        elif upper_inclusive is True:
            normalized_end = observed_upper_date + timedelta(days=1)
        else:
            return False

        return (
            normalized_start == expected_start_date
            and normalized_end == expected_end_date
        )

    if lower_inclusive is not True or upper_inclusive is not False:
        return False

    expected_start_dt = _canonical_datetime_bound(expected_start)
    expected_end_dt = _canonical_datetime_bound(expected_end)
    observed_lower_dt = _canonical_datetime_bound(observed_lower)
    observed_upper_dt = _canonical_datetime_bound(observed_upper)
    if (
        expected_start_dt is not None
        and expected_end_dt is not None
        and observed_lower_dt is not None
        and observed_upper_dt is not None
    ):
        return (
            observed_lower_dt == expected_start_dt
            and observed_upper_dt == expected_end_dt
        )

    return (
        observed_lower == expected_start
        and observed_upper == expected_end
    )


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
    expected = material_coverage_period(contract)
    assert expected is not None
    if expected.end is None:
        raise ResearchAnalyticalScopeError(
            "R1_OPEN_ENDED_TIME_SCOPE_UNSUPPORTED",
            "R1 requires a bounded period before Evidence admission",
        )

    predicates = tuple(attestation.manifest.temporal_predicates)
    if not predicates:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "accepted bounded period is absent from the native occurrence",
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

    # Observe the material half-open interval, independent of whether Metabase
    # encoded it as two predicates, BETWEEN/during, or another attested form.
    lower_bounds = {
        (item.lower_bound, item.lower_inclusive)
        for item in predicates
        if item.lower_bound is not None
    }
    upper_bounds = {
        (item.upper_bound, item.upper_inclusive)
        for item in predicates
        if item.upper_bound is not None
    }
    if len(lower_bounds) != 1 or len(upper_bounds) != 1:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "observed temporal bounds are ambiguous",
        )
    observed_lower, lower_inclusive = next(iter(lower_bounds))
    observed_upper, upper_inclusive = next(iter(upper_bounds))
    if not _matches_half_open_temporal_interval(
        expected_start=expected.start,
        expected_end=expected.end,
        observed_lower=observed_lower,
        lower_inclusive=lower_inclusive,
        observed_upper=observed_upper,
        upper_inclusive=upper_inclusive,
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_TIME_SCOPE_MISMATCH",
            "observed temporal bounds differ from accepted half-open period",
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
    if (
        contract.comparison is not None
        or contract.temporal_observation is not None
    ) and time_field_id is not None:
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

    if isinstance(ranking, AnalyticalEvidenceSynthesisRankingInvariant):
        if manifest.limit is not None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_RANKING_SCOPE_MISMATCH",
                (
                    "evidence-synthesis ranking cannot authorize native "
                    "material truncation"
                ),
            )
        return

    if ranking.limit is None:
        if manifest.limit is not None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_RANKING_SCOPE_MISMATCH",
                "native occurrence introduced unauthorized ranking truncation",
            )
    elif manifest.limit != ranking.limit:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
            "native ranking limit differs from accepted ranking invariant",
        )

    ranking_binding = _require_binding(
        bindings,
        ranking.measure,
        column_required=False,
    )
    ranking_metric_id = ranking_binding.native_metric_entity_id
    if ranking_metric_id is None:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_RESOURCE_BINDING_REQUIRED",
            (
                f"{ranking.measure}: ranking target requires a governed "
                "Metabase-native metric resource"
            ),
        )

    metric_by_occurrence = {
        (item.stage_number, item.aggregation_index): item.metabase_metric_entity_id
        for item in manifest.native_metric_references
    }
    observed_semantic_orders = {
        (
            metric_by_occurrence[(item.stage_number, item.aggregation_index)],
            item.direction,
        )
        for item in manifest.order_bys
        if item.aggregation_index is not None
        and (item.stage_number, item.aggregation_index) in metric_by_occurrence
    }
    if (ranking_metric_id, ranking.direction) not in observed_semantic_orders:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
            "observed ranking target/direction differs from accepted ranking invariant",
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
    refs = _refs(session)
    bindings = _bindings(session)
    _assert_metric_scope(
        contract=contract,
        refs=refs,
        bindings=bindings,
        attestation=attestation,
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
        temporal_observation=contract.temporal_observation,
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

def _material_binding(
    bindings: Mapping[str, NativeMaterialBinding],
    candidate_id: str,
) -> NativeMaterialBinding:
    binding = bindings.get(candidate_id)
    if binding is None:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_MATERIAL_BINDING_REQUIRED",
            candidate_id,
        )
    return binding


def _material_field_identity(binding: NativeMaterialBinding) -> tuple[int, int | None]:
    if binding.field_id is None:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_MATERIAL_FIELD_BINDING_REQUIRED",
            binding.candidate_id,
        )
    return binding.field_id, binding.table_id


def _observed_field_identity(value) -> tuple[int, int | None]:
    return int(value.field_id), (
        int(value.table_id) if value.table_id is not None else None
    )


def _assert_material_runtime_identity(
    observation: NativeMaterialObservation,
    *,
    expected_engine: NativeEngineIdentity,
    expected_metabase_subject: int,
) -> None:
    runtime = observation.runtime_identity
    checks = (
        ("repository", expected_engine.repository),
        ("revision_sha", expected_engine.engine_sha),
        ("upstream_base_sha", expected_engine.upstream_base_sha),
        ("runtime_tag", expected_engine.runtime_tag),
        ("build_identity", expected_engine.build_identity),
        ("image_identity", expected_engine.runtime_image_identity),
    )
    for key, expected in checks:
        if expected is not None and str(runtime.get(key) or "") != str(expected):
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_ENGINE_IDENTITY_MISMATCH",
                f"material observation {key} differs from the pinned engine",
            )
    if not runtime.get("runtime_instance_id"):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_ENGINE_IDENTITY_MISSING",
            "material observation has no runtime instance identity",
        )
    if observation.authenticated_metabase_subject != expected_metabase_subject:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_SUBJECT_MISMATCH",
            "material observation belongs to another Metabase subject",
        )


def _assert_material_metric_scope(
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
) -> None:
    expected: set[tuple[int, str]] = set()
    for candidate_id in contract.metric_refs:
        binding = _material_binding(bindings, candidate_id)
        if binding.metric_id is None or not binding.metric_entity_id:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_METRIC_RESOURCE_BINDING_REQUIRED",
                candidate_id,
            )
        expected.add((binding.metric_id, binding.metric_entity_id))
    observed = {
        (item.metabase_metric_id, item.metabase_metric_entity_id)
        for item in observation.native_metrics
    }
    if observed != expected:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_METRIC_IDENTITY_MISMATCH",
            "observed governed Metabase metric identities differ from accepted scope",
        )


def _assert_material_filter_scope(
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
) -> None:
    unmatched = list(observation.filters)
    if len(unmatched) != len(contract.filters):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_FILTER_SCOPE_MISMATCH",
            "material filter count differs from accepted scope",
        )
    for expected in contract.filters:
        binding = _material_binding(bindings, expected.source_candidate_id)
        field_identity = _material_field_identity(binding)
        match = next(
            (
                item
                for item in unmatched
                if _observed_field_identity(item) == field_identity
                and item.operator == "="
                and tuple(item.values) == (expected.value,)
            ),
            None,
        )
        if match is None:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_FILTER_SCOPE_MISMATCH",
                expected.source_candidate_id,
            )
        unmatched.remove(match)


def _material_expected_period(
    contract: AnalyticalRequestContract,
) -> tuple[str | None, str | None, str | None]:
    time_ref = _time_field_ref(contract)
    if time_ref is None:
        return None, None, None
    coverage_period = material_coverage_period(contract)
    assert coverage_period is not None
    return time_ref, coverage_period.start, coverage_period.end


def _assert_material_time_scope(
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
) -> tuple[int, int | None] | None:
    time_ref, start, end = _material_expected_period(contract)
    if time_ref is None:
        if observation.temporal_scopes:
            raise _native_temporal_scope_error(
                detail="native occurrence introduced unaccepted temporal scope",
                expected={
                    "time_ref": None,
                    "period": None,
                },
                observed={
                    "temporal_scopes": [
                        item.model_dump(mode="json")
                        for item in observation.temporal_scopes
                    ],
                },
            )
        return None
    binding = _material_binding(bindings, time_ref)
    expected_identity = _material_field_identity(binding)
    matches = [
        item
        for item in observation.temporal_scopes
        if (item.time_field_id, item.table_id) == expected_identity
    ]
    if len(matches) != 1 or len(observation.temporal_scopes) != 1:
        raise _native_temporal_scope_error(
            detail="material temporal scope targets another field or is ambiguous",
            expected={
                "time_ref": time_ref,
                "start": start,
                "end": end,
                "field_identity": expected_identity,
            },
            observed={
                "temporal_scopes": [
                    item.model_dump(mode="json")
                    for item in observation.temporal_scopes
                ],
            },
        )
    item = matches[0]
    assert start is not None and end is not None
    if not _matches_half_open_temporal_interval(
        expected_start=start,
        expected_end=end,
        observed_lower=item.lower_bound,
        lower_inclusive=item.lower_inclusive,
        observed_upper=item.upper_bound,
        upper_inclusive=item.upper_inclusive,
    ):
        raise _native_temporal_scope_error(
            detail="observed temporal bounds differ from accepted half-open period",
            expected={
                "time_ref": time_ref,
                "start": start,
                "end": end,
                "field_identity": expected_identity,
            },
            observed={
                "time_field_id": item.time_field_id,
                "table_id": item.table_id,
                "lower_bound": item.lower_bound,
                "lower_inclusive": item.lower_inclusive,
                "upper_bound": item.upper_bound,
                "upper_inclusive": item.upper_inclusive,
            },
        )
    return expected_identity


def _assert_material_dimension_scope(
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
    *,
    time_identity: tuple[int, int | None] | None,
) -> None:
    required = {
        _material_field_identity(_material_binding(bindings, candidate_id))
        for candidate_id in contract.dimension_refs
    }
    observed = {
        _observed_field_identity(item)
        for item in observation.dimensions
        if item.role == "breakout"
    }
    # Exact accepted equality filters already constrain their governed fields.
    # Repeating one of those same fields as a breakout changes only physical
    # result shape; it cannot broaden the accepted row set or mint new semantic
    # dimension authority. Such breakouts are therefore allowed but never
    # required. Unfiltered extra dimensions remain unauthorized.
    fixed_filter_dimensions = {
        _material_field_identity(
            _material_binding(bindings, item.source_candidate_id)
        )
        for item in contract.filters
    }
    required.difference_update(fixed_filter_dimensions)
    if (
        contract.comparison is not None
        or contract.temporal_observation is not None
    ) and time_identity is not None:
        # A typed period comparison or causal CHANGE observation requires the
        # governed temporal grain. This is semantic material authority, not a
        # physical query-plan prescription.
        required.add(time_identity)
        allowed = set(required) | fixed_filter_dimensions
    else:
        # Within an already accepted bounded period, Metabase may expose the
        # same governed temporal field as an additional breakout so cognition
        # can inspect change inside that period. This adds no new scope or data
        # source; any other extra breakout remains unauthorized.
        allowed = set(required) | fixed_filter_dimensions
        if contract.period is not None and time_identity is not None:
            allowed.add(time_identity)
    if not required.issubset(observed) or not observed.issubset(allowed):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_DIMENSION_SCOPE_MISMATCH",
            "material breakout identities differ from accepted dimension scope",
        )


def _assert_material_ranking_scope(
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
) -> None:
    ranking = contract.ranking
    # Metabase may add deterministic ORDER BY clauses for presentation/stability.
    # Without LIMIT they do not restrict the material row set and therefore do
    # not mint Dima ranking authority. A native LIMIT is material: it can remove
    # rows and must remain authorized by an accepted ranking invariant.
    restrictive_ordering = tuple(
        item for item in observation.ranking
        if item.limit is not None
    )
    if ranking is None:
        if restrictive_ordering:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_RANKING_SCOPE_MISMATCH",
                "native occurrence introduced an unaccepted row-limiting ranking",
            )
        return
    if isinstance(ranking, AnalyticalEvidenceSynthesisRankingInvariant):
        if restrictive_ordering:
            raise ResearchAnalyticalScopeError(
                "R1_NATIVE_RANKING_SCOPE_MISMATCH",
                "evidence-synthesis ranking has no authorized native row limit",
            )
        return
    binding = _material_binding(bindings, ranking.measure)
    if binding.metric_id is None or not binding.metric_entity_id:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_RESOURCE_BINDING_REQUIRED",
            ranking.measure,
        )
    matches = [
        item
        for item in observation.ranking
        if item.target.kind == "metric"
        and item.target.metabase_metric_id == binding.metric_id
        and item.target.metabase_metric_entity_id == binding.metric_entity_id
        and item.direction == ranking.direction
        and item.limit == ranking.limit
    ]
    if len(matches) != 1 or len(observation.ranking) != 1:
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RANKING_SCOPE_MISMATCH",
            "material ranking target/direction/limit differs from accepted scope",
        )


def assert_material_native_scope(
    *,
    session: ResearchSession,
    obligation_id: str,
    contract: AnalyticalRequestContract,
    observation: NativeMaterialObservation,
    bindings: Mapping[str, NativeMaterialBinding],
    expected_engine: NativeEngineIdentity,
    expected_metabase_subject: int,
) -> AnalyticalRequestObservation:
    """Compare engine-reported material semantics to accepted Research authority.

    Only stable native ids and material values participate. Physical aggregation
    algebra/count, query representation, schema/table/column names, and P13
    attestation grammar are intentionally outside this R5 boundary.
    """

    del obligation_id
    _assert_material_runtime_identity(
        observation,
        expected_engine=expected_engine,
        expected_metabase_subject=expected_metabase_subject,
    )
    if any(
        binding.database_id != observation.database_id
        for binding in bindings.values()
    ):
        raise ResearchAnalyticalScopeError(
            "R1_NATIVE_RESOURCE_DATABASE_MISMATCH",
            "material observation database differs from governed bindings",
        )
    _assert_material_metric_scope(contract, observation, bindings)
    _assert_material_filter_scope(contract, observation, bindings)
    time_identity = _assert_material_time_scope(contract, observation, bindings)
    _assert_material_dimension_scope(
        contract,
        observation,
        bindings,
        time_identity=time_identity,
    )
    _assert_material_ranking_scope(contract, observation, bindings)

    request = AnalyticalRequestObservation(
        scope_identity=contract.scope_identity,
        metric_refs=contract.metric_refs,
        dimension_refs=contract.dimension_refs,
        filters=contract.filters,
        period=contract.period,
        comparison=contract.comparison,
        temporal_observation=contract.temporal_observation,
        ranking=contract.ranking,
        grain_constraints=contract.grain_constraints,
        requested_output_surfaces=contract.requested_output_surfaces,
    )
    assert_request_invariants(contract, request)
    return request

