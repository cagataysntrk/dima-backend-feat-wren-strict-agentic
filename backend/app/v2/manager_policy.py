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
    intent_description: str = ""


class ManagerCapabilityRegistry:
    _SPECS = {
        ManagerCapabilityKey.PERFORMANCE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.PERFORMANCE,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric"}),
            exclusion_required_kinds=frozenset({"metric"}),
            allowed_kinds=frozenset({"metric", "filter", "period"}),
            effect_family="measure",
            intent_description=(
                "Read/show/measure the level, value or state of a metric. "
                "Not for explaining why, causes, drivers, anomalies or decline investigation."
            ),
        ),
        ManagerCapabilityKey.BREAKDOWN: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.BREAKDOWN,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric", "dimension"}),
            exclusion_required_kinds=frozenset({"dimension"}),
            allowed_kinds=frozenset({"metric", "dimension", "filter", "period"}),
            effect_family="group_by",
            intent_description="Group/break down a metric by a requested dimension.",
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
            intent_description="Top/bottom ordering of a metric by a dimension with direction and limit.",
        ),
        ManagerCapabilityKey.COMPARISON: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.COMPARISON,
            lane=ManagerCapabilityLane.STANDARD,
            required_kinds=frozenset({"metric", "comparison"}),
            exclusion_required_kinds=frozenset({"comparison"}),
            allowed_kinds=frozenset({"metric", "comparison", "period", "filter"}),
            effect_family="compare",
            intent_description="Compare a metric against a governed reference period or comparison baseline.",
        ),
        ManagerCapabilityKey.RELATIONSHIP: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.RELATIONSHIP,
            lane=ManagerCapabilityLane.RESEARCH,
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="relationship",
            intent_description="Investigate a requested relationship/association between semantic concepts or domains.",
        ),
        ManagerCapabilityKey.ROOT_CAUSE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.ROOT_CAUSE,
            lane=ManagerCapabilityLane.RESEARCH,
            required_kinds=frozenset({"metric"}),
            exclusion_required_kinds=frozenset({"metric"}),
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="root_cause",
            intent_description=(
                "Investigate why an outcome, change, decline, increase or anomaly happened; "
                "search for causes/drivers through research orchestration."
            ),
        ),
        ManagerCapabilityKey.TREND: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.TREND,
            lane=ManagerCapabilityLane.RESEARCH,
            allowed_kinds=_RESEARCH_KINDS,
            effect_family="trend",
            intent_description="Investigate how a metric changes over time as a trend.",
        ),
        ManagerCapabilityKey.REPORT: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.REPORT,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="report",
            intent_description="Produce a report deliverable; presentation only.",
        ),
        ManagerCapabilityKey.TABLE: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.TABLE,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="table",
            intent_description="Produce a table deliverable; presentation only.",
        ),
        ManagerCapabilityKey.CHART: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.CHART,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="chart",
            intent_description="Produce a chart deliverable; presentation only.",
        ),
        ManagerCapabilityKey.EXPLAIN: ManagerCapabilitySpec(
            key=ManagerCapabilityKey.EXPLAIN,
            lane=ManagerCapabilityLane.PRESENTATION,
            executable=False,
            effect_family="explain",
            intent_description="Explain an already established result/evidence; presentation only.",
        ),
    }

    def get(self, key: ManagerCapabilityKey) -> ManagerCapabilitySpec:
        try:
            return self._SPECS[key]
        except KeyError as exc:
            raise KeyError(f"unregistered Manager capability: {key}") from exc

    def registered(self, key: ManagerCapabilityKey) -> bool:
        return key in self._SPECS

    def manager_contract(self) -> tuple[dict[str, object], ...]:
        """Safe capability-shape projection for the Manager prompt.

        It contains no canonical semantic identifiers or user-language heuristics.
        """
        rows: list[dict[str, object]] = []
        for key in ManagerCapabilityKey:
            spec = self.get(key)
            rows.append(
                {
                    "capability": key.value,
                    "lane": spec.lane.value,
                    "executable": spec.executable,
                    "required_semantic_kinds": sorted(spec.required_kinds),
                    "excluded_required_semantic_kinds": sorted(
                        spec.exclusion_required_kinds
                    ),
                    "allowed_semantic_kinds": sorted(spec.allowed_kinds),
                    "required_operation_params": sorted(spec.required_params),
                    "allowed_operation_params": sorted(spec.allowed_params),
                    "intent_description": spec.intent_description,
                }
            )
        return tuple(rows)
