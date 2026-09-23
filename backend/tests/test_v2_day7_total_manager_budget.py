"""Provider-free Day7 budget authority tests."""

from __future__ import annotations

import pytest

from app.v2.manager_models import ManagerBudget, ManagerState
from app.v2.manager_runtime import ManagerBudgetError, ManagerRuntime, ManagerStateError


def _runtime() -> ManagerRuntime:
    runtime = ManagerRuntime(
        request_ref="day7-global-turn-budget",
        budget=ManagerBudget(
            max_total_manager_turns=6,
            max_preacceptance_turns=2,
            max_manager_turns=6,
        ),
    )
    runtime.begin_understanding()
    return runtime


def _turns(runtime: ManagerRuntime, *, pre: int, research: int) -> None:
    for _ in range(pre):
        runtime.note_manager_turn(phase="preacceptance")
    for _ in range(research):
        runtime.note_manager_turn(phase="research")


def test_one_pre_plus_five_research_is_allowed_at_global_six():
    runtime = _runtime()
    _turns(runtime, pre=1, research=5)

    assert runtime.snapshot.manager_turns == 6
    assert runtime.snapshot.preacceptance_turns == 1
    assert runtime.snapshot.research_manager_turns == 5
    assert runtime.snapshot.state != ManagerState.BUDGET_EXHAUSTED


def test_two_pre_plus_four_research_is_allowed_at_global_six():
    runtime = _runtime()
    _turns(runtime, pre=2, research=4)

    assert runtime.snapshot.manager_turns == 6
    assert runtime.snapshot.preacceptance_turns == 2
    assert runtime.snapshot.research_manager_turns == 4
    assert runtime.snapshot.state != ManagerState.BUDGET_EXHAUSTED


@pytest.mark.parametrize(
    ("pre", "research"),
    [
        (1, 5),
        (2, 4),
    ],
)
def test_seventh_total_manager_turn_is_rejected_without_counter_drift(
    pre: int,
    research: int,
):
    runtime = _runtime()
    _turns(runtime, pre=pre, research=research)

    before = runtime.snapshot
    with pytest.raises(ManagerBudgetError, match="total Manager turn budget exhausted"):
        runtime.note_manager_turn(phase="research")

    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED
    assert runtime.snapshot.manager_turns == before.manager_turns == 6
    assert runtime.snapshot.preacceptance_turns == before.preacceptance_turns == pre
    assert runtime.snapshot.research_manager_turns == before.research_manager_turns == research


def test_budget_exhaustion_is_terminal_and_finish_cannot_hide_it():
    runtime = _runtime()
    _turns(runtime, pre=1, research=5)

    with pytest.raises(ManagerBudgetError):
        runtime.note_manager_turn(phase="research")

    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED

    with pytest.raises(
        ManagerStateError,
        match="budget-exhausted Manager run cannot transition to COMPLETED",
    ):
        runtime.finish()

    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED
