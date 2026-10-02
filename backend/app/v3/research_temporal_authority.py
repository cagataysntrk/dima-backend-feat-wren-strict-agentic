"""Typed temporal-authority resolution for Research material.

This module separates user calendar scope from temporal observation material.
It never parses wording, invents dates, plans queries, or performs analytics.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.v3.research_contracts import CausalEffectObservation


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


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
    """Resolve CHANGE material without manufacturing calendar authority.

    Explicit accepted periods stay exact. When the user asks about change but
    supplies no calendar bounds, one uniquely governed temporal dimension may
    be used only as an observation axis. Multiple axes require clarification;
    absence of any governed axis is unsupported.
    """

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
