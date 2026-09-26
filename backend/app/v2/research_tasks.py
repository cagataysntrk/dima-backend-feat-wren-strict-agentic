"""Day 7 Research task materialization on top of existing accepted authority.

This is domain orchestration, not a second agent kernel.  It materializes bounded
ResearchTask objects from already-accepted obligations and evidence-grounded proposals.
It never creates semantic handles, USER_MUST obligations or query truth.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from typing import Callable

from pydantic import Field

from app.v2.manager_errors import ManagerRecoverableToolError
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationStatus,
)
from app.v2.models import FrozenModel, ResearchTask, ResearchTaskKind
from app.v2.research_fanout import (
    CardinalityObservation,
    CardinalitySource,
    FanoutDecision,
    FanoutRequest,
    PriorityProvenance,
    ResearchFanoutPolicy,
)


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


class ResearchBranchMaterialization(FrozenModel):
    decision: FanoutDecision
    registered_tasks: tuple[ResearchTask, ...] = ()


class ResearchSeedSet(FrozenModel):
    considered_obligation_ids: tuple[str, ...]
    registered_tasks: tuple[ResearchTask, ...] = ()
    deferred_obligation_ids: tuple[str, ...] = ()
    already_accounted_obligation_ids: tuple[str, ...] = ()


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

    @classmethod
    def capability_for_task_kind(
        cls,
        task_kind: ResearchTaskKind,
    ) -> ManagerCapabilityKey:
        matches = [
            capability
            for capability, kind in cls._TASK_KIND_BY_CAPABILITY.items()
            if kind == task_kind
        ]
        if len(matches) != 1:
            raise ResearchTaskMaterializationError(
                f"Research task kind {task_kind.value} has {len(matches)} capability owners"
            )
        return matches[0]

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

    def seed_orchestrated_subtask(
        self,
        *,
        runtime,
        parent_obligation_id: str,
        subtask_capability_key: ManagerCapabilityKey,
        task_id: str,
        input_refs: tuple[str, ...],
    ) -> ResearchTask:
        """Create one server-owned observational seed under an orchestration umbrella.

        This deliberately does not add ROOT_CAUSE to _TASK_KIND_BY_CAPABILITY. The
        selected subtask keeps its existing governed task family while the parent
        ROOT_CAUSE USER_MUST remains the research/completion authority.
        """
        contract = runtime.accepted_contract
        ledger = runtime.ledger
        if contract is None or ledger is None:
            raise ResearchTaskMaterializationError(
                "orchestrated seed requires accepted Research authority"
            )
        accepted = runtime.authority_registry.accepted(contract.turn_id)
        if accepted is None or accepted[0].value != "RESEARCH":
            raise ResearchTaskMaterializationError(
                "orchestrated seed requires Research authority family"
            )

        parent = self._ledger_item(runtime, parent_obligation_id)
        if parent.capability_key != ManagerCapabilityKey.ROOT_CAUSE:
            raise ResearchTaskMaterializationError(
                "orchestrated Day8 seed requires ROOT_CAUSE parent authority"
            )
        if parent.status not in {
            ObligationStatus.ACCEPTED,
            ObligationStatus.READY,
            ObligationStatus.IN_PROGRESS,
        }:
            raise ResearchTaskMaterializationError(
                "orchestrated Day8 seed requires active ROOT_CAUSE parent"
            )
        if tuple(dict.fromkeys(input_refs)) != tuple(
            dict.fromkeys(parent.semantic_handle_refs)
        ):
            raise ResearchTaskMaterializationError(
                "orchestrated seed must preserve all accepted ROOT_CAUSE semantic handles"
            )

        task_kind = self.task_kind_for_capability(subtask_capability_key)
        return ResearchTask(
            task_id=task_id,
            question_id=parent_obligation_id,
            task_kind=task_kind.value,
            input_refs=tuple(dict.fromkeys(input_refs)),
            origin="USER_SEED",
        )

    def seed_initial_user_must(
        self,
        *,
        runtime,
        task_registry,
        executable_task_kinds: tuple[ResearchTaskKind, ...],
        max_seed_tasks: int = 4,
    ) -> ResearchSeedSet:
        """Project accepted USER_MUST obligations into a bounded READY task set.

        This is a projection over existing authority, not a planner.  It never executes
        tasks and never drops non-executable obligations: unsupported/unready/excess
        obligations are returned explicitly as deferred so the ledger remains the full
        completion truth.
        """
        if max_seed_tasks < 1 or max_seed_tasks > 4:
            raise ValueError("Day7 initial seed bound must be between 1 and 4")
        ledger = runtime.ledger
        contract = runtime.accepted_contract
        if contract is None or ledger is None:
            raise ResearchTaskMaterializationError(
                "initial Research seed set requires accepted Research authority"
            )
        accepted = runtime.authority_registry.accepted(contract.turn_id)
        if accepted is None or accepted[0].value != "RESEARCH":
            raise ResearchTaskMaterializationError(
                "initial Research seed set requires Research authority family"
            )

        executable = set(executable_task_kinds)
        considered = tuple(item.obligation_id for item in ledger.active_user_must)
        selected: list[ResearchTask] = []
        deferred: list[str] = []
        accounted: list[str] = []
        terminal = {
            ObligationStatus.VERIFIED,
            ObligationStatus.BLOCKED_DATA_GAP,
            ObligationStatus.LIMITED,
            ObligationStatus.UNSUPPORTED,
        }
        seedable = {
            ObligationStatus.ACCEPTED,
            ObligationStatus.READY,
            ObligationStatus.IN_PROGRESS,
        }

        for item in ledger.active_user_must:
            if item.status in terminal:
                accounted.append(item.obligation_id)
                continue
            if item.status not in seedable:
                deferred.append(item.obligation_id)
                continue
            try:
                task_kind = self.task_kind_for_capability(item.capability_key)
            except ResearchTaskMaterializationError:
                deferred.append(item.obligation_id)
                continue
            if task_kind not in executable or not item.semantic_handle_refs:
                deferred.append(item.obligation_id)
                continue
            if len(selected) >= max_seed_tasks:
                deferred.append(item.obligation_id)
                continue
            selected.append(
                ResearchTask(
                    task_id=f"seed:{item.obligation_id}",
                    question_id=item.obligation_id,
                    task_kind=task_kind.value,
                    input_refs=item.semantic_handle_refs,
                    origin="USER_SEED",
                )
            )

        registered = task_registry.register_many(tuple(selected))
        return ResearchSeedSet(
            considered_obligation_ids=considered,
            registered_tasks=registered,
            deferred_obligation_ids=tuple(deferred),
            already_accounted_obligation_ids=tuple(accounted),
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


    def materialize_derived_candidates(
        self,
        *,
        runtime,
        evidence_store,
        task_registry,
        parent_task: ResearchTask,
        proposals: tuple[DerivedResearchTaskProposal, ...],
        cardinality: CardinalityObservation | None = None,
        priority_provenance: PriorityProvenance = PriorityProvenance.NONE,
        fanout_policy: ResearchFanoutPolicy | None = None,
        max_branch_depth: int = 3,
        max_children: int = 4,
        unknown_children: int = 2,
    ) -> ResearchBranchMaterialization:
        """Materialize a governed candidate set, then bound it before registration.

        Candidate cognition is not authority: every proposal first passes the same
        evidence/parent/handle provenance checks as a single derived task.  The
        deterministic fanout policy then uses ONLY canonical remaining query budget,
        branch depth and governed/unknown cardinality information.  Registration is
        the sole lifecycle side effect.
        """
        if not proposals:
            raise ResearchTaskMaterializationError(
                "derived branch candidate set cannot be empty"
            )

        materialized = tuple(
            self.materialize_derived(
                runtime=runtime,
                evidence_store=evidence_store,
                parent_task=parent_task,
                proposal=proposal,
                max_branch_depth=max_branch_depth,
            )
            for proposal in proposals
        )
        by_id: dict[str, ResearchTask] = {}
        for task in materialized:
            existing = by_id.get(task.task_id)
            if existing is not None and existing != task:
                raise ResearchTaskMaterializationError(
                    f"conflicting derived candidate task identity: {task.task_id}"
                )
            by_id[task.task_id] = task

        observation = cardinality or CardinalityObservation(
            source=CardinalitySource.UNKNOWN
        )
        policy = fanout_policy or ResearchFanoutPolicy()
        decision = policy.decide(
            FanoutRequest(
                candidate_keys=tuple(by_id),
                cardinality=observation,
                priority_provenance=priority_provenance,
                remaining_query_budget=runtime.remaining_data_queries,
                current_branch_depth=parent_task.branch_depth,
                max_branch_depth=max_branch_depth,
                max_children=max_children,
                unknown_children=unknown_children,
            )
        )
        selected = tuple(
            by_id[task_id]
            for task_id in decision.selected_candidate_keys
        )
        registered = task_registry.register_many(selected)
        return ResearchBranchMaterialization(
            decision=decision,
            registered_tasks=registered,
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
    commit_authorized_at: float | None = None


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

        # A terminal execution may have a canonical receipt (complete or blocked).
        # Receipt identity wins before terminal-state rejection so duplicate delivery is
        # idempotent without re-executing the governed tool.
        receipt = self._receipts.get(task.task_id)
        if receipt is not None:
            receipt_tool, receipt_action, result = receipt
            if receipt_tool != tool_id or receipt_action != action_fingerprint:
                raise ResearchTaskLifecycleError(
                    f"ResearchTask completed with different execution identity: {task.task_id}"
                )
            return result

        if current.state == "complete":
            raise ResearchTaskLifecycleError(
                f"completed ResearchTask cannot re-execute without canonical restored receipt: {task.task_id}"
            )
        if current.state in {"cancelled", "failed", "blocked"}:
            raise ResearchTaskLifecycleError(
                f"{current.state} ResearchTask cannot execute: {task.task_id}"
            )

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
        # Deadline is judged exactly once at the accepted-Research commit boundary.
        # After commit is authorized, later lifecycle finalization must not manufacture a
        # timeout after Evidence/UOL truth has already been committed.
        if inflight.commit_authorized_at is None:
            now = self._clock()
            if inflight.deadline_at is not None and now >= inflight.deadline_at:
                self._inflight.pop(task_id, None)
                self._tasks[task_id] = current.model_copy(update={"state": "failed"})
                raise ResearchTaskTimeoutError(
                    f"ResearchTask deadline exceeded before commit: {task_id}"
                )
            self._inflight[task_id] = replace(
                inflight,
                commit_authorized_at=now,
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

    def block_execution(
        self,
        *,
        task_id: str,
        tool_id: str,
        action_fingerprint: str,
        result: object,
    ) -> ResearchTask:
        """Commit one fail-closed governed terminal without fabricating Evidence."""
        self.assert_execution_active(
            task_id=task_id,
            tool_id=tool_id,
            action_fingerprint=action_fingerprint,
        )
        current = self.get(task_id)
        self._inflight.pop(task_id, None)
        blocked = current.model_copy(update={"state": "blocked"})
        self._tasks[task_id] = blocked
        self._receipts[task_id] = (tool_id, action_fingerprint, result)
        return blocked

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
