"""Typed completion policy for upstream material limitations.

This module projects terminality already owned by canonical P14 Research state.
It does not create Evidence, P18/P19 judgments, or presentation truth.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.v3.research import ObligationState


@dataclass(frozen=True)
class MaterialLimitationTerminal:
    requirement_id: str
    limitation_ref: str | None


def project_material_limitation_terminals(
    *,
    session,
    material_groups,
    completed_material_group_ids: tuple[str, ...],
) -> tuple[MaterialLimitationTerminal, ...]:
    """Project P14 LIMITED authority through only terminal material groups.

    A directly LIMITED analytical obligation is terminal in its own right.
    When a completed MaterialGroup's anchor is LIMITED, every consumer of that
    exact shared material is LIMITED by the same upstream authority. Uncompleted
    groups never inherit terminality.
    """

    obligation_map = {
        item.obligation_id: item
        for item in session.obligations
    }
    output: dict[str, MaterialLimitationTerminal] = {}

    def add(requirement_id: str, obligation) -> None:
        refs = tuple(getattr(obligation, "limitation_refs", ()) or ())
        output[requirement_id] = MaterialLimitationTerminal(
            requirement_id=requirement_id,
            limitation_ref=refs[-1] if refs else None,
        )

    for obligation in session.obligations:
        if obligation.state == ObligationState.LIMITED:
            add(obligation.obligation_id, obligation)

    completed = set(completed_material_group_ids)
    for group in material_groups:
        if group.material_group_id not in completed:
            continue
        anchor = obligation_map.get(group.anchor_requirement_id)
        if anchor is None or anchor.state != ObligationState.LIMITED:
            continue
        for requirement_id in group.consumer_requirement_ids:
            add(requirement_id, anchor)

    return tuple(
        output[key]
        for key in sorted(output)
    )
