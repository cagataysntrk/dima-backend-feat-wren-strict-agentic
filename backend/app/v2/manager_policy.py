"""Registered Day 6.5 Manager capabilities and their semantic binding algebra.

This registry is the single source of truth for which semantic roles and operation
parameters each capability may carry. It contains no user-language rules and no
provider/model-specific behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.v2.manager_models import ManagerCapabilityKey


class ManagerCapabilityLane(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"
    PRESENTATION = "PRESENTATION"


_STANDARD_KINDS = frozenset({"metric", "dimension", "filter", "period", "comparison"})
_RESEARCH_KINDS = _STANDARD_KINDS


@dataclass(frozen=True)
class ManagerCapabilitySpec:
    key: ManagerCapabilityKey
    lane: ManagerCapabilityLane
    executable: bool = True
    required_kinds: frozenset[str] = field(default_factory=frozenset)
    exclusion_required_kinds: frozenset[str] = field(default_factory=frozenset)
    allowed_kinds: frozenset[str] = field(default_factory=frozenset)
    required_params: frozenset[str] = field(default_factory=frozenset)
    allowed_params: frozenset[str] = field(default_factory=frozenset)
    effect_family: str | None = None


class ManagerCapabilityRegistry:
    _SPECS = {
        ManagerCapabilityKey.PERFORMANCE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.PERFORMANCE,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric"}),
            exclusion_required_kinds=frozenset({"metric"}),
            allowed_kinds=frozenset({"metric", "filter", "period"}),
            effect_family="measure",
        ),
        ManagerCapabilityKey.BREAKDOWN: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.BREAKDOWN,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric", "dimension"}),
            exclusion_required_kinds=frozenset({"dimension"}),
            allowed_kinds=frozenset({"metric", "dimension", "filter", "period"}),
            effect_family="group_by",
        ),
        ManagerCapabilityKey.RANKING: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.RANKING,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric", "dimension"}),
            # "sıralama yapma" can be a generic exclusion; semantic scope is optional.
            exclusion_required_kinds=frozenset(),
            allowed_kinds=frozenset({"metric", "dimension", "filter", "period"}),
            required_params=frozenset({"ranking_direction", "ranking_limit"}),
            allowed_params=frozenset({"ranking_direction", "ranking_limit"}),
            effect_family="rank",
        ),
        ManagerCapabilityKey.COMPARISON: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.COMPARISON,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric", "comparison"}),
            exclusion_required_kinds=frozenset({"comparison"}),
            allowed_kinds=frozenset({"metric", "comparison", "period", "filter"}),
            effect_family="compare",
        ),
        ManagerCapabilityKey.RELATIONSHIP: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.RELATIONSHIP,
            lane=ManagerCapabilityLane.RESEARCH,
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="relationship",
        ),
        ManagerCapabilityKey.ROOT_CAUSE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.ROOT_CAUSE,
            lane=ManagerCapabilityLane.RESEARCH,
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="root_cause",
        ),
        ManagerCapabilityKey.TREND: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.TREND,
            lane=ManagerCapabilityLane.RESEARCH,
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="trend",
        ),
        ManagerCapabilityKey.REPORT: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.REPORT,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="report",
        ),
        ManagerCapabilityKey.TABLE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.TABLE,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="table",
        ),
        ManagerCapabilityKey.CHART: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.CHART,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="chart",
        ),
        ManagerCapabilityKey.EXPLAIN: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.EXPLAIN,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="explain",
        ),
    }

    def get(self, key: ManagerCapabilityKey) -> ManagerCapabilitySpec:
        try:
            return self._SPECS[key]
        except KeyError as exc:
            raise KeyError(f"unregistered Manager capability: {key}") from exc

    def registered(self, key: ManagerCapabilityKey) -> bool:
        return key in self._SPECS
