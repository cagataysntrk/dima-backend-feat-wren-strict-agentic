"""High-information D10-G provider-free hardening attacks."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.epistemics import (
    CurrentRunEvidenceView,
    CurrentRunObligationView,
    EvidenceLinkedFindingBuilder,
    HypothesisLedger,
    RootCauseObligationVerifier,
)
from app.v2.manager_executor import EvidenceStore
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
    UserIntentEnvelope,
    UserObligationLedger,
    CandidateObligation,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.models import (
    BoundedSemanticContextV0,
    ContextVersionV0,
    EpistemicLabel,
    EvidenceArtifact,
    HypothesisEvidenceRelation,
    HypothesisStatus,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import ProductAskRequest, ProductRequestContext
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.research_scheduler import (
    ResearchTaskInvocationCompileError,
    ResearchTaskInvocationCompiler,
)
from app.v2.capability_bindings import CapabilityBindingValidator
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import (
    AcceptedAuthorityConflict,
    AcceptedAuthorityRegistry,
    StandardAuthoritySealer,
)
from app.v2.standard_builder import StandardWorkMode
from app.v2.standard_lane import StandardLaneEngine
from app.v2.manager_models import StandardProjection
from app.v2.model_policy import ModelProfile, ModelRole


def _profile(role: ModelRole) -> ModelProfile:
    return ModelProfile(role=role, provider="rule", model="rule")


def _dummy_cognition() -> ResearchCognition:
    class LLM:
        def structured_json(self, *args, **kwargs):
            raise RuntimeError("not used")

    return ResearchCognition(
        manager_llm=LLM(),
        manager_profile=_profile(ModelRole.RESEARCH_MANAGER),
        semantic_provider=None,
        semantic_profile=_profile(ModelRole.SEMANTIC_LINKER),
        temporal_provider=None,
        temporal_profile=_profile(ModelRole.TEMPORAL_NORMALIZER),
    )


def _standard_lane() -> StandardLaneEngine:
    def structured(*args, **kwargs):
        raise RuntimeError("not used")

    return StandardLaneEngine(
        intent_structured=structured,
        coverage_structured=structured,
        semantic_provider=None,
        temporal_provider=None,
    )


def test_product_coordinator_physically_shares_cross_lane_authority_registry():
    standard = _standard_lane()
    research = ResearchLaneService(cognition=_dummy_cognition())
    coordinator = ProductCoordinator(
        standard_lane=standard,
        research_lane=research,
    )

    assert standard.authority_registry is research.authority_registry
    assert standard.authority_registry is coordinator._authority_registry


def test_identical_fresh_payloads_have_distinct_turn_authority_and_initial_lineage():
    body = ProductAskRequest(
        question="aynı soru",
        session_id="same-session",
        thread_id="same-thread",
    )
    common = dict(
        request_ref="r-correlation-same",
        tenant_binding="id:tenant-a",
        principal=object(),
        tenant_runtime=TenantAnalyticsRuntimeV0(
            tenant_id="tenant-a",
            tenant_slug="tenant-a",
            principal_user_id="u",
            roles=("owner",),
            mdl_version="mdl",
            catalog="catalog",
            schema_name="main",
            db_online=True,
        ),
        service=object(),
        schema={"cubes": []},
        semantic_context=BoundedSemanticContextV0(
            context_version=ContextVersionV0(
                version="ctx",
                mdl_version="mdl",
                compact_catalog_builder_version="test",
                business_rules_hash="0" * 64,
                prompt_context_policy_version="test",
            )
        ),
        contract_store=None,
        session_id=body.session_id,
        thread_id=body.thread_id,
    )
    first = ProductRequestContext(**common)
    second = ProductRequestContext(**common)

    assert first.request_ref == second.request_ref
    assert first.turn_ref != second.turn_ref

    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    metric = handles.mint_from_resolver(
        tenant_binding="id:tenant-a",
        context_version="ctx",
        resolver_provenance_id="metric-turn-identity",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-turn-identity",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    message = "net gelir"
    hash1 = spans.register_message(message_id=first.turn_ref, text=message)
    hash2 = spans.register_message(message_id=second.turn_ref, text=message)
    span1 = spans.mint_exact(message_id=first.turn_ref, surface=message)
    span2 = spans.mint_exact(message_id=second.turn_ref, surface=message)

    def accepted(turn_ref, source_hash, source_ref):
        return gate.evaluate(
            envelope=UserIntentEnvelope(
                attempt_id="a1",
                turn_id=turn_ref,
                request_ref="r-correlation-same",
                source_message_hash=source_hash,
                model_role="RESEARCH_MANAGER",
                obligations=(
                    CandidateObligation(
                        obligation_id="U1",
                        capability_key=ManagerCapabilityKey.PERFORMANCE,
                        origin=ObligationOrigin.USER_MUST,
                        source_refs=(source_ref,),
                        semantic_handle_refs=(metric.handle_id,),
                    ),
                ),
            ),
            tenant_binding="id:tenant-a",
            context_version="ctx",
        )

    a = accepted(first.turn_ref, hash1, span1.source_ref)
    b = accepted(second.turn_ref, hash2, span2.source_ref)
    assert a.contract is not None and b.contract is not None
    assert a.contract.turn_id != b.contract.turn_id
    assert a.contract.lineage_id != b.contract.lineage_id


def test_same_payload_across_tenants_cannot_share_turn_or_run_identity():
    base = dict(
        request_ref="r-same-correlation",
        principal=object(),
        service=object(),
        schema={"cubes": []},
        semantic_context=BoundedSemanticContextV0(
            context_version=ContextVersionV0(
                version="ctx",
                mdl_version="mdl",
                compact_catalog_builder_version="test",
                business_rules_hash="0" * 64,
                prompt_context_policy_version="test",
            )
        ),
        contract_store=None,
        session_id="s",
        thread_id="t",
    )
    a = ProductRequestContext(
        **base,
        tenant_binding="id:A",
        tenant_runtime=TenantAnalyticsRuntimeV0(
            tenant_id="A", tenant_slug="a", principal_user_id="u",
            roles=("owner",), mdl_version="mdl", catalog="c", schema_name="main",
            db_online=True,
        ),
    )
    b = ProductRequestContext(
        **base,
        tenant_binding="id:B",
        tenant_runtime=TenantAnalyticsRuntimeV0(
            tenant_id="B", tenant_slug="b", principal_user_id="u",
            roles=("owner",), mdl_version="mdl", catalog="c", schema_name="main",
            db_online=True,
        ),
    )
    assert a.turn_ref != b.turn_ref
    ra = ManagerRuntime(request_ref=a.request_ref, turn_ref=a.turn_ref)
    rb = ManagerRuntime(request_ref=b.request_ref, turn_ref=b.turn_ref)
    assert ra.snapshot.run_id != rb.snapshot.run_id


def test_shared_registry_rejects_cross_family_second_authority_same_turn():
    shared = AcceptedAuthorityRegistry()
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx",
        resolver_provenance_id="metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    standard = StandardAuthoritySealer(semantic_handles=handles).seal(
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=(metric.handle_id,),
        ),
        turn_id="turn_shared",
        request_ref="r",
        source_message_hash="a" * 64,
        context_version="ctx",
        tenant_binding="tenant-a",
        accepted_attempt_id="a1",
        model_role="FAST_LANGUAGE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )
    shared.commit(standard)
    research = AcceptedTurnContract(
        contract_id="atc_" + "b" * 24,
        lineage_id="atl_" + "c" * 20,
        version=1,
        turn_id="turn_shared",
        request_ref="r",
        source_message_hash="a" * 64,
        accepted_attempt_id="a2",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U1",),
        context_version="ctx",
        accepted_at_iso="2026-09-24T00:00:00+00:00",
    )
    with pytest.raises(AcceptedAuthorityConflict):
        shared.commit(research)


def _root_fixture():
    tenant = "tenant-root"
    ctx = "ctx-root"
    root_id = "U_ROOT"
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=ctx,
        resolver_provenance_id="root-metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="root-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Production.output",
            cube_names=("Production",),
        ),
    )
    ledger = UserObligationLedger(
        lineage_id="atl-root",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id=root_id,
                capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.IN_PROGRESS,
                source_refs=("src_" + "1" * 24,),
                semantic_handle_refs=(metric.handle_id,),
                introduced_in_version=1,
            ),
        ),
    )
    runtime = ManagerRuntime(request_ref="root", turn_ref="turn_root")
    runtime._ledger = ledger
    runtime._accepted_contract = AcceptedTurnContract(
        contract_id="atc-root",
        lineage_id="atl-root",
        version=1,
        turn_id="turn_root",
        request_ref="root",
        source_message_hash="a" * 64,
        accepted_attempt_id="a1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=(root_id,),
        context_version=ctx,
        accepted_at_iso="2026-09-24T00:00:00+00:00",
    )
    runtime._snapshot = ManagerRunSnapshot(
        run_id=runtime.snapshot.run_id,
        state=ManagerState.INVESTIGATING,
        accepted_contract_id="atc-root",
        lineage_id="atl-root",
        evidence_refs=("E1", "E2"),
        inspected_evidence_refs=("E1", "E2"),
    )
    store = EvidenceStore()
    tasks = ResearchTaskRegistry()
    from app.v2.models import ResearchTask
    tasks.register(
        ResearchTask(
            task_id="seed:U_ROOT",
            question_id=root_id,
            task_kind="query",
            input_refs=(metric.handle_id,),
            origin="USER_SEED",
            state="complete",
        )
    )
    for ref in ("E1", "E2"):
        store.put(
            EvidenceArtifact(
                artifact_id=ref,
                task_id="seed:U_ROOT",
                obligation_ids=(root_id,),
                query_contract_refs=(f"QC_{ref}",),
                evidence_kind="standard_analytics",
                verified=True,
                payload={"executions": ()},
            )
        )
    hypothesis = HypothesisLedger(
        parent_obligation_id=root_id,
        accepted_contract_id="atc-root",
        lineage_id="atl-root",
        run_id=runtime.snapshot.run_id,
        obligation_ledger=ledger,
        obligation_view=CurrentRunObligationView(runtime),
        evidence_store=store,
        evidence_view=CurrentRunEvidenceView(runtime),
        semantic_handles=handles,
        research_tasks=tasks,
        tenant_binding=tenant,
        context_version=ctx,
    )
    entry = hypothesis.register(
        statement="Gece vardiyası üretimi %27 düşürdü.",
        semantic_handle_refs=(metric.handle_id,),
        trigger_evidence_refs=("E1",),
        limitations=(),
    )
    return runtime, hypothesis, tasks, store, metric, entry


def test_hypothesis_status_reconciles_from_admitted_relations_only():
    _, ledger, _, _, _, entry = _root_fixture()
    supported = ledger.attach_evidence(
        entry.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    assert supported.status == HypothesisStatus.SUPPORTED
    mixed = ledger.attach_evidence(
        entry.hypothesis_id,
        evidence_ref="E2",
        relation=HypothesisEvidenceRelation.CONTRADICTS,
    )
    assert mixed.status == HypothesisStatus.INCONCLUSIVE
    assert any("Karışık" in item for item in mixed.limitations)

    runtime, ledger2, _, _, _, entry2 = _root_fixture()
    del runtime
    refuted = ledger2.attach_evidence(
        entry2.hypothesis_id,
        evidence_ref="E2",
        relation=HypothesisEvidenceRelation.CONTRADICTS,
    )
    assert refuted.status == HypothesisStatus.REFUTED


def test_root_completion_requires_accounted_hypothesis_and_no_pending_next_test():
    runtime, ledger, tasks, _, _, entry = _root_fixture()
    assert RootCauseObligationVerifier().reconcile(
        runtime=runtime,
        hypothesis_ledger=ledger,
        task_registry=tasks,
    ) is False

    ledger.attach_evidence(
        entry.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    assert RootCauseObligationVerifier().reconcile(
        runtime=runtime,
        hypothesis_ledger=ledger,
        task_registry=tasks,
    ) is True
    root = runtime.ledger.active_user_must[0]
    assert root.status == ObligationStatus.VERIFIED
    assert "nedensel doğruluk" in root.verdict
    assert EpistemicLabel.CONFIRMED_CAUSE.value not in root.verdict


def test_model_invented_numeric_hypothesis_never_becomes_canonical_finding_statement():
    _, ledger, _, _, _, entry = _root_fixture()
    supported = ledger.attach_evidence(
        entry.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    assert "%27" in supported.statement  # retained for cognition/audit

    finding = EvidenceLinkedFindingBuilder(ledger=ledger).build(
        statement=supported.statement,
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence_refs=("E1",),
        hypothesis_ref=supported.hypothesis_id,
    )
    assert "%27" not in finding.statement
    assert "Production.output" in finding.statement
    assert finding.semantic_handle_refs == supported.semantic_handle_refs
    assert finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert any("nedenselliği doğrulamaz" in x for x in finding.limitations)


def test_lossless_user_seed_compiles_without_language_or_semantic_guessing():
    tenant = "tenant-scheduler"
    ctx = "ctx-scheduler"
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=ctx,
        resolver_provenance_id="m",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="m",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    obligation = ObligationLedgerItem(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=(metric.handle_id,),
        introduced_in_version=1,
    )
    binding_result = CapabilityBindingValidator(
        semantic_handles=handles,
    ).validate(
        obligation,
        tenant_binding=tenant,
        context_version=ctx,
    )
    assert binding_result.valid and binding_result.binding is not None

    from app.v2.models import ResearchTask
    task = ResearchTask(
        task_id="seed:U1",
        question_id="U1",
        task_kind="QUERY",
        input_refs=(metric.handle_id,),
        origin="USER_SEED",
    )
    compiled = ResearchTaskInvocationCompiler().compile(
        task=task,
        obligation=obligation,
        binding=binding_result.binding,
    )
    assert compiled.tool_id == "wren.query"
    assert compiled.call.name.value == "run_analytics"
    assert compiled.call.args["metric_handles"] == [metric.handle_id]
    assert compiled.call.args["obligation_ids"] == ["U1"]


def test_nonlossless_task_binding_mismatch_never_auto_compiles():
    tenant = "tenant-scheduler"
    ctx = "ctx-scheduler"
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=ctx,
        resolver_provenance_id="m2",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="m2",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    extra = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=ctx,
        resolver_provenance_id="m3",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="m3",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.margin",
            cube_names=("Sales",),
        ),
    )
    obligation = ObligationLedgerItem(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=(metric.handle_id,),
        introduced_in_version=1,
    )
    binding = CapabilityBindingValidator(
        semantic_handles=handles,
    ).validate(
        obligation,
        tenant_binding=tenant,
        context_version=ctx,
    ).binding
    assert binding is not None

    from app.v2.models import ResearchTask
    task = ResearchTask(
        task_id="seed:U1",
        question_id="U1",
        task_kind="QUERY",
        input_refs=(metric.handle_id, extra.handle_id),
        origin="USER_SEED",
    )
    with pytest.raises(
        ResearchTaskInvocationCompileError,
        match="exactly account",
    ):
        ResearchTaskInvocationCompiler().compile(
            task=task,
            obligation=obligation,
            binding=binding,
        )


class _InspectionExecutor:
    def __init__(self, store):
        self.evidence_store = store

    def execute(self, call, validated_args, runtime):
        if call.name.value == "inspect_evidence":
            runtime.mark_evidence_inspected(validated_args.evidence_ref)
            return self.evidence_store.get(validated_args.evidence_ref)
        if call.name.value == "request_clarification":
            return validated_args
        raise AssertionError(f"unexpected tool: {call.name.value}")


def _inspection_runtime(*, evidence_refs, latest_ref):
    runtime = ManagerRuntime(
        request_ref="inspection-correlation",
        turn_ref="turn_inspection",
    )
    ledger = UserObligationLedger(
        lineage_id="atl-inspection",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.IN_PROGRESS,
                source_refs=("src_" + "1" * 24,),
                introduced_in_version=1,
            ),
        ),
    )
    runtime._ledger = ledger
    runtime._accepted_contract = AcceptedTurnContract(
        contract_id="atc-inspection",
        lineage_id="atl-inspection",
        version=1,
        turn_id="turn_inspection",
        request_ref="inspection-correlation",
        source_message_hash="a" * 64,
        accepted_attempt_id="a1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U1",),
        context_version="ctx-inspection",
        accepted_at_iso="2026-09-24T00:00:00+00:00",
    )
    runtime._snapshot = ManagerRunSnapshot(
        run_id=runtime.snapshot.run_id,
        state=ManagerState.INVESTIGATING,
        accepted_contract_id="atc-inspection",
        lineage_id="atl-inspection",
        evidence_refs=tuple(evidence_refs),
        inspected_evidence_refs=(),
        latest_evidence_ref=latest_ref,
    )
    store = EvidenceStore()
    for ref in evidence_refs:
        store.put(
            EvidenceArtifact(
                artifact_id=ref,
                task_id=f"task:{ref}",
                obligation_ids=("U1",),
                query_contract_refs=(f"QC:{ref}",),
                evidence_kind="standard_analytics",
                verified=True,
                payload={
                    "query_count": 1,
                    "executions": (
                        {
                            "execution_id": f"exec:{ref}",
                            "role": "primary",
                            "columns": ("metric",),
                            "row_count": 1,
                            "rows": ({"metric": 1.0},),
                        },
                    ),
                },
            )
        )
    return runtime, store


def test_fresh_evidence_provider_failure_does_not_record_inspection():
    runtime, store = _inspection_runtime(
        evidence_refs=("E_FRESH",),
        latest_ref="E_FRESH",
    )

    class FailingLLM:
        def structured_json(self, *args, **kwargs):
            raise RuntimeError("provider failed before cognition receipt")

    outcome = ResearchManagerLoop(
        llm=FailingLLM(),
        source_spans=SourceSpanRegistry(),
    ).run(
        question="incele",
        message_id="turn_inspection",
        request_ref="inspection-correlation",
        runtime=runtime,
        executor=_InspectionExecutor(store),
    )

    assert runtime.snapshot.inspected_evidence_refs == ()
    assert any(item.get("kind") == "model_error" for item in outcome.observations)


def test_old_opaque_evidence_requires_explicit_inspection_while_fresh_delta_auto_discloses():
    runtime, store = _inspection_runtime(
        evidence_refs=("E_OLD", "E_FRESH"),
        latest_ref="E_FRESH",
    )

    class InspectOldLLM:
        def __init__(self):
            self.calls = 0

        def structured_json(self, system, user, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return {
                    "action": "inspect_evidence",
                    "evidence_ref": "E_OLD",
                }
            return {
                "action": "request_clarification",
                "obligation_ids": ["U1"],
                "clarification_reason": "test stop",
            }

    llm = InspectOldLLM()
    outcome = ResearchManagerLoop(
        llm=llm,
        source_spans=SourceSpanRegistry(),
    ).run(
        question="incele",
        message_id="turn_inspection",
        request_ref="inspection-correlation",
        runtime=runtime,
        executor=_InspectionExecutor(store),
    )

    assert set(runtime.snapshot.inspected_evidence_refs) == {"E_FRESH", "E_OLD"}
    assert any(
        item.get("kind") == "fresh_evidence_disclosed"
        and item.get("evidence_ref") == "E_FRESH"
        for item in outcome.observations
    )
    assert any(
        item.get("kind") == "tool"
        and item.get("tool") == "inspect_evidence"
        for item in outcome.observations
    )


def test_pending_root_next_test_blocks_investigation_completion():
    runtime, ledger, tasks, _, _, entry = _root_fixture()
    ledger.attach_evidence(
        entry.hypothesis_id,
        evidence_ref="E1",
        relation=HypothesisEvidenceRelation.SUPPORTS,
    )
    from app.v2.models import ResearchTask
    pending = ResearchTask(
        task_id="rt_pending_root",
        question_id="U_ROOT",
        task_kind="QUERY",
        input_refs=entry.semantic_handle_refs,
        origin="AGENT_DERIVED",
        parent_task_id="seed:U_ROOT",
        parent_obligation_id="U_ROOT",
        trigger_evidence_ref="E1",
        branch_depth=1,
    )
    tasks.register(pending)
    ledger.link_next_test(
        entry.hypothesis_id,
        task_ref=pending.task_id,
    )

    assert RootCauseObligationVerifier().reconcile(
        runtime=runtime,
        hypothesis_ledger=ledger,
        task_registry=tasks,
    ) is False
    root = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_ROOT"
    )
    assert root.status == ObligationStatus.IN_PROGRESS



def test_deterministic_scheduler_cancel_blocks_late_evidence_commit():
    """G14.20: deterministic scheduling keeps the Day7 cancel commit_guard."""

    from app.v2.models import ResearchTask
    from app.v2.research_scheduler import DeterministicResearchScheduler
    from app.v2.research_tools import ResearchToolRunner
    from control_plane.authorize import Principal

    tenant = "tenant-cancel-scheduler"
    ctx = "ctx-cancel-scheduler"
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=ctx,
        resolver_provenance_id="cancel-metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="cancel-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    obligation = ObligationLedgerItem(
        obligation_id="U_CANCEL",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.IN_PROGRESS,
        source_refs=("src_" + "c" * 24,),
        semantic_handle_refs=(metric.handle_id,),
        introduced_in_version=1,
    )
    binding = CapabilityBindingValidator(
        semantic_handles=handles,
    ).validate(
        obligation,
        tenant_binding=tenant,
        context_version=ctx,
    ).binding
    assert binding is not None

    contract = AcceptedTurnContract(
        contract_id="atc-cancel",
        lineage_id="atl-cancel",
        version=1,
        turn_id="turn_cancel",
        request_ref="r-cancel",
        source_message_hash="c" * 64,
        accepted_attempt_id="a1",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U_CANCEL",),
        context_version=ctx,
        accepted_at_iso="2026-09-24T00:00:00+00:00",
    )
    runtime = ManagerRuntime(
        request_ref="r-cancel",
        turn_ref="turn_cancel",
    )
    runtime._accepted_contract = contract
    runtime._ledger = UserObligationLedger(
        lineage_id=contract.lineage_id,
        version=1,
        items=(obligation,),
    )
    runtime.authority_registry.commit(contract)
    runtime._snapshot = ManagerRunSnapshot(
        run_id=runtime.snapshot.run_id,
        state=ManagerState.INVESTIGATING,
        accepted_contract_id=contract.contract_id,
        lineage_id=contract.lineage_id,
    )

    principal = Principal(
        user_id="cancel-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="cancel",
    )
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="cancel",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version="mdl-cancel",
        catalog="cancel",
        schema_name="main",
        db_online=True,
    )

    class CancelBeforeCommitExecutor:
        def __init__(self):
            self.principal = principal
            self.tenant_binding = tenant
            self.tenant_runtime = tenant_runtime
            self.evidence_store = EvidenceStore()
            self.commit_attempts = 0

        def execute(self, call, validated_args, bound_runtime, commit_guard=None):
            self.commit_attempts += 1
            assert commit_guard is not None
            commit_guard()
            raise AssertionError("cancelled execution must not cross commit guard")

    executor = CancelBeforeCommitExecutor()
    task = ResearchTask(
        task_id="seed:U_CANCEL",
        question_id="U_CANCEL",
        task_kind="QUERY",
        input_refs=(metric.handle_id,),
        origin="USER_SEED",
    )
    tasks = ResearchTaskRegistry()
    tasks.register(task)

    with pytest.raises(Exception):
        DeterministicResearchScheduler(
            runner=ResearchToolRunner(),
        ).execute(
            task=task,
            obligation=obligation,
            binding=binding,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=tasks,
            cancel_check=lambda: True,
        )

    assert executor.commit_attempts == 1
    assert tasks.get(task.task_id).state == "cancelled"
    assert runtime.snapshot.evidence_refs == ()
    # The governed query attempt is still metered; cancellation blocks Evidence commit,
    # not accounting of work already attempted before the commit boundary.
    assert runtime.snapshot.data_queries == 1
