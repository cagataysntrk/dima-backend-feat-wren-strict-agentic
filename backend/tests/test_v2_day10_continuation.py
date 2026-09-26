"""Provider-free D10-D signed section continuation boundary attacks."""

from __future__ import annotations

import base64
import json
from types import SimpleNamespace

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_models import (
    AcceptanceStatus,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveType,
    SemanticBindingRef,
    UserIntentEnvelope,
)
from app.v2.manager_preacceptance import (
    ContinuationDirectiveParentResolutionError,
    DraftResearchDirective,
    DraftSemanticSurface,
    IntentDraft,
    IntentDraftObligation,
    PreAcceptanceController,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.report_builder import (
    ReportBlock,
    ReportBlockKind,
    ReportClaimKind,
    ReportDocument,
    ReportEvidenceRef,
    ReportFindingRef,
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.report_continuation import (
    ReportContextEntry,
    ReportContextRegistry,
    ReportSectionContinuationSigner,
    StaleReportContinuationError,
    continuation_analytical_authority,
    continuation_conversation,
    continuation_scope_by_kind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


RPT = "rpt_" + "1" * 24
SEC = "rsec_" + "2" * 24
BLK = "rblk_" + "3" * 24
CTX_REF = "rctx_" + "4" * 24


def _report() -> ReportDocument:
    block = ReportBlock(
        block_id=BLK,
        block_kind=ReportBlockKind.TEXT,
        claim_kind=ReportClaimKind.NARRATIVE,
        content="Canonical presentation text.",
    )
    section = ReportSection(
        section_id=SEC,
        title="Section title is presentation only",
        blocks=(block,),
        semantic_scope=("sem_" + "a" * 24,),
        followup_context_ref=CTX_REF,
    )
    return ReportDocument(
        report_id=RPT,
        title="Report",
        sections=(section,),
        provenance=ReportSourceProvenance(
            accepted_contract_id="atc-1",
            lineage_id="atl-1",
            run_id="mgr-1",
            tenant_binding="tenant-a",
            context_version="ctx-a",
        ),
    )


def _signer():
    return ReportSectionContinuationSigner(signing_key=b"day10-test-key")


def _token():
    return _signer().mint(
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        report_id=RPT,
        section_id=SEC,
        followup_context_ref=CTX_REF,
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
    )


def test_section_token_contains_only_opaque_control_identity():
    token = _token()
    encoded = token.split(".", 1)[0]
    encoded += "=" * (-len(encoded) % 4)
    payload = json.loads(base64.urlsafe_b64decode(encoded))

    assert set(payload) == {
        "version",
        "tenant_binding",
        "context_version",
        "flow_binding",
        "report_id",
        "section_id",
        "followup_context_ref",
        "source_run_ref",
        "lineage_ref",
    }
    raw = json.dumps(payload)
    assert "sem_" not in raw
    assert "Evidence" not in raw
    assert "canonical" not in raw
    assert "formula" not in raw
    assert "Section title" not in raw


def test_tampered_and_foreign_context_tokens_fail_closed():
    signer = _signer()
    token = _token()
    body, signature = token.split(".", 1)
    tampered = ("A" if body[0] != "A" else "B") + body[1:] + "." + signature

    with pytest.raises(StaleReportContinuationError, match="signature|format"):
        signer.verify(
            tampered,
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )

    for kwargs, message in (
        ({"tenant_binding": "tenant-b"}, "tenant"),
        ({"context_version": "ctx-b"}, "context"),
        ({"session_id": "session-b"}, "session/thread"),
        ({"thread_id": "thread-b"}, "session/thread"),
    ):
        params = {
            "tenant_binding": "tenant-a",
            "context_version": "ctx-a",
            "session_id": "session-a",
            "thread_id": "thread-a",
        }
        params.update(kwargs)
        with pytest.raises(StaleReportContinuationError, match=message):
            signer.verify(token, **params)


def test_registry_revalidates_current_principal_and_exact_section_identity():
    report = _report()
    registry = ReportContextRegistry(max_entries=4)
    research_result = object()
    registry.register(
        report=report,
        research_result=research_result,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=1,
    )
    payload = _signer().verify(
        _token(),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )

    entry = registry.resolve(
        payload,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )
    assert entry.report is report
    assert entry.research_result is research_result
    assert entry.section.section_id == SEC

    with pytest.raises(StaleReportContinuationError, match="principal"):
        registry.resolve(
            payload,
            principal_subject="user-b",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )

    wrong_section = payload.model_copy(
        update={"section_id": "rsec_" + "f" * 24}
    )
    with pytest.raises(StaleReportContinuationError, match="section"):
        registry.resolve(
            wrong_section,
            principal_subject="user-a",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )


def test_evicted_or_missing_registry_context_requires_rebind():
    report = _report()
    registry = ReportContextRegistry(max_entries=1)
    registry.register(
        report=report,
        research_result=object(),
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=1,
    )
    payload = _signer().verify(
        _token(),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
    )

    # A new report/section evicts the sole bounded entry.
    new_section = report.sections[0].model_copy(
        update={
            "section_id": "rsec_" + "5" * 24,
            "followup_context_ref": "rctx_" + "6" * 24,
        }
    )
    new_report = report.model_copy(
        update={
            "report_id": "rpt_" + "7" * 24,
            "sections": (new_section,),
        }
    )
    registry.register(
        report=new_report,
        research_result=object(),
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=2,
    )

    with pytest.raises(StaleReportContinuationError, match="rebind"):
        registry.resolve(
            payload,
            principal_subject="user-a",
            tenant_binding="tenant-a",
            context_version="ctx-a",
            session_id="session-a",
            thread_id="thread-a",
        )



def test_stream_adapter_uses_same_product_coordinator_and_bound_control_signals():
    import inspect
    import app.routers.ask_v2 as route

    source = inspect.getsource(route.ask_v2_stream)
    assert "_coordinator.handle(" in source
    assert "ProductCoordinator(" not in source
    assert "_controls.register(" in source
    assert "cancel_check=control.cancelled" in source
    assert "answer_now_check=control.answer_now_requested" in source
    assert "ProductEventKind.KEEPALIVE" in source
    assert "control.signal(ProductControlAction.CANCEL)" in source
    assert "_controls.release(control.control_ref)" in source


def _semantic_scope():
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-a",
        resolver_provenance_id="section:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-a",
        resolver_provenance_id="turn:dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    foreign = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-a",
        resolver_provenance_id="foreign:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="foreign-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.margin",
            cube_names=("Sales",),
        ),
    )
    return handles, metric.handle_id, dimension.handle_id, foreign.handle_id


def test_preacceptance_inherits_unique_required_metric_without_forging_source_binding():
    handles, metric, dimension, _ = _semantic_scope()
    spans = SourceSpanRegistry()
    question = "bölge"
    source_hash = spans.register_message(message_id="turn-2", text=question)
    source_ref = spans.mint_exact(message_id="turn-2", surface="bölge").source_ref
    runtime = ManagerRuntime(request_ref="request-2")
    controller = PreAcceptanceController(
        structured=lambda *args, **kwargs: {},
        source_spans=spans,
        context_scope_by_kind={"metric": (metric,)},
    )
    draft = IntentDraft(
        obligations=(
            IntentDraftObligation(
                obligation_id="U2",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin="USER_MUST",
                priority="MUST",
                polarity="REQUIRED",
                source_surfaces=("bölge",),
                semantic_surfaces=(
                    DraftSemanticSurface(surface="bölge", kind_hint="dimension"),
                ),
            ),
        ),
    )
    grounded = {
        ("U2", "bölge", "dimension"): SemanticBindingRef(
            source_ref=source_ref,
            handle_id=dimension,
            target_kind="dimension",
        )
    }

    envelope = controller._envelope(
        draft=draft,
        grounded=grounded,
        message_id="turn-2",
        source_hash=source_hash,
        request_ref="request-2",
        runtime=runtime,
    )
    item = envelope.obligations[0]

    assert item.semantic_handle_refs == (dimension, metric)
    assert item.scope_refs == (metric,)
    assert tuple(binding.handle_id for binding in item.semantic_bindings) == (dimension,)


def test_acceptance_allows_only_signed_context_scope_and_versions_immutably():
    handles, metric, _, foreign = _semantic_scope()
    spans = SourceSpanRegistry()
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
        allowed_context_scope_refs=(metric,),
    )

    hash1 = spans.register_message(message_id="turn-1", text="gelir")
    src1 = spans.mint_exact(message_id="turn-1", surface="gelir").source_ref
    first = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a1",
            turn_id="turn-1",
            request_ref="req-lineage",
            source_message_hash=hash1,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U1",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(src1,),
                    semantic_handle_refs=(metric,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
    )
    assert first.status == AcceptanceStatus.ACCEPTED
    assert first.contract.version == 1

    hash2 = spans.register_message(message_id="turn-2", text="detaylandır")
    src2 = spans.mint_exact(message_id="turn-2", surface="detaylandır").source_ref
    second = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a2",
            turn_id="turn-2",
            request_ref="req-lineage-2",
            source_message_hash=hash2,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U2",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(src2,),
                    semantic_handle_refs=(metric,),
                    scope_refs=(metric,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )
    assert second.status == AcceptanceStatus.ACCEPTED
    assert second.contract.version == 2
    assert second.contract.turn_id != first.contract.turn_id
    assert second.contract.lineage_id == first.contract.lineage_id
    assert second.contract.supersedes_contract_id == first.contract.contract_id
    assert first.contract.version == 1
    assert second.ledger.version == 2
    assert next(item for item in second.ledger.items if item.obligation_id == "U2").scope_refs == (metric,)

    rejected = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a3",
            turn_id="turn-3",
            request_ref="req-lineage-3",
            source_message_hash=hash2,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U3",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(src2,),
                    semantic_handle_refs=(foreign,),
                    scope_refs=(foreign,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )
    assert rejected.status == AcceptanceStatus.REJECTED
    assert any("not admitted" in reason for reason in rejected.reasons)


def test_signed_section_projects_only_its_governed_scope_into_conversation():
    handles, metric, dimension, _ = _semantic_scope()
    report = _report()
    section = report.sections[0].model_copy(
        update={"semantic_scope": (metric, dimension)}
    )
    report = report.model_copy(update={"sections": (section,)})
    research_result = type("Result", (), {"semantic_handles": handles})()
    registry = ReportContextRegistry()
    entry = registry.register(
        report=report,
        research_result=research_result,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        session_id="session-a",
        thread_id="thread-a",
        source_run_ref="mgr-1",
        lineage_ref="atl-1",
        report_version=1,
    )[0]

    scope = continuation_scope_by_kind(entry)
    conversation = continuation_conversation(entry)

    assert scope == {"metric": (metric,), "dimension": (dimension,)}
    assert tuple(item.canonical_name for item in conversation.focus.metrics) == (
        "Sales.revenue",
    )
    assert tuple(item.canonical_name for item in conversation.focus.dimensions) == (
        "Sales.region",
    )
    assert conversation.topic.cube == "Sales"
    assert set(conversation.focus_labels) == {"Sales.revenue", "Sales.region"}


def _authority_entry(
    *,
    parent_refs: tuple[str, ...] = ("U_ROOT",),
    include_foreign: bool = True,
) -> ReportContextEntry:
    semantic_by_parent = {
        parent_ref: f"sem_{index:024x}"
        for index, parent_ref in enumerate(parent_refs, start=1)
    }
    foreign_semantic = "sem_" + "f" * 24

    blocks = tuple(
        ReportBlock(
            block_id=f"rblk_{index:024x}",
            block_kind=ReportBlockKind.ROOT_CAUSE,
            claim_kind=ReportClaimKind.EPISTEMIC,
            content=f"finding {parent_ref}",
            finding_refs=(ReportFindingRef(finding_ref=f"find-{parent_ref}"),),
        )
        for index, parent_ref in enumerate(parent_refs, start=10)
    )
    evidence_refs = tuple(
        ReportEvidenceRef(
            evidence_ref=f"evi-{parent_ref}",
            query_contract_refs=(f"qc-{parent_ref}",),
        )
        for parent_ref in parent_refs
    )
    section = ReportSection(
        section_id=SEC,
        title="Typed presentation title",
        blocks=blocks or (
            ReportBlock(
                block_id=BLK,
                block_kind=ReportBlockKind.TEXT,
                claim_kind=ReportClaimKind.NARRATIVE,
                content="presentation only",
            ),
        ),
        evidence_refs=evidence_refs,
        semantic_scope=tuple(semantic_by_parent.values()),
        followup_context_ref=CTX_REF,
    )
    report = ReportDocument(
        report_id=RPT,
        title="Report",
        sections=(section,),
        provenance=ReportSourceProvenance(
            accepted_contract_id="atc-prior",
            lineage_id="atl-prior",
            run_id="mgr-prior",
            tenant_binding="tenant-a",
            context_version="ctx-a",
        ),
    )

    ledger_items = [
        SimpleNamespace(
            obligation_id=parent_ref,
            capability_key=ManagerCapabilityKey.ROOT_CAUSE,
            origin=ObligationOrigin.USER_MUST,
            priority=ObligationPriority.MUST,
            polarity=ObligationPolarity.REQUIRED,
            status=ObligationStatus.VERIFIED,
            semantic_handle_refs=(semantic_by_parent[parent_ref],),
            evidence_refs=(f"evi-{parent_ref}",),
        )
        for parent_ref in parent_refs
    ]
    if include_foreign:
        ledger_items.append(
            SimpleNamespace(
                obligation_id="U_FOREIGN",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                semantic_handle_refs=(foreign_semantic,),
                evidence_refs=("evi-foreign",),
            )
        )

    prior = SimpleNamespace(
        accepted_contract=SimpleNamespace(
            contract_id="atc-prior",
            lineage_id="atl-prior",
            version=1,
        ),
        ledger=SimpleNamespace(
            lineage_id="atl-prior",
            version=1,
            items=tuple(ledger_items),
        ),
        evidence=tuple(
            SimpleNamespace(
                artifact_id=f"evi-{parent_ref}",
                obligation_ids=(parent_ref,),
            )
            for parent_ref in parent_refs
        ),
        findings=tuple(
            SimpleNamespace(
                finding_id=f"find-{parent_ref}",
                parent_obligation_id=parent_ref,
            )
            for parent_ref in parent_refs
        ),
    )
    return ReportContextEntry(
        report=report,
        section=section,
        research_result=prior,
        principal_subject="user-a",
        tenant_binding="tenant-a",
        context_version="ctx-a",
        flow_binding="flow-a",
        source_run_ref="mgr-prior",
        lineage_ref="atl-prior",
        report_version=1,
    )


def test_signed_section_authority_projection_uses_typed_provenance_not_random_active_ledger():
    entry = _authority_entry()
    authority = continuation_analytical_authority(entry)

    assert authority.admitted_parent_refs == ("U_ROOT",)
    assert "U_FOREIGN" not in authority.admitted_parent_refs
    assert authority.lineage_id == "atl-prior"
    assert authority.contract_id == "atc-prior"
    assert authority.ledger_version == 1


def test_signed_section_authority_projection_preserves_multiple_parent_ambiguity():
    entry = _authority_entry(parent_refs=("U_ROOT_A", "U_ROOT_B"))
    authority = continuation_analytical_authority(entry)

    assert set(authority.admitted_parent_refs) == {"U_ROOT_A", "U_ROOT_B"}


def test_signed_section_parent_hydration_never_asks_model_for_prior_opaque_id():
    spans = SourceSpanRegistry()
    question = "raporu derinleştir ve gerekirse governed araştırma yap"
    source_hash = spans.register_message(message_id="turn-2", text=question)
    controller = PreAcceptanceController(
        structured=lambda *args, **kwargs: {},
        source_spans=spans,
        signed_section_continuation=True,
        allowed_continuation_parent_refs=("U_ROOT",),
    )
    draft = IntentDraft(
        obligations=(
            IntentDraftObligation(
                obligation_id="U_REPORT",
                capability_key=ManagerCapabilityKey.REPORT,
                origin="USER_MUST",
                priority="MUST",
                polarity="REQUIRED",
                source_surfaces=("raporu derinleştir",),
            ),
        ),
        research_directives=(
            DraftResearchDirective(
                directive_id="D_BROADEN",
                directive_type="BROADEN_WITHIN_BUDGET",
                condition="WITHIN_SYSTEM_BUDGET",
                parent_scope="SIGNED_SECTION_ANALYTICAL_AUTHORITY",
                parent_obligation_id=None,
                source_surfaces=("gerekirse governed araştırma yap",),
            ),
        ),
    )

    envelope = controller._envelope(
        draft=draft,
        grounded={},
        message_id="turn-2",
        source_hash=source_hash,
        request_ref="request-2",
        runtime=ManagerRuntime(request_ref="request-2"),
    )

    assert envelope.research_directives[0].directive_type == (
        ResearchDirectiveType.BROADEN_WITHIN_BUDGET
    )
    assert envelope.research_directives[0].parent_obligation_id == "U_ROOT"
    assert "U_ROOT" not in draft.model_dump_json()


@pytest.mark.parametrize("parents", [(), ("U_A", "U_B")])
def test_signed_section_parent_hydration_fails_closed_when_not_unique(parents):
    spans = SourceSpanRegistry()
    question = "raporu derinleştir ve gerekirse governed araştırma yap"
    source_hash = spans.register_message(message_id="turn-2", text=question)
    controller = PreAcceptanceController(
        structured=lambda *args, **kwargs: {},
        source_spans=spans,
        signed_section_continuation=True,
        allowed_continuation_parent_refs=parents,
    )
    draft = IntentDraft(
        obligations=(
            IntentDraftObligation(
                obligation_id="U_REPORT",
                capability_key=ManagerCapabilityKey.REPORT,
                origin="USER_MUST",
                priority="MUST",
                polarity="REQUIRED",
                source_surfaces=("raporu derinleştir",),
            ),
        ),
        research_directives=(
            DraftResearchDirective(
                directive_id="D1",
                directive_type="BROADEN_WITHIN_BUDGET",
                condition="WITHIN_SYSTEM_BUDGET",
                parent_scope="SIGNED_SECTION_ANALYTICAL_AUTHORITY",
                parent_obligation_id=None,
                source_surfaces=("gerekirse governed araştırma yap",),
            ),
        ),
    )

    with pytest.raises(
        ContinuationDirectiveParentResolutionError,
        match="one unambiguous inherited analytical authority",
    ):
        controller._envelope(
            draft=draft,
            grounded={},
            message_id="turn-2",
            source_hash=source_hash,
            request_ref="request-2",
            runtime=ManagerRuntime(request_ref="request-2"),
        )


def _accepted_analytical_parent():
    handles, metric, _, _ = _semantic_scope()
    spans = SourceSpanRegistry()
    first_hash = spans.register_message(message_id="turn-1", text="gelir")
    first_src = spans.mint_exact(message_id="turn-1", surface="gelir").source_ref
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )
    first = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a1",
            turn_id="turn-1",
            request_ref="req-1",
            source_message_hash=first_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_ROOT",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(first_src,),
                    semantic_handle_refs=(metric,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
    )
    assert first.status == AcceptanceStatus.ACCEPTED
    return handles, spans, first


def _continuation_envelope(
    *,
    spans: SourceSpanRegistry,
    directive_parent: str,
    directive_type: ResearchDirectiveType,
) -> UserIntentEnvelope:
    question = "raporu derinleştir; gerekirse araştır"
    source_hash = spans.register_message(message_id="turn-2", text=question)
    report_src = spans.mint_exact(
        message_id="turn-2",
        surface="raporu derinleştir",
    ).source_ref
    policy_src = spans.mint_exact(
        message_id="turn-2",
        surface="gerekirse araştır",
    ).source_ref
    condition = (
        ResearchDirectiveCondition.WITHIN_SYSTEM_BUDGET
        if directive_type == ResearchDirectiveType.BROADEN_WITHIN_BUDGET
        else ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION
    )
    return UserIntentEnvelope(
        attempt_id="a2",
        turn_id="turn-2",
        request_ref="req-2",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U_REPORT",
                capability_key=ManagerCapabilityKey.REPORT,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(report_src,),
            ),
        ),
        research_directives=(
            ResearchDirective(
                directive_id="D1",
                directive_type=directive_type,
                parent_obligation_id=directive_parent,
                condition=condition,
                source_refs=(policy_src,),
            ),
        ),
    )


@pytest.mark.parametrize(
    "directive_type",
    [
        ResearchDirectiveType.BROADEN_WITHIN_BUDGET,
        ResearchDirectiveType.ADAPT_ON_EVIDENCE,
    ],
)
def test_acceptance_hydrates_only_admitted_signed_section_analytical_parent(
    directive_type,
):
    handles, spans, first = _accepted_analytical_parent()
    prior_contract_dump = first.contract.model_dump(mode="json")
    prior_ledger_dump = first.ledger.model_dump(mode="json")
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
        allowed_continuation_parent_refs=("U_ROOT",),
    )

    second = gate.evaluate(
        envelope=_continuation_envelope(
            spans=spans,
            directive_parent="U_ROOT",
            directive_type=directive_type,
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )

    assert second.status == AcceptanceStatus.ACCEPTED
    assert second.contract.version == 2
    assert second.contract.supersedes_contract_id == first.contract.contract_id
    assert second.contract.lineage_id == first.contract.lineage_id
    assert second.contract.research_directives[0].parent_obligation_id == "U_ROOT"
    assert first.contract.model_dump(mode="json") == prior_contract_dump
    assert first.ledger.model_dump(mode="json") == prior_ledger_dump


def test_report_presentation_obligation_cannot_become_analytical_directive_parent():
    handles, spans, first = _accepted_analytical_parent()
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
        allowed_continuation_parent_refs=("U_ROOT",),
    )

    rejected = gate.evaluate(
        envelope=_continuation_envelope(
            spans=spans,
            directive_parent="U_REPORT",
            directive_type=ResearchDirectiveType.BROADEN_WITHIN_BUDGET,
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )

    assert rejected.status == AcceptanceStatus.REJECTED
    assert any(
        "active analytical authority" in reason
        for reason in rejected.reasons
    )


def test_arbitrary_active_ledger_parent_is_rejected_without_section_admission():
    handles, spans, first = _accepted_analytical_parent()
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
        allowed_continuation_parent_refs=(),
    )

    rejected = gate.evaluate(
        envelope=_continuation_envelope(
            spans=spans,
            directive_parent="U_ROOT",
            directive_type=ResearchDirectiveType.BROADEN_WITHIN_BUDGET,
        ),
        tenant_binding="tenant-a",
        context_version="ctx-a",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )

    assert rejected.status == AcceptanceStatus.REJECTED
    assert any("parent obligation missing" in reason for reason in rejected.reasons)
