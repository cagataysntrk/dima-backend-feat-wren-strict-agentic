"""Day8-C deterministic ROOT_CAUSE orchestration boundaries.

This module owns no semantic, query, Evidence, lifecycle or causal truth. It only:
- selects a unique lossless existing DIRECT task shape for observational bootstrap;
- admits model next-test proposals against governed Day8/Day7 identities;
- mints server-owned ResearchTask identity;
- delegates materialization/fanout/registration to the sealed Day7 machinery.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from app.v2.capability_bindings import CapabilityBindingValidator
from app.v2.epistemics import HypothesisLedger, HypothesisLedgerError
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
    ObligationStatus,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityLane,
    ManagerCapabilityRegistry,
)
from app.v2.models import (
    FrozenModel,
    HypothesisNextTestProposal,
    ResearchTask,
    ResearchTaskKind,
)
from app.v2.obligation_ledger import UserObligationLedgerService
from app.v2.research_fanout import CardinalityObservation, CardinalitySource
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskMaterializationError,
    ResearchTaskRegistry,
    ResearchTaskService,
)
from app.v2.research_tools import (
    ResearchToolContractError,
    ResearchToolRegistry,
)
from app.v2.semantic_handles import SemanticHandleRegistry


class RootCauseOrchestrationError(RuntimeError):
    """Day8-C proposal/applicability violation."""


class RootCauseBootstrapStatus(StrEnum):
    EVIDENCE_READY = "EVIDENCE_READY"
    TASK_READY = "TASK_READY"
    NO_APPLICABLE_TASK = "NO_APPLICABLE_TASK"
    AMBIGUOUS_TASK = "AMBIGUOUS_TASK"


class RootCauseBootstrapResult(FrozenModel):
    status: RootCauseBootstrapStatus
    evidence_refs: tuple[str, ...] = ()
    candidate_task_kinds: tuple[ResearchTaskKind, ...] = ()
    selected_capability: ManagerCapabilityKey | None = None
    task: ResearchTask | None = None
    reason: str


class RootCauseBootstrapPolicy:
    """Choose observational work by applicability, never by causal guess."""

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
        task_service: ResearchTaskService | None = None,
        tool_registry: ResearchToolRegistry | None = None,
    ) -> None:
        self._handles = semantic_handles
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._bindings = CapabilityBindingValidator(
            semantic_handles=semantic_handles,
            capabilities=self._capabilities,
        )
        self._tasks = task_service or ResearchTaskService()
        self._tools = tool_registry or ResearchToolRegistry()
        self._obligations = UserObligationLedgerService()

    @staticmethod
    def _active_root(item) -> bool:
        return (
            item.capability_key == ManagerCapabilityKey.ROOT_CAUSE
            and item.origin == ObligationOrigin.USER_MUST
            and item.polarity == ObligationPolarity.REQUIRED
            and item.status
            in {
                ObligationStatus.ACCEPTED,
                ObligationStatus.READY,
                ObligationStatus.IN_PROGRESS,
            }
        )

    def _belongs_to_root(self, *, ledger, obligation_id: str, root_id: str) -> bool:
        current = obligation_id
        seen: set[str] = set()
        while current not in seen:
            if current == root_id:
                return True
            seen.add(current)
            try:
                item = self._obligations.get(ledger, current)
            except Exception:
                return False
            if item.parent_obligation_id is None:
                return False
            current = item.parent_obligation_id
        return False

    def _inspected_verified_evidence(
        self,
        *,
        runtime,
        evidence_store,
        root_id: str,
    ) -> tuple[str, ...]:
        ledger = runtime.ledger
        if ledger is None:
            return ()
        ready: list[str] = []
        for ref in runtime.snapshot.inspected_evidence_refs:
            if ref not in runtime.snapshot.evidence_refs:
                continue
            try:
                evidence = evidence_store.get(ref)
            except Exception:
                continue
            if not evidence.verified or not evidence.query_contract_refs:
                continue
            if any(
                self._belongs_to_root(
                    ledger=ledger,
                    obligation_id=obligation_id,
                    root_id=root_id,
                )
                for obligation_id in evidence.obligation_ids
            ):
                ready.append(ref)
        return tuple(dict.fromkeys(ready))

    def _applicable_candidates(
        self,
        *,
        root_item,
        tenant_binding: str,
        context_version: str,
    ) -> tuple[tuple[ManagerCapabilityKey, ResearchTaskKind], ...]:
        out: list[tuple[ManagerCapabilityKey, ResearchTaskKind]] = []
        for capability in ManagerCapabilityKey:
            spec = self._capabilities.get(capability)
            if spec.execution_mode != ManagerCapabilityExecutionMode.DIRECT:
                continue
            if spec.lane not in {
                ManagerCapabilityLane.STANDARD,
                ManagerCapabilityLane.RESEARCH,
            }:
                continue
            try:
                task_kind = self._tasks.task_kind_for_capability(capability)
                self._tools.tool_id_for_task_kind(task_kind)
            except (ResearchTaskMaterializationError, ResearchToolContractError):
                continue

            candidate = root_item.model_copy(
                update={"capability_key": capability}
            )
            binding = self._bindings.validate(
                candidate,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )
            if binding.valid:
                out.append((capability, task_kind))
        return tuple(out)

    @staticmethod
    def _seed_id(
        *,
        runtime,
        root_id: str,
        capability: ManagerCapabilityKey,
        task_kind: ResearchTaskKind,
        input_refs: tuple[str, ...],
    ) -> str:
        contract = runtime.accepted_contract
        if contract is None:
            raise RootCauseOrchestrationError(
                "ROOT_CAUSE bootstrap requires accepted Research authority"
            )
        payload = {
            "accepted_contract_id": contract.contract_id,
            "run_id": runtime.snapshot.run_id,
            "root_obligation_id": root_id,
            "subtask_capability": capability.value,
            "task_kind": task_kind.value,
            "input_refs": list(input_refs),
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "rt_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def prepare(
        self,
        *,
        runtime,
        evidence_store,
        task_registry: ResearchTaskRegistry,
        root_obligation_id: str,
        tenant_binding: str,
        context_version: str,
    ) -> RootCauseBootstrapResult:
        if runtime.accepted_contract is None or runtime.ledger is None:
            raise RootCauseOrchestrationError(
                "ROOT_CAUSE bootstrap requires accepted contract + ledger"
            )
        root = self._obligations.get(runtime.ledger, root_obligation_id)
        if not self._active_root(root):
            raise RootCauseOrchestrationError(
                "ROOT_CAUSE bootstrap requires active accepted USER_MUST authority"
            )

        existing = self._inspected_verified_evidence(
            runtime=runtime,
            evidence_store=evidence_store,
            root_id=root_obligation_id,
        )
        if existing:
            return RootCauseBootstrapResult(
                status=RootCauseBootstrapStatus.EVIDENCE_READY,
                evidence_refs=existing,
                reason="current VERIFIED inspected Evidence already exists",
            )

        candidates = self._applicable_candidates(
            root_item=root,
            tenant_binding=tenant_binding,
            context_version=context_version,
        )
        kinds = tuple(item[1] for item in candidates)
        if not candidates:
            return RootCauseBootstrapResult(
                status=RootCauseBootstrapStatus.NO_APPLICABLE_TASK,
                candidate_task_kinds=(),
                reason="no existing DIRECT task shape losslessly preserves ROOT_CAUSE semantics",
            )
        if len(candidates) != 1:
            return RootCauseBootstrapResult(
                status=RootCauseBootstrapStatus.AMBIGUOUS_TASK,
                candidate_task_kinds=kinds,
                reason="multiple DIRECT task shapes are applicable; silent selection is forbidden",
            )

        capability, task_kind = candidates[0]
        task = self._tasks.seed_orchestrated_subtask(
            runtime=runtime,
            parent_obligation_id=root_obligation_id,
            subtask_capability_key=capability,
            task_id=self._seed_id(
                runtime=runtime,
                root_id=root_obligation_id,
                capability=capability,
                task_kind=task_kind,
                input_refs=root.semantic_handle_refs,
            ),
            input_refs=root.semantic_handle_refs,
        )
        registered = task_registry.register(task)
        return RootCauseBootstrapResult(
            status=RootCauseBootstrapStatus.TASK_READY,
            candidate_task_kinds=(task_kind,),
            selected_capability=capability,
            task=registered,
            reason=(
                "one existing DIRECT analytical task shape losslessly preserves "
                "accepted ROOT_CAUSE semantics"
            ),
        )


class HypothesisNextTestBoundary:
    """Admit bounded next-test cognition without model-owned task identity."""

    def __init__(
        self,
        *,
        ledger: HypothesisLedger,
        runtime,
        evidence_store,
        semantic_handles: SemanticHandleRegistry,
        task_registry: ResearchTaskRegistry,
        tenant_binding: str,
        context_version: str,
        task_service: ResearchTaskService | None = None,
        capabilities: ManagerCapabilityRegistry | None = None,
        tool_registry: ResearchToolRegistry | None = None,
    ) -> None:
        self._ledger = ledger
        self._runtime = runtime
        self._evidence_store = evidence_store
        self._handles = semantic_handles
        self._task_registry = task_registry
        self._tenant_binding = tenant_binding
        self._context_version = context_version
        self._tasks = task_service or ResearchTaskService()
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._bindings = CapabilityBindingValidator(
            semantic_handles=semantic_handles,
            capabilities=self._capabilities,
        )
        self._tools = tool_registry or ResearchToolRegistry()
        self._obligations = UserObligationLedgerService()

    def _validated_hypothesis_and_evidence(self, proposal: HypothesisNextTestProposal):
        self._ledger.assert_active_root_authority()
        hypothesis = self._ledger.get(proposal.hypothesis_ref)
        evidence = self._ledger.validated_evidence(proposal.trigger_evidence_ref)
        if not self._ledger.evidence_view.contains_inspected(
            proposal.trigger_evidence_ref
        ):
            raise RootCauseOrchestrationError(
                "INSPECTION_REQUIRED: next-test proposal requires inspected Evidence"
            )
        admissible = {
            *hypothesis.trigger_evidence_refs,
            *(link.evidence_ref for link in hypothesis.evidence_links),
        }
        if proposal.trigger_evidence_ref not in admissible:
            raise RootCauseOrchestrationError(
                "next-test trigger Evidence is unrelated to the hypothesis"
            )
        try:
            parent_task = self._task_registry.get(evidence.task_id)
        except Exception as exc:
            raise RootCauseOrchestrationError(
                "next-test parent ResearchTask is unavailable"
            ) from exc
        if parent_task.state != "complete":
            raise RootCauseOrchestrationError(
                "next-test requires completed parent ResearchTask"
            )
        return hypothesis, evidence, parent_task

    def _validate_handles(
        self,
        *,
        proposal: HypothesisNextTestProposal,
        admissible_evidence_refs: set[str],
    ) -> None:
        root_id = self._ledger.state.parent_obligation_id
        for handle_id in proposal.input_refs:
            try:
                handle = self._handles.validate(
                    handle_id,
                    tenant_binding=self._tenant_binding,
                    context_version=self._context_version,
                )
            except (KeyError, ValueError) as exc:
                raise RootCauseOrchestrationError(
                    f"invalid/non-governed next-test semantic handle: {handle_id}"
                ) from exc
            if (
                handle.parent_obligation_id is not None
                and handle.parent_obligation_id != root_id
            ):
                raise RootCauseOrchestrationError(
                    "next-test semantic handle belongs to another obligation"
                )
            if handle.trigger_evidence_ref is not None:
                if handle.trigger_evidence_ref not in admissible_evidence_refs:
                    raise RootCauseOrchestrationError(
                        "derived semantic handle trigger is unrelated to hypothesis Evidence"
                    )
                self._ledger.validated_evidence(handle.trigger_evidence_ref)
                if not self._ledger.evidence_view.contains_inspected(
                    handle.trigger_evidence_ref
                ):
                    raise RootCauseOrchestrationError(
                        "derived semantic handle requires inspected trigger Evidence"
                    )

    def _capability_for(self, proposal: HypothesisNextTestProposal) -> ManagerCapabilityKey:
        try:
            self._tools.tool_id_for_task_kind(proposal.task_kind)
            capability = self._tasks.capability_for_task_kind(proposal.task_kind)
        except (ResearchToolContractError, ResearchTaskMaterializationError) as exc:
            raise RootCauseOrchestrationError(
                f"next-test task kind is not a declared governed execution family: {proposal.task_kind.value}"
            ) from exc

        spec = self._capabilities.get(capability)
        if spec.execution_mode != ManagerCapabilityExecutionMode.DIRECT:
            raise RootCauseOrchestrationError(
                "next-test task kind is not backed by DIRECT governed capability"
            )
        # Current Day7 relationship execution binds directly to a RELATIONSHIP
        # obligation. Day8 must not create an advertised dead-end under ROOT_CAUSE.
        if proposal.task_kind == ResearchTaskKind.RELATIONSHIP:
            raise RootCauseOrchestrationError(
                "derived RELATIONSHIP under ROOT_CAUSE requires a separate governed "
                "derived-obligation adapter; fail closed rather than bypass CrossDomainJoinGate"
            )
        return capability

    def _validate_shape(
        self,
        *,
        proposal: HypothesisNextTestProposal,
        capability: ManagerCapabilityKey,
    ) -> None:
        ledger = self._runtime.ledger
        if ledger is None:
            raise RootCauseOrchestrationError("next-test requires obligation ledger")
        root = self._obligations.get(
            ledger,
            self._ledger.state.parent_obligation_id,
        )
        candidate = root.model_copy(
            update={
                "capability_key": capability,
                "semantic_handle_refs": proposal.input_refs,
                "ranking_direction": proposal.ranking_direction,
                "ranking_limit": proposal.ranking_limit,
            }
        )
        result = self._bindings.validate(
            candidate,
            tenant_binding=self._tenant_binding,
            context_version=self._context_version,
        )
        if not result.valid:
            raise RootCauseOrchestrationError(
                "next-test semantic/input shape is not applicable: "
                + "; ".join(result.reasons)
            )

    @staticmethod
    def _task_id(
        *,
        ledger: HypothesisLedger,
        proposal: HypothesisNextTestProposal,
        parent_task: ResearchTask,
    ) -> str:
        payload = {
            "root_obligation_id": ledger.state.parent_obligation_id,
            "hypothesis_ref": proposal.hypothesis_ref,
            "parent_task_id": parent_task.task_id,
            "trigger_evidence_ref": proposal.trigger_evidence_ref,
            "task_kind": proposal.task_kind.value,
            "input_refs": list(proposal.input_refs),
            "ranking_direction": proposal.ranking_direction,
            "ranking_limit": proposal.ranking_limit,
            "accepted_contract_id": ledger.state.accepted_contract_id,
            "run_id": ledger.state.run_id,
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "rt_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def materialize(self, proposal: HypothesisNextTestProposal) -> ResearchTask:
        hypothesis, _evidence, parent_task = self._validated_hypothesis_and_evidence(
            proposal
        )
        admissible_evidence = {
            *hypothesis.trigger_evidence_refs,
            *(link.evidence_ref for link in hypothesis.evidence_links),
        }
        self._validate_handles(
            proposal=proposal,
            admissible_evidence_refs=admissible_evidence,
        )
        capability = self._capability_for(proposal)
        self._validate_shape(proposal=proposal, capability=capability)

        server_task_id = self._task_id(
            ledger=self._ledger,
            proposal=proposal,
            parent_task=parent_task,
        )
        derived = DerivedResearchTaskProposal(
            task_id=server_task_id,
            task_kind=proposal.task_kind,
            parent_task_id=parent_task.task_id,
            parent_obligation_id=self._ledger.state.parent_obligation_id,
            trigger_evidence_ref=proposal.trigger_evidence_ref,
            input_refs=proposal.input_refs,
            material_reason=proposal.material_reason,
        )
        materialized = self._tasks.materialize_derived_candidates(
            runtime=self._runtime,
            evidence_store=self._evidence_store,
            task_registry=self._task_registry,
            parent_task=parent_task,
            proposals=(derived,),
            cardinality=CardinalityObservation(source=CardinalitySource.UNKNOWN),
        )
        if not materialized.registered_tasks:
            raise RootCauseOrchestrationError(
                "next-test fanout/budget policy denied task materialization"
            )
        task = materialized.registered_tasks[0]
        try:
            self._ledger.link_next_test(
                proposal.hypothesis_ref,
                task_ref=task.task_id,
            )
        except HypothesisLedgerError as exc:
            raise RootCauseOrchestrationError(str(exc)) from exc
        return task
