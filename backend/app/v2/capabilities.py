"""Typed analytics capability registry for V2 routing.

This module contains no user-language parsing, provider/model branches, domain literals,
or execution logic. It only declares which typed analytical operations Core can express
and which require Research orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.v2.models import ResearchNonRelationshipGoalKind


class AnalyticsCapabilityLane(StrEnum):
    CORE_STANDARD = "core_standard"
    RESEARCH = "research"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AnalyticsCapabilityAssessment:
    lanes: tuple[AnalyticsCapabilityLane, ...]

    @property
    def has_blocked(self) -> bool:
        return AnalyticsCapabilityLane.BLOCKED in self.lanes

    @property
    def has_research(self) -> bool:
        return AnalyticsCapabilityLane.RESEARCH in self.lanes

    @property
    def all_standard(self) -> bool:
        return bool(self.lanes) and all(
            lane == AnalyticsCapabilityLane.CORE_STANDARD for lane in self.lanes
        )


class AnalyticsCapabilityRegistry:
    """Single owner for typed operation capability declarations.

    Adding a new operation changes this registry, not routing conditionals scattered
    across the product. OTHER is intentionally absent from accepted capability maps:
    unclassified semantics fail closed.
    """

    _LANES = {
        ResearchNonRelationshipGoalKind.PERFORMANCE: AnalyticsCapabilityLane.CORE_STANDARD,
        ResearchNonRelationshipGoalKind.BREAKDOWN: AnalyticsCapabilityLane.CORE_STANDARD,
        ResearchNonRelationshipGoalKind.RANKING: AnalyticsCapabilityLane.CORE_STANDARD,
        ResearchNonRelationshipGoalKind.COMPARISON: AnalyticsCapabilityLane.CORE_STANDARD,
        ResearchNonRelationshipGoalKind.ROOT_CAUSE: AnalyticsCapabilityLane.RESEARCH,
        ResearchNonRelationshipGoalKind.TREND: AnalyticsCapabilityLane.RESEARCH,
    }

    def lane_for(
        self,
        kind: ResearchNonRelationshipGoalKind,
    ) -> AnalyticsCapabilityLane:
        return self._LANES.get(kind, AnalyticsCapabilityLane.BLOCKED)

    def assess(
        self,
        kinds: tuple[ResearchNonRelationshipGoalKind, ...],
    ) -> AnalyticsCapabilityAssessment:
        return AnalyticsCapabilityAssessment(
            lanes=tuple(self.lane_for(kind) for kind in kinds)
        )

    @property
    def standard_capabilities(self) -> frozenset[ResearchNonRelationshipGoalKind]:
        return frozenset(
            kind
            for kind, lane in self._LANES.items()
            if lane == AnalyticsCapabilityLane.CORE_STANDARD
        )
