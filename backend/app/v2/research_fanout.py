"""Day 7 deterministic cardinality-aware Research fanout policy.

This module never decides semantic truth and never mints members. It only limits an
already-governed candidate set using cardinality information when available, the
canonical Manager query budget, and branch depth.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from app.v2.models import FrozenModel


class CardinalitySource(StrEnum):
    GOVERNED_METADATA = "GOVERNED_METADATA"
    VERIFIED_EVIDENCE = "VERIFIED_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class CardinalityClass(StrEnum):
    LOW = "LOW"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class FanoutStrategy(StrEnum):
    COMPLETE_BOUNDED = "COMPLETE_BOUNDED"
    BOUNDED_SUBSET = "BOUNDED_SUBSET"
    BOUNDED_TOP_K = "BOUNDED_TOP_K"
    CONSERVATIVE_BOUNDED = "CONSERVATIVE_BOUNDED"
    STOP = "STOP"


class CardinalityObservation(FrozenModel):
    estimate: int | None = Field(default=None, ge=0)
    source: CardinalitySource
    exact: bool = False

    @model_validator(mode="after")
    def _source_consistency(self):
        if self.source == CardinalitySource.UNKNOWN:
            if self.estimate is not None or self.exact:
                raise ValueError("UNKNOWN cardinality cannot claim an estimate/exactness")
        elif self.estimate is None:
            raise ValueError("known cardinality source requires an estimate")
        return self


class FanoutRequest(FrozenModel):
    candidate_keys: tuple[str, ...]
    cardinality: CardinalityObservation
    remaining_query_budget: int = Field(ge=0)
    current_branch_depth: int = Field(ge=0)
    max_branch_depth: int = Field(default=3, ge=1)
    max_children: int = Field(default=4, ge=1)
    unknown_children: int = Field(default=2, ge=1)

    @model_validator(mode="after")
    def _unknown_bound(self):
        if self.unknown_children > self.max_children:
            raise ValueError("unknown_children cannot exceed max_children")
        return self


class FanoutDecision(FrozenModel):
    classification: CardinalityClass
    allowed_children: int = Field(ge=0)
    strategy: FanoutStrategy
    selected_candidate_keys: tuple[str, ...] = ()
    deduplicated_candidate_count: int = Field(ge=0)
    reason: str


class ResearchFanoutPolicy:
    """Bound fanout without becoming semantic or interestingness authority."""

    @staticmethod
    def _dedupe(keys: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(key for key in keys if str(key).strip()))

    def decide(self, request: FanoutRequest) -> FanoutDecision:
        candidates = self._dedupe(request.candidate_keys)
        observation = request.cardinality

        if observation.estimate is None:
            classification = CardinalityClass.UNKNOWN
        elif observation.estimate <= request.max_children:
            classification = CardinalityClass.LOW
        else:
            classification = CardinalityClass.HIGH

        if not candidates:
            return FanoutDecision(
                classification=classification,
                allowed_children=0,
                strategy=FanoutStrategy.STOP,
                deduplicated_candidate_count=0,
                reason="no governed candidate branches",
            )

        if request.current_branch_depth >= request.max_branch_depth:
            return FanoutDecision(
                classification=classification,
                allowed_children=0,
                strategy=FanoutStrategy.STOP,
                deduplicated_candidate_count=len(candidates),
                reason="branch depth exhausted",
            )

        if request.remaining_query_budget <= 0:
            return FanoutDecision(
                classification=classification,
                allowed_children=0,
                strategy=FanoutStrategy.STOP,
                deduplicated_candidate_count=len(candidates),
                reason="Research data-query budget exhausted",
            )

        if classification == CardinalityClass.LOW:
            assert observation.estimate is not None
            semantic_cap = min(observation.estimate, len(candidates))
            allowed = min(
                semantic_cap,
                request.max_children,
                request.remaining_query_budget,
            )
            strategy = (
                FanoutStrategy.COMPLETE_BOUNDED
                if allowed == semantic_cap
                else FanoutStrategy.BOUNDED_SUBSET
            )
            reason = (
                "exact/known low cardinality; enumerate only within governed candidates"
                if strategy == FanoutStrategy.COMPLETE_BOUNDED
                else "low cardinality narrowed by query budget or safety bound"
            )
        elif classification == CardinalityClass.HIGH:
            allowed = min(
                len(candidates),
                request.max_children,
                request.remaining_query_budget,
            )
            strategy = FanoutStrategy.BOUNDED_TOP_K
            reason = (
                "high cardinality; preserve caller-provided governed priority order "
                "and cap branches; no synthetic Other member is created"
            )
        else:
            allowed = min(
                len(candidates),
                request.unknown_children,
                request.max_children,
                request.remaining_query_budget,
            )
            strategy = FanoutStrategy.CONSERVATIVE_BOUNDED
            reason = (
                "cardinality unavailable; UNKNOWN is conservatively bounded and "
                "never interpreted as unlimited"
            )

        selected = candidates[:allowed]
        return FanoutDecision(
            classification=classification,
            allowed_children=allowed,
            strategy=strategy,
            selected_candidate_keys=selected,
            deduplicated_candidate_count=len(candidates),
            reason=reason,
        )


def governed_dimension_cardinality(
    *,
    schema: dict,
    cube_name: str,
    dimension_name: str,
) -> CardinalityObservation:
    """Read exact low-cardinality values only when Wren schema actually exposes them.

    Absence is UNKNOWN, not HIGH: the current catalog does not prove why values are
    absent (high cardinality, unavailable enrichment, or unsupported expression).
    """

    cube = next(
        (item for item in tuple(schema.get("cubes") or ()) if item.get("name") == cube_name),
        None,
    )
    if cube is None:
        return CardinalityObservation(source=CardinalitySource.UNKNOWN)

    values_map = cube.get("dimension_values") or {}
    values = values_map.get(dimension_name)
    if values is None:
        return CardinalityObservation(source=CardinalitySource.UNKNOWN)

    return CardinalityObservation(
        estimate=len(tuple(values)),
        source=CardinalitySource.GOVERNED_METADATA,
        exact=True,
    )
