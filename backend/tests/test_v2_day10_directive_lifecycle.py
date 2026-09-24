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
from app.v2.manager_runtime import ManagerRuntime, ManagerStateError
from app.v2.models import EvidenceArtifact
from app.v2.research_tasks import ResearchTaskRegistry


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
