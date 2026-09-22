"""Focused provider-free Day 6.5 authority tests."""

from __future__ import annotations

import pytest

from app.v2.acceptance import (
    AcceptedAuthorityConflict,
    AcceptedContractRegistry,
    IntentAcceptanceGate,
)
from app.v2.completion import CompletionGate
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    RepresentabilityDecision,
    ResearchRunTerminal,
    StandardProjection,
    UserIntentEnvelope,
    UserObligationLedger,
)
from app.v2.models import (
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    PeriodKind,
)
from app.v2.representability import RepresentabilityGate
from app.v2.standard_projection import StandardProjectionCompiler
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


def _setup():
    spans = SourceSpanRegistry()
    text = "ürünleri karşılaştır ve makinelerle ilişkisini incele"
    source_hash = spans.register_message(message_id="m1", text=text)
    comparison = spans.mint_exact(message_id="m1", surface="karşılaştır")
    relationship = spans.mint_exact(message_id="m1", surface="makinelerle ilişkisini incele")
    handles = SemanticHandleRegistry()
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-1",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-1",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    base = ResolvedPeriod(
        kind=PeriodKind.THIS_MONTH,
        source_text="bu ay",
        time_dimension="Sales.order_date",
        start="2026-09-01",
        end="2026-09-21",
    )
    comp = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="comparison-1",
        target_kind="comparison",
        canonical_target=ResolvedComparison(
            mode="previous_period",
            source_text="önceki ay",
            base_period=base,
            reference_period=ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="önceki ay",
                time_dimension="Sales.order_date",
                start="2026-08-01",
                end="2026-08-21",
            ),
        ),
    )
    return spans, handles, gate, source_hash, comparison, relationship, metric, comp


def _envelope(*obligations, source_hash: str, attempt: str = "a1", turn: str = "t1"):
    return UserIntentEnvelope(
        attempt_id=attempt,
        turn_id=turn,
        request_ref="req-1",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=tuple(obligations),
    )


def test_runtime_source_refs_and_foreign_handle_are_non_bypassable():
    _, handles, gate, source_hash, comparison, _, metric, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.COMPARISON,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id,),
    )
    bad = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-b",
        context_version="ctx-1",
    )
    assert bad.status.value == "REJECTED"
    assert any("foreign-tenant" in reason for reason in bad.reasons)

    fabricated = obligation.model_copy(update={"source_refs": ("src_" + "0" * 24,)})
    bad_source = gate.evaluate(
        envelope=_envelope(fabricated, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert bad_source.status.value == "REJECTED"


def test_exactly_one_accepted_authority_per_turn():
    _, _, gate, source_hash, comparison, _, metric, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id,),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert accepted.contract is not None
    registry = AcceptedContractRegistry()
    registry.commit(accepted.contract)

    # Exact retry is idempotent.
    registry.commit(accepted.contract)

    # A different semantic authority for the same turn is forbidden.
    conflicting = accepted.contract.model_copy(
        update={"contract_id": "atc_" + "f" * 24}
    )
    with pytest.raises(AcceptedAuthorityConflict):
        registry.commit(conflicting)


def test_standard_lossless_requires_complete_projection():
    _, _, gate, source_hash, comparison, _, metric, comp = _setup()
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.COMPARISON,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(comparison.source_ref,),
        semantic_handle_refs=(metric.handle_id, comp.handle_id),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    incomplete = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=(metric.handle_id,),
        ),
    )
    assert incomplete.decision == RepresentabilityDecision.STANDARD_BUILD_REQUIRED

    complete = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
        projection=StandardProjection(
            obligation_ids=("U1",),
            metric_handles=(metric.handle_id,),
            comparison_handle=comp.handle_id,
        ),
    )
    assert complete.decision == RepresentabilityDecision.STANDARD_LOSSLESS


def test_relationship_remains_research_required():
    _, _, gate, source_hash, _, relationship, _, _ = _setup()
    obligation = CandidateObligation(
        obligation_id="U2",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(relationship.source_ref,),
    )
    accepted = gate.evaluate(
        envelope=_envelope(obligation, source_hash=source_hash, turn="t2"),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    decision = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
    )
    assert decision.decision == RepresentabilityDecision.RESEARCH_REQUIRED


def test_evidence_presence_is_not_verification():
    ledger = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.ACCEPTED,
                source_refs=("src_" + "1" * 24,),
                evidence_refs=("E1",),
                introduced_in_version=1,
            ),
        ),
    )
    result = CompletionGate().evaluate(ledger)
    assert result.allowed is False
    assert result.terminal is None


def test_partial_and_verified_complete_are_distinct():
    base = dict(
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        source_refs=("src_" + "1" * 24,),
        introduced_in_version=1,
    )
    partial = UserObligationLedger(
        lineage_id="atl-1",
        version=1,
        items=(
            ObligationLedgerItem(obligation_id="U1", status=ObligationStatus.VERIFIED, **base),
            ObligationLedgerItem(
                obligation_id="U2",
                status=ObligationStatus.BLOCKED_DATA_GAP,
                blocker="missing data",
                **base,
            ),
        ),
    )
    assert CompletionGate().evaluate(partial).terminal == ResearchRunTerminal.PARTIAL

    complete = UserObligationLedger(
        lineage_id="atl-2",
        version=1,
        items=(
            ObligationLedgerItem(obligation_id="U1", status=ObligationStatus.VERIFIED, **base),
        ),
    )
    result = CompletionGate().evaluate(complete)
    assert result.allowed is True
    assert result.terminal == ResearchRunTerminal.VERIFIED_COMPLETE


def test_repair_supersedes_and_preserves_unrelated_obligations():
    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)

    first_text = "net geliri incele ve bölgelerle ilişkisini değerlendir"
    first_hash = spans.register_message(message_id="turn-1", text=first_text)
    revenue_span = spans.mint_exact(message_id="turn-1", surface="net geliri")
    relation_span = spans.mint_exact(message_id="turn-1", surface="bölgelerle ilişkisini değerlendir")

    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-revenue",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-revenue",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    first = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a1",
            turn_id="turn-1",
            request_ref="repair-session",
            source_message_hash=first_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_REVENUE",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(revenue_span.source_ref,),
                    semantic_handle_refs=(metric.handle_id,),
                ),
                CandidateObligation(
                    obligation_id="U_REL",
                    capability_key=ManagerCapabilityKey.RELATIONSHIP,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(relation_span.source_ref,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert first.status.value == "ACCEPTED"
    assert first.contract is not None and first.ledger is not None

    repair_text = "bölge ilişkisini çıkar"
    repair_hash = spans.register_message(message_id="turn-2", text=repair_text)
    repair_span = spans.mint_exact(message_id="turn-2", surface=repair_text)
    repaired = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="a2",
            turn_id="turn-2",
            request_ref="repair-session",
            source_message_hash=repair_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_REL",
                    capability_key=ManagerCapabilityKey.RELATIONSHIP,
                    origin=ObligationOrigin.USER_MUST,
                    polarity=ObligationPolarity.EXCLUDED,
                    source_refs=(repair_span.source_ref,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
        active_contract=first.contract,
        active_ledger=first.ledger,
    )
    assert repaired.status.value == "ACCEPTED"
    assert repaired.contract is not None and repaired.ledger is not None
    assert repaired.contract.version == 2
    assert repaired.contract.supersedes_contract_id == first.contract.contract_id
    assert "U_REVENUE" in repaired.contract.obligation_ids
    assert "U_REL" in repaired.contract.exclusion_ids

    revenue = next(item for item in repaired.ledger.items if item.obligation_id == "U_REVENUE")
    relation = next(item for item in repaired.ledger.items if item.obligation_id == "U_REL")
    assert revenue.source_refs == (revenue_span.source_ref,)
    assert revenue.introduced_in_version == 1
    assert relation.polarity == ObligationPolarity.EXCLUDED
    assert relation.introduced_in_version == 2


def test_ranking_authority_survives_acceptance_and_compiles_losslessly():
    spans = SourceSpanRegistry()
    text = "bölgelerde en yüksek 2 net geliri göster"
    source_hash = spans.register_message(message_id="rank-1", text=text)
    source = spans.mint_exact(message_id="rank-1", surface=text)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-rank",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-rank",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="dimension-rank",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dimension-rank",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    accepted = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="rank-a1",
            turn_id="rank-1",
            request_ref="rank-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_RANK",
                    capability_key=ManagerCapabilityKey.RANKING,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(source.source_ref,),
                    semantic_handle_refs=(metric.handle_id, dimension.handle_id),
                    ranking_direction="desc",
                    ranking_limit=2,
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert accepted.status.value == "ACCEPTED"
    item = accepted.ledger.items[0]
    assert item.ranking_direction == "desc"
    assert item.ranking_limit == 2

    compiled = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=accepted.contract,
        ledger=accepted.ledger,
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert compiled.compiled is True
    assert compiled.projection is not None
    assert compiled.projection.metric_handles == (metric.handle_id,)
    assert compiled.projection.dimension_handles == (dimension.handle_id,)
    assert compiled.projection.ranking_direction == "desc"
    assert compiled.projection.limit == 2

    decision = RepresentabilityGate().decide(
        contract=accepted.contract,
        ledger=accepted.ledger,
        projection=compiled.projection,
    )
    assert decision.decision == RepresentabilityDecision.STANDARD_LOSSLESS


def test_standard_projection_compiler_rejects_research_and_foreign_handle():
    spans = SourceSpanRegistry()
    text = "net gelir ve hat ilişkisini incele"
    source_hash = spans.register_message(message_id="mix-1", text=text)
    revenue_source = spans.mint_exact(message_id="mix-1", surface="net gelir")
    relation_source = spans.mint_exact(message_id="mix-1", surface="hat ilişkisini incele")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-mix",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-mix",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    accepted = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="mix-a1",
            turn_id="mix-1",
            request_ref="mix-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_PERF",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(revenue_source.source_ref,),
                    semantic_handle_refs=(metric.handle_id,),
                ),
                CandidateObligation(
                    obligation_id="U_REL",
                    capability_key=ManagerCapabilityKey.RELATIONSHIP,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(relation_source.source_ref,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    compiled = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=accepted.contract,
        ledger=accepted.ledger,
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert compiled.compiled is False
    assert any("not standard" in reason for reason in compiled.reasons)

    # Compiler also independently re-validates tenant/context ownership.
    standard_only = accepted.ledger.model_copy(
        update={"items": (accepted.ledger.items[0],)}
    )
    contract_only = accepted.contract.model_copy(
        update={"obligation_ids": ("U_PERF",)}
    )
    foreign = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=contract_only,
        ledger=standard_only,
        tenant_binding="tenant-b",
        context_version="ctx-1",
    )
    assert foreign.compiled is False
    assert any("foreign-tenant" in reason for reason in foreign.reasons)


def test_acceptance_rejects_incomplete_standard_semantic_shape():
    spans = SourceSpanRegistry()
    text = "bölgelere göre net geliri göster"
    source_hash = spans.register_message(message_id="shape-1", text=text)
    source = spans.mint_exact(message_id="shape-1", surface=text)
    handles = SemanticHandleRegistry()
    dimension = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="dim-only",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dim-only",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    result = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="shape-a1",
            turn_id="shape-1",
            request_ref="shape-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_BREAK",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(source.source_ref,),
                    semantic_handle_refs=(dimension.handle_id,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert result.status.value == "REJECTED"
    assert any("missing required semantic kinds: metric" in reason for reason in result.reasons)


def test_excluded_ranking_does_not_require_operation_parameters():
    item = CandidateObligation(
        obligation_id="X_RANK",
        capability_key=ManagerCapabilityKey.RANKING,
        origin=ObligationOrigin.USER_MUST,
        polarity=ObligationPolarity.EXCLUDED,
        source_refs=("src_" + "1" * 24,),
    )
    assert item.ranking_direction is None
    assert item.ranking_limit is None


def test_opposite_breakdown_polarity_conflicts_on_same_semantic_dimension():
    spans = SourceSpanRegistry()
    text = "net geliri bölgelere göre göster ama bölge kırılımı yapma"
    source_hash = spans.register_message(message_id="polarity-1", text=text)
    required_source = spans.mint_exact(message_id="polarity-1", surface="bölgelere göre")
    excluded_source = spans.mint_exact(message_id="polarity-1", surface="bölge kırılımı yapma")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-polarity",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-polarity",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    region = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="region-polarity",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="region-polarity",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    result = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="polarity-a1",
            turn_id="polarity-1",
            request_ref="polarity-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_BREAK",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(required_source.source_ref,),
                    semantic_handle_refs=(metric.handle_id, region.handle_id),
                ),
                CandidateObligation(
                    obligation_id="X_BREAK",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    polarity=ObligationPolarity.EXCLUDED,
                    source_refs=(excluded_source.source_ref,),
                    semantic_handle_refs=(region.handle_id,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert result.status.value == "NEEDS_CLARIFICATION"
    assert any("conflicting semantic effect group_by/dimension" in reason for reason in result.reasons)


def test_required_product_breakdown_and_excluded_region_breakdown_are_not_conflicting():
    spans = SourceSpanRegistry()
    text = "net geliri ürünlere göre göster ama bölge kırılımı yapma"
    source_hash = spans.register_message(message_id="polarity-2", text=text)
    required_source = spans.mint_exact(message_id="polarity-2", surface="ürünlere göre")
    excluded_source = spans.mint_exact(message_id="polarity-2", surface="bölge kırılımı yapma")

    handles = SemanticHandleRegistry()
    def _mint(candidate_id, kind, canonical):
        return handles.mint_from_resolver(
            tenant_binding="tenant-a",
            context_version="ctx-1",
            resolver_provenance_id=candidate_id,
            target_kind=kind,
            canonical_target=ResolvedSemanticRef(
                candidate_id=candidate_id,
                target_kind=SemanticTargetKind(kind),
                canonical_name=canonical,
                cube_names=("Sales",),
            ),
        )

    metric = _mint("metric-disjoint", "metric", "Sales.revenue")
    product = _mint("product-disjoint", "dimension", "Sales.product")
    region = _mint("region-disjoint", "dimension", "Sales.region")

    result = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    ).evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="polarity-a2",
            turn_id="polarity-2",
            request_ref="polarity-request-2",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_PRODUCT",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(required_source.source_ref,),
                    semantic_handle_refs=(metric.handle_id, product.handle_id),
                ),
                CandidateObligation(
                    obligation_id="X_REGION",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    origin=ObligationOrigin.USER_MUST,
                    polarity=ObligationPolarity.EXCLUDED,
                    source_refs=(excluded_source.source_ref,),
                    semantic_handle_refs=(region.handle_id,),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert result.status.value == "ACCEPTED"


def test_model_open_questions_are_advisory_not_clarification_authority():
    spans = SourceSpanRegistry()
    text = "net gelir ne durumda?"
    source_hash = spans.register_message(message_id="open-q-1", text=text)
    source = spans.mint_exact(message_id="open-q-1", surface="net gelir")
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-open-q",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-open-q",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)
    result = gate.evaluate(
        envelope=UserIntentEnvelope(
            attempt_id="open-q-a1",
            turn_id="open-q-1",
            request_ref="open-q-request",
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=(
                CandidateObligation(
                    obligation_id="U_PERF",
                    capability_key=ManagerCapabilityKey.PERFORMANCE,
                    origin=ObligationOrigin.USER_MUST,
                    source_refs=(source.source_ref,),
                    semantic_handle_refs=(metric.handle_id,),
                    open_questions=("model thinks there may be more detail",),
                ),
            ),
        ),
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    assert result.status.value == "ACCEPTED"
