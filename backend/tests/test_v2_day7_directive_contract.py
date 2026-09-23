"""Focused Day7 contract proof: research directive is policy, not USER_MUST capability."""

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveType,
    UserIntentEnvelope,
)
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


def _breakdown_case():
    spans = SourceSpanRegistry()
    text = (
        "net geliri bölgelere göre araştır; "
        "bir bölge ayrışırsa kanıtı gördükten sonra başka kırılıma bak"
    )
    source_hash = spans.register_message(message_id="d7-directive", text=text)
    obligation_source = spans.mint_exact(
        message_id="d7-directive",
        surface="net geliri bölgelere göre araştır",
    )
    directive_source = spans.mint_exact(
        message_id="d7-directive",
        surface="bir bölge ayrışırsa kanıtı gördükten sonra başka kırılıma bak",
    )
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="d7-directive-metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="d7-directive-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="d7-directive-dim",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="d7-directive-dim",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    return spans, handles, source_hash, obligation_source, directive_source, metric, dimension


def test_adapt_directive_can_parent_standard_breakdown_without_retyping_user_must():
    spans, handles, source_hash, obligation_source, directive_source, metric, dimension = (
        _breakdown_case()
    )
    result = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    ).evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="d7-directive-a1",
            turn_id="d7-directive",
            request_ref="d7-directive-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_BREAK",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(obligation_source.source_ref,),
                    semantic_handle_refs=(metric.handle_id, dimension.handle_id),
                ),
            ),
            research_directives=(
                ResearchDirective(
                    directive_id="R1",
                    directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
                    parent_obligation_id="U_BREAK",
                    condition=ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
                    source_refs=(directive_source.source_ref,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )

    assert result.status.value == "ACCEPTED"
    assert result.ledger is not None
    assert result.contract is not None
    assert len(result.ledger.items) == 1
    assert result.ledger.items[0].capability_key == ManagerCapabilityKey.BREAKDOWN
    assert result.contract.research_directives[0].parent_obligation_id == "U_BREAK"


def test_adapt_directive_rejects_nonexecutable_presentation_parent():
    spans = SourceSpanRegistry()
    text = "rapor hazırla; sonuç yeni yön gösterirse oraya da bak"
    source_hash = spans.register_message(message_id="d7-directive-report", text=text)
    report_source = spans.mint_exact(
        message_id="d7-directive-report",
        surface="rapor hazırla",
    )
    directive_source = spans.mint_exact(
        message_id="d7-directive-report",
        surface="sonuç yeni yön gösterirse oraya da bak",
    )

    result = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=SemanticHandleRegistry(),
    ).evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="d7-directive-report-a1",
            turn_id="d7-directive-report",
            request_ref="d7-directive-report-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_REPORT",
                    capability_key=ManagerCapabilityKey.REPORT,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(report_source.source_ref,),
                ),
            ),
            research_directives=(
                ResearchDirective(
                    directive_id="R1",
                    directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
                    parent_obligation_id="U_REPORT",
                    condition=ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
                    source_refs=(directive_source.source_ref,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )

    assert result.status.value == "REJECTED"
    assert any(
        "research directive parent must be executable analytical obligation" in reason
        for reason in result.reasons
    )
