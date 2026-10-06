"""Deterministic authorization law for adaptive analytical deepening.

This module owns no planning, Evidence, hypothesis or native execution. It only
answers whether the accepted user/product intent authorizes P19 to consider one
bounded information-gain re-entry.
"""
from __future__ import annotations

from app.v3.research_contracts import ResearchGoalKind


def adaptive_investigation_authorized(
    *,
    goal_kind: ResearchGoalKind,
    explicit_follow_verified_material: bool,
) -> bool:
    """Return the single semantic authorization bit for adaptive deepening.

    ROOT_CAUSE is already bounded investigation authority and therefore does not
    require a duplicate FOLLOW_VERIFIED_MATERIAL flag. Ordinary direct analysis
    may deepen only when that explicit follow authority is present.
    """

    return (
        goal_kind == ResearchGoalKind.ROOT_CAUSE
        or explicit_follow_verified_material
    )
