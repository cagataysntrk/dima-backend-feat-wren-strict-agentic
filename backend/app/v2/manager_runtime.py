"""Bounded Day 6.5 Manager state machine.

This runtime owns state/budget/tool-policy enforcement only. Model prompting and actual
trust-plane tool execution are injected later through a narrow executor boundary.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from typing import Protocol, Any

from app.v2.acceptance import AcceptedContractRegistry
from app.v2.completion import CompletionGate
from app.v2.manager_errors import ManagerRecoverableToolError
from app.v2.manager_models import (
    AcceptanceResult,
    AcceptanceStatus,
    ManagerBudget,
    ManagerRunSnapshot,
    ManagerState,
    ObligationStatus,
    ResearchDirectiveDisposition,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    ResearchRunTerminal,
    SemanticResolutionReceipt,
    UserObligationLedger,
)
from app.v2.standard_authority import AcceptedAuthorityRegistry
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
    ManagerToolPolicyError,
    ManagerToolRegistry,
)


class ManagerToolExecutor(Protocol):
    def execute(self, call: ManagerToolCall, validated_args: Any, runtime: "ManagerRuntime") -> Any:
        ...


class ManagerBudgetError(RuntimeError):
    pass


class ManagerStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class ManagerStepResult:
    snapshot: ManagerRunSnapshot
    tool_result: Any = None


class ManagerRuntime:
    def __init__(
        self,
        *,
        request_ref: str,
        turn_ref: str | None = None,
        budget: ManagerBudget | None = None,
        tools: ManagerToolRegistry | None = None,
        contract_registry: AcceptedContractRegistry | None = None,
        authority_registry: AcceptedAuthorityRegistry | None = None,
    ) -> None:
        run_identity = turn_ref or request_ref
        run_id = "mgr_" + hashlib.sha256(run_identity.encode("utf-8")).hexdigest()[:20]
        self._budget = budget or ManagerBudget()
        self._tools = tools or ManagerToolRegistry()
        self._contracts = contract_registry or AcceptedContractRegistry()
        self._authorities = authority_registry or AcceptedAuthorityRegistry()
        self._snapshot = ManagerRunSnapshot(run_id=run_id, state=ManagerState.INITIAL)
        self._ledger: UserObligationLedger | None = None
        self._accepted_contract = None
        self._semantic_receipts: list[SemanticResolutionReceipt] = []
        self._directive_dispositions: dict[str, ResearchDirectiveDisposition] = {}

    @classmethod
    def restore_canonical(
        cls,
        *,
        snapshot: ManagerRunSnapshot,
        accepted_contract,
        ledger: UserObligationLedger,
        directive_dispositions: tuple[ResearchDirectiveDisposition, ...] = (),
        budget: ManagerBudget | None = None,
    ) -> "ManagerRuntime":
        """Restore terminal canonical runtime state without restoring scratch cognition."""

        if accepted_contract is None:
            raise ManagerStateError("runtime restore requires accepted contract")
        if (
            snapshot.accepted_contract_id != accepted_contract.contract_id
            or snapshot.lineage_id != accepted_contract.lineage_id
            or ledger.lineage_id != accepted_contract.lineage_id
            or ledger.version != accepted_contract.version
        ):
            raise ManagerStateError(
                "runtime restore contract/ledger/snapshot authority mismatch"
            )
        if snapshot.state not in {
            ManagerState.COMPLETED,
            ManagerState.BUDGET_EXHAUSTED,
            ManagerState.BLOCKED,
            ManagerState.NEEDS_CLARIFICATION,
            ManagerState.FAILED,
        }:
            raise ManagerStateError(
                "runtime restore requires a persisted terminal checkpoint"
            )

        restored = cls(
            request_ref=f"restore:{snapshot.run_id}",
            budget=budget,
        )
        restored._contracts.validate(accepted_contract)
        restored._authorities.validate(accepted_contract)
        restored._contracts.commit(accepted_contract)
        restored._authorities.commit(accepted_contract)
        restored._snapshot = snapshot
        restored._accepted_contract = accepted_contract
        restored._ledger = ledger
        restored._semantic_receipts = []
        restored._directive_dispositions = {
            item.directive_id: item
            for item in directive_dispositions
        }
        expected_directives = {
            item.directive_id
            for item in accepted_contract.research_directives
            if item.directive_type == ResearchDirectiveType.ADAPT_ON_EVIDENCE
        }
        if set(restored._directive_dispositions) != expected_directives:
            raise ManagerStateError(
                "runtime restore directive disposition set mismatch"
            )
        return restored

    @property
    def snapshot(self) -> ManagerRunSnapshot:
        return self._snapshot

    @property
    def budget(self) -> ManagerBudget:
        """Read-only canonical Research budget; fanout must not invent a second budget."""
        return self._budget

    @property
    def remaining_data_queries(self) -> int:
        return max(self._budget.max_data_queries - self._snapshot.data_queries, 0)

    @property
    def ledger(self) -> UserObligationLedger | None:
        return self._ledger

    @property
    def accepted_contract(self):
        return self._accepted_contract

    @property
    def authority_registry(self) -> AcceptedAuthorityRegistry:
        return self._authorities

    @property
    def semantic_resolution_receipts(self) -> tuple[SemanticResolutionReceipt, ...]:
        return tuple(self._semantic_receipts)

    @property
    def directive_dispositions(self) -> tuple[ResearchDirectiveDisposition, ...]:
        if self._accepted_contract is None:
            return ()
        return tuple(
            self._directive_dispositions[item.directive_id]
            for item in self._accepted_contract.research_directives
            if item.directive_id in self._directive_dispositions
        )

    def directive_disposition(
        self,
        directive_id: str,
    ) -> ResearchDirectiveDisposition:
        try:
            return self._directive_dispositions[directive_id]
        except KeyError as exc:
            raise ManagerStateError(
                f"unknown accepted research directive: {directive_id}"
            ) from exc

    def account_research_directive(
        self,
        *,
        directive_id: str,
        status: ResearchDirectiveDispositionStatus,
        evidence_ref: str | None,
        branch_task_refs: tuple[str, ...] = (),
        reason: str | None = None,
    ) -> ResearchDirectiveDisposition:
        if self._accepted_contract is None:
            raise ManagerStateError("directive accounting requires accepted contract")
        directive = next(
            (
                item
                for item in self._accepted_contract.research_directives
                if item.directive_id == directive_id
            ),
            None,
        )
        if directive is None:
            raise ManagerStateError(
                f"directive is not part of accepted contract: {directive_id}"
            )
        if directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE:
            raise ManagerStateError(
                "only ADAPT_ON_EVIDENCE has completion-relevant disposition"
            )
        if status == ResearchDirectiveDispositionStatus.BLOCKED:
            if self._ledger is None:
                raise ManagerStateError(
                    "BLOCKED directive accounting requires accepted obligation ledger"
                )
            parent = next(
                (
                    item
                    for item in self._ledger.items
                    if item.obligation_id == directive.parent_obligation_id
                ),
                None,
            )
            if parent is None:
                raise ManagerStateError(
                    "BLOCKED directive parent obligation is absent from accepted ledger"
                )
            if parent.status not in {
                ObligationStatus.BLOCKED_DATA_GAP,
                ObligationStatus.LIMITED,
                ObligationStatus.UNSUPPORTED,
            }:
                raise ManagerStateError(
                    "BLOCKED directive requires authoritative partial-terminal parent"
                )
        current = self.directive_disposition(directive_id)
        if current.status != ResearchDirectiveDispositionStatus.OPEN:
            candidate = ResearchDirectiveDisposition(
                directive_id=directive.directive_id,
                directive_type=directive.directive_type,
                parent_obligation_id=directive.parent_obligation_id,
                status=status,
                evidence_ref=evidence_ref,
                branch_task_refs=tuple(dict.fromkeys(branch_task_refs)),
                reason=reason,
            )
            if candidate == current:
                return current
            raise ManagerStateError(
                f"research directive already terminal: {directive_id}"
            )
        if status == ResearchDirectiveDispositionStatus.OPEN:
            raise ManagerStateError("directive accounting must be terminal")
        disposition = ResearchDirectiveDisposition(
            directive_id=directive.directive_id,
            directive_type=directive.directive_type,
            parent_obligation_id=directive.parent_obligation_id,
            status=status,
            evidence_ref=evidence_ref,
            branch_task_refs=tuple(dict.fromkeys(branch_task_refs)),
            reason=reason,
        )
        self._directive_dispositions[directive_id] = disposition
        return disposition

    @property
    def has_accepted_contract(self) -> bool:
        return self._snapshot.accepted_contract_id is not None

    def reset_semantic_resolution_receipts(self) -> None:
        """Start a fresh pre-acceptance draft attempt without receipt carry-over.

        A report-section continuation keeps the immutable active contract as the lineage
        head but re-enters UNDERSTANDING for a new user turn. Only that explicit state may
        clear current-turn semantic receipts while preserving prior accepted authority.
        """
        if self.has_accepted_contract and self._snapshot.state != ManagerState.UNDERSTANDING:
            raise ManagerStateError(
                "accepted authority semantic receipts may reset only for explicit follow-up understanding"
            )
        self._semantic_receipts = []

    def _record_semantic_receipts(self, result: Any) -> int:
        """Persist USER_SOURCE binding provenance only; never infer intent completeness."""
        added = 0
        existing = {
            (item.source_ref, item.handle_id)
            for item in self._semantic_receipts
        }
        for resolved in tuple(getattr(result, "resolved", ()) or ()):
            source_ref = getattr(resolved, "source_ref", None)
            provenance = getattr(resolved, "provenance", None)
            handle = getattr(resolved, "handle", None)
            if (
                provenance != "USER_SOURCE"
                or not source_ref
                or handle is None
            ):
                continue
            key = (source_ref, handle.handle_id)
            if key in existing:
                continue
            self._semantic_receipts.append(
                SemanticResolutionReceipt(
                    source_ref=source_ref,
                    handle_id=handle.handle_id,
                    target_kind=handle.target_kind,
                )
            )
            existing.add(key)
            added += 1
        return added

    def begin_understanding(self) -> ManagerRunSnapshot:
        if self._snapshot.state != ManagerState.INITIAL:
            raise ManagerStateError("understanding can start only from INITIAL")
        self._snapshot = self._snapshot.model_copy(update={"state": ManagerState.UNDERSTANDING})
        return self._snapshot

    def begin_followup_turn(self) -> ManagerRunSnapshot:
        """Open a new user turn on the same accepted Research lineage/run.

        Evidence and immutable accepted authority remain; per-turn budgets/receipts reset.
        No contract fields are mutated here. The next PROPOSE_ACCEPTANCE must produce a
        new version through IntentAcceptanceGate.
        """
        if self._accepted_contract is None or self._ledger is None:
            raise ManagerStateError("follow-up requires active accepted contract + ledger")
        if self._snapshot.state not in {
            ManagerState.COMPLETED,
            ManagerState.BUDGET_EXHAUSTED,
            ManagerState.BLOCKED,
            ManagerState.NEEDS_CLARIFICATION,
        }:
            raise ManagerStateError(
                f"follow-up cannot open from non-terminal state {self._snapshot.state.value}"
            )
        self._semantic_receipts = []
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.UNDERSTANDING,
                "terminal_status": None,
                "tool_calls": 0,
                "data_queries": 0,
                "manager_turns": 0,
                "preacceptance_turns": 0,
                "research_manager_turns": 0,
                "last_error": None,
            }
        )
        return self._snapshot

    def note_manager_turn(
        self,
        *,
        phase: str = "research",
    ) -> ManagerRunSnapshot:
        if phase not in {"preacceptance", "research"}:
            raise ValueError("manager turn phase must be preacceptance or research")

        total_turns = self._snapshot.manager_turns + 1
        if total_turns > self._budget.max_total_manager_turns:
            self._snapshot = self._snapshot.model_copy(
                update={"state": ManagerState.BUDGET_EXHAUSTED}
            )
            raise ManagerBudgetError("total Manager turn budget exhausted")

        if phase == "preacceptance":
            phase_turns = self._snapshot.preacceptance_turns + 1
            if phase_turns > self._budget.max_preacceptance_turns:
                self._snapshot = self._snapshot.model_copy(
                    update={"state": ManagerState.BUDGET_EXHAUSTED}
                )
                raise ManagerBudgetError("preacceptance Manager turn budget exhausted")
            self._snapshot = self._snapshot.model_copy(
                update={
                    "manager_turns": total_turns,
                    "preacceptance_turns": phase_turns,
                }
            )
            return self._snapshot

        phase_turns = self._snapshot.research_manager_turns + 1
        if phase_turns > self._budget.max_manager_turns:
            self._snapshot = self._snapshot.model_copy(
                update={"state": ManagerState.BUDGET_EXHAUSTED}
            )
            raise ManagerBudgetError("research Manager turn budget exhausted")
        self._snapshot = self._snapshot.model_copy(
            update={
                "manager_turns": total_turns,
                "research_manager_turns": phase_turns,
            }
        )
        return self._snapshot

    def call_tool(self, call: ManagerToolCall, *, executor: ManagerToolExecutor) -> ManagerStepResult:
        validated = self._tools.validate(
            call,
            state=self._snapshot.state,
            has_accepted_contract=self.has_accepted_contract,
        )
        spec = self._tools.spec(call.name)

        tool_calls = self._snapshot.tool_calls + 1
        data_queries = self._snapshot.data_queries + int(spec.data_query)
        if tool_calls > self._budget.max_tool_calls or data_queries > self._budget.max_data_queries:
            self._snapshot = self._snapshot.model_copy(
                update={"state": ManagerState.BUDGET_EXHAUSTED}
            )
            raise ManagerBudgetError("manager tool/data-query budget exhausted")

        self._snapshot = self._snapshot.model_copy(
            update={"tool_calls": tool_calls, "data_queries": data_queries}
        )
        try:
            result = executor.execute(call, validated, self)
        except ManagerRecoverableToolError as exc:
            self._snapshot = self._snapshot.model_copy(
                update={"last_error": f"{exc.code}: {exc}"}
            )
            raise
        except Exception as exc:
            self._snapshot = self._snapshot.model_copy(
                update={
                    "state": ManagerState.FAILED,
                    "terminal_status": ResearchRunTerminal.FAILED,
                    "last_error": str(exc),
                }
            )
            raise

        if call.name == ManagerToolName.RESOLVE_SEMANTICS:
            self._record_semantic_receipts(result)
            if self._snapshot.state == ManagerState.INITIAL:
                self._snapshot = self._snapshot.model_copy(update={"state": ManagerState.UNDERSTANDING})
        elif call.name == ManagerToolName.PROPOSE_ACCEPTANCE:
            if not isinstance(result, AcceptanceResult):
                raise ManagerStateError("propose_acceptance executor must return AcceptanceResult")
            if result.status == AcceptanceStatus.ACCEPTED:
                assert result.contract is not None and result.ledger is not None
                # Two-phase validation keeps Research lineage/version truth and
                # cross-family XOR aligned without creating a second Research body.
                self._contracts.validate(result.contract)
                self._authorities.validate(result.contract)
                self._contracts.commit(result.contract)
                self._authorities.commit(result.contract)
                self._accepted_contract = result.contract
                self._ledger = result.ledger
                self._directive_dispositions = {
                    directive.directive_id: ResearchDirectiveDisposition(
                        directive_id=directive.directive_id,
                        directive_type=directive.directive_type,
                        parent_obligation_id=directive.parent_obligation_id,
                        status=ResearchDirectiveDispositionStatus.OPEN,
                    )
                    for directive in result.contract.research_directives
                    if directive.directive_type == ResearchDirectiveType.ADAPT_ON_EVIDENCE
                }
                self._snapshot = self._snapshot.model_copy(
                    update={
                        "state": ManagerState.CONTRACT_ACCEPTED,
                        "accepted_contract_id": result.contract.contract_id,
                        "lineage_id": result.contract.lineage_id,
                    }
                )
            elif result.status == AcceptanceStatus.NEEDS_CLARIFICATION:
                self._snapshot = self._snapshot.model_copy(
                    update={"state": ManagerState.NEEDS_CLARIFICATION}
                )
            else:
                self._snapshot = self._snapshot.model_copy(
                    update={"state": ManagerState.UNDERSTANDING}
                )
        elif call.name in {ManagerToolName.RUN_ANALYTICS, ManagerToolName.RUN_RELATIONSHIP}:
            self._snapshot = self._snapshot.model_copy(update={"state": ManagerState.INVESTIGATING})
        elif call.name == ManagerToolName.REQUEST_CLARIFICATION:
            self._snapshot = self._snapshot.model_copy(update={"state": ManagerState.NEEDS_CLARIFICATION})

        return ManagerStepResult(snapshot=self._snapshot, tool_result=result)

    def block_unsupported(self, reason: str) -> ManagerRunSnapshot:
        """Deterministic stop for a recognized capability without a current governed path."""
        if self._snapshot.state in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
        }:
            raise ManagerStateError(
                "terminal Manager state cannot transition to unsupported block"
            )
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.BLOCKED,
                "last_error": reason,
            }
        )
        return self._snapshot

    def pause_partial(self) -> ManagerRunSnapshot:
        """Stop user-controlled Research without claiming CompletionGate success.

        Obligation/Evidence truth is unchanged. BLOCKED is the existing resumable,
        non-completion state; terminal_status=PARTIAL makes the product disposition typed.
        """
        if self._snapshot.state in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
        }:
            raise ManagerStateError(
                "terminal Manager state cannot transition to user partial"
            )
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.BLOCKED,
                "terminal_status": ResearchRunTerminal.PARTIAL,
                "last_error": None,
            }
        )
        return self._snapshot

    def require_clarification(self, reason: str) -> ManagerRunSnapshot:
        """Deterministic safe stop when semantic authority cannot progress."""
        if self._snapshot.state in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
        }:
            raise ManagerStateError(
                "terminal Manager state cannot transition to clarification"
            )
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.NEEDS_CLARIFICATION,
                "last_error": reason,
            }
        )
        return self._snapshot

    def note_additional_data_queries(self, count: int) -> ManagerRunSnapshot:
        if count < 0:
            raise ValueError("additional data query count negatif olamaz")
        total = self._snapshot.data_queries + count
        if total > self._budget.max_data_queries:
            self._snapshot = self._snapshot.model_copy(
                update={"state": ManagerState.BUDGET_EXHAUSTED}
            )
            raise ManagerBudgetError("manager data-query budget exhausted")
        self._snapshot = self._snapshot.model_copy(update={"data_queries": total})
        return self._snapshot

    def attach_evidence(self, evidence_ref: str) -> ManagerRunSnapshot:
        if self._snapshot.state not in {
            ManagerState.CONTRACT_ACCEPTED,
            ManagerState.INVESTIGATING,
        }:
            raise ManagerStateError("evidence can be attached only during accepted investigation")
        refs = tuple(dict.fromkeys((*self._snapshot.evidence_refs, evidence_ref)))
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.INVESTIGATING,
                "evidence_refs": refs,
                "latest_evidence_ref": evidence_ref,
            }
        )
        return self._snapshot

    def mark_evidence_inspected(self, evidence_ref: str) -> ManagerRunSnapshot:
        if evidence_ref not in self._snapshot.evidence_refs:
            raise ManagerStateError(
                "only evidence attached to current Research run can be inspected"
            )
        refs = tuple(
            dict.fromkeys((*self._snapshot.inspected_evidence_refs, evidence_ref))
        )
        self._snapshot = self._snapshot.model_copy(
            update={"inspected_evidence_refs": refs}
        )
        return self._snapshot

    def replace_ledger(self, ledger: UserObligationLedger) -> None:
        if self._ledger is None:
            raise ManagerStateError("accepted ledger does not exist")
        if ledger.lineage_id != self._ledger.lineage_id:
            raise ManagerStateError("ledger lineage cannot change")
        self._ledger = ledger

    def finish(self, gate: CompletionGate | None = None) -> ManagerRunSnapshot:
        if self._snapshot.state == ManagerState.BUDGET_EXHAUSTED:
            raise ManagerStateError(
                "budget-exhausted Manager run cannot transition to COMPLETED"
            )
        if self._ledger is None:
            raise ManagerStateError("cannot finish without accepted obligation ledger")
        outcome = (gate or CompletionGate()).evaluate(self._ledger)
        if not outcome.allowed:
            raise ManagerStateError("; ".join(outcome.reasons) or "completion rejected")
        self._snapshot = self._snapshot.model_copy(
            update={
                "state": ManagerState.COMPLETED,
                "terminal_status": outcome.terminal,
            }
        )
        return self._snapshot
