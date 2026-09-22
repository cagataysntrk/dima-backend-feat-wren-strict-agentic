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
        budget: ManagerBudget | None = None,
        tools: ManagerToolRegistry | None = None,
        contract_registry: AcceptedContractRegistry | None = None,
        authority_registry: AcceptedAuthorityRegistry | None = None,
    ) -> None:
        run_id = "mgr_" + hashlib.sha256(request_ref.encode("utf-8")).hexdigest()[:20]
        self._budget = budget or ManagerBudget()
        self._tools = tools or ManagerToolRegistry()
        self._contracts = contract_registry or AcceptedContractRegistry()
        self._authorities = authority_registry or AcceptedAuthorityRegistry()
        self._snapshot = ManagerRunSnapshot(run_id=run_id, state=ManagerState.INITIAL)
        self._ledger: UserObligationLedger | None = None
        self._accepted_contract = None
        self._semantic_receipts: list[SemanticResolutionReceipt] = []

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
    def has_accepted_contract(self) -> bool:
        return self._snapshot.accepted_contract_id is not None

    def reset_semantic_resolution_receipts(self) -> None:
        """Start a fresh pre-acceptance draft attempt without receipt carry-over."""
        if self.has_accepted_contract:
            raise ManagerStateError(
                "accepted authority semantic receipts cannot be reset"
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

    def note_manager_turn(self) -> ManagerRunSnapshot:
        turns = self._snapshot.manager_turns + 1
        if turns > self._budget.max_manager_turns:
            self._snapshot = self._snapshot.model_copy(
                update={"state": ManagerState.BUDGET_EXHAUSTED}
            )
            raise ManagerBudgetError("manager turn budget exhausted")
        self._snapshot = self._snapshot.model_copy(update={"manager_turns": turns})
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
