from __future__ import annotations

from types import SimpleNamespace

from app.v3.brain_v2.activities import MaterialActivityDisposition
from app.v3.brain_v2.completion_policy import (
    material_limitation_disposition,
    project_material_limitation_terminals,
)
from app.v3.research import ObligationState


def _obligation(
    obligation_id: str,
    state: ObligationState,
    *limitation_refs: str,
):
    return SimpleNamespace(
        obligation_id=obligation_id,
        state=state,
        limitation_refs=tuple(limitation_refs),
    )


def _group(
    group_id: str,
    anchor: str,
    *consumers: str,
):
    return SimpleNamespace(
        material_group_id=group_id,
        anchor_requirement_id=anchor,
        consumer_requirement_ids=tuple(consumers),
    )


def test_direct_p14_limitation_is_terminal_without_evidence() -> None:
    session = SimpleNamespace(
        obligations=(
            _obligation(
                "goal.a",
                ObligationState.LIMITED,
                "lim_symbolic_a",
            ),
        )
    )

    terminals = project_material_limitation_terminals(
        session=session,
        material_groups=(),
        completed_material_group_ids=(),
    )

    assert terminals == (
        terminals[0].__class__(
            requirement_id="goal.a",
            limitation_ref="lim_symbolic_a",
        ),
    )


def test_completed_shared_material_limitation_propagates_only_to_its_consumers() -> None:
    session = SimpleNamespace(
        obligations=(
            _obligation(
                "goal.anchor",
                ObligationState.LIMITED,
                "lim_shared",
            ),
            _obligation("goal.consumer", ObligationState.READY),
            _obligation("goal.other", ObligationState.READY),
        )
    )
    group = _group(
        "mg_" + "a" * 24,
        "goal.anchor",
        "goal.anchor",
        "goal.consumer",
    )

    terminals = project_material_limitation_terminals(
        session=session,
        material_groups=(group,),
        completed_material_group_ids=(group.material_group_id,),
    )
    by_id = {item.requirement_id: item for item in terminals}

    assert set(by_id) == {"goal.anchor", "goal.consumer"}
    assert by_id["goal.anchor"].limitation_ref == "lim_shared"
    assert by_id["goal.consumer"].limitation_ref == "lim_shared"


def test_uncompleted_group_does_not_propagate_anchor_limitation() -> None:
    session = SimpleNamespace(
        obligations=(
            _obligation(
                "goal.anchor",
                ObligationState.LIMITED,
                "lim_shared",
            ),
            _obligation("goal.consumer", ObligationState.READY),
        )
    )
    group = _group(
        "mg_" + "b" * 24,
        "goal.anchor",
        "goal.anchor",
        "goal.consumer",
    )

    terminals = project_material_limitation_terminals(
        session=session,
        material_groups=(group,),
        completed_material_group_ids=(),
    )

    assert tuple(item.requirement_id for item in terminals) == ("goal.anchor",)


def test_material_limitation_disposition_preserves_retryable_nonterminality() -> None:
    assert material_limitation_disposition(
        obligation_state=ObligationState.READY.value,
    ) == MaterialActivityDisposition.WAITING
    assert material_limitation_disposition(
        obligation_state=ObligationState.DELEGATED.value,
    ) == MaterialActivityDisposition.WAITING
    assert material_limitation_disposition(
        obligation_state=ObligationState.LIMITED.value,
    ) == MaterialActivityDisposition.LIMITED
