"""Day 6.5 capability-binding algebra invariants.

These tests protect the canonical obligation representation itself. They are entirely
provider-free and must pass before any live/stochastic Manager probe is meaningful.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_models import (
    AcceptedTurnContract,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserIntentEnvelope,
    UserObligationLedger,
)
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_projection import StandardProjectionCompiler


TENANT = "tenant-a"
CONTEXT = "ctx-1"


def _handle(
    registry: SemanticHandleRegistry,
    *,
    candidate_id: str,
    kind: str,
    canonical_name: str,
):
    target_kind = SemanticTargetKind(kind)
    return registry.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        resolver_provenance_id=candidate_id,
        target_kind=kind,
        canonical_target=ResolvedSemanticRef(
            candidate_id=candidate_id,
            target_kind=target_kind,
            canonical_name=canonical_name,
            cube_names=("Sales",),
        ),
    )


def _setup(text: str):
    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id="turn-1", text=text)
    source = spans.mint_exact(message_id="turn-1", surface=text)
    handles = SemanticHandleRegistry()
    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )
    return spans, source_hash, source, handles, gate


def _envelope(source_hash: str, *obligations: CandidateObligation):
    return UserIntentEnvelope(
        attempt_id="a1",
        turn_id="turn-1",
        request_ref="req-1",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=tuple(obligations),
    )


def test_performance_with_dimension_is_invalid_atomic_contract():
    _, source_hash, source, handles, gate = _setup(
        "net geliri bölgelere göre göster"
    )
    metric = _handle(
        handles,
        candidate_id="metric-1",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    region = _handle(
        handles,
        candidate_id="region-1",
        kind="dimension",
        canonical_name="Sales.region",
    )
    result = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id, region.handle_id),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "REJECTED"
    assert any(
        "performance contains forbidden semantic kinds: dimension" in reason
        for reason in result.reasons
    )


def test_performance_required_and_breakdown_excluded_is_valid_when_not_requested():
    _, source_hash, source, handles, gate = _setup(
        "net geliri incele ama bölge kırılımı yapma"
    )
    metric = _handle(
        handles,
        candidate_id="metric-2",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    region = _handle(
        handles,
        candidate_id="region-2",
        kind="dimension",
        canonical_name="Sales.region",
    )
    result = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U_PERF",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id,),
            ),
            CandidateObligation(
                obligation_id="X_BREAK",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                polarity=ObligationPolarity.EXCLUDED,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(region.handle_id,),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "ACCEPTED"


def test_required_and_excluded_same_breakdown_effect_requires_clarification():
    _, source_hash, source, handles, gate = _setup(
        "net geliri bölgelere göre göster ama bölge kırılımı yapma"
    )
    metric = _handle(
        handles,
        candidate_id="metric-3",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    region = _handle(
        handles,
        candidate_id="region-3",
        kind="dimension",
        canonical_name="Sales.region",
    )
    result = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U_BREAK",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id, region.handle_id),
            ),
            CandidateObligation(
                obligation_id="X_BREAK",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                polarity=ObligationPolarity.EXCLUDED,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(region.handle_id,),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "NEEDS_CLARIFICATION"
    assert any("conflicting semantic effect group_by/dimension" in r for r in result.reasons)


def test_required_product_breakdown_and_excluded_region_effect_are_disjoint():
    _, source_hash, source, handles, gate = _setup(
        "net geliri ürünlere göre göster ama bölge kırılımı yapma"
    )
    metric = _handle(
        handles,
        candidate_id="metric-4",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    product = _handle(
        handles,
        candidate_id="product-4",
        kind="dimension",
        canonical_name="Sales.product",
    )
    region = _handle(
        handles,
        candidate_id="region-4",
        kind="dimension",
        canonical_name="Sales.region",
    )
    result = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U_PRODUCT",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id, product.handle_id),
            ),
            CandidateObligation(
                obligation_id="X_REGION",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                polarity=ObligationPolarity.EXCLUDED,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(region.handle_id,),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "ACCEPTED"


def test_comparison_without_comparison_handle_is_rejected():
    _, source_hash, source, handles, gate = _setup(
        "net geliri geçen ayla karşılaştır"
    )
    metric = _handle(
        handles,
        candidate_id="metric-5",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    result = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U_COMPARE",
                capability_key=ManagerCapabilityKey.COMPARISON,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id,),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "REJECTED"
    assert any("missing required semantic kinds: comparison" in r for r in result.reasons)


def test_ranking_requires_dimension_and_operation_parameters():
    _, source_hash, source, handles, gate = _setup(
        "en yüksek 2 net geliri göster"
    )
    metric = _handle(
        handles,
        candidate_id="metric-6",
        kind="metric",
        canonical_name="Sales.revenue",
    )

    with pytest.raises((ValidationError, ValueError)):
        CandidateObligation(
            obligation_id="U_RANK_NOPARAM",
            capability_key=ManagerCapabilityKey.RANKING,
            origin=ObligationOrigin.USER_MUST,
            source_refs=(source.source_ref,),
            semantic_handle_refs=(metric.handle_id,),
        )

    missing_dimension = CandidateObligation(
        obligation_id="U_RANK",
        capability_key=ManagerCapabilityKey.RANKING,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(source.source_ref,),
        semantic_handle_refs=(metric.handle_id,),
        ranking_direction="desc",
        ranking_limit=2,
    )
    result = gate.evaluate(
        envelope=_envelope(source_hash, missing_dimension),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert result.status.value == "REJECTED"
    assert any("missing required semantic kinds: dimension" in r for r in result.reasons)


def test_two_valid_standard_obligations_merge_into_one_projection():
    _, source_hash, source, handles, gate = _setup(
        "net geliri göster ve bölgelere göre kır"
    )
    metric = _handle(
        handles,
        candidate_id="metric-7",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    region = _handle(
        handles,
        candidate_id="region-7",
        kind="dimension",
        canonical_name="Sales.region",
    )
    accepted = gate.evaluate(
        envelope=_envelope(
            source_hash,
            CandidateObligation(
                obligation_id="U_PERF",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id,),
            ),
            CandidateObligation(
                obligation_id="U_BREAK",
                capability_key=ManagerCapabilityKey.BREAKDOWN,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id, region.handle_id),
            ),
        ),
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert accepted.status.value == "ACCEPTED"

    compiled = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=accepted.contract,
        ledger=accepted.ledger,
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert compiled.compiled is True
    assert compiled.projection is not None
    assert compiled.projection.metric_handles == (metric.handle_id,)
    assert compiled.projection.dimension_handles == (region.handle_id,)


def test_invalid_atom_cannot_be_laundered_by_valid_obligation_in_compiler():
    handles = SemanticHandleRegistry()
    metric = _handle(
        handles,
        candidate_id="metric-8",
        kind="metric",
        canonical_name="Sales.revenue",
    )
    region = _handle(
        handles,
        candidate_id="region-8",
        kind="dimension",
        canonical_name="Sales.region",
    )

    malformed_performance = ObligationLedgerItem(
        obligation_id="U_BAD",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=(metric.handle_id, region.handle_id),
        introduced_in_version=1,
    )
    valid_breakdown = ObligationLedgerItem(
        obligation_id="U_GOOD",
        capability_key=ManagerCapabilityKey.BREAKDOWN,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src_" + "2" * 24,),
        semantic_handle_refs=(metric.handle_id, region.handle_id),
        introduced_in_version=1,
    )
    ledger = UserObligationLedger(
        lineage_id="atl-test",
        version=1,
        items=(malformed_performance, valid_breakdown),
    )
    contract = AcceptedTurnContract(
        contract_id="atc-test",
        lineage_id="atl-test",
        version=1,
        turn_id="turn-test",
        request_ref="req-test",
        source_message_hash="a" * 64,
        accepted_attempt_id="attempt-test",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U_BAD", "U_GOOD"),
        context_version=CONTEXT,
        accepted_at_iso="2026-09-21T00:00:00+00:00",
    )

    compiled = StandardProjectionCompiler(
        semantic_handles=handles,
    ).compile(
        contract=contract,
        ledger=ledger,
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    assert compiled.compiled is False
    assert any(
        "performance contains forbidden semantic kinds: dimension" in reason
        for reason in compiled.reasons
    )


def test_manager_binding_contract_is_registry_derived_and_semantic_safe():
    contract = {
        row["capability"]: row
        for row in ManagerCapabilityRegistry().manager_contract()
    }
    performance = contract["performance"]
    breakdown = contract["breakdown"]

    assert performance["required_semantic_kinds"] == ["metric"]
    assert "dimension" not in performance["allowed_semantic_kinds"]
    assert breakdown["required_semantic_kinds"] == ["dimension", "metric"]
    assert set(breakdown["allowed_semantic_kinds"]) == {
        "dimension",
        "filter",
        "metric",
        "period",
    }

    blob = str(contract)
    assert "Sales.revenue" not in blob
    assert "sales_omega" not in blob
    assert "net_value_x" not in blob
