"""Day 7 Research task materialization on top of existing accepted authority.

This is domain orchestration, not a second agent kernel.  It materializes bounded
ResearchTask objects from already-accepted obligations and evidence-grounded proposals.
It never creates semantic handles, USER_MUST obligations or query truth.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from pydantic import Field

from app.v2.manager_errors import ManagerRecoverableToolError
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationStatus,
)
from app.v2.models import FrozenModel, ResearchTask, ResearchTaskKind


class ResearchTaskMaterializationError(RuntimeError):
    pass


class DerivedResearchTaskProposal(FrozenModel):
    task_id: str = Field(min_length=1)
    task_kind: ResearchTaskKind
    parent_task_id: str = Field(min_length=1)
    parent_obligation_id: str = Field(min_length=1)
    trigger_evidence_ref: str = Field(min_length=1)
    input_refs: tuple[str, ...] = Field(min_length=1)
    material_reason: str = Field(min_length=1, max_length=500)


class ResearchTaskService:
    """Materialize seed/derived tasks without owning cognition or execution truth."""

    _TASK_KIND_BY_CAPABILITY = {
        ManagerCapabilityKey.PERFORMANCE: ResearchTaskKind.QUERY,
        ManagerCapabilityKey.COMPARISON: ResearchTaskKind.COMPARE,
        ManagerCapabilityKey.TREND: ResearchTaskKind.TREND,
        ManagerCapabilityKey.BREAKDOWN: ResearchTaskKind.BREAKDOWN,
        ManagerCapabilityKey.RANKING: ResearchTaskKind.RANK,
        ManagerCapabilityKey.RELATIONSHIP: ResearchTaskKind.RELATIONSHIP,
    }

    @classmethod
    def task_kind_for_capability(
        cls,
        capability_key: ManagerCapabilityKey,
    ) -> ResearchTaskKind:
        try:
            return cls._TASK_KIND_BY_CAPABILITY[capability_key]
        except KeyError as exc:
            raise ResearchTaskMaterializationError(
                f"no Day7 task kind for {capability_key.value}"
            ) from exc

    @staticmethod
    def _ledger_item(runtime, obligation_id: str):
        ledger = runtime.ledger
        if ledger is None:
            raise ResearchTaskMaterializationError(
                "Research task materialization requires accepted obligation ledger"
            )
        try:
            return next(
                item
                for item in ledger.items
                if item.obligation_id == obligation_id
            )
        except StopIteration as exc:
            raise ResearchTaskMaterializationError(
                f"unknown accepted obligation: {obligation_id}"
            ) from exc

    def seed_for_obligation(
        self,
        *,
        runtime,
        obligation_id: str,
        task_id: str,
    ) -> ResearchTask:
        contract = runtime.accepted_contract
        if contract is None:
            raise ResearchTaskMaterializationError(
                "seed ResearchTask requires accepted Research authority"
            )
        accepted = runtime.authority_registry.accepted(contract.turn_id)
        if accepted is None or accepted[0].value != "RESEARCH":
            raise ResearchTaskMaterializationError(
                "seed ResearchTask requires Research authority family"
            )

        item = self._ledger_item(runtime, obligation_id)
        if item.status == ObligationStatus.SUPERSEDED:
            raise ResearchTaskMaterializationError(
                "superseded obligation cannot seed Research work"
            )
        task_kind = self.task_kind_for_capability(item.capability_key)

        if not item.semantic_handle_refs:
            raise ResearchTaskMaterializationError(
                "seed ResearchTask requires accepted semantic handles"
            )

        return ResearchTask(
            task_id=task_id,
            question_id=obligation_id,
            task_kind=task_kind.value,
            input_refs=item.semantic_handle_refs,
            origin="USER_SEED",
        )

    def materialize_derived(
        self,
        *,
        runtime,
        evidence_store,
        parent_task: ResearchTask,
        proposal: DerivedResearchTaskProposal,
        max_branch_depth: int = 3,
    ) -> ResearchTask:
        if parent_task.state != "complete":
            raise ResearchTaskMaterializationError(
                "derived ResearchTask requires completed parent task"
            )
        if proposal.parent_task_id != parent_task.task_id:
            raise ResearchTaskMaterializationError(
                "derived proposal parent_task_id mismatch"
            )
        if proposal.parent_obligation_id != parent_task.question_id:
            raise ResearchTaskMaterializationError(
                "derived proposal parent obligation mismatch"
            )
        parent = self._ledger_item(runtime, proposal.parent_obligation_id)
        if parent.status == ObligationStatus.SUPERSEDED:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask cannot attach to superseded obligation"
            )

        evidence_ref = proposal.trigger_evidence_ref
        if evidence_ref not in runtime.snapshot.evidence_refs:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask requires current-run evidence"
            )
        if evidence_ref not in runtime.snapshot.inspected_evidence_refs:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask requires inspected evidence"
            )
        try:
            evidence = evidence_store.get(evidence_ref)
        except Exception as exc:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask evidence unavailable"
            ) from exc
        if not evidence.verified:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask requires verified evidence"
            )
        if proposal.parent_obligation_id not in evidence.obligation_ids:
            raise ResearchTaskMaterializationError(
                "derived ResearchTask evidence does not support declared parent"
            )

        depth = parent_task.branch_depth + 1
        if depth > max_branch_depth:
            raise ResearchTaskMaterializationError(
                f"derived ResearchTask exceeds branch depth {max_branch_depth}"
            )

        return ResearchTask(
            task_id=proposal.task_id,
            question_id=proposal.parent_obligation_id,
            task_kind=proposal.task_kind.value,
            input_refs=proposal.input_refs,
            origin="AGENT_DERIVED",
            parent_task_id=proposal.parent_task_id,
            parent_obligation_id=proposal.parent_obligation_id,
            trigger_evidence_ref=evidence_ref,
            branch_depth=depth,
        )


class ResearchTaskLifecycleError(ManagerRecoverableToolError):
    code = "research_task_lifecycle"


class ResearchTaskTimeoutError(ResearchTaskLifecycleError):
    code = "research_task_timeout"


@dataclass(frozen=True)
class ResearchTaskExecutionLease:
    tool_id: str
    action_fingerprint: str
    started_at: float
    deadline_at: float | None


class ResearchTaskRegistry:
    """Run-scoped task identity/lifecycle guard.

    This is not semantic authority and does not execute tools. It only guarantees that
    one task identity cannot be delivered as two different actions, that in-flight
    duplicates do not execute twice, that fanout is bounded, and that cancellation is
    terminal.
    """

    def __init__(
        self,
        *,
        max_fanout: int = 4,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_fanout < 1:
            raise ValueError("max_fanout must be >= 1")
        self.max_fanout = max_fanout
        self._clock = clock
        self._tasks: dict[str, ResearchTask] = {}
        self._receipts: dict[str, tuple[str, str, object]] = {}
        self._inflight: dict[str, ResearchTaskExecutionLease] = {}

    @staticmethod
    def _identity(task: ResearchTask) -> dict:
        payload = task.model_dump(mode="json")
        payload.pop("state", None)
        return payload

    def get(self, task_id: str) -> ResearchTask:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise ResearchTaskLifecycleError(f"unknown ResearchTask: {task_id}") from exc

    def register(self, task: ResearchTask) -> ResearchTask:
        existing = self._tasks.get(task.task_id)
        if existing is None:
            self._tasks[task.task_id] = task
            return task
        if self._identity(existing) != self._identity(task):
            raise ResearchTaskLifecycleError(
                f"ResearchTask identity conflict: {task.task_id}"
            )
        return existing

    def register_many(self, tasks: tuple[ResearchTask, ...]) -> tuple[ResearchTask, ...]:
        unique_new = {
            task.task_id
            for task in tasks
            if task.task_id not in self._tasks
        }
        if len(unique_new) > self.max_fanout:
            raise ResearchTaskLifecycleError(
                f"Research task fanout {len(unique_new)} exceeds {self.max_fanout}"
            )
        return tuple(self.register(task) for task in tasks)

    def begin_execution(
        self,
        *,
        task: ResearchTask,
        tool_id: str,
        action_fingerprint: str,
        timeout_ms: int | None = None,
    ) -> object | None:
        current = self.register(task)
        if current.state in {"cancelled", "failed", "blocked"}:
            raise ResearchTaskLifecycleError(
                f"{current.state} ResearchTask cannot execute: {task.task_id}"
            )

        receipt = self._receipts.get(task.task_id)
        if receipt is not None:
            receipt_tool, receipt_action, result = receipt
            if receipt_tool != tool_id or receipt_action != action_fingerprint:
                raise ResearchTaskLifecycleError(
                    f"ResearchTask completed with different execution identity: {task.task_id}"
                )
            return result

        inflight = self._inflight.get(task.task_id)
        if inflight is not None:
            if (
                inflight.tool_id != tool_id
                or inflight.action_fingerprint != action_fingerprint
            ):
                raise ResearchTaskLifecycleError(
                    f"ResearchTask in-flight identity conflict: {task.task_id}"
                )
            raise ResearchTaskLifecycleError(
                f"duplicate in-flight ResearchTask delivery: {task.task_id}"
            )

        now = self._clock()
        deadline_at = (
            None
            if timeout_ms is None
            else now + (max(0, timeout_ms) / 1000.0)
        )
        self._inflight[task.task_id] = ResearchTaskExecutionLease(
            tool_id=tool_id,
            action_fingerprint=action_fingerprint,
            started_at=now,
            deadline_at=deadline_at,
        )
        self._tasks[task.task_id] = current.model_copy(update={"state": "running"})
        return None

    def assert_execution_active(
        self,
        *,
        task_id: str,
        tool_id: str,
        action_fingerprint: str,
    ) -> None:
        current = self.get(task_id)
        inflight = self._inflight.get(task_id)
        if current.state == "cancelled":
            raise ResearchTaskLifecycleError(
                f"late completion cannot resurrect cancelled ResearchTask: {task_id}"
            )
        if current.state != "running":
            raise ResearchTaskLifecycleError(
                f"ResearchTask is not active for commit: {task_id} ({current.state})"
            )
        if (
            inflight is None
            or inflight.tool_id != tool_id
            or inflight.action_fingerprint != action_fingerprint
        ):
            raise ResearchTaskLifecycleError(
                f"ResearchTask completion identity mismatch: {task_id}"
            )
        if (
            inflight.deadline_at is not None
            and self._clock() >= inflight.deadline_at
        ):
            self._inflight.pop(task_id, None)
            self._tasks[task_id] = current.model_copy(update={"state": "failed"})
            raise ResearchTaskTimeoutError(
                f"ResearchTask deadline exceeded before commit: {task_id}"
            )

    def complete_execution(
        self,
        *,
        task_id: str,
        tool_id: str,
        action_fingerprint: str,
        result: object,
    ) -> ResearchTask:
        self.assert_execution_active(
            task_id=task_id,
            tool_id=tool_id,
            action_fingerprint=action_fingerprint,
        )
        current = self.get(task_id)
        self._inflight.pop(task_id, None)
        completed = current.model_copy(update={"state": "complete"})
        self._tasks[task_id] = completed
        self._receipts[task_id] = (tool_id, action_fingerprint, result)
        return completed

    def cancel(self, task_id: str) -> ResearchTask:
        current = self.get(task_id)
        if current.state in {"complete", "failed", "blocked", "cancelled"}:
            return current
        cancelled = current.model_copy(update={"state": "cancelled"})
        self._tasks[task_id] = cancelled
        return cancelled

    def fail(self, task_id: str) -> ResearchTask:
        current = self.get(task_id)
        if current.state == "cancelled":
            return current
        failed = current.model_copy(update={"state": "failed"})
        self._tasks[task_id] = failed
        self._inflight.pop(task_id, None)
        return failed

    def execution_lease(self, task_id: str) -> ResearchTaskExecutionLease:
        try:
            return self._inflight[task_id]
        except KeyError as exc:
            raise ResearchTaskLifecycleError(
                f"ResearchTask has no active execution lease: {task_id}"
            ) from exc

    def now(self) -> float:
        return self._clock()

    @property
    def tasks(self) -> tuple[ResearchTask, ...]:
        return tuple(self._tasks.values())
