"""Canonical typed temporal authority for Research.

Temporal meaning is resolved once from accepted typed periods and then projected
through ScopePatch, AnalyticalRequestContract and AnalyticalIntentV1.  This
module never parses wording, invents dates, plans queries, or performs analytics.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.v3.research_contracts import (
    CausalEffectObservation,
    ResearchTimePeriod,
    TemporalChangeFrameMode,
    TemporalRole,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class TemporalAuthorityError(ValueError):
    """Typed temporal authority cannot represent the accepted frames safely."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class CanonicalTemporalAuthority(Frozen):
    """One scope-level temporal meaning over canonical accepted periods."""

    periods: tuple[ResearchTimePeriod, ...] = ()
    change_frame_mode: TemporalChangeFrameMode | None = None
    baseline_period: ResearchTimePeriod | None = None
    comparison_period: ResearchTimePeriod | None = None
    span_period: ResearchTimePeriod | None = None

    def model_post_init(self, __context) -> None:
        if self.change_frame_mode == TemporalChangeFrameMode.PAIR:
            if (
                self.baseline_period is None
                or self.comparison_period is None
                or self.span_period is not None
            ):
                raise ValueError("PAIR temporal authority requires baseline+comparison only")
        elif self.change_frame_mode == TemporalChangeFrameMode.SPAN:
            if (
                self.span_period is None
                or self.baseline_period is not None
                or self.comparison_period is not None
            ):
                raise ValueError("SPAN temporal authority requires one bounded span only")
        elif any(
            item is not None
            for item in (
                self.baseline_period,
                self.comparison_period,
                self.span_period,
            )
        ):
            raise ValueError("untyped temporal authority cannot carry a change frame")


def _period_identity(
    value: ResearchTimePeriod,
) -> tuple[str, str, str, str]:
    return (
        value.time_dimension_candidate_id,
        value.start,
        value.end,
        value.role.value,
    )


def resolve_temporal_authority(
    periods: tuple[ResearchTimePeriod, ...],
    *,
    require_change_frame: bool = False,
) -> CanonicalTemporalAuthority:
    """Canonicalize exact duplicate frames and resolve one scope-level frame.

    Exact duplicate typed periods are coalesced. A true role-bound baseline /
    comparison pair is PAIR. A bounded MATERIAL_WINDOW becomes SPAN only when
    the accepted analytical semantics explicitly require a CHANGE frame.
    Neutral material windows remain neutral. Distinct simultaneous change
    frames are never guessed or ordered.
    """

    canonical: list[ResearchTimePeriod] = []
    seen: set[tuple[str, str, str, str]] = set()
    for item in periods:
        identity = _period_identity(item)
        if identity in seen:
            continue
        seen.add(identity)
        canonical.append(item)

    baseline = tuple(
        item for item in canonical
        if item.role == TemporalRole.BASELINE_PERIOD
    )
    comparison = tuple(
        item for item in canonical
        if item.role == TemporalRole.COMPARISON_PERIOD
    )
    spans = tuple(
        item for item in canonical
        if item.role == TemporalRole.MATERIAL_WINDOW
    )

    if baseline or comparison:
        if len(baseline) != 1 or len(comparison) != 1:
            raise TemporalAuthorityError(
                "TEMPORAL_PAIR_AMBIGUOUS",
                "temporal comparison requires exactly one distinct baseline and comparison frame",
            )
        if spans:
            raise TemporalAuthorityError(
                "TEMPORAL_FRAME_AMBIGUOUS",
                "PAIR and SPAN temporal meanings cannot be active simultaneously",
            )
        if (
            baseline[0].time_dimension_candidate_id
            != comparison[0].time_dimension_candidate_id
        ):
            raise TemporalAuthorityError(
                "TEMPORAL_TIME_DIMENSION_DRIFT",
                "one temporal frame cannot span two governed time dimensions",
            )
        return CanonicalTemporalAuthority(
            periods=tuple(canonical),
            change_frame_mode=TemporalChangeFrameMode.PAIR,
            baseline_period=baseline[0],
            comparison_period=comparison[0],
        )

    if require_change_frame and spans:
        if len(spans) != 1:
            raise TemporalAuthorityError(
                "TEMPORAL_SPAN_AMBIGUOUS",
                "multiple distinct bounded SPAN change frames require clarification",
            )
        return CanonicalTemporalAuthority(
            periods=tuple(canonical),
            change_frame_mode=TemporalChangeFrameMode.SPAN,
            span_period=spans[0],
        )

    # MATERIAL_WINDOW is neutral temporal material unless the accepted
    # analytical semantics explicitly require a CHANGE frame. Multiple neutral
    # windows are legal governed scope and must not be promoted to ambiguity by
    # a presentation-independent temporal resolver.
    return CanonicalTemporalAuthority(periods=tuple(canonical))


class ChangeTemporalAuthorityDisposition(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    EXPLICIT_BOUNDED = "EXPLICIT_BOUNDED"
    OBSERVE_GOVERNED_TIME = "OBSERVE_GOVERNED_TIME"
    CLARIFY_TIME_AXIS = "CLARIFY_TIME_AXIS"
    BLOCKED_NO_TIME_AXIS = "BLOCKED_NO_TIME_AXIS"


class ChangeTemporalAuthority(Frozen):
    disposition: ChangeTemporalAuthorityDisposition
    time_dimension_id: str | None = Field(default=None, min_length=1)

    def model_post_init(self, __context) -> None:
        if (
            self.disposition
            == ChangeTemporalAuthorityDisposition.OBSERVE_GOVERNED_TIME
        ) != (self.time_dimension_id is not None):
            raise ValueError(
                "only governed-time observation may carry an implicit time axis"
            )


def resolve_change_temporal_authority(
    *,
    effect_observation: CausalEffectObservation | None,
    explicit_temporal_material: bool,
    governed_temporal_dimension_ids: tuple[str, ...],
) -> ChangeTemporalAuthority:
    """Resolve CHANGE material without manufacturing calendar authority."""

    if effect_observation != CausalEffectObservation.CHANGE:
        return ChangeTemporalAuthority(
            disposition=ChangeTemporalAuthorityDisposition.NOT_APPLICABLE
        )
    if explicit_temporal_material:
        return ChangeTemporalAuthority(
            disposition=ChangeTemporalAuthorityDisposition.EXPLICIT_BOUNDED
        )

    ids = tuple(dict.fromkeys(governed_temporal_dimension_ids))
    if len(ids) == 1:
        return ChangeTemporalAuthority(
            disposition=(
                ChangeTemporalAuthorityDisposition.OBSERVE_GOVERNED_TIME
            ),
            time_dimension_id=ids[0],
        )
    if len(ids) > 1:
        return ChangeTemporalAuthority(
            disposition=ChangeTemporalAuthorityDisposition.CLARIFY_TIME_AXIS
        )
    return ChangeTemporalAuthority(
        disposition=ChangeTemporalAuthorityDisposition.BLOCKED_NO_TIME_AXIS
    )
