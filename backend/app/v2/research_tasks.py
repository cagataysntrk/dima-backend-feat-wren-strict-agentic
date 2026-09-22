"""Day 7 Research task materialization on top of existing accepted authority.

This is domain orchestration, not a second agent kernel.  It materializes bounded
ResearchTask objects from already-accepted obligations and evidence-grounded proposals.
It never creates semantic handles, USER_MUST obligations or query truth.
"""

from __future__ import annotations

from pydantic import Field

from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationStatus,
)
from app.v2.models import FrozenModel, ResearchTask
from app.v2.research_tools import ResearchTaskKind


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
