"""Provider-free D7-A2 proofs for run-scoped ResearchTaskRegistry."""

from __future__ import annotations

import pytest

from app.v2.models import ResearchTask
from app.v2.research_tasks import (
    ResearchTaskLifecycleError,
    ResearchTaskRegistry,
)
from app.v2.research_tools import ResearchTaskKind


def _task(
    task_id: str = "T1",
    *,
    question_id: str = "U1",
    input_refs: tuple[str, ...] = ("sem_a",),
) -> ResearchTask:
    return ResearchTask(
        task_id=task_id,
        question_id=question_id,
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=input_refs,
    )


def test_same_task_same_completed_delivery_reuses_receipt_without_second_side_effect():
    registry = ResearchTaskRegistry()
    task = _task()
    side_effects = 0

    prior = registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    assert prior is None
    side_effects += 1
    completed = registry.complete_execution(
        task_id=task.task_id,
        tool_id="wren.query",
        action_fingerprint="act-1",
        result={"evidence_ref": "E1"},
    )
    assert completed.state == "complete"

    replay = registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    if replay is None:
        side_effects += 1

    assert replay == {"evidence_ref": "E1"}
    assert side_effects == 1


def test_same_task_id_with_different_immutable_identity_is_rejected():
    registry = ResearchTaskRegistry()
    registry.register(_task())

    with pytest.raises(ResearchTaskLifecycleError, match="identity conflict"):
        registry.register(_task(question_id="U2"))


def test_duplicate_delivery_while_in_flight_is_rejected():
    registry = ResearchTaskRegistry()
    task = _task()
    assert registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    ) is None

    with pytest.raises(ResearchTaskLifecycleError, match="duplicate in-flight"):
        registry.begin_execution(
            task=task,
            tool_id="wren.query",
            action_fingerprint="act-1",
        )


def test_completed_task_with_different_execution_identity_is_rejected():
    registry = ResearchTaskRegistry()
    task = _task()
    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    registry.complete_execution(
        task_id=task.task_id,
        tool_id="wren.query",
        action_fingerprint="act-1",
        result="receipt-1",
    )

    with pytest.raises(
        ResearchTaskLifecycleError,
        match="completed with different execution identity",
    ):
        registry.begin_execution(
            task=task,
            tool_id="wren.query",
            action_fingerprint="act-2",
        )


def test_cancel_pending_task_is_terminal_and_cannot_execute():
    registry = ResearchTaskRegistry()
    task = registry.register(_task())
    cancelled = registry.cancel(task.task_id)
    assert cancelled.state == "cancelled"

    with pytest.raises(ResearchTaskLifecycleError, match="cancelled"):
        registry.begin_execution(
            task=task,
            tool_id="wren.query",
            action_fingerprint="act-1",
        )


def test_cancel_running_task_is_terminal():
    registry = ResearchTaskRegistry()
    task = _task()
    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    assert registry.get(task.task_id).state == "running"

    cancelled = registry.cancel(task.task_id)
    assert cancelled.state == "cancelled"
    assert registry.get(task.task_id).state == "cancelled"


def test_late_completion_after_cancel_cannot_resurrect_or_create_receipt():
    registry = ResearchTaskRegistry()
    task = _task()
    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    registry.cancel(task.task_id)

    with pytest.raises(ResearchTaskLifecycleError, match="cannot resurrect"):
        registry.complete_execution(
            task_id=task.task_id,
            tool_id="wren.query",
            action_fingerprint="act-1",
            result={"evidence_ref": "LATE"},
        )

    assert registry.get(task.task_id).state == "cancelled"
    with pytest.raises(ResearchTaskLifecycleError, match="cancelled"):
        registry.begin_execution(
            task=task,
            tool_id="wren.query",
            action_fingerprint="act-1",
        )


def test_failed_task_does_not_silently_restart():
    registry = ResearchTaskRegistry()
    task = _task()
    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )
    failed = registry.fail(task.task_id)
    assert failed.state == "failed"

    with pytest.raises(ResearchTaskLifecycleError, match="failed"):
        registry.begin_execution(
            task=task,
            tool_id="wren.query",
            action_fingerprint="act-1",
        )
    assert registry.get(task.task_id).state == "failed"


def test_inflight_execution_identity_conflict_is_rejected():
    registry = ResearchTaskRegistry()
    task = _task()
    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-1",
    )

    with pytest.raises(ResearchTaskLifecycleError, match="in-flight identity conflict"):
        registry.begin_execution(
            task=task,
            tool_id="wren.breakdown",
            action_fingerprint="act-2",
        )


def test_register_many_above_generic_fanout_bound_is_rejected_without_partial_registration():
    registry = ResearchTaskRegistry(max_fanout=2)
    tasks = (
        _task("T1"),
        _task("T2"),
        _task("T3"),
    )

    with pytest.raises(ResearchTaskLifecycleError, match="fanout 3 exceeds 2"):
        registry.register_many(tasks)

    assert registry.tasks == ()



class _Clock:
    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_deadline_is_frozen_once_commit_is_authorized():
    clock = _Clock(10.0)
    registry = ResearchTaskRegistry(clock=clock)
    task = _task()

    registry.begin_execution(
        task=task,
        tool_id="wren.query",
        action_fingerprint="act-deadline",
        timeout_ms=1_000,
    )
    clock.advance(0.999)
    registry.assert_execution_active(
        task_id=task.task_id,
        tool_id="wren.query",
        action_fingerprint="act-deadline",
    )

    # Accepted-commit authorization happened before the deadline.  Final lifecycle
    # bookkeeping may occur later without retroactively invalidating committed truth.
    clock.advance(10.0)
    completed = registry.complete_execution(
        task_id=task.task_id,
        tool_id="wren.query",
        action_fingerprint="act-deadline",
        result={"evidence_ref": "E1"},
    )
    assert completed.state == "complete"
