"""Dima V1 material analytical request invariants.

This is deliberately not a query planner. It carries only the already-accepted
business request invariants that must survive native Metabot implementation.
SQL, MBQL, join plans, aggregation implementation, temporal implementation and
query optimality are outside this module's authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytics_contract import (
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedRanking,
)
from app.v3.research_contracts import RankingBasis, TemporalChangeFrameMode


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AnalyticalScopeIdentity(FrozenModel):
    lineage_id: str = Field(min_length=1)
    version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")


class AnalyticalFilterInvariant(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    source_candidate_id: str = Field(min_length=1)
    dimension_name: str = Field(min_length=1)
    value: str


class AnalyticalPeriodInvariant(FrozenModel):
    kind: str = Field(min_length=1)
    time_dimension: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str | None = None


class AnalyticalComparisonInvariant(FrozenModel):
    mode: str = Field(min_length=1)
    base_period: AnalyticalPeriodInvariant
    reference_period: AnalyticalPeriodInvariant


class AnalyticalTemporalObservationInvariant(FrozenModel):
    """Typed requirement that change over governed time remain observable."""

    kind: Literal["change"] = "change"
    time_dimension: str = Field(min_length=1)
    minimum_distinct_values: int = Field(default=2, ge=2)


class AnalyticalTemporalChangeFrame(FrozenModel):
    """Read-only typed CHANGE temporal view over already accepted period authority."""

    mode: TemporalChangeFrameMode
    time_dimension: str = Field(min_length=1)
    span_period: AnalyticalPeriodInvariant | None = None
    baseline_period: AnalyticalPeriodInvariant | None = None
    comparison_period: AnalyticalPeriodInvariant | None = None

    @model_validator(mode="after")
    def coherent(self):
        if self.mode == TemporalChangeFrameMode.PAIR:
            if (
                self.span_period is not None
                or self.baseline_period is None
                or self.comparison_period is None
            ):
                raise ValueError("PAIR frame requires baseline+comparison only")
            if (
                self.baseline_period.time_dimension != self.time_dimension
                or self.comparison_period.time_dimension != self.time_dimension
            ):
                raise ValueError("PAIR frame must use one governed time dimension")
            if (
                self.baseline_period.start,
                self.baseline_period.end,
            ) == (
                self.comparison_period.start,
                self.comparison_period.end,
            ):
                raise ValueError("PAIR frame periods must be distinct")
            return self

        if (
            self.span_period is None
            or self.baseline_period is not None
            or self.comparison_period is not None
        ):
            raise ValueError("SPAN frame requires one bounded span only")
        if self.span_period.time_dimension != self.time_dimension:
            raise ValueError("SPAN frame must use its governed time dimension")
        if self.span_period.end is None:
            raise ValueError("SPAN frame must be bounded")
        return self


class AnalyticalRankingInvariant(FrozenModel):
    """Native ranking WHAT; Metabot still owns analytical HOW."""

    kind: Literal["native_metric"] = "native_metric"
    measure: str = Field(min_length=1)
    direction: Literal["asc", "desc"]
    limit: int | None = Field(default=None, ge=1, le=1000)
    basis: RankingBasis = RankingBasis.LEVEL


class AnalyticalEvidenceSynthesisRankingInvariant(FrozenModel):
    """Ranking obligation satisfied from governed evidence, not native ORDER BY."""

    kind: Literal["evidence_synthesis"] = "evidence_synthesis"
    direction: Literal["asc", "desc", "unspecified"] = "unspecified"
    limit: int | None = Field(default=None, ge=1, le=1000)


class AnalyticalRequestContract(FrozenModel):
    authority_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    scope_identity: AnalyticalScopeIdentity
    scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    metric_refs: tuple[str, ...] = Field(min_length=1)
    dimension_refs: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterInvariant, ...] = ()
    period: AnalyticalPeriodInvariant | None = None
    comparison: AnalyticalComparisonInvariant | None = None
    temporal_observation: AnalyticalTemporalObservationInvariant | None = None
    temporal_change_frame: AnalyticalTemporalChangeFrame | None = None
    ranking: (
        AnalyticalRankingInvariant
        | AnalyticalEvidenceSynthesisRankingInvariant
        | None
    ) = None
    grain_constraints: tuple[str, ...] = ()
    requested_output_surfaces: tuple[str, ...] = ()

    @property
    def material_fingerprint(self) -> str:
        """Stable material need identity, independent of session/version provenance."""
        payload = {
            "semantic_context_version": self.semantic_context_version,
            "scope_fingerprint": self.scope_fingerprint,
            "metric_refs": sorted(self.metric_refs),
            "dimension_refs": sorted(self.dimension_refs),
            "filters": sorted(
                (
                    item.model_dump(mode="json")
                    for item in self.filters
                ),
                key=lambda item: (
                    item["semantic_ref"],
                    item["source_candidate_id"],
                    item["dimension_name"],
                    item["value"],
                ),
            ),
            "period": (
                self.period.model_dump(mode="json")
                if self.period is not None
                else None
            ),
            "comparison": (
                self.comparison.model_dump(mode="json")
                if self.comparison is not None
                else None
            ),
            "temporal_observation": (
                self.temporal_observation.model_dump(mode="json")
                if self.temporal_observation is not None
                else None
            ),
            "temporal_change_frame": (
                self.temporal_change_frame.model_dump(mode="json")
                if self.temporal_change_frame is not None
                else None
            ),
            "ranking": (
                self.ranking.model_dump(mode="json")
                if self.ranking is not None
                else None
            ),
            "grain_constraints": sorted(self.grain_constraints),
            "requested_output_surfaces": sorted(
                self.requested_output_surfaces
            ),
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @property
    def fingerprint(self) -> str:
        # Backward-compatible alias for call sites that already treat this as
        # material identity. Authority/request provenance lives in separate fields.
        return self.material_fingerprint

    @model_validator(mode="after")
    def coherent_ranking_basis(self):
        ranking = self.ranking
        if not (
            isinstance(ranking, AnalyticalRankingInvariant)
            and ranking.basis == RankingBasis.CHANGE
        ):
            return self
        if self.temporal_change_frame is not None:
            return self
        # Compatibility for older deterministic PAIR fixtures: accepted
        # comparison authority predates the explicit read-only frame view.
        # SPAN is never inferred from an arbitrary period at this boundary;
        # forward Research must project its explicit TemporalChangeFrame.
        if self.comparison is not None:
            return self
        raise ValueError(
            "change ranking requires typed PAIR or bounded SPAN authority"
        )

    @model_validator(mode="after")
    def coherent_temporal_change_frame(self):
        frame = self.temporal_change_frame
        ranking = self.ranking
        if frame is None:
            return self
        if (
            not isinstance(ranking, AnalyticalRankingInvariant)
            or ranking.basis != RankingBasis.CHANGE
        ):
            raise ValueError("temporal change frame requires CHANGE ranking")
        if frame.mode == TemporalChangeFrameMode.PAIR:
            if self.comparison is None:
                raise ValueError("PAIR frame requires accepted comparison authority")
            if self.period is not None:
                raise ValueError("PAIR frame cannot also use one span period")
            expected = (
                self.comparison.reference_period,
                self.comparison.base_period,
            )
            observed = (
                frame.baseline_period,
                frame.comparison_period,
            )
            if observed != expected:
                raise ValueError("PAIR frame must be a view of accepted comparison authority")
        else:
            if self.period is None or self.comparison is not None:
                raise ValueError("SPAN frame requires one accepted period and no comparison")
            if frame.span_period != self.period:
                raise ValueError("SPAN frame must be a view of accepted period authority")
        return self

    @model_validator(mode="after")
    def coherent_temporal_observation(self):
        requirement = self.temporal_observation
        if requirement is None:
            return self
        if self.comparison is not None:
            time_dimensions = {
                self.comparison.base_period.time_dimension,
                self.comparison.reference_period.time_dimension,
            }
        elif self.period is not None:
            time_dimensions = {self.period.time_dimension}
        else:
            # Observation-only CHANGE authority owns a governed time axis
            # without manufacturing a user calendar filter. Native/result
            # validation still requires that exact axis as a breakout.
            time_dimensions = {requirement.time_dimension}
        if time_dimensions != {requirement.time_dimension}:
            raise ValueError(
                "temporal change observation dimension must match accepted time"
            )
        return self



class MaterialCoverageContract(FrozenModel):
    """Deterministic material need projected from accepted analytical authority.

    This is not a second truth store and never describes SQL/MBQL. It separates
    what one analytical operation must make observable from material that is
    semantically legal but not required. The user-authorized scope identity stays
    on AnalyticalRequestContract; this projection is execution-local.
    """

    scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    required_metric_refs: tuple[str, ...] = Field(min_length=1)
    allowed_metric_refs: tuple[str, ...] = Field(min_length=1)
    required_breakout_refs: tuple[str, ...] = ()
    allowed_breakout_refs: tuple[str, ...] = ()
    exact_filter_source_refs: tuple[str, ...] = ()
    time_dimension_ref: str | None = None
    time_breakout_requirement: Literal["none", "allowed", "required"] = "none"
    ranking_rowset_constraint: bool = False

    @model_validator(mode="after")
    def required_is_subset_of_allowed(self):
        if not set(self.required_metric_refs).issubset(
            set(self.allowed_metric_refs)
        ):
            raise ValueError("required metrics must be allowed material")
        if not set(self.required_breakout_refs).issubset(
            set(self.allowed_breakout_refs)
        ):
            raise ValueError("required breakouts must be allowed material")
        if (
            self.time_breakout_requirement != "none"
            and self.time_dimension_ref is None
        ):
            raise ValueError("time breakout policy requires a governed time ref")
        return self


def _contract_time_dimension(
    contract: AnalyticalRequestContract,
) -> str | None:
    if contract.comparison is not None:
        values = {
            contract.comparison.base_period.time_dimension,
            contract.comparison.reference_period.time_dimension,
        }
        if len(values) != 1:
            raise ValueError("comparison material spans multiple time dimensions")
        return next(iter(values))
    if contract.temporal_observation is not None:
        return contract.temporal_observation.time_dimension
    if contract.period is not None:
        return contract.period.time_dimension
    return None


def material_coverage_contract(
    contract: AnalyticalRequestContract,
) -> MaterialCoverageContract:
    """Project required/allowed material algebra without changing authority.

    Current metric semantics are intentionally closed: every requested governed
    metric is required and no additional metric is legal unless a future typed
    authority explicitly expands allowed_metric_refs.

    Dimension semantics distinguish required analytical breakouts from an
    accepted temporal field that Metabase may expose as useful grain inside a
    bounded period. Exact equality-filter redundancy is handled at the native
    binding boundary because the filter's entity-value ref and its dimension ref
    can legally map to the same stable field identity.
    """

    required_breakouts = tuple(dict.fromkeys(contract.dimension_refs))
    allowed_breakouts = list(required_breakouts)
    time_ref = _contract_time_dimension(contract)
    time_policy: Literal["none", "allowed", "required"] = "none"
    if time_ref is not None:
        if (
            contract.comparison is not None
            or contract.temporal_observation is not None
        ):
            time_policy = "required"
            if time_ref not in required_breakouts:
                required_breakouts = tuple(
                    (*required_breakouts, time_ref)
                )
            if time_ref not in allowed_breakouts:
                allowed_breakouts.append(time_ref)
        elif contract.period is not None:
            time_policy = "allowed"
            if time_ref not in allowed_breakouts:
                allowed_breakouts.append(time_ref)

    ranking_rowset_constraint = bool(
        isinstance(contract.ranking, AnalyticalRankingInvariant)
        and contract.ranking.limit is not None
    )
    return MaterialCoverageContract(
        scope_fingerprint=contract.scope_fingerprint,
        material_fingerprint=contract.material_fingerprint,
        required_metric_refs=tuple(dict.fromkeys(contract.metric_refs)),
        allowed_metric_refs=tuple(dict.fromkeys(contract.metric_refs)),
        required_breakout_refs=required_breakouts,
        allowed_breakout_refs=tuple(allowed_breakouts),
        exact_filter_source_refs=tuple(
            dict.fromkeys(
                item.source_candidate_id for item in contract.filters
            )
        ),
        time_dimension_ref=time_ref,
        time_breakout_requirement=time_policy,
        ranking_rowset_constraint=ranking_rowset_constraint,
    )


class AnalyticalRequestObservation(FrozenModel):
    """Engine-reported material semantics, never physical query implementation."""

    scope_identity: AnalyticalScopeIdentity
    metric_refs: tuple[str, ...] = Field(min_length=1)
    dimension_refs: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterInvariant, ...] = ()
    period: AnalyticalPeriodInvariant | None = None
    comparison: AnalyticalComparisonInvariant | None = None
    temporal_observation: AnalyticalTemporalObservationInvariant | None = None
    ranking: (
        AnalyticalRankingInvariant
        | AnalyticalEvidenceSynthesisRankingInvariant
        | None
    ) = None
    grain_constraints: tuple[str, ...] = ()
    requested_output_surfaces: tuple[str, ...] = ()


class NativeAnalyticalRequestObservation(FrozenModel):
    """Material semantic observation bound to one exact native occurrence.

    The semantics are compared to AnalyticalRequestContract. The identity fields
    bind that observation to the exact engine attestation/artifact; no SQL/MBQL
    representation is carried or interpreted here.
    """

    attestation_id: str = Field(min_length=1)
    native_conversation_id: UUID
    native_query_id: str = Field(min_length=1)
    exact_artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    request: AnalyticalRequestObservation


class AnalyticalRequestMismatch(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _period(value: ResolvedPeriod) -> AnalyticalPeriodInvariant:
    return AnalyticalPeriodInvariant(
        kind=value.kind,
        time_dimension=value.time_dimension,
        start=value.start,
        end=value.end,
    )


def _comparison(value: ResolvedComparison) -> AnalyticalComparisonInvariant:
    return AnalyticalComparisonInvariant(
        mode=value.mode,
        base_period=_period(value.base_period),
        reference_period=_period(value.reference_period),
    )


def _ranking(value: ResolvedRanking) -> AnalyticalRankingInvariant:
    return AnalyticalRankingInvariant(
        measure=value.measure,
        direction=value.direction,
        limit=value.limit,
    )


def _filter(value: ResolvedFilterRef) -> AnalyticalFilterInvariant:
    return AnalyticalFilterInvariant(
        semantic_ref=value.semantic_ref,
        source_candidate_id=value.source_candidate_id,
        dimension_name=value.dimension_name,
        value=value.value,
    )


def analytical_request_contract_from_intent(
    intent: ResolvedAnalyticsIntent,
    *,
    scope_lineage_id: str,
    scope_version_id: str,
    requested_output_surfaces: tuple[str, ...] = (),
) -> AnalyticalRequestContract:
    """Project accepted material invariants without inspecting a query artifact."""

    return AnalyticalRequestContract(
        authority_id=intent.authority_id,
        request_ref=intent.request_ref,
        semantic_context_version=intent.semantic_context_version,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id=scope_lineage_id,
            version_id=scope_version_id,
        ),
        metric_refs=tuple(item.semantic_ref for item in intent.metrics),
        dimension_refs=tuple(item.semantic_ref for item in intent.dimensions),
        filters=tuple(_filter(item) for item in intent.filters),
        period=_period(intent.period) if intent.period is not None else None,
        comparison=(
            _comparison(intent.comparison)
            if intent.comparison is not None
            else None
        ),
        ranking=_ranking(intent.ranking) if intent.ranking is not None else None,
        grain_constraints=intent.grain_constraints,
        requested_output_surfaces=tuple(
            dict.fromkeys(requested_output_surfaces)
        ),
    )


def observation_from_contract(
    contract: AnalyticalRequestContract,
) -> AnalyticalRequestObservation:
    """Test/adapter seam for a native semantic observation with no query-plan facts."""

    return AnalyticalRequestObservation(
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


def native_observation_from_contract(
    contract: AnalyticalRequestContract,
    *,
    attestation_id: str,
    native_conversation_id: UUID | str,
    native_query_id: str,
    exact_artifact_fingerprint: str,
) -> NativeAnalyticalRequestObservation:
    """Adapter/test seam for already-observed native material semantics."""

    return NativeAnalyticalRequestObservation(
        attestation_id=attestation_id,
        native_conversation_id=native_conversation_id,
        native_query_id=native_query_id,
        exact_artifact_fingerprint=exact_artifact_fingerprint,
        request=observation_from_contract(contract),
    )



def _filter_identity(
    value: AnalyticalFilterInvariant,
) -> tuple[str, str, str, str]:
    return (
        value.semantic_ref,
        value.source_candidate_id,
        value.dimension_name,
        value.value,
    )


def _set_is_narrowing_or_extension(
    parent_values,
    child_values,
) -> bool:
    parent_set = set(parent_values)
    child_set = set(child_values)
    return (
        parent_set.issubset(child_set)
        or child_set.issubset(parent_set)
    )


def assert_child_request_scope(
    parent: AnalyticalRequestContract,
    child: AnalyticalRequestContract,
) -> None:
    """Validate one typed P17 child scope without creating a second planner.

    Child execution stays inside the same accepted authority/context/version.
    It may retain the parent material scope or explicitly narrow/extend exactly
    one set-like analytical family. Time, comparison, ranking and output intent
    require a versioned ResearchScope change rather than a P17 child mutation.
    """

    immutable_checks = (
        ("AUTHORITY", parent.authority_id, child.authority_id),
        (
            "SEMANTIC_CONTEXT",
            parent.semantic_context_version,
            child.semantic_context_version,
        ),
        ("SCOPE", parent.scope_identity, child.scope_identity),
    )
    for label, expected, actual in immutable_checks:
        if expected != actual:
            raise AnalyticalRequestMismatch(
                f"ANALYTICAL_CHILD_{label}_MISMATCH",
                f"P17 child changed accepted {label.lower()} identity",
            )

    if parent.period != child.period:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_TIME_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted time without a scope version change",
        )
    if parent.comparison != child.comparison:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_COMPARISON_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted comparison intent",
        )
    if parent.temporal_observation != child.temporal_observation:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_TEMPORAL_OBSERVATION_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted effect-observation intent",
        )
    if parent.ranking != child.ranking:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_RANKING_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted ranking basis",
        )
    if parent.requested_output_surfaces != child.requested_output_surfaces:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_OUTPUT_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted output surfaces",
        )

    changed: list[tuple[str, tuple, tuple]] = []
    if parent.metric_refs != child.metric_refs:
        changed.append(("METRIC", parent.metric_refs, child.metric_refs))

    dimension_changed = (
        parent.dimension_refs != child.dimension_refs
        or parent.grain_constraints != child.grain_constraints
    )
    if dimension_changed:
        if (
            parent.grain_constraints != parent.dimension_refs
            or child.grain_constraints != child.dimension_refs
        ):
            raise AnalyticalRequestMismatch(
                "ANALYTICAL_CHILD_DIMENSION_GRAIN_MISMATCH",
                "P17 child dimension mutation must preserve dimension/grain identity",
            )
        changed.append(
            ("DIMENSION", parent.dimension_refs, child.dimension_refs)
        )

    parent_filters = tuple(_filter_identity(x) for x in parent.filters)
    child_filters = tuple(_filter_identity(x) for x in child.filters)
    if parent_filters != child_filters:
        changed.append(("FILTER", parent_filters, child_filters))

    if len(changed) > 1:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_MULTI_DIMENSION_MUTATION",
            "P17 child may narrow or extend only one analytical family",
        )
    if not changed:
        return

    label, expected, actual = changed[0]
    if label == "METRIC" and not actual:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_METRIC_SCOPE_EMPTY",
            "P17 child must retain at least one accepted metric",
        )
    if not _set_is_narrowing_or_extension(expected, actual):
        raise AnalyticalRequestMismatch(
            f"ANALYTICAL_CHILD_{label}_REPLACEMENT_FORBIDDEN",
            (
                "P17 child scope must be a typed narrowing/extension, "
                "not an unrelated replacement"
            ),
        )


def assert_request_invariants(
    contract: AnalyticalRequestContract,
    observation: AnalyticalRequestObservation,
) -> None:
    checks = (
        ("SCOPE", contract.scope_identity, observation.scope_identity),
        ("METRIC", contract.metric_refs, observation.metric_refs),
        ("DIMENSION", contract.dimension_refs, observation.dimension_refs),
        ("FILTER", contract.filters, observation.filters),
        ("TIME", contract.period, observation.period),
        ("COMPARISON", contract.comparison, observation.comparison),
        (
            "TEMPORAL_OBSERVATION",
            contract.temporal_observation,
            observation.temporal_observation,
        ),
        ("RANKING", contract.ranking, observation.ranking),
        ("GRAIN", contract.grain_constraints, observation.grain_constraints),
        (
            "OUTPUT_SURFACE",
            contract.requested_output_surfaces,
            observation.requested_output_surfaces,
        ),
    )
    for label, expected, actual in checks:
        if expected != actual:
            raise AnalyticalRequestMismatch(
                f"ANALYTICAL_REQUEST_{label}_MISMATCH",
                f"accepted {label.lower()} invariant changed",
            )
