"""Day14 durable persistence/resume, idempotency, and stale-writer attacks."""

from __future__ import annotations

import pytest

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
    ResearchDirectiveDisposition,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    ResearchRunTerminal,
    UserObligationLedger,
)
from app.v2.models import (
    EvidenceArtifact,
    HypothesisLedgerState,
    ResearchTask,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.persistence import (
    CanonicalResumeState,
    CheckpointScope,
    DurableCheckpointStore,
    StaleCheckpointWrite,
    restore_evidence_store,
    restore_research_context,
    restore_semantic_handles,
    restore_task_registry,
)
from app.v2.product_models import VersionedReport
from app.v2.report_builder import (
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.research_tasks import ResearchTaskLifecycleError
from app.v2.semantic_handles import SemanticHandleRegistry


def _scope() -> CheckpointScope:
    return CheckpointScope(
        tenant_binding="tenant:a",
        principal_subject="user-a",
        session_id="session-a",
        thread_id="thread-a",
        context_version="ctx-day14",
        lineage_id="atl-day14",
    )


def _semantic_records():
    registry = SemanticHandleRegistry()
    handle = registry.mint_from_binding_gate(
        tenant_binding="tenant:a",
        context_version="ctx-day14",
        candidate_id="cand_day14",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="cand_day14",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="net_revenue",
            cube_names=("sales",),
        ),
        parent_obligation_id="U1",
    )
    return registry.export_records(
        tenant_binding="tenant:a",
        context_version="ctx-day14",
    ), handle.handle_id


def _evidence() -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id="evi_day14",
        task_id="task-day14",
        obligation_ids=("U1",),
        query_contract_refs=("c-day14",),
        evidence_kind="standard_analytics",
        verified=True,
        tenant_binding="tenant:a",
        principal_subject="user-a",
        context_version="ctx-day14",
        run_id="mgr-day14",
        lineage_id="atl-day14",
        accepted_contract_id="atc-day14",
    )


def _report(version: int) -> VersionedReport:
    report = ReportDocument(
        report_id="rpt_" + str(version) * 24,
        title=f"Report v{version}",
        sections=(
            ReportSection(
                section_id="rsec_" + str(version + 1) * 24,
                title="Summary",
                blocks=(
                    ReportBlock(
                        block_id="rblk_" + str(version + 2) * 24,
                        block_kind=ReportBlockKind.TEXT,
                        claim_kind=ReportClaimKind.NARRATIVE,
                        content=f"Immutable report version {version}",
                    ),
                ),
                followup_context_ref="rctx_" + str(version + 3) * 24,
            ),
        ),
        provenance=ReportSourceProvenance(
            accepted_contract_id="atc-day14",
            lineage_id="atl-day14",
            run_id="mgr-day14",
            tenant_binding="tenant:a",
            context_version="ctx-day14",
        ),
    )
    return VersionedReport(
        version=version,
        report=report,
        supersedes_report_ref=(
            None if version == 1 else "rpt_" + str(version - 1) * 24
        ),
        source_run_ref="mgr-day14",
    )


def _state(*, report_version: int = 1) -> CanonicalResumeState:
    semantic_records, _ = _semantic_records()
    return CanonicalResumeState(
        research_tasks=(
            ResearchTask(
                task_id="task-day14",
                question_id="U1",
                task_kind="QUERY",
                input_refs=(semantic_records[0].handle.handle_id,),
                state="complete",
            ),
        ),
        evidence=(_evidence(),),
        reports=(_report(report_version),),
        completion_status=ResearchRunTerminal.VERIFIED_COMPLETE,
        semantic_bindings=semantic_records,
    )


def test_checkpoint_survives_store_reconstruction_and_restores_authorities(tmp_path):
    scope = _scope()
    first_store = DurableCheckpointStore(tmp_path)
    committed = first_store.commit(
        scope=scope,
        state=_state(),
        expected_revision=0,
    )

    # Simulate process restart: new repository object, same durable directory.
    restarted = DurableCheckpointStore(tmp_path)
    loaded = restarted.load(scope)

    assert loaded == committed
    assert loaded.revision == 1
    assert loaded.state.completion_status == ResearchRunTerminal.VERIFIED_COMPLETE

    evidence_store = restore_evidence_store(loaded)
    assert evidence_store.get("evi_day14") == _evidence()

    semantic_registry = restore_semantic_handles(loaded)
    _, handle_id = _semantic_records()
    restored = semantic_registry.binding_for_execution(
        handle_id,
        tenant_binding="tenant:a",
        context_version="ctx-day14",
    )
    assert restored.canonical_target.canonical_name == "net_revenue"


def test_exact_resume_retry_is_idempotent_and_does_not_increment_revision(tmp_path):
    store = DurableCheckpointStore(tmp_path)
    scope = _scope()
    state = _state()

    first = store.commit(scope=scope, state=state, expected_revision=0)
    replay = store.commit(scope=scope, state=state, expected_revision=0)

    assert replay == first
    assert replay.revision == 1


def test_stale_contract_or_report_writer_cannot_last_write_win(tmp_path):
    store = DurableCheckpointStore(tmp_path)
    scope = _scope()

    first = store.commit(scope=scope, state=_state(report_version=1), expected_revision=0)
    winner = store.commit(
        scope=scope,
        state=_state(report_version=2),
        expected_revision=first.revision,
    )

    assert winner.revision == 2
    assert winner.state.reports[-1].version == 2

    with pytest.raises(StaleCheckpointWrite, match="stale checkpoint writer"):
        store.commit(
            scope=scope,
            state=_state(report_version=1),
            expected_revision=first.revision,
        )

    assert store.load(scope) == winner


def test_completed_research_task_after_restart_cannot_duplicate_side_effect():
    checkpoint = DurableCheckpointStore.__new__(DurableCheckpointStore)
    # Registry reconstruction is independent of storage adapter instance.
    state = _state()
    scope = _scope()
    from app.v2.persistence import DurableCheckpoint
    cp = DurableCheckpoint(
        checkpoint_id="v2cp_" + "a" * 24,
        scope=scope,
        revision=1,
        state_hash="b" * 64,
        state=state,
    )
    registry = restore_task_registry(cp)
    task = registry.get("task-day14")
    assert task.state == "complete"

    with pytest.raises(
        ResearchTaskLifecycleError,
        match="completed ResearchTask cannot re-execute",
    ):
        registry.begin_execution(
            task=task,
            tool_id="run_analytics",
            action_fingerprint="same-delivery",
        )


def test_scope_key_prevents_foreign_principal_or_context_resume(tmp_path):
    store = DurableCheckpointStore(tmp_path)
    scope = _scope()
    store.commit(scope=scope, state=_state(), expected_revision=0)

    assert store.load(
        scope.model_copy(update={"principal_subject": "user-b"})
    ) is None
    assert store.load(
        scope.model_copy(update={"context_version": "ctx-stale"})
    ) is None


def test_terminal_runtime_rehydrates_and_opens_followup_without_losing_lineage(tmp_path):
    scope = _scope()
    records, handle_id = _semantic_records()
    contract = AcceptedTurnContract(
        contract_id="atc-day14",
        lineage_id="atl-day14",
        version=1,
        turn_id="turn-1",
        request_ref="req-1",
        source_message_hash="a" * 64,
        accepted_attempt_id="attempt-1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U1",),
        context_version="ctx-day14",
        accepted_at_iso="2026-09-26T00:00:00+00:00",
    )
    ledger = UserObligationLedger(
        lineage_id="atl-day14",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=("src-day14",),
                semantic_handle_refs=(handle_id,),
                evidence_refs=("evi_day14",),
                introduced_in_version=1,
            ),
        ),
    )
    snapshot = ManagerRunSnapshot(
        run_id="mgr-day14",
        state=ManagerState.COMPLETED,
        terminal_status=ResearchRunTerminal.VERIFIED_COMPLETE,
        accepted_contract_id=contract.contract_id,
        lineage_id=contract.lineage_id,
        evidence_refs=("evi_day14",),
        inspected_evidence_refs=("evi_day14",),
        latest_evidence_ref="evi_day14",
    )
    state = CanonicalResumeState(
        manager_snapshot=snapshot,
        accepted_contract=contract,
        ledger=ledger,
        evidence=(_evidence(),),
        completion_status=ResearchRunTerminal.VERIFIED_COMPLETE,
        semantic_bindings=records,
    )
    store = DurableCheckpointStore(tmp_path)
    checkpoint = store.commit(
        scope=scope,
        state=state,
        expected_revision=0,
    )

    restored = restore_research_context(checkpoint)
    assert restored.runtime.snapshot == snapshot
    assert restored.accepted_contract == contract
    assert restored.ledger == ledger
    assert restored.evidence_store.get("evi_day14") == _evidence()

    followup = restored.runtime.begin_followup_turn()
    assert followup.state == ManagerState.UNDERSTANDING
    assert followup.accepted_contract_id == contract.contract_id
    assert followup.lineage_id == contract.lineage_id
    assert followup.evidence_refs == ("evi_day14",)
    assert followup.inspected_evidence_refs == ("evi_day14",)
    assert followup.manager_turns == 0
    assert followup.preacceptance_turns == 0
    assert followup.research_manager_turns == 0


def _accepted_resume_authority():
    records, handle_id = _semantic_records()
    contract = AcceptedTurnContract(
        contract_id="atc-day14",
        lineage_id="atl-day14",
        version=1,
        turn_id="turn-1",
        request_ref="req-1",
        source_message_hash="a" * 64,
        accepted_attempt_id="attempt-1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U1",),
        context_version="ctx-day14",
        accepted_at_iso="2026-09-26T00:00:00+00:00",
    )
    ledger = UserObligationLedger(
        lineage_id="atl-day14",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.IN_PROGRESS,
                source_refs=("src-day14",),
                semantic_handle_refs=(handle_id,),
                evidence_refs=(),
                introduced_in_version=1,
            ),
        ),
    )
    snapshot = ManagerRunSnapshot(
        run_id="mgr-day14",
        state=ManagerState.RESEARCHING,
        accepted_contract_id=contract.contract_id,
        lineage_id=contract.lineage_id,
    )
    return records, contract, ledger, snapshot


def test_crash_after_accepted_contract_restores_authority_without_fabricating_evidence(tmp_path):
    records, contract, ledger, snapshot = _accepted_resume_authority()
    state = CanonicalResumeState(
        manager_snapshot=snapshot,
        accepted_contract=contract,
        ledger=ledger,
        semantic_bindings=records,
    )
    store = DurableCheckpointStore(tmp_path)
    checkpoint = store.commit(
        scope=_scope(),
        state=state,
        expected_revision=0,
    )

    restored = restore_research_context(checkpoint)

    assert restored.accepted_contract == contract
    assert restored.ledger == ledger
    assert restored.evidence == ()
    assert restored.runtime.snapshot.state == ManagerState.RESEARCHING


def test_crash_after_evidence_creation_preserves_evidence_before_obligation_consumption(tmp_path):
    records, contract, ledger, snapshot = _accepted_resume_authority()
    evidence = _evidence()
    state = CanonicalResumeState(
        manager_snapshot=snapshot.model_copy(
            update={
                "evidence_refs": (evidence.artifact_id,),
                "latest_evidence_ref": evidence.artifact_id,
            }
        ),
        accepted_contract=contract,
        ledger=ledger,
        evidence=(evidence,),
        semantic_bindings=records,
    )
    checkpoint = DurableCheckpointStore(tmp_path).commit(
        scope=_scope(),
        state=state,
        expected_revision=0,
    )

    restored = restore_research_context(checkpoint)

    assert restored.evidence_store.get(evidence.artifact_id) == evidence
    assert restored.ledger.items[0].status == ObligationStatus.IN_PROGRESS
    assert restored.ledger.items[0].evidence_refs == ()


def test_open_root_and_directive_state_survive_restart_without_terminal_laundering(tmp_path):
    records, contract, ledger, snapshot = _accepted_resume_authority()
    hypothesis = HypothesisLedgerState(
        parent_obligation_id="U1",
        accepted_contract_id=contract.contract_id,
        lineage_id=contract.lineage_id,
        run_id=snapshot.run_id,
        entries=(),
    )
    directive = ResearchDirectiveDisposition(
        directive_id="dir-day14",
        directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
        parent_obligation_id="U1",
        status=ResearchDirectiveDispositionStatus.OPEN,
    )
    state = CanonicalResumeState(
        manager_snapshot=snapshot,
        accepted_contract=contract,
        ledger=ledger,
        hypothesis_states=(hypothesis,),
        directive_dispositions=(directive,),
        semantic_bindings=records,
        completion_status=None,
    )
    store = DurableCheckpointStore(tmp_path)
    checkpoint = store.commit(
        scope=_scope(),
        state=state,
        expected_revision=0,
    )
    loaded = store.load(_scope())

    assert loaded is not None
    assert loaded.state.hypothesis_states == (hypothesis,)
    assert loaded.state.directive_dispositions == (directive,)
    assert loaded.state.completion_status is None


def test_report_v1_is_preserved_when_stale_v2_writer_loses_cas(tmp_path):
    store = DurableCheckpointStore(tmp_path)
    scope = _scope()
    base = store.commit(
        scope=scope,
        state=_state(report_version=1),
        expected_revision=0,
    )
    winner = store.commit(
        scope=scope,
        state=_state(report_version=2),
        expected_revision=base.revision,
    )

    with pytest.raises(StaleCheckpointWrite):
        store.commit(
            scope=scope,
            state=_state(report_version=1),
            expected_revision=base.revision,
        )

    loaded = store.load(scope)
    assert loaded == winner
    assert loaded.state.reports[0].version == 2
    assert _report(1).report.title == "Report v1"
