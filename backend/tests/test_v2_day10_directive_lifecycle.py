"""D10-H typed ResearchDirective lifecycle attacks."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.manager_executor import EvidenceStore
from app.v2.manager_loop import (
    ManagerActionKind,
    ManagerDecisionTransport,
    ResearchManagerLoop,
)
from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerCapabilityKey,
    ManagerRunSnapshot,
    ManagerState,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveDisposition,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    UserObligationLedger,
)
from app.v2.manager_runtime import (
    ManagerBudgetError,
    ManagerRuntime,
    ManagerStateError,
)
from app.v2.models import EvidenceArtifact
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.source_spans import SourceSpanRegistry
from lab.v2_certification_oracle import certify_adaptive_lifecycle


def _runtime_with_directive(
    directive_type: ResearchDirectiveType,
    *,
    evidence_obligation: str = "U1",
    inspected: bool = True,
):
    condition = {
        ResearchDirectiveType.ADAPT_ON_EVIDENCE:
            ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
        ResearchDirectiveType.BROADEN_WITHIN_BUDGET:
            ResearchDirectiveCondition.WITHIN_SYSTEM_BUDGET,
    }[directive_type]
    directive = ResearchDirective(
        directive_id="R1",
        directive_type=directive_type,
        parent_obligation_id="U1",
        condition=condition,
        source_refs=("src_" + "1" * 24,),
    )
    contract = AcceptedTurnContract(
        contract_id="atc-directive",
        lineage_id="atl-directive",
        version=1,
        turn_id="turn-directive",
        request_ref="request-directive",
        source_message_hash="a" * 64,
        accepted_attempt_id="attempt-1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U1",),
        research_directives=(directive,),
        context_version="ctx",
        accepted_at_iso="2026-09-24T00:00:00+00:00",
    )
    ledger = UserObligationLedger(
        lineage_id="atl-directive",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=("src_" + "1" * 24,),
                evidence_refs=("E1",),
                introduced_in_version=1,
            ),
        ),
    )
    runtime = ManagerRuntime(
        request_ref="request-directive",
        turn_ref="turn-directive",
    )
    runtime._accepted_contract = contract
    runtime._ledger = ledger
    runtime._snapshot = ManagerRunSnapshot(
        run_id=runtime.snapshot.run_id,
        state=ManagerState.INVESTIGATING,
        accepted_contract_id=contract.contract_id,
        lineage_id=contract.lineage_id,
        evidence_refs=("E1",),
        inspected_evidence_refs=("E1",) if inspected else (),
    )
    runtime._directive_dispositions = (
        {
            "R1": ResearchDirectiveDisposition(
                directive_id="R1",
                directive_type=directive_type,
                parent_obligation_id="U1",
                status=ResearchDirectiveDispositionStatus.OPEN,
            )
        }
        if directive_type == ResearchDirectiveType.ADAPT_ON_EVIDENCE
        else {}
    )
    store = EvidenceStore()
    store.put(
        EvidenceArtifact(
            artifact_id="E1",
            task_id="seed:U1",
            obligation_ids=(evidence_obligation,),
            query_contract_refs=("QC1",),
            evidence_kind="standard_analytics",
            verified=True,
            payload={"executions": ()},
        )
    )
    return runtime, store


def test_no_material_direction_is_typed_action_not_fake_analytical_truth():
    decision = ManagerDecisionTransport(
        action=ManagerActionKind.DISPOSITION_RESEARCH_DIRECTIVE,
        directive_id="R1",
        directive_evidence_ref="E1",
        directive_disposition="NO_MATERIAL_DIRECTION",
        directive_reason="Doğrulanmış sonuç yeni maddi yön göstermiyor.",
    )
    assert decision.directive_disposition == "NO_MATERIAL_DIRECTION"

    runtime, store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    disposition = ResearchManagerLoop._admit_no_material_direction(
        runtime=runtime,
        evidence_store=store,
        directive_id=decision.directive_id,
        evidence_ref=decision.directive_evidence_ref,
        reason=decision.directive_reason,
    )

    assert disposition.status == ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION
    assert disposition.evidence_ref == "E1"
    assert disposition.branch_task_refs == ()
    assert runtime.snapshot.evidence_refs == ("E1",)

    tasks = ResearchTaskRegistry()
    assert ResearchManagerLoop._try_deterministic_finish(
        runtime=runtime,
        task_registry=tasks,
    ) is True
    assert tuple(tasks.tasks) == ()
    assert runtime.snapshot.state == ManagerState.COMPLETED


def test_no_material_direction_requires_current_inspected_parent_lineage_evidence():
    runtime, store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        inspected=False,
    )
    with pytest.raises(ManagerStateError, match="inspected"):
        ResearchManagerLoop._admit_no_material_direction(
            runtime=runtime,
            evidence_store=store,
            directive_id="R1",
            evidence_ref="E1",
            reason="No material direction.",
        )

    runtime2, store2 = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        evidence_obligation="U_FOREIGN",
        inspected=True,
    )
    with pytest.raises(ManagerStateError, match="parent obligation lineage"):
        ResearchManagerLoop._admit_no_material_direction(
            runtime=runtime2,
            evidence_store=store2,
            directive_id="R1",
            evidence_ref="E1",
            reason="No material direction.",
        )


def test_open_adapt_directive_blocks_finish_until_accounted():
    runtime, _ = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    assert ResearchManagerLoop._try_deterministic_finish(
        runtime=runtime,
        task_registry=ResearchTaskRegistry(),
    ) is False
    assert runtime.snapshot.state == ManagerState.INVESTIGATING


def test_broaden_within_budget_is_policy_not_hidden_completion_obligation():
    runtime, _ = _runtime_with_directive(
        ResearchDirectiveType.BROADEN_WITHIN_BUDGET
    )
    tasks = ResearchTaskRegistry()
    assert runtime.directive_dispositions == ()
    assert ResearchManagerLoop._try_deterministic_finish(
        runtime=runtime,
        task_registry=tasks,
    ) is True
    assert runtime.snapshot.state == ManagerState.COMPLETED
    assert tuple(tasks.tasks) == ()


def test_applied_adapt_disposition_requires_branch_task_refs():
    runtime, _ = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    with pytest.raises(ValueError, match="branch task refs"):
        runtime.account_research_directive(
            directive_id="R1",
            status=ResearchDirectiveDispositionStatus.APPLIED,
            evidence_ref="E1",
            branch_task_refs=(),
            reason="invalid",
        )

    applied = runtime.account_research_directive(
        directive_id="R1",
        status=ResearchDirectiveDispositionStatus.APPLIED,
        evidence_ref="E1",
        branch_task_refs=("D1",),
        reason="governed branch executed",
    )
    assert applied.status == ResearchDirectiveDispositionStatus.APPLIED
    assert applied.branch_task_refs == ("D1",)


def test_preacceptance_retry_does_not_consume_research_phase_budget():
    canonical = ManagerRuntime(
        request_ref="budget-canonical",
        turn_ref="turn-budget-canonical",
    )
    canonical.note_manager_turn(phase="preacceptance")
    canonical.note_manager_turn(phase="preacceptance")
    assert canonical.snapshot.preacceptance_turns == 2
    assert canonical.snapshot.manager_turns == 2
    assert canonical.budget.max_preacceptance_turns == 4
    assert canonical.budget.max_manager_turns == 4
    assert canonical.budget.max_total_manager_turns == 8

    revision = ManagerRuntime(
        request_ref="budget-revision",
        turn_ref="turn-budget-revision",
    )
    for _ in range(4):
        revision.note_manager_turn(phase="preacceptance")
    for _ in range(4):
        revision.note_manager_turn(phase="research")

    assert revision.snapshot.preacceptance_turns == 4
    assert revision.snapshot.research_manager_turns == 4
    assert revision.snapshot.manager_turns == 8

    with pytest.raises(ManagerBudgetError, match="total Manager turn budget exhausted"):
        revision.note_manager_turn(phase="research")
    assert revision.snapshot.state == ManagerState.BUDGET_EXHAUSTED


def test_research_phase_has_its_own_four_turn_hard_cap():
    runtime = ManagerRuntime(
        request_ref="budget-research-phase",
        turn_ref="turn-budget-research-phase",
    )
    for _ in range(2):
        runtime.note_manager_turn(phase="preacceptance")
    for _ in range(4):
        runtime.note_manager_turn(phase="research")

    assert runtime.snapshot.manager_turns == 6
    assert runtime.snapshot.research_manager_turns == 4

    with pytest.raises(ManagerBudgetError, match="research Manager turn budget exhausted"):
        runtime.note_manager_turn(phase="research")
    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED



def test_action_availability_projects_only_parent_lineage_evidence_for_open_directive():
    runtime, store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        evidence_obligation="U1",
        inspected=True,
    )
    store.put(
        EvidenceArtifact(
            artifact_id="E_ROOT",
            task_id="seed:U_FOREIGN",
            obligation_ids=("U_FOREIGN",),
            query_contract_refs=("QC_ROOT",),
            evidence_kind="standard_analytics",
            verified=True,
            payload={"executions": ()},
        )
    )
    runtime._snapshot = runtime.snapshot.model_copy(
        update={
            "evidence_refs": ("E1", "E_ROOT"),
            "inspected_evidence_refs": ("E1", "E_ROOT"),
        }
    )

    class _NoopLLM:
        def structured_json(self, *args, **kwargs):
            raise AssertionError("availability projection must not call provider")

    loop = ResearchManagerLoop(
        llm=_NoopLLM(),
        source_spans=SourceSpanRegistry(),
    )
    action_set = loop._action_set(
        runtime=runtime,
        observations=[],
        action_frontier={"progress_fingerprint": "prog-directive-lineage"},
        research_state=None,
        hypothesis_ledgers={},
        evidence_store=store,
        research_tasks=(),
        governed_semantic_inventory=(),
    )

    dispositions = [
        item
        for item in action_set.action_instances
        if item.action_kind == "disposition_research_directive"
    ]
    assert len(dispositions) == 1
    assert dispositions[0].binding("directive_id") == "R1"
    assert dispositions[0].binding("parent_obligation_id") == "U1"
    assert dispositions[0].binding("evidence_ref") == "E1"
    assert all(
        item.binding("evidence_ref") != "E_ROOT"
        for item in dispositions
    )


def _set_parent_terminal(
    runtime: ManagerRuntime,
    status: ObligationStatus,
    *,
    evidence_refs: tuple[str, ...] = (),
):
    item = runtime.ledger.items[0]
    runtime._ledger = runtime.ledger.model_copy(
        update={
            "items": (
                item.model_copy(
                    update={
                        "status": status,
                        "evidence_refs": evidence_refs,
                    }
                ),
            )
        }
    )
    runtime._snapshot = runtime.snapshot.model_copy(
        update={
            "evidence_refs": evidence_refs,
            "inspected_evidence_refs": evidence_refs,
        }
    )


@pytest.mark.parametrize(
    "status",
    [
        ObligationStatus.BLOCKED_DATA_GAP,
        ObligationStatus.LIMITED,
        ObligationStatus.UNSUPPORTED,
    ],
)
def test_partial_terminal_parent_reconciles_adapt_to_blocked_without_evidence_or_model(
    status,
):
    runtime, _store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    _set_parent_terminal(runtime, status)

    reconciled = ResearchManagerLoop._reconcile_blocked_research_directives(
        runtime=runtime,
    )

    assert reconciled == ("R1",)
    disposition = runtime.directive_disposition("R1")
    assert disposition.status == ResearchDirectiveDispositionStatus.BLOCKED
    assert disposition.evidence_ref is None
    assert disposition.branch_task_refs == ()
    assert status.value in disposition.reason

    assert ResearchManagerLoop._try_deterministic_finish(
        runtime=runtime,
        task_registry=ResearchTaskRegistry(),
    ) is True
    assert runtime.snapshot.state == ManagerState.COMPLETED
    assert runtime.snapshot.terminal_status.value == "PARTIAL"


@pytest.mark.parametrize(
    "status",
    [ObligationStatus.VERIFIED, ObligationStatus.ACCEPTED],
)
def test_nonpartial_parent_cannot_auto_block_adapt_directive(status):
    runtime, _store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    _set_parent_terminal(
        runtime,
        status,
        evidence_refs=("E1",) if status == ObligationStatus.VERIFIED else (),
    )

    assert ResearchManagerLoop._reconcile_blocked_research_directives(
        runtime=runtime,
    ) == ()
    assert (
        runtime.directive_disposition("R1").status
        == ResearchDirectiveDispositionStatus.OPEN
    )
    with pytest.raises(
        ManagerStateError,
        match="authoritative partial-terminal parent",
    ):
        runtime.account_research_directive(
            directive_id="R1",
            status=ResearchDirectiveDispositionStatus.BLOCKED,
            evidence_ref=None,
            branch_task_refs=(),
            reason="not-authoritative-block",
        )


def test_blocked_disposition_shape_allows_no_evidence_only_with_reason_and_no_branches():
    valid = ResearchDirectiveDisposition(
        directive_id="R1",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.BLOCKED,
        evidence_ref=None,
        branch_task_refs=(),
        reason="authoritative parent terminal partial",
    )
    assert valid.evidence_ref is None

    with pytest.raises(ValueError, match="bounded reason"):
        ResearchDirectiveDisposition(
            directive_id="R1",
            directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
            parent_obligation_id="U1",
            status=ResearchDirectiveDispositionStatus.BLOCKED,
            evidence_ref=None,
            branch_task_refs=(),
            reason=None,
        )
    with pytest.raises(ValueError, match="branch task refs"):
        ResearchDirectiveDisposition(
            directive_id="R1",
            directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
            parent_obligation_id="U1",
            status=ResearchDirectiveDispositionStatus.BLOCKED,
            evidence_ref=None,
            branch_task_refs=("D1",),
            reason="blocked",
        )


def test_blocked_certification_accepts_authoritative_partial_parent_without_evidence():
    runtime, _store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    _set_parent_terminal(runtime, ObligationStatus.BLOCKED_DATA_GAP)
    ResearchManagerLoop._reconcile_blocked_research_directives(runtime=runtime)
    directive = runtime.accepted_contract.research_directives[0]
    disposition = runtime.directive_disposition("R1")

    certification = certify_adaptive_lifecycle(
        directive=directive,
        disposition=disposition,
        evidence_items=(),
        ledger=runtime.ledger,
        inspected_evidence_refs=(),
        product_verified_complete=False,
    )

    assert certification.valid is True
    assert certification.lifecycle_outcome == "VALID_PRODUCT_TERMINAL"
    assert (
        certification.certification_coverage
        == "CERTIFICATION_COVERAGE_INCOMPLETE"
    )
    assert certification.evidence_ref is None


def test_blocked_certification_can_never_greenwash_verified_complete():
    runtime, _store = _runtime_with_directive(
        ResearchDirectiveType.ADAPT_ON_EVIDENCE
    )
    _set_parent_terminal(runtime, ObligationStatus.LIMITED)
    ResearchManagerLoop._reconcile_blocked_research_directives(runtime=runtime)

    certification = certify_adaptive_lifecycle(
        directive=runtime.accepted_contract.research_directives[0],
        disposition=runtime.directive_disposition("R1"),
        evidence_items=(),
        ledger=runtime.ledger,
        inspected_evidence_refs=(),
        product_verified_complete=True,
    )

    assert certification.valid is False
    assert certification.lifecycle_outcome == "INVALID"
    assert any("VERIFIED_COMPLETE" in item for item in certification.errors)
