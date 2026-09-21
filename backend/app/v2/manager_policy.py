"""Registered Day 6.5 Manager capabilities.

This is the only vocabulary the acceptance/representability layer understands. It
contains no user-language rules and no provider/model-specific behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.v2.manager_models import ManagerCapabilityKey


class ManagerCapabilityLane(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"
    PRESENTATION = "PRESENTATION"


@dataclass(frozen=True)
class ManagerCapabilitySpec:
    key: ManagerCapabilityKey
    lane: ManagerCapabilityLane
    executable: bool = True


class ManagerCapabilityRegistry:
    _SPECS = {
        ManagerCapabilityKey.PERFORMANCE: ManagerCapabilitySpec(
            ManagerCapabilityKey.PERFORMANCE, ManagerCapabilityLane.STANDARD
        ),
        ManagerCapabilityKey.BREAKDOWN: ManagerCapabilitySpec(
            ManagerCapabilityKey.BREAKDOWN, ManagerCapabilityLane.STANDARD
        ),
        ManagerCapabilityKey.RANKING: ManagerCapabilitySpec(
            ManagerCapabilityKey.RANKING, ManagerCapabilityLane.STANDARD
        ),
        ManagerCapabilityKey.COMPARISON: ManagerCapabilitySpec(
            ManagerCapabilityKey.COMPARISON, ManagerCapabilityLane.STANDARD
        ),
        ManagerCapabilityKey.RELATIONSHIP: ManagerCapabilitySpec(
            ManagerCapabilityKey.RELATIONSHIP, ManagerCapabilityLane.RESEARCH
        ),
        ManagerCapabilityKey.ROOT_CAUSE: ManagerCapabilitySpec(
            ManagerCapabilityKey.ROOT_CAUSE, ManagerCapabilityLane.RESEARCH
        ),
        ManagerCapabilityKey.TREND: ManagerCapabilitySpec(
            ManagerCapabilityKey.TREND, ManagerCapabilityLane.RESEARCH
        ),
        ManagerCapabilityKey.REPORT: ManagerCapabilitySpec(
            ManagerCapabilityKey.REPORT, ManagerCapabilityLane.PRESENTATION, executable=False
        ),
        ManagerCapabilityKey.TABLE: ManagerCapabilitySpec(
            ManagerCapabilityKey.TABLE, ManagerCapabilityLane.PRESENTATION, executable=False
        ),
        ManagerCapabilityKey.CHART: ManagerCapabilitySpec(
            ManagerCapabilityKey.CHART, ManagerCapabilityLane.PRESENTATION, executable=False
        ),
        ManagerCapabilityKey.EXPLAIN: ManagerCapabilitySpec(
            ManagerCapabilityKey.EXPLAIN, ManagerCapabilityLane.PRESENTATION, executable=False
        ),
    }

    def get(self, key: ManagerCapabilityKey) -> ManagerCapabilitySpec:
        try:
            return self._SPECS[key]
        except KeyError as exc:
            raise KeyError(f"unregistered Manager capability: {key}") from exc

    def registered(self, key: ManagerCapabilityKey) -> bool:
        return key in self._SPECS
