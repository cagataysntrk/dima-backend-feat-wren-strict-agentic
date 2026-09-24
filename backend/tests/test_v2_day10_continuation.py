"""Provider-free D10-D signed section continuation boundary attacks."""

from __future__ import annotations

import base64
import json

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_models import (
    AcceptanceStatus,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    SemanticBindingRef,
    UserIntentEnvelope,
)
from app.v2.manager_preacceptance import (
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
    ReportSection,
    ReportSourceProvenance,
)
from app.v2.report_continuation import (
    ReportContextRegistry,
    ReportSectionContinuationSigner,
    StaleReportContinuationError,
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
